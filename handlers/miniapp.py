import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

import asyncio
import json
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, FSInputFile, CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from common import keyboard

miniapp_router = Router()

# URL веб-приложения
WEBAPP_URL_PIZZA = "https://van4956.github.io/bot_04_copilot_v2/pizza_calculator/"
WEBAPP_URL_RANDOM = "https://van4956.github.io/bot_04_copilot_v2/random_generator/"
WEBAPP_URL_SNAKE = "https://van4956.github.io/bot_04_copilot_v2/snake_game/"

@miniapp_router.message(Command("mini"))
async def cmd_miniapp(message: types.Message, workflow_data: dict):
    user_id = message.from_user.id
    await message.answer(text="Mini apps Telegram",reply_markup=keyboard.del_kb)
    await asyncio.sleep(1)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🍕 Калькулятор", web_app=WebAppInfo(url=WEBAPP_URL_PIZZA)))
    builder.row(InlineKeyboardButton(text="🎲 Рандомайзер", web_app=WebAppInfo(url=WEBAPP_URL_RANDOM)))
    builder.row(InlineKeyboardButton(text="🐍 Змейка", web_app=WebAppInfo(url=WEBAPP_URL_SNAKE)))
    builder.row(InlineKeyboardButton(text="📊 Топ 10", callback_data='mini_leaderboard'))
    builder.row(InlineKeyboardButton(text=_("Назад на главную ↩️"), callback_data='mini_back_to_main'))

    photo = FSInputFile("common/images/image_miniapp.jpg")
    await message.answer_photo(
        photo=photo,
        caption=_("Фабрика по производству мини-приложений:"),
        reply_markup=builder.adjust(2,2,1,).as_markup()
    )
    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/service",
                    command_name="/miniapp")

# callback "назад на главную"
@miniapp_router.callback_query(F.data == 'mini_back_to_main')
async def callback_about(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer(_('Назад на главную ↩️'))
    await asyncio.sleep(1)
    await callback.message.answer(_('Главная панель'), reply_markup=keyboard.start_keyboard())

@miniapp_router.message(F.web_app_data)
async def handle_web_app_data(message: Message,  workflow_data: dict):
    try:
        analytics = workflow_data['analytics']
        data = json.loads(message.web_app_data.data)
        ic(data)

        if data.get('action') == 'game_start' and data.get('game') == 'snake':
            await analytics(user_id=message.from_user.id,
                            category_name="/game",
                            command_name="/snake")

    except json.JSONDecodeError:
        logger.error("Failed to parse web app data")
    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Error processing web app data: %s", e)