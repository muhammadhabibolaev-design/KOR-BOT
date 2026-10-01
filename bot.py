import os
import asyncio

from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


# =========================================================
# НАСТРОЙКИ
# =========================================================

# Токен НЕ хранится в коде.
# Render передаст его через переменную BOT_TOKEN.
TOKEN = os.getenv("BOT_TOKEN")

# ID администратора
ADMIN_ID = 7274986315

# Render автоматически передаст PORT.
PORT = int(os.getenv("PORT", "10000"))

# После создания сервиса Render даст адрес вида:
# https://kor-bot.onrender.com
#
# Его добавим в Render как переменную WEBHOOK_URL.
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Секрет webhook.
# Можно задать любой длинный случайный текст в Render.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "kor-webhook-secret")


if not TOKEN:
    raise RuntimeError(
        "Не найдена переменная BOT_TOKEN. "
        "Добавьте BOT_TOKEN в Environment Variables на Render."
    )

if not WEBHOOK_URL:
    raise RuntimeError(
        "Не найдена переменная WEBHOOK_URL. "
        "Добавьте WEBHOOK_URL в Environment Variables на Render."
    )


# =========================================================
# СОСТОЯНИЯ АНКЕТЫ
# =========================================================

class Application(StatesGroup):
    business_name = State()
    business_description = State()
    website_type = State()
    existing_site = State()
    features = State()
    materials = State()
    style = State()
    references = State()
    deadline = State()
    contact = State()


dp = Dispatcher(storage=MemoryStorage())


# =========================================================
# КНОПКА ОТМЕНЫ
# =========================================================

def cancel_button():
    return InlineKeyboardButton(
        text="❌ Отмена",
        callback_data="cancel_application"
    )


def cancel_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [cancel_button()]
        ]
    )


# =========================================================
# ОТМЕНА
# =========================================================

@dp.message(Command("cancel"))
async def cancel_application_command(
    message: Message,
    state: FSMContext
):
    current_state = await state.get_state()

    if current_state is None:
        await message.answer(
            "Сейчас у вас нет активной заявки."
        )
        return

    await state.clear()

    await message.answer(
        "❌ Заявка отменена.\n\n"
        "Чтобы начать новую заявку, нажмите /start"
    )


@dp.callback_query(F.data == "cancel_application")
async def cancel_application_button(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    await state.clear()

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await callback.message.answer(
        "❌ Заявка отменена.\n\n"
        "Чтобы начать новую заявку, нажмите /start"
    )


# =========================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =========================================================

async def go_to_features(
    message: Message,
    state: FSMContext
):
    await state.set_state(Application.features)

    await message.answer(
        "Какие функции нужны на сайте?\n\n"
        "Можно выбрать несколько, затем нажмите «Готово».",
        reply_markup=features_keyboard()
    )


async def go_to_materials(
    message: Message,
    state: FSMContext
):
    await state.set_state(Application.materials)

    await message.answer(
        "Теперь материалы.\n\n"
        "Есть ли у вас логотип и фотографии?",
        reply_markup=materials_keyboard()
    )


async def go_to_style(
    message: Message,
    state: FSMContext
):
    await state.set_state(Application.style)

    await message.answer(
        "🎨 Какой стиль вам нравится?",
        reply_markup=style_keyboard()
    )


# =========================================================
# КЛАВИАТУРЫ
# =========================================================

def start_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Заказать сайт",
                    callback_data="start_application"
                )
            ]
        ]
    )


def website_type_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Лендинг",
                    callback_data="type_landing"
                ),
                InlineKeyboardButton(
                    text="Корпоративный",
                    callback_data="type_corporate"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Интернет-магазин",
                    callback_data="type_shop"
                ),
                InlineKeyboardButton(
                    text="Индивидуальный",
                    callback_data="type_custom"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Не знаю",
                    callback_data="type_unknown"
                )
            ],
            [
                cancel_button()
            ]
        ]
    )


def existing_site_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да",
                    callback_data="site_yes"
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data="site_no"
                )
            ],
            [
                cancel_button()
            ]
        ]
    )


