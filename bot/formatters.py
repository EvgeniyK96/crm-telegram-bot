"""Turn CRM API payloads into Telegram messages (HTML parse mode). Pure functions, no I/O."""
from datetime import date
from decimal import Decimal
from html import escape

from .texts import DOC_EN, STATUS_EN, UNIT_EN, t

ORDER_ICONS = {"confirmed": "🟡", "in_production": "🔵", "ready": "🟢"}


def money(value) -> str:
    return f"{Decimal(value):,.0f}".replace(",", " ") + " ₸"


def qty(value) -> str:
    """'40.000' → '40', '59.455' → '59.455'."""
    return format(Decimal(value).normalize(), "f")


def unit(code: str, lang: str) -> str:
    return UNIT_EN.get(code, code) if lang == "en" else code


def _short_date(value: str, lang: str) -> str:
    d = date.fromisoformat(value)
    return d.strftime("%b %d") if lang == "en" else d.strftime("%d.%m")


def target_title(target: dict, lang: str) -> str:
    title = target["title"]
    if lang == "en" and target["type"] in DOC_EN:
        # «Задание ПЗ-00005» → «Production task ПЗ-00005»
        title = f"{DOC_EN[target['type']]} {title.split(' ', 1)[-1]}"
    return escape(title)


def status_label(code: str, fallback: str, lang: str) -> str:
    return STATUS_EN.get(code, fallback) if lang == "en" else fallback


def event(entry: dict, lang: str) -> str:
    target = target_title(entry["target"], lang) if entry.get("target") else ""
    author = escape(entry.get("author_name") or "")
    kind = entry["kind"]
    if kind == "status":
        old_ru, _, new_ru = entry["text"].partition(" → ")
        return t(lang, "ev_status", target=target,
                 old=escape(status_label(entry.get("old_status") or "", old_ru, lang)),
                 new=escape(status_label(entry.get("new_status") or "", new_ru, lang))) + f"\n<i>{t(lang, 'by', author=author)}</i>"
    if kind == "created":
        return t(lang, "ev_created", target=target) + f"\n<i>{t(lang, 'by', author=author)}</i>"
    if kind == "comment":
        return t(lang, "ev_comment", author=author, target=target, text=escape(entry["text"]))
    return t(lang, "ev_post", author=author, text=escape(entry["text"]))


def shortage_alert(row: dict, lang: str) -> str:
    return t(lang, "alert_shortage", name=escape(row["name"]), unit=unit(row["unit_code"], lang),
             available=qty(row["available"]), min=qty(row["min_stock"]), short=qty(row["shortage"]))


def expiry_alert(row: dict, lang: str) -> str:
    key = "alert_expired" if row["status"] == "expired" else "alert_expiring"
    return t(lang, key, name=escape(row["name"]), number=row["number"], balance=qty(row["balance"]),
             unit=unit(row["unit_code"], lang), value=money(row["value"]), days=row["days_left"])


def digest(dash: dict, today: date, lang: str) -> str:
    sales, wh = dash["sales"], dash["warehouse"]
    load = dash.get("production", {}).get("load", [])
    lines = [
        t(lang, "digest_title", date=today.strftime("%d.%m.%Y")),
        "",
        t(lang, "revenue_mtd", value=money(sales["revenue"])),
        t(lang, "gross_profit", value=money(sales["gross_profit"])),
    ]
    if "finance" in dash:
        lines.append(t(lang, "receivables", value=money(dash["finance"]["receivables"]),
                       overdue=money(dash["finance"]["overdue"])))
    lines += [
        "",
        t(lang, "orders_line", **{k: sales["orders"].get(k, 0) for k in ("in_production", "ready", "confirmed")}),
        t(lang, "shops_line", in_progress=sum(d["in_progress"] for d in load), planned=sum(d["planned"] for d in load)),
        "",
        t(lang, "attention"),
    ]
    expired = [r for r in wh["expiring"] if r["status"] == "expired"]
    soon = [r for r in wh["expiring"] if r["status"] != "expired"]
    attention = []
    if wh["below_min"]:
        attention.append(t(lang, "n_shortages", n=len(wh["below_min"])))
    if soon:
        attention.append(t(lang, "n_expiring", n=len(soon)))
    if expired:
        attention.append(t(lang, "n_expired", n=len(expired), value=money(sum(Decimal(r["value"]) for r in expired))))
    lines += attention or [t(lang, "all_good")]
    return "\n".join(lines)


def stock_list(dash: dict, lang: str) -> str:
    rows = dash["warehouse"]["below_min"]
    if not rows:
        return t(lang, "stock_empty")
    return "\n".join([t(lang, "stock_title"), ""] + [
        t(lang, "stock_row", name=escape(r["name"]), available=qty(r["available"]), min=qty(r["min_stock"]),
          unit=unit(r["unit_code"], lang), short=qty(r["shortage"]))
        for r in rows
    ])


def expiry_list(dash: dict, lang: str, limit: int = 15) -> str:
    rows = sorted(dash["warehouse"]["expiring"], key=lambda r: r["days_left"])
    if not rows:
        return t(lang, "exp_empty")
    out = [t(lang, "exp_title"), ""]
    for r in rows[:limit]:
        key = "exp_row_expired" if r["status"] == "expired" else "exp_row_soon"
        out.append(t(lang, key, name=escape(r["name"]), number=r["number"], balance=qty(r["balance"]),
                     unit=unit(r["unit_code"], lang), days=abs(r["days_left"])))
    if len(rows) > limit:
        out.append(f"… +{len(rows) - limit}")
    return "\n".join(out)


def orders_list(orders: list[dict], today: date, lang: str) -> str:
    if not orders:
        return t(lang, "orders_empty")
    out = [t(lang, "orders_title"), ""]
    for o in orders:
        due = _short_date(o["delivery_date"], lang)
        if date.fromisoformat(o["delivery_date"]) < today and o["status"] != "shipped":
            due += f" ⚠️ {t(lang, 'overdue')}"
        out.append(t(lang, "order_row", icon=ORDER_ICONS.get(o["status"], "⚪"), number=o["number"],
                     client=escape(o["client_name"]), status=escape(status_label(o["status"], o["status_display"], lang)),
                     date=due, total=money(o["total"])))
    return "\n".join(out)


def feed(entries: list[dict], lang: str) -> str:
    if not entries:
        return t(lang, "feed_empty")
    return "\n\n".join([t(lang, "feed_title")] + [event(e, lang) for e in entries])
