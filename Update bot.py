from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# ---------- STATES ----------
class Form(StatesGroup):
    category = State()
    identity = State()
    message = State()

# ---------- KEYBOARDS ----------
menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.add("📢 Taklif", "⚠️ E’tiroz")

identity_kb = ReplyKeyboardMarkup(resize_keyboard=True)
identity_kb.add("📞 Raqam bilan", "👤 Anonim")

# ---------- START ----------
@dp.message_handler(commands="start", state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Assalomu alaykum!\nTaklif yoki e’tirozingizni tanlang:",
        reply_markup=menu_kb
    )
    await Form.category.set()

# ---------- CATEGORY ----------
@dp.message_handler(state=Form.category)
async def choose_category(message: types.Message, state: FSMContext):
    if message.text not in ["📢 Taklif", "⚠️ E’tiroz"]:
        await message.answer("Iltimos, tugmalardan foydalaning.")
        return

    await state.update_data(category=message.text)
    await message.answer(
        "Raqam bilan yuborasizmi yoki anonim?",
        reply_markup=identity_kb
    )
    await Form.identity.set()

# ---------- IDENTITY ----------
@dp.message_handler(state=Form.identity)
async def choose_identity(message: types.Message, state: FSMContext):
    if message.text not in ["📞 Raqam bilan", "👤 Anonim"]:
        await message.answer("Iltimos, tugmalardan foydalaning.")
        return

    await state.update_data(identity=message.text)
    await message.answer("Marhamat, murojaatingizni yozing:")
    await Form.message.set()

# ---------- MESSAGE ----------
@dp.message_handler(state=Form.message)
async def receive_message(message: types.Message, state: FSMContext):
    data = await state.get_data()

    category = data["category"]
    identity = data["identity"]

    user = message.from_user
    contact = user.phone_number if identity == "📞 Raqam bilan" else "Anonim"

    admin_text = (
        f"🆕 Yangi murojaat\n"
        f"📂 Turi: {category}\n"
        f"👤 User: @{user.username}\n"
        f"📞 Aloqa: {contact}\n\n"
        f"📝 Xabar:\n{message.text}"
    )

    await bot.send_message(ADMIN_ID, admin_text)

    await message.answer(
        "Rahmat! Murojaatingiz qabul qilindi ✅\n\n"
        "Yana murojaat qoldirmoqchimisiz?",
        reply_markup=menu_kb
    )

    # 🔥 MUHIM QISM
    await state.finish()
    await Form.category.set()

# ---------- RUN ----------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
