"""Entry point: python -m bot"""
import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import BotCommand

from . import formatters as fmt
from .config import Config
from .crm import CRMClient, CRMError
from .handlers import build_router, open_button
from .storage import Storage
from .watcher import Watcher

log = logging.getLogger("crm-bot")

COMMANDS = {
    "en": [("today", "Daily digest"), ("orders", "Open orders"), ("stock", "Below minimum stock"),
           ("expiring", "Expiry control"), ("feed", "Latest activity"), ("alerts", "Alerts on/off")],
    "ru": [("today", "Сводка"), ("orders", "Открытые заказы"), ("stock", "Сырьё ниже минимума"),
           ("expiring", "Сроки годности"), ("feed", "Последние события"), ("alerts", "Уведомления вкл/выкл")],
}


async def broadcast(bot: Bot, storage: Storage, text: str, markup=None) -> None:
    for chat_id in storage.subscribers():
        try:
            await bot.send_message(chat_id, text, reply_markup=markup, disable_web_page_preview=True)
        except TelegramForbiddenError:
            storage.unsubscribe(chat_id)  # the user blocked the bot


async def watch_loop(bot: Bot, cfg: Config, watcher: Watcher, storage: Storage) -> None:
    while True:
        try:
            for alert in await watcher.check():
                await broadcast(bot, storage, alert.text, open_button(cfg, alert.path))
        except CRMError as e:
            log.warning("watch: %s", e)
        except Exception:
            log.exception("watch failed")
        await asyncio.sleep(cfg.poll_seconds)


async def digest_loop(bot: Bot, cfg: Config, crm: CRMClient, storage: Storage) -> None:
    while True:
        now = datetime.now(cfg.tz)
        run_at = now.replace(hour=cfg.digest_time.hour, minute=cfg.digest_time.minute, second=0, microsecond=0)
        if run_at <= now:
            run_at += timedelta(days=1)
        await asyncio.sleep((run_at - now).total_seconds())
        try:
            text = fmt.digest(await crm.dashboard(), run_at.date(), cfg.lang)
            await broadcast(bot, storage, text, open_button(cfg, "/analytics"))
        except Exception:
            log.exception("digest failed")


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    cfg = Config.from_env()
    crm = CRMClient(cfg.crm_url, cfg.crm_username, cfg.crm_password)
    storage = Storage(cfg.db_path)
    bot = Bot(cfg.bot_token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(build_router(cfg, crm, storage))
    await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS[cfg.lang]])

    tasks = [asyncio.create_task(watch_loop(bot, cfg, Watcher(crm, storage, cfg.lang), storage)),
             asyncio.create_task(digest_loop(bot, cfg, crm, storage))]
    try:
        await dp.start_polling(bot)
    finally:
        for task in tasks:
            task.cancel()
        await crm.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
