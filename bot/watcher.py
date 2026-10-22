"""Polls the CRM and decides what is new since the last check.

The CRM has no webhooks, so the watcher compares snapshots:
- activity feed: entries with id above the last seen one;
- warehouse: alert keys ("shortage:41", "expired:73") that were not active last time.
A key that disappears (stock replenished, batch written off) is forgotten, so it alerts again if it comes back.
The first run only records a baseline: no flood of old news after deploy.
"""
from dataclasses import dataclass

from . import formatters as fmt
from .crm import CRMClient
from .storage import Storage


@dataclass
class Alert:
    text: str
    path: str | None = None  # CRM web route for an "Open in CRM" button


def warehouse_keys(dash: dict) -> dict[str, dict]:
    wh = dash["warehouse"]
    keys = {f"shortage:{r['item']}": r for r in wh["below_min"]}
    keys |= {f"{r['status']}:{r['lot']}": r for r in wh["expiring"]}
    return keys


class Watcher:
    def __init__(self, crm: CRMClient, storage: Storage, lang: str):
        self.crm, self.storage, self.lang = crm, storage, lang

    async def check(self) -> list[Alert]:
        return await self._activity() + await self._warehouse()

    async def _activity(self) -> list[Alert]:
        entries = await self.crm.activity(limit=30)
        last = self.storage.get("last_activity_id")
        newest = max((e["id"] for e in entries), default=last or 0)
        self.storage.set("last_activity_id", max(newest, last or 0))
        if last is None:
            return []
        fresh = sorted((e for e in entries if e["id"] > last), key=lambda e: e["id"])
        return [Alert(fmt.event(e, self.lang), (e.get("target") or {}).get("path")) for e in fresh]

    async def _warehouse(self) -> list[Alert]:
        current = warehouse_keys(await self.crm.dashboard())
        known = self.storage.get("warehouse_keys")
        self.storage.set("warehouse_keys", sorted(current))
        if known is None:
            return []
        alerts = []
        for key in sorted(current.keys() - set(known)):
            row = current[key]
            if key.startswith("shortage:"):
                alerts.append(Alert(fmt.shortage_alert(row, self.lang), "/stock"))
            else:
                alerts.append(Alert(fmt.expiry_alert(row, self.lang), f"/trace/{row['lot']}"))
        return alerts
