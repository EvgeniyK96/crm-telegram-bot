from datetime import date

import httpx
import pytest

from bot import formatters as fmt
from bot.crm import CRMClient
from bot.storage import Storage
from bot.watcher import Watcher



def entry(id_, kind="status", **kw):
    base = {"id": id_, "kind": kind, "text": "Запланировано → В работе", "author_name": "Admin",
            "old_status": "planned", "new_status": "in_progress",
            "target": {"type": "production.productiontask", "id": 5, "title": "Задание ПЗ-00005", "path": "/tasks/5"}}
    return base | kw


def dashboard(below_min=(), expiring=()):
    return {"warehouse": {"below_min": list(below_min), "expiring": list(expiring)},
            "sales": {"revenue": "1000", "gross_profit": "400", "orders": {"in_production": 2}},
            "production": {"load": [{"in_progress": 1, "planned": 3}]}}


MILK = {"item": 41, "name": "Молоко 3,2%", "unit_code": "л", "available": "0", "min_stock": "40.000", "shortage": "40.000"}
LOT = {"lot": 73, "number": "П-000073", "name": "Сливки", "unit_code": "л", "balance": "8.000",
       "days_left": 2, "status": "expiring", "value": "17600.00"}


class FakeCRM:
    def __init__(self):
        self.feed, self.dash = [], dashboard()

    async def activity(self, limit=20):
        return sorted(self.feed, key=lambda e: -e["id"])[:limit]

    async def dashboard(self):
        return self.dash


@pytest.fixture
def setup():
    crm = FakeCRM()
    return crm, Watcher(crm, Storage(":memory:"), "en")


async def test_first_run_is_silent_baseline(setup):
    crm, watcher = setup
    crm.feed, crm.dash = [entry(1), entry(2)], dashboard([MILK], [LOT])
    assert await watcher.check() == []


async def test_new_activity_is_reported_once_in_order(setup):
    crm, watcher = setup
    crm.feed = [entry(1)]
    await watcher.check()
    crm.feed += [entry(3, kind="created"), entry(2)]
    alerts = await watcher.check()
    assert [a.path for a in alerts] == ["/tasks/5", "/tasks/5"]
    assert "Planned → In progress" in alerts[0].text and "created" in alerts[1].text
    assert await watcher.check() == []


async def test_warehouse_alert_repeats_only_after_recovery(setup):
    crm, watcher = setup
    await watcher.check()
    crm.dash = dashboard([MILK])
    assert len(await watcher.check()) == 1
    assert await watcher.check() == []  # still short: no repeat
    crm.dash = dashboard()
    await watcher.check()  # replenished
    crm.dash = dashboard([MILK])
    assert "Low stock" in (await watcher.check())[0].text


async def test_expiring_then_expired_are_separate_alerts(setup):
    crm, watcher = setup
    await watcher.check()
    crm.dash = dashboard(expiring=[LOT])
    assert "expiring" in (await watcher.check())[0].text
    crm.dash = dashboard(expiring=[LOT | {"status": "expired", "days_left": -1}])
    alert = (await watcher.check())[0]
    assert "expired" in alert.text and alert.path == "/trace/73"


async def test_crm_client_refreshes_expired_token():
    calls = []

    def handler(request: httpx.Request):
        calls.append(request.url.path)
        if request.url.path.endswith("/jwt/create/"):
            return httpx.Response(200, json={"access": "old", "refresh": "r"})
        if request.url.path.endswith("/jwt/refresh/"):
            return httpx.Response(200, json={"access": "new"})
        if request.headers["Authorization"] == "Bearer old":
            return httpx.Response(401)
        return httpx.Response(200, json={"results": [entry(1)]})

    crm = CRMClient("https://crm.test/api", "u", "p", transport=httpx.MockTransport(handler))
    assert (await crm.activity())[0]["id"] == 1
    assert calls == ["/api/auth/jwt/create/", "/api/activity/", "/api/auth/jwt/refresh/", "/api/activity/"]
    await crm.close()


def test_formatting_escapes_html_and_translates():
    text = fmt.event(entry(1, kind="comment", text="<b>hi</b> & bye"), "en")
    assert "&lt;b&gt;hi&lt;/b&gt; &amp; bye" in text and "Production task ПЗ-00005" in text
    assert fmt.money("126000.00") == "126 000 ₸"
    assert fmt.qty("59.455") == "59.455" and fmt.qty("40.000") == "40"
    assert "0 of 40 L" in fmt.stock_list(dashboard([MILK]), "en")


def test_orders_overdue_mark():
    orders = [{"number": "ЗК-1", "client_name": "Shop", "status": "ready", "status_display": "Готов",
               "delivery_date": "2026-10-20", "total": "100"}]
    assert "overdue" in fmt.orders_list(orders, date(2026, 10, 23), "en")
    assert "overdue" not in fmt.orders_list(orders, date(2026, 10, 20), "en")