def features_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📞 Звонок",
                    callback_data="feature_call"
                ),
                InlineKeyboardButton(
                    text="✈️ Telegram",
                    callback_data="feature_telegram"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 WhatsApp",
                    callback_data="feature_whatsapp"
                ),
                InlineKeyboardButton(
                    text="📍 Карта",
                    callback_data="feature_map"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Форма",
                    callback_data="feature_form"
                ),
                InlineKeyboardButton(
                    text="📅 Запись",
                    callback_data="feature_booking"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛍 Каталог",
                    callback_data="feature_catalog"
                ),
                InlineKeyboardButton(
                    text="💳 Магазин",
                    callback_data="feature_store"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Готово →",
                    callback_data="features_done"
                )
            ],
            [
                cancel_button()
            ]
        ]
    )


def materials_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Логотип есть",
                    callback_data="logo_yes"
                ),
                InlineKeyboardButton(
                    text="Логотипа нет",
                    callback_data="logo_no"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Фото есть",
                    callback_data="photos_yes"
                ),
                InlineKeyboardButton(
                    text="Фото нет",
                    callback_data="photos_no"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Пропустить",
                    callback_data="materials_skip"
                )
            ],
            [
                cancel_button()
            ]
        ]
    )


def style_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Минимализм",
                    callback_data="style_minimal"
                ),
                InlineKeyboardButton(
                    text="Премиум",
                    callback_data="style_premium"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Тёмный",
                    callback_data="style_dark"
                ),
                InlineKeyboardButton(
                    text="Яркий",
                    callback_data="style_bright"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Строгий",
                    callback_data="style_strict"
                ),
                InlineKeyboardButton(
                    text="Не знаю",
                    callback_data="style_unknown"
                )
            ],
            [
                cancel_button()
            ]
        ]
    )


def contact_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Telegram",
                    callback_data="contact_telegram"
                ),
                InlineKeyboardButton(
                    text="WhatsApp",
                    callback_data="contact_whatsapp"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Телефон",
                    callback_data="contact_phone"
                )
            ],
            [
                cancel_button()
            ]
        ]
    )


def admin_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Связаться",
                    callback_data="admin_contact"
                ),
                InlineKeyboardButton(
                    text="📌 В работе",
                    callback_data="admin_work"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✅ Завершено",
                    callback_data="admin_done"
                )
            ]
        ]
    )


# =========================================================
# START
# =========================================================

@dp.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext
):
    await state.clear()

    await message.answer(
        "KOR / DIGITAL\n\n"
        "Создаём сайты, которые выглядят дорого "
        "и помогают бизнесу выглядеть сильнее.\n\n"
        "От идеи до готового сайта — всё в одном месте.",
        reply_markup=start_keyboard()
    )


# =========================================================
# НАЧАЛО АНКЕТЫ
# =========================================================

