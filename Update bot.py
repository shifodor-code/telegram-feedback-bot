from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# ================= STATES =================
class Form(StatesGroup):
    category = State()
    identity = State()
    contact = State()
    text = State()

# ================= KEYBOARDS =================
category_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
category_kb.add("📢 Taklif", "⚠️ E’tiroz")

identity_kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
identity_kb.add("📞 Raqam bilan", "👤 Anonim")

contact_kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
contact_kb.add(types.KeyboardButton("📲 Raqamni yuborish", request_contact=True))

# ================= START =================
@dp.message_handler(commands="start", state="*")
async def start(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        "Assalomu alaykum!\nTaklif yoki e’tirozingizni tanlang:",
        reply_markup=category_kb
    )
    await Form.category.set()

# ================= CATEGORY =================
@dp.message_handler(lambda m: m.text in ["📢 Taklif", "⚠️ E’tiroz"], state=Form.category)
async def choose_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer(
        "Raqam bilan yuborasizmi yoki anonim?",
        reply_markup=identity_kb
    )
    await Form.identity.set()

# ================= IDENTITY =================
@dp.message_handler(lambda m: m.text == "📞 Raqam bilan", state=Form.identity)
async def with_number(message: types.Message, state: FSMContext):
    await message.answer(
        "Raqamingizni yuboring:",
        reply_markup=contact_kb
    )
    await Form.contact.set()

@dp.message_handler(lambda m: m.text == "👤 Anonim", state=Form.identity)
async def anonymous(message: types.Message, state: FSMContext):
    await state.update_data(contact="Anonim")
    await message.answer("Marhamat, murojaatingizni yozing:")
    await Form.text.set()

# ================= CONTACT =================
@dp.message_handler(content_types=types.ContentType.CONTACT, state=Form.contact)
async def get_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(contact=phone)
    await message.answer("Marhamat, murojaatingizni yozing:")
    await Form.text.set()

# ================= TEXT =================
@dp.message_handler(state=Form.text)
async def receive_text(message: types.Message, state: FSMContext):
    data = await state.get_data()

    category = data["category"]
    contact = data["contact"]

    text = (
    f"🆕 Yangi murojaat\n\n"
    f"📌 Turi: {category}\n"
    f"🆔 User ID: {message.from_user.id}\n"
    f"👤 Username: @{message.from_user.username or 'username yo‘q'}\n"
    f"📞 Aloqa: {contact}\n\n"
    f"📝 Matn:\n{message.text}"
)

    sent = await bot.send_message(ADMIN_ID, text)
    # foydalanuvchi ID ni admin xabariga bog‘lab qo‘yamiz
    await sent.reply(f"USER_ID:{message.from_user.id}")

    await message.answer(
        "Rahmat! Murojaatingiz qabul qilindi ✅\n/start buyrug‘i bilan yana yuborishingiz mumkin",
        reply_markup=types.ReplyKeyboardRemove()
    )

    await state.finish()

# ================= ADMIN REPLY =================
@dp.message_handler(lambda m: m.reply_to_message and m.from_user.id == ADMIN_ID)
async def admin_reply(message: types.Message):
    if "USER_ID:" in message.reply_to_message.text:
        user_id = int(message.reply_to_message.text.split("USER_ID:")[1])
        await bot.send_message(
            user_id,
            f"📩 Administrator javobi:\n\n{message.text}"
        )

# ================= RUN =================
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
