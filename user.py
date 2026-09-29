from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import subjects, subject, resources

router = Router()

def home_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 المواد", callback_data="subjects")],
        [InlineKeyboardButton(text="🌳 شجرة المواد", callback_data="tree")],
        [InlineKeyboardButton(text="🔍 البحث عن مادة", callback_data="search")],
        [InlineKeyboardButton(text="ℹ️ عن المكتبة", callback_data="about")]
    ])

@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "🎓 <b>Computer Science Student Bot</b>\\n\\n"
        "مكتبة قسم علوم الحاسوب 👩🏻‍💻\\n"
        "اختار من القائمة:",
        reply_markup=home_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "subjects")
async def show_subjects(call: CallbackQuery):
    rows = await subjects()
    buttons = [[InlineKeyboardButton(text=f"💻 {r[1]} — {r[2]} وحدات", callback_data=f"sub:{r[0]}")] for r in rows]
    buttons.append([InlineKeyboardButton(text="🔙 الرئيسية", callback_data="home")])
    await call.message.edit_text("📚 <b>مواد قسم علوم الحاسوب</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("sub:"))
async def show_subject(call: CallbackQuery):
    sid = int(call.data.split(":")[1])
    s = await subject(sid)
    if not s:
        await call.answer("المادة غير موجودة", show_alert=True)
        return
    _, name, units, year, semester, prereq = s
    text = f"💻 <b>{name}</b>\\n\\n"
    text += f"🔢 الوحدات: {units}\\n"
    if year: text += f"🎓 السنة: {year}\\n"
    if semester: text += f"📅 الفصل: {semester}\\n"
    if prereq: text += f"🔗 المتطلب السابق: {prereq}\\n"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 المراجع والكتب", callback_data=f"cat:{sid}:مراجع")],
        [InlineKeyboardButton(text="📝 الشيتات", callback_data=f"cat:{sid}:شيتات")],
        [InlineKeyboardButton(text="📋 الأسئلة", callback_data=f"cat:{sid}:أسئلة")],
        [InlineKeyboardButton(text="🔙 المواد", callback_data="subjects")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("cat:"))
async def show_category(call: CallbackQuery):
    _, sid, category = call.data.split(":")
    rows = await resources(int(sid), category)
    if not rows:
        text = f"📂 <b>{category}</b>\\n\\nلا توجد ملفات مضافة لهذه المادة حتى الآن."
    else:
        text = f"📂 <b>{category}</b>\\n\\n"
        for i, (_, title, _) in enumerate(rows, 1):
            text += f"{i}. {title}\\n"
    buttons = []
    for rid, title, _ in rows:
        buttons.append([InlineKeyboardButton(text=f"📄 {title}", callback_data=f"file:{rid}")])
    buttons.append([InlineKeyboardButton(text="🔙 المادة", callback_data=f"sub:{sid}")])
    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
    await call.answer()

@router.callback_query(F.data.startswith("file:"))
async def send_file(call: CallbackQuery):
    import aiosqlite
    async with aiosqlite.connect("library.db") as db:
        cur = await db.execute("SELECT title,file_id FROM resources WHERE id=?", (int(call.data.split(":")[1]),))
        row = await cur.fetchone()
    if row:
        await call.message.answer_document(row[1], caption=f"📄 {row[0]}")
    await call.answer()

@router.callback_query(F.data == "tree")
async def tree(call: CallbackQuery):
    await call.message.answer(
        "🌳 <b>شجرة مواد قسم علوم الحاسوب</b>\\n\\n"
        "هنا نقدر نضيف صورة الشجرة الأصلية، ومع الوقت نخلي كل مادة قابلة للضغط مباشرة.",
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "about")
async def about(call: CallbackQuery):
    await call.message.edit_text(
        "🎓 <b>Computer Science Student Bot</b>\\n\\n"
        "مكتبة طلاب قسم علوم الحاسوب.\\n"
        "📚 كتب ومراجع\\n📝 شيتات\\n📋 أسئلة\\n🌳 شجرة المواد",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 الرئيسية", callback_data="home")]
        ]),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "home")
async def home(call: CallbackQuery):
    await call.message.edit_text(
        "🎓 <b>Computer Science Student Bot</b>\\n\\nمكتبة قسم علوم الحاسوب 👩🏻‍💻",
        reply_markup=home_keyboard(),
        parse_mode="HTML"
    )
    await call.answer()

@router.callback_query(F.data == "search")
async def search(call: CallbackQuery):
    await call.answer("اكتبي اسم المادة في رسالة جديدة للبحث.", show_alert=True)

@router.message()
async def text_search(message: Message):
    q = message.text.strip().lower()
    if len(q) < 2:
        return
    rows = await subjects()
    matches = [r for r in rows if q in r[1].lower()]
    if not matches:
        return
    buttons = [[InlineKeyboardButton(text=f"💻 {r[1]}", callback_data=f"sub:{r[0]}")] for r in matches]
    await message.answer("🔍 <b>نتائج البحث:</b>", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")
