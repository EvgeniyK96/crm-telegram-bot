"""UI strings. The CRM itself is in Russian; the bot speaks English or Russian (BOT_LANG)."""

TEXTS = {
    "en": {
        "welcome": "👋 <b>CRM Factory bot</b>\n\nI watch the factory CRM and message you when something needs attention: "
                   "raw materials below minimum, batches about to expire, order and production status changes.\n\n"
                   "Alerts are <b>{state}</b> for this chat.",
        "on": "on", "off": "off",
        "subscribed": "🔔 Alerts are on. Daily digest at {time}.",
        "unsubscribed": "🔕 Alerts are off. Commands still work.",
        "denied": "⛔ This bot is private.",
        "crm_down": "⚠️ CRM is not responding, try again in a minute.",
        "help": "<b>Commands</b>\n/today — daily digest\n/stock — raw materials below minimum\n"
                "/expiring — batches expiring or expired\n/orders — open orders by delivery date\n"
                "/feed — latest CRM activity\n/alerts — turn alerts on or off",
        "btn_today": "📊 Today", "btn_stock": "📦 Stock", "btn_expiring": "⏳ Expiry",
        "btn_orders": "🧾 Orders", "btn_feed": "📰 Feed", "btn_open": "Open in CRM",
        "digest_title": "📊 <b>Daily digest · {date}</b>",
        "revenue_mtd": "Revenue this month: <b>{value}</b>",
        "gross_profit": "Gross profit: {value}",
        "receivables": "Receivables: {value} (overdue {overdue})",
        "orders_line": "Orders: {in_production} in production · {ready} ready · {confirmed} confirmed",
        "shops_line": "Production tasks: {in_progress} in progress · {planned} planned",
        "attention": "<b>Needs attention</b>",
        "n_shortages": "📦 Below minimum stock: {n}",
        "n_expiring": "⏳ Expiring soon: {n}",
        "n_expired": "❌ Expired: {n}, worth {value}",
        "all_good": "✅ Nothing needs attention",
        "stock_title": "📦 <b>Below minimum stock</b>",
        "stock_row": "• {name}: {available} of {min} {unit} (short {short})",
        "stock_empty": "✅ All raw materials are above minimum.",
        "exp_title": "⏳ <b>Expiry control</b>",
        "exp_row_expired": "❌ {name} · {number}: {balance} {unit}, expired {days} d ago",
        "exp_row_soon": "⚠️ {name} · {number}: {balance} {unit}, {days} d left",
        "exp_empty": "✅ No batches are close to expiry.",
        "orders_title": "🧾 <b>Open orders</b>",
        "order_row": "{icon} <b>{number}</b> · {client}\n    {status} · due {date} · {total}",
        "orders_empty": "No open orders.",
        "feed_title": "📰 <b>Latest activity</b>",
        "feed_empty": "The feed is empty.",
        "alert_shortage": "📦 <b>Low stock</b>\n{name}: {available} {unit} left, minimum is {min} {unit}.\nShort by <b>{short} {unit}</b>.",
        "alert_expiring": "⏳ <b>Batch expiring</b>\n{name} · {number}\n{balance} {unit} worth {value}, {days} d left.",
        "alert_expired": "❌ <b>Batch expired</b>\n{name} · {number}\n{balance} {unit} worth {value}. Write it off.",
        "ev_created": "🆕 {target} created",
        "ev_status": "🔄 {target}: {old} → {new}",
        "ev_comment": "💬 {author} on {target}:\n{text}",
        "ev_post": "📣 {author}: {text}",
        "by": "by {author}",
        "overdue": "overdue",
    },
    "ru": {
        "welcome": "👋 <b>Бот CRM фабрики</b>\n\nСлежу за CRM и пишу, когда нужно вмешаться: сырьё ниже минимума, "
                   "партии с истекающим сроком, смена статусов заказов и заданий.\n\nУведомления в этом чате: <b>{state}</b>.",
        "on": "включены", "off": "выключены",
        "subscribed": "🔔 Уведомления включены. Сводка каждый день в {time}.",
        "unsubscribed": "🔕 Уведомления выключены. Команды работают.",
        "denied": "⛔ Это закрытый бот.",
        "crm_down": "⚠️ CRM не отвечает, попробуйте через минуту.",
        "help": "<b>Команды</b>\n/today — сводка за день\n/stock — сырьё ниже минимума\n"
                "/expiring — сроки годности\n/orders — открытые заказы по дате отгрузки\n"
                "/feed — последние события CRM\n/alerts — включить или выключить уведомления",
        "btn_today": "📊 Сводка", "btn_stock": "📦 Склад", "btn_expiring": "⏳ Сроки",
        "btn_orders": "🧾 Заказы", "btn_feed": "📰 Лента", "btn_open": "Открыть в CRM",
        "digest_title": "📊 <b>Сводка · {date}</b>",
        "revenue_mtd": "Выручка за месяц: <b>{value}</b>",
        "gross_profit": "Валовая прибыль: {value}",
        "receivables": "Дебиторка: {value} (просрочено {overdue})",
        "orders_line": "Заказы: в производстве {in_production} · готовы {ready} · подтверждены {confirmed}",
        "shops_line": "Задания: в работе {in_progress} · запланировано {planned}",
        "attention": "<b>Требует внимания</b>",
        "n_shortages": "📦 Ниже минимума: {n} поз.",
        "n_expiring": "⏳ Истекает срок: {n} партий",
        "n_expired": "❌ Просрочено: {n} партий на {value}",
        "all_good": "✅ Всё в порядке",
        "stock_title": "📦 <b>Ниже минимального остатка</b>",
        "stock_row": "• {name}: {available} из {min} {unit} (не хватает {short})",
        "stock_empty": "✅ Всё сырьё выше минимума.",
        "exp_title": "⏳ <b>Сроки годности</b>",
        "exp_row_expired": "❌ {name} · {number}: {balance} {unit}, просрочено {days} дн.",
        "exp_row_soon": "⚠️ {name} · {number}: {balance} {unit}, осталось {days} дн.",
        "exp_empty": "✅ Партий с истекающим сроком нет.",
        "orders_title": "🧾 <b>Открытые заказы</b>",
        "order_row": "{icon} <b>{number}</b> · {client}\n    {status} · отгрузка {date} · {total}",
        "orders_empty": "Открытых заказов нет.",
        "feed_title": "📰 <b>Последние события</b>",
        "feed_empty": "Лента пуста.",
        "alert_shortage": "📦 <b>Мало на складе</b>\n{name}: осталось {available} {unit}, минимум {min} {unit}.\nНе хватает <b>{short} {unit}</b>.",
        "alert_expiring": "⏳ <b>Истекает срок</b>\n{name} · {number}\n{balance} {unit} на {value}, осталось {days} дн.",
        "alert_expired": "❌ <b>Партия просрочена</b>\n{name} · {number}\n{balance} {unit} на {value}. Нужно списать.",
        "ev_created": "🆕 Создан документ: {target}",
        "ev_status": "🔄 {target}: {old} → {new}",
        "ev_comment": "💬 {author}, {target}:\n{text}",
        "ev_post": "📣 {author}: {text}",
        "by": "{author}",
        "overdue": "просрочен",
    },
}

# CRM status codes → English labels. In Russian the CRM's own wording is used as is.
STATUS_EN = {
    "new": "New", "draft": "Draft", "confirmed": "Confirmed", "in_production": "In production",
    "ready": "Ready to ship", "shipped": "Shipped", "cancelled": "Cancelled", "planned": "Planned",
    "in_progress": "In progress", "done": "Done", "active": "Active", "archived": "Archived",
    "sent": "Sent", "received": "Received", "partial": "Partially received", "posted": "Posted", "paid": "Paid",
}

# Activity target types → English document names (the CRM's titles are «Заказ ЗК-00009» etc.)
UNIT_EN = {"л": "L", "кг": "kg", "г": "g", "шт": "pcs", "уп": "pk"}

DOC_EN = {
    "sales.salesorder": "Order", "sales.shipment": "Invoice", "production.productiontask": "Production task",
    "purchasing.purchaseorder": "Purchase order", "purchasing.receipt": "Goods receipt", "recipes.recipe": "Recipe",
}


def t(lang: str, key: str, **kw) -> str:
    table = TEXTS.get(lang, TEXTS["en"])
    return table[key].format(**kw) if kw else table[key]
