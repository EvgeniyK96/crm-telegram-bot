"""Settings come from environment variables (see .env.example)."""
import os
from dataclasses import dataclass, field
from datetime import time
from zoneinfo import ZoneInfo


def _ids(raw: str) -> frozenset[int]:
    return frozenset(int(x) for x in raw.replace(" ", "").split(",") if x)


@dataclass(frozen=True)
class Config:
    bot_token: str
    crm_url: str
    crm_username: str
    crm_password: str
    crm_web_url: str = ""
    lang: str = "en"
    allowed_users: frozenset[int] = field(default_factory=frozenset)
    poll_seconds: int = 60
    digest_time: time = time(9, 0)
    tz: ZoneInfo = ZoneInfo("Asia/Almaty")
    db_path: str = "bot.sqlite3"

    @classmethod
    def from_env(cls) -> "Config":
        env = os.environ
        hh, mm = env.get("DIGEST_TIME", "09:00").split(":")
        crm_url = env["CRM_API_URL"].rstrip("/")
        return cls(
            bot_token=env["BOT_TOKEN"],
            crm_url=crm_url,
            crm_username=env["CRM_USERNAME"],
            crm_password=env["CRM_PASSWORD"],
            # Links in messages open the web UI; by default it sits next to /api
            crm_web_url=env.get("CRM_WEB_URL", crm_url.removesuffix("/api")).rstrip("/"),
            lang=env.get("BOT_LANG", "en"),
            allowed_users=_ids(env.get("ALLOWED_USER_IDS", "")),
            poll_seconds=int(env.get("POLL_SECONDS", "60")),
            digest_time=time(int(hh), int(mm)),
            tz=ZoneInfo(env.get("TZ_NAME", "Asia/Almaty")),
            db_path=env.get("DB_PATH", "bot.sqlite3"),
        )
