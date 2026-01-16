from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ===== STATES =====
class Form(StatesGroup):
    category = State()
    identity = State()
    text = State()

# ===== KEYBOARDS =====
category_kb = ReplyKeyboardMarkup(resize_keyboard=True)
category_kb.add("📢 Taklif", "⚠️ E’tiroz")

identity_kb = ReplyKeyboardMarkup(resize_keyboard=True)
identity_kb.add("📱 Raqamim bilan", "🙈 Anonim")

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.add("📢 Taklif", "⚠️ E’tiroz")

# ===== HANDLERS =====
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "Assalomu alaykum!\nMurojaat turini tanlang:",
        reply_markup=category_kb
    )
    await Form.category.set()

@dp.message_handler(state=Form.category)
async def choose_category(message: types.Message, state: FSMContext):
    if message.text not in ["📢 Taklif", "⚠️ E’tiroz"]:
        return
    await state.update_data(category=message.text)
    await message.answer(
        "Qanday yubormoqchisiz?",
        reply_markup=identity_kb
    )
    await Form.identity.set()

@dp.message_handler(state=Form.identity)
async def choose_identity(message: types.Message, state: FSMContext):
    if message.text not in ["📱 Raqamim bilan", "🙈 Anonim"]:
        return
    await state.update_data(identity=message.text)
    await message.answer("Marhamat, murojaatingizni yozing:")
    await Form.text.set()

@dp.message_handler(state=Form.text)
async def receive_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user = message.from_user

    if data["identity"] == "🙈 Anonim":
        sender = "Anonim"
        reply_id = None
    else:
        sender = f"@{user.username}" if user.username else f"ID: {user.id}"
        reply_id = user.id

    text_to_admin = (
        f"{data['category']}\n"
        f"👤 {sender}\n"
        f"📝 {message.text}"
    )

    sent = await bot.send_message(ADMIN_ID, text_to_admin)

    if reply_id:
        await sent.reply("📝 Admin javob berishi mumkin")

    await message.answer(
        "Rahmat! Murojaatingiz qabul qilindi ✅",
        reply_markup=menu_kb
    )

    await state.finish()

# ===== ADMIN REPLY =====
@dp.message_handler(lambda m: m.reply_to_message and m.from_user.id == ADMIN_ID)
async def admin_reply(message: types.Message):
    original = message.reply_to_message.text
    if "ID:" in original:
        try:
            user_id = int(original.split("ID:")[1].split("\n")[0])
            await bot.send_message(
                user_id,
                f"📩 Admin javobi:\n{message.text}"
            )
        except:
            pass

# ===== START =====
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
