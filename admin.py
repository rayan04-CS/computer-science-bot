import os
import aiosqlite
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from database import add_subject, add_resource

router = Router()
DB = "library.db"

def is_admin(message: Message):
    admins = [x.strip() for x in os.getenv("ADMIN_IDS","").split(",") if x.strip()]
    return str(message.from_user.id) in admins

@router.message(Command("addsubject"))
async def addsubject(message: Message):
    if not is_admin(message):
        return
    # /addsubject اسم المادة | الوحدات | السنة | الفصل | المتطلب
    raw = message.text.partition(" ")[2]
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) < 1 or not parts[0]:
        await message.answer("الصيغة:\\n/addsubject اسم المادة | الوحدات | السنة | الفصل | المتطلب")
        return
    name = parts[0]
    units = int(parts[1]) if len(parts)>1 and parts[1].isdigit() else 0
    year = int(parts[2]) if len(parts)>2 and parts[2].isdigit() else 0
    semester = parts[3] if len(parts)>3 else ""
    prereq = parts[4] if len(parts)>4 else ""
    sid = await add_subject(name, units, year, semester, prereq)
    await message.answer(f"✅ تمت إضافة المادة. رقمها: {sid}")

@router.message(Command("addfile"))
async def addfile_help(message: Message):
    if not is_admin(message):
        return
    await message.answer(
        "📤 لإضافة ملف، سنكمل في النسخة التالية بواجهة أزرار كاملة داخل البوت، "
        "بحيث تختاري المادة ثم (المراجع/الشيتات/الأسئلة) ثم ترسلي الملف."
    )

@router.message(F.document)
async def document_received(message: Message):
    if not is_admin(message):
        return
    await message.answer(
        "📄 استلمت الملف. في النسخة الكاملة، البوت سيطلب منك المادة والقسم "
        "ثم يحفظ Telegram file_id تلقائياً."
    )
