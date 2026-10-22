"""Commands and menu buttons."""
from datetime import datetime

from aiogram import BaseMiddleware, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message, ReplyKeyboardMarkup

from . import formatters as fmt
from .config import Config
from .crm import CRMClient, CRMError
from .storage import Storage
from .texts import t


class AccessMiddleware(BaseMiddleware):
    """With ALLOWED_USER_IDS set, everyone else gets a polite refusal."""

    def __init__(self, allowed: frozenset[int], lang: str):
        self.allowed, self.lang = allowed, lang

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if self.allowed and (user is None or user.id not in self.allowed):
            if isinstance(event, Message):
                await event.answer(t(self.lang, "denied"))
            return None
        return await handler(event, data)


def menu(lang: str) -> ReplyKeyboardMarkup:
    b = lambda key: KeyboardButton(text=t(lang, key))  # noqa: E731
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [b("btn_today"), b("btn_orders")],
        [b("btn_stock"), b("btn_expiring"), b("btn_feed")],
    ])


def open_button(cfg: Config, path: str | None) -> InlineKeyboardMarkup | None:
    if not (cfg.crm_web_url and path):
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=t(cfg.lang, "btn_open"), url=cfg.crm_web_url + path)]])


def build_router(cfg: Config, crm: CRMClient, storage: Storage) -> Router:
    router = Router()
    router.message.middleware(AccessMiddleware(cfg.allowed_users, cfg.lang))
    lang = cfg.lang

    def today():
        return datetime.now(cfg.tz).date()

    async def reply(message: Message, render, path: str | None = None):
        try:
            text = await render()
        except CRMError:
            text, path = t(lang, "crm_down"), None
        await message.answer(text, reply_markup=open_button(cfg, path), disable_web_page_preview=True)

    @router.message(CommandStart())
    async def start(message: Message):
        storage.subscribe(message.chat.id)
        await message.answer(t(lang, "welcome", state=t(lang, "on")), reply_markup=menu(lang))
        await message.answer(t(lang, "help"))

    @router.message(Command("help"))
    async def help_(message: Message):
        await message.answer(t(lang, "help"), reply_markup=menu(lang))

    @router.message(Command("alerts"))
    async def alerts(message: Message):
        if storage.is_subscribed(message.chat.id):
            storage.unsubscribe(message.chat.id)
            await message.answer(t(lang, "unsubscribed"))
        else:
            storage.subscribe(message.chat.id)
            await message.answer(t(lang, "subscribed", time=cfg.digest_time.strftime("%H:%M")))

    @router.message(Command("today"))
    @router.message(F.text == t(lang, "btn_today"))
    async def today_(message: Message):
        async def render():
            return fmt.digest(await crm.dashboard(), today(), lang)
        await reply(message, render, "/analytics")

    @router.message(Command("stock"))
    @router.message(F.text == t(lang, "btn_stock"))
    async def stock(message: Message):
        async def render():
            return fmt.stock_list(await crm.dashboard(), lang)
        await reply(message, render, "/stock")

    @router.message(Command("expiring"))
    @router.message(F.text == t(lang, "btn_expiring"))
    async def expiring(message: Message):
        async def render():
            return fmt.expiry_list(await crm.dashboard(), lang)
        await reply(message, render, "/stock")

    @router.message(Command("orders"))
    @router.message(F.text == t(lang, "btn_orders"))
    async def orders(message: Message):
        async def render():
            return fmt.orders_list(await crm.open_orders(), today(), lang)
        await reply(message, render, "/orders")

    @router.message(Command("feed"))
    @router.message(F.text == t(lang, "btn_feed"))
    async def feed(message: Message):
        async def render():
            return fmt.feed(await crm.activity(limit=8), lang)
        await reply(message, render, "/feed")

    return router
