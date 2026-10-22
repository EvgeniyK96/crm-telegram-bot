"""Read-only client for the CRM REST API (Django + DRF, JWT auth)."""
import httpx

OPEN_ORDER_STATUSES = ("confirmed", "in_production", "ready")


class CRMError(RuntimeError):
    pass


class CRMClient:
    def __init__(self, base_url: str, username: str, password: str, *, transport=None):
        self._creds = {"username": username, "password": password}
        self._access: str | None = None
        self._refresh: str | None = None
        self._http = httpx.AsyncClient(base_url=base_url, timeout=30, transport=transport)

    async def close(self) -> None:
        await self._http.aclose()

    async def _login(self) -> None:
        r = await self._http.post("/auth/jwt/create/", json=self._creds)
        if r.status_code != 200:
            raise CRMError(f"CRM login failed: {r.status_code}")
        tokens = r.json()
        self._access, self._refresh = tokens["access"], tokens["refresh"]

    async def _renew(self) -> None:
        # Access tokens are short-lived: try the refresh token first, log in again if it expired too
        if self._refresh:
            r = await self._http.post("/auth/jwt/refresh/", json={"refresh": self._refresh})
            if r.status_code == 200:
                self._access = r.json()["access"]
                return
        await self._login()

    async def get(self, path: str, **params) -> dict:
        if not self._access:
            await self._login()
        for attempt in range(2):
            r = await self._http.get(path, params=params, headers={"Authorization": f"Bearer {self._access}"})
            if r.status_code == 401 and attempt == 0:
                await self._renew()
                continue
            if r.status_code != 200:
                raise CRMError(f"GET {path}: {r.status_code}")
            return r.json()
        raise CRMError(f"GET {path}: unauthorized")

    async def dashboard(self, date_from: str | None = None, date_to: str | None = None) -> dict:
        params = {k: v for k, v in {"date_from": date_from, "date_to": date_to}.items() if v}
        return await self.get("/reports/dashboard/", **params)

    async def activity(self, limit: int = 20) -> list[dict]:
        """Latest feed entries, newest first."""
        return (await self.get("/activity/", page_size=limit))["results"]

    async def open_orders(self) -> list[dict]:
        data = await self.get("/sales/orders/", status=list(OPEN_ORDER_STATUSES),
                              ordering="delivery_date", page_size=50)
        return data["results"]