@dp.callback_query(F.data == "start_application")
async def start_application(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    await state.clear()
    await state.set_state(Application.business_name)

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await callback.message.answer(
        "Начнём с основ.\n\n"
        "🏢 Как называется ваш бизнес?",
        reply_markup=cancel_keyboard()
    )


# =========================================================
# 1. НАЗВАНИЕ
# =========================================================

@dp.message(Application.business_name)
async def business_name(
    message: Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "Напишите название текстом.",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(
        business_name=message.text.strip()
    )

    await state.set_state(
        Application.business_description
    )

    await message.answer(
        "Принято.\n\n"
        "💼 Чем занимается ваш бизнес?",
        reply_markup=cancel_keyboard()
    )


# =========================================================
# 2. СФЕРА
# =========================================================

@dp.message(Application.business_description)
async def business_description(
    message: Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "Напишите ответ текстом.",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(
        business_description=message.text.strip()
    )

    await state.set_state(
        Application.website_type
    )

    await message.answer(
        "Какой сайт вам нужен?",
        reply_markup=website_type_keyboard()
    )


# =========================================================
# 3. ТИП САЙТА
# =========================================================

@dp.callback_query(
    Application.website_type,
    F.data.startswith("type_")
)
async def website_type(
    callback: CallbackQuery,
    state: FSMContext
):
    types = {
        "type_landing": "Лендинг",
        "type_corporate": "Корпоративный сайт",
        "type_shop": "Интернет-магазин",
        "type_custom": "Индивидуальный проект",
        "type_unknown": "Пока не знаю",
    }

    selected = types.get(callback.data)

    if not selected:
        await callback.answer()
        return

    await state.update_data(
        website_type=selected
    )

    await callback.answer(
        f"✓ {selected}"
    )

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await state.set_state(
        Application.existing_site
    )

    await callback.message.answer(
        "🔗 У вас уже есть сайт?",
        reply_markup=existing_site_keyboard()
    )


# =========================================================
# 4. СУЩЕСТВУЮЩИЙ САЙТ
# =========================================================

@dp.callback_query(
    Application.existing_site,
    F.data == "site_yes"
)
async def site_yes(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await callback.message.answer(
        "Отправьте ссылку на текущий сайт.\n\n"
        "Если ссылки нет, напишите «нет».",
        reply_markup=cancel_keyboard()
    )


@dp.callback_query(
    Application.existing_site,
    F.data == "site_no"
)
async def site_no(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await state.update_data(
        existing_site="Нет"
    )

    await go_to_features(
        callback.message,
        state
    )


@dp.message(Application.existing_site)
async def site_url(
    message: Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "Отправьте ссылку или напишите «нет».",
            reply_markup=cancel_keyboard()
        )
        return

    text = message.text.strip()

    if text.lower() == "нет":
        existing_site = "Нет"
    else:
        existing_site = text

    await state.update_data(
        existing_site=existing_site
    )

    await go_to_features(
        message,
        state
    )


# =========================================================
# 5. ФУНКЦИИ
# =========================================================

@dp.callback_query(
    Application.features,
    F.data.startswith("feature_")
)
async def feature_select(
    callback: CallbackQuery,
    state: FSMContext
):
    feature_names = {
        "feature_call": "Звонок",
        "feature_telegram": "Telegram",
        "feature_whatsapp": "WhatsApp",
        "feature_map": "Карта",
        "feature_form": "Форма заявки",
        "feature_booking": "Онлайн-запись",
        "feature_catalog": "Каталог",
        "feature_store": "Интернет-магазин",
    }

    selected = feature_names.get(callback.data)

    if not selected:
        await callback.answer()
        return

    data = await state.get_data()

    features = data.get("features", [])

    if selected not in features:
        features.append(selected)

        await state.update_data(
            features=features
        )

        await callback.answer(
            f"✓ {selected}"
        )
    else:
        await callback.answer(
            "Уже выбрано"
        )


@dp.callback_query(
    Application.features,
    F.data == "features_done"
)
async def features_done(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    data = await state.get_data()

    if not data.get("features"):
        await callback.message.answer(
            "Выберите хотя бы одну функцию."
        )
        return

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await go_to_materials(
        callback.message,
        state
    )


# =========================================================
# 6. МАТЕРИАЛЫ
# =========================================================

@dp.callback_query(
    Application.materials,
    F.data.in_({
        "logo_yes",
        "logo_no",
        "photos_yes",
        "photos_no"
    })
)
async def materials_select(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()

    logo = data.get("logo")
    photos = data.get("photos")

    if callback.data == "logo_yes":
        logo = "Есть"

    elif callback.data == "logo_no":
        logo = "Нет"

    elif callback.data == "photos_yes":
        photos = "Есть"

    elif callback.data == "photos_no":
        photos = "Нет"

    await state.update_data(
        logo=logo,
        photos=photos
    )

    await callback.answer("Сохранено")

    if logo is not None and photos is not None:

        try:
            await callback.message.edit_reply_markup(
                reply_markup=None
            )
        except Exception:
            pass

        await go_to_style(
            callback.message,
            state
        )


@dp.callback_query(
    Application.materials,
    F.data == "materials_skip"
)
async def materials_skip(
    callback: CallbackQuery,
    state: FSMContext
):
    await callback.answer()

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await state.update_data(
        logo="Не указано",
        photos="Не указано"
    )

    await go_to_style(
        callback.message,
        state
    )


# =========================================================
# 7. СТИЛЬ
# =========================================================

@dp.callback_query(
    Application.style,
    F.data.startswith("style_")
)
async def style(
    callback: CallbackQuery,
    state: FSMContext
):
    styles = {
        "style_minimal": "Минимализм",
        "style_premium": "Премиум",
        "style_dark": "Тёмный",
        "style_bright": "Яркий",
        "style_strict": "Строгий",
        "style_unknown": "Пока не знаю",
    }

    selected = styles.get(callback.data)

    if not selected:
        await callback.answer()
        return

    await state.update_data(
        style=selected
    )

    await callback.answer(
        f"✓ {selected}"
    )

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    await state.set_state(
        Application.references
    )

    await callback.message.answer(
        "🔎 Есть сайты, которые вам нравятся?\n\n"
        "Отправьте ссылку или напишите «нет».",
        reply_markup=cancel_keyboard()
    )


# =========================================================
# 8. РЕФЕРЕНСЫ
# =========================================================

@dp.message(Application.references)
async def references(
    message: Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "Отправьте ссылку или напишите «нет».",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(
        references=message.text.strip()
    )

    await state.set_state(
        Application.deadline
    )

    await message.answer(
        "⏱ Когда примерно нужен готовый сайт?\n\n"
        "Например: «через неделю», "
        "«до конца месяца» или «срок не важен».",
        reply_markup=cancel_keyboard()
    )


# =========================================================
# 9. СРОК
# =========================================================

@dp.message(Application.deadline)
async def deadline(
    message: Message,
    state: FSMContext
):
    if not message.text:
        await message.answer(
            "Напишите срок текстом.",
            reply_markup=cancel_keyboard()
        )
        return

    await state.update_data(
        deadline=message.text.strip()
    )

    await state.set_state(
        Application.contact
    )

    await message.answer(
        "📱 Как удобнее связаться с вами?",
        reply_markup=contact_keyboard()
    )


# =========================================================
# 10. КОНТАКТ
# =========================================================

@dp.callback_query(
    Application.contact,
    F.data.startswith("contact_")
)
async def contact(
    callback: CallbackQuery,
    state: FSMContext
):
    contacts = {
        "contact_telegram": "Telegram",
        "contact_whatsapp": "WhatsApp",
        "contact_phone": "Телефон",
    }

    selected = contacts.get(callback.data)

    if not selected:
        await callback.answer()
        return

    await state.update_data(
        contact=selected
    )

    data = await state.get_data()

    await callback.answer(
        f"✓ {selected}"
    )

    try:
        await callback.message.edit_reply_markup(
            reply_markup=None
        )
    except Exception:
        pass

    features = ", ".join(
        data.get("features", [])
    ) or "Не указано"

    # =====================================================
    # СООБЩЕНИЕ КЛИЕНТУ
    # =====================================================

    client_message = (
        "Заявка принята ✅\n\n"
        "Спасибо! Мы получили вашу заявку.\n"
        "Свяжемся с вами для обсуждения проекта.\n\n"
        "KOR / DIGITAL"
    )

    await callback.message.answer(
        client_message
    )

    # =====================================================
    # ДАННЫЕ КЛИЕНТА
    # =====================================================

    username = (
        f"@{callback.from_user.username}"
        if callback.from_user.username
        else "нет username"
    )

    # =====================================================
    # ЗАЯВКА АДМИНУ
    # =====================================================

    admin_message = (
        "🔥 НОВАЯ ЗАЯВКА KOR\n\n"

        f"👤 Клиент: {callback.from_user.full_name}\n"
        f"📱 Username: {username}\n"
        f"🆔 Telegram ID: {callback.from_user.id}\n\n"

        "━━━━━━━━━━━━━━━━\n\n"

        f"🏢 Бизнес:\n"
        f"{data.get('business_name', 'Не указано')}\n\n"

        f"💼 Сфера:\n"
        f"{data.get('business_description', 'Не указано')}\n\n"

        f"🌐 Тип сайта:\n"
        f"{data.get('website_type', 'Не указано')}\n\n"

        f"🔗 Текущий сайт:\n"
        f"{data.get('existing_site', 'Не указано')}\n\n"

        f"⚙️ Функции:\n"
        f"{features}\n\n"

        f"📁 Логотип:\n"
        f"{data.get('logo', 'Не указано')}\n\n"

        f"📷 Фото:\n"
        f"{data.get('photos', 'Не указано')}\n\n"

        f"🎨 Стиль:\n"
        f"{data.get('style', 'Не указано')}\n\n"

        f"🔎 Референсы:\n"
        f"{data.get('references', 'Не указано')}\n\n"

        f"⏱ Срок:\n"
        f"{data.get('deadline', 'Не указано')}\n\n"

        f"📱 Связь:\n"
        f"{data.get('contact', 'Не указано')}\n\n"

        "━━━━━━━━━━━━━━━━"
    )

    await callback.message.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
        reply_markup=admin_keyboard()
    )

    await state.clear()


# =========================================================
# КНОПКИ АДМИНА
# =========================================================

@dp.callback_query(F.data == "admin_contact")
async def admin_contact(
    callback: CallbackQuery
):
    await callback.answer(
        "Заявка отмечена для связи."
    )


@dp.callback_query(F.data == "admin_work")
async def admin_work(
    callback: CallbackQuery
):
    await callback.answer(
        "Заявка отмечена как «В работе»."
    )


@dp.callback_query(F.data == "admin_done")
async def admin_done(
    callback: CallbackQuery
):
    await callback.answer(
        "Заявка завершена."
    )


# =========================================================
# HEALTH CHECK
# =========================================================

async def health_check(request):
    return web.Response(
        text="KOR / DIGITAL BOT OK",
        status=200
    )


# =========================================================
# TELEGRAM WEBHOOK
# =========================================================

async def telegram_webhook(request):
    # Проверяем секретный заголовок
    secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token"
    )

    if secret != WEBHOOK_SECRET:
        return web.Response(
            text="Unauthorized",
            status=401
        )

    try:
        data = await request.json()

        update = Update.model_validate(data)

        bot = request.app["bot"]

        await dp.feed_update(
            bot,
            update
        )

        return web.Response(
            text="OK",
            status=200
        )

    except Exception as e:
        print("Webhook error:", repr(e))

        return web.Response(
            text="Internal Server Error",
            status=500
        )


# =========================================================
# ЗАПУСК WEB SERVER
# =========================================================

async def on_startup(app):
    bot = app["bot"]

    webhook_url = WEBHOOK_URL.rstrip("/") + "/telegram"

    print("================================")
    print("KOR / DIGITAL BOT")
    print("================================")
    print("Webhook:", webhook_url)
    print("Port:", PORT)

    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET,
        drop_pending_updates=True
    )

    print("Telegram webhook установлен.")


async def on_shutdown(app):
    bot = app["bot"]

    print("Удаляю Telegram webhook...")

    try:
        await bot.delete_webhook()
    except Exception as e:
        print("Ошибка удаления webhook:", repr(e))

    await bot.session.close()

    print("KOR остановлен.")


async def main():

    bot = Bot(token=TOKEN)

    app = web.Application()

    app["bot"] = bot

    # Главная проверка Render
    app.router.add_get(
        "/",
        health_check
    )

    # Health check
    app.router.add_get(
        "/health",
        health_check
    )

    # Telegram
    app.router.add_post(
        "/telegram",
        telegram_webhook
    )

    app.on_startup.append(
        on_startup
    )

    app.on_cleanup.append(
        on_shutdown
    )

    print(
        f"Запускаю HTTP-сервер на 0.0.0.0:{PORT}"
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        PORT
    )

    await site.start()

    print("KOR / DIGITAL работает.")

    # Не даём процессу завершиться
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())