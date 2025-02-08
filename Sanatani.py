import aiohttp, aiofiles, asyncio, base64, logging
import os, platform, random, re, socket
import sys, time, textwrap
import yt_dlp

from os import getenv
import asyncio
from io import BytesIO
from time import strftime
from functools import partial
from dotenv import load_dotenv
from datetime import datetime
from typing import Union, List, Pattern
from logging.handlers import RotatingFileHandler
from pathlib import Path

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from motor.motor_asyncio import AsyncIOMotorClient as _mongo_async_
from pyrogram import filters
from pyrogram import Client, filters as pyrofl
from pytgcalls import PyTgCalls, filters as pytgfl
from pyrogram.types import Message ,CallbackQuery

from pyrogram import idle, __version__ as pyro_version
from pytgcalls.__version__ import __version__ as pytgcalls_version

from ntgcalls import TelegramServerError
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import (
    ChatAdminRequired,
    FloodWait,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)
from pytgcalls.exceptions import NoActiveGroupCall
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls.types import ChatUpdate, Update, GroupCallConfig 
from pytgcalls.types import Call, MediaStream, AudioQuality, VideoQuality

from PIL import Image, ImageDraw, ImageEnhance
from PIL import ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch



class Wheel:
    def __init__(self):
        self.is_active = False
        self.participants = []
        self.prize = ""

# ایجاد نمونه از کلاس
wheel = Wheel()

loop = asyncio.get_event_loop()


# versions dictionary
__version__ = {
    "AP": "1.0.0 Mini",
    "Python": platform.python_version(),
    "Pyrogram": pyro_version,
    "PyTgCalls": pytgcalls_version,
}
COOKIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "youtube.cookies.txt")

# تنظیمات پایه برای yt-dlp
ydl_config = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# اضافه کردن کوکی اگر فایل وجود داشته باشد
if os.path.exists(COOKIES_FILE):
    ydl_config['cookiefile'] = COOKIES_FILE

# تنظیمات جستجو
ydl_opts = ydl_config.copy()

# تنظیمات دانلود
download_opts = ydl_config.copy()
download_opts.update({
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'prefer_ffmpeg': True,
    'keepvideo': False,
    'outtmpl': '%(title)s.%(ext)s',
})
calls = {}
# store all logs
logging.basicConfig(
    format="[%(name)s]:: %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
    handlers=[
        RotatingFileHandler("logs.txt", maxBytes=(1024 * 1024 * 5), backupCount=10),
        logging.StreamHandler(),
    ],
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)

LOGGER = logging.getLogger("SYSTEM")


# config variables
if os.path.exists("Config.env"):
    load_dotenv("Config.env")


API_ID = int(getenv("API_ID", "29135868"))
API_HASH = getenv("API_HASH", "04dc2f1bdf0049f6990ed2eb3d10f2ec")
BOT_TOKEN = getenv("BOT_TOKEN", "7590617310:AAGs56QoaLWXlz6rcbLs_YUXHD8Az9gpiiM")
STRING_SESSION = getenv("STRING_SESSION", "")
MONGO_DB_URL = getenv("MONGO_DB_URL", "mongodb+srv://ranger1:mohaMmoha900@cluster2.24a45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2")
OWNER_ID = int(getenv("OWNER_ID", "6543211255"))
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "-1002421251357"))
START_IMAGE_URL = getenv("START_IMAGE_URL", "https://files.catbox.moe/dclvrs.mp4")
REPO_IMAGE_URL = getenv("REPO_IMAGE_URL", "https://files.catbox.moe/nswh7s.jpg")
STATS_IMAGE_URL = getenv("STATS_IMAGE_URL", "https://files.catbox.moe/2hgoq7.jpg")
API_URL = "https://free-api.chatgpt4.ai/chat/completions"



# اتصال به دیتابیس

ACTIVE_AUDIO_CHATS = []
ACTIVE_VIDEO_CHATS = []
ACTIVE_MEDIA_CHATS = []
volume_level = {}  # {chat_id: volume}

MUSIC_HELP = """
🎵 **دستورات پخش موزیک:**

◈ `پخش` یا `play`
› پخش موزیک در گروه

◈ `مکث` یا `pause` 
› توقف موقت پخش

◈ `ادامه` یا `resume`
› ادامه پخش موزیک

◈ `بعدی` یا `skip`
› رد کردن آهنگ فعلی

◈ `اتمام` یا `end`
› پایان پخش و خروج
"""

YOUTUBE_HELP = """
📥 **دستورات دانلود:**

◈ `دانلود` یا `dl`
› دانلود از یوتیوب
مثال: `دانلود shape of you`

◈ `یوتیوب` یا `yt`
› جستجو در یوتیوب
مثال: `یوتیوب shape of you`
"""

ADMIN_HELP = """
👮‍♂️ **دستورات مدیریت:**

◈ `صدا` یا `vol`
› تنظیم صدای پخش (0-200)

◈ `بن` یا `ban`
› محدود کردن کاربر

◈ `آنبن` یا `unban`
› رفع محدودیت کاربر
"""

PLAYLIST_HELP = """
📋 **دستورات پلی‌لیست:**

◈ `لیست` یا `queue`
› نمایش صف پخش

◈ `پاک` یا `clean`
› پاک کردن صف پخش

◈ `حذف` یا `del`
› حذف یک آهنگ از صف
"""
QUEUE = {}

# Command & Callback Handlers
def get_wheel_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎯 شرکت در قرعه‌کشی", callback_data="join_wheel")],
        [InlineKeyboardButton("📜 لیست شرکت‌کنندگان", callback_data="participants_list")],
        [InlineKeyboardButton("🎲 چرخاندن گردونه", callback_data="spin_wheel")]
    ])

def cdx(commands: Union[str, List[str]]):
    # حذف / از لیست پیشوندها
    return pyrofl.command(commands, ["!", ".",""])


def cdz(commands: Union[str, List[str]]):
    # حذف / از لیست پیشوندها 
    return pyrofl.command(commands, ["", "!", "."])


def rgx(pattern: Union[str, Pattern]):
    return pyrofl.regex(pattern)


bot_owner_only = pyrofl.user(OWNER_ID)


# all clients

app = Client(
    name="App",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=str(STRING_SESSION),
)

bot = Client(
    name="Bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

call = PyTgCalls(app)
call_config = GroupCallConfig(auto_start=False)

mongo_async_cli = _mongo_async_(MONGO_DB_URL)
mongodb = mongo_async_cli.adityaxdb
subscriptions = mongodb.subscriptions

# store start time
__start_time__ = time.time()


# start and run


async def main():
    LOGGER.info("🐬 Updating Directories ...")
    if "cache" not in os.listdir():
        os.mkdir("cache")
    if "cookies.txt" not in os.listdir():
        LOGGER.info("⚠️ 'cookies.txt' - Not Found❗")
        sys.exit()
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    for file in os.listdir():
        if file.endswith(".session"):
            os.remove(file)
    for file in os.listdir():
        if file.endswith(".session-journal"):
            os.remove(file)
    LOGGER.info("✅ All Directories Updated.")
    await asyncio.sleep(1)
    LOGGER.info("🌐 Checking Required Variables ...")
    if API_ID == 0:
        LOGGER.info("❌ 'API_ID' - Not Found ‼️")
        sys.exit()
    if not API_HASH:
        LOGGER.info("❌ 'API_HASH' - Not Found ‼️")
        sys.exit()
    if not BOT_TOKEN:
        LOGGER.info("❌ 'BOT_TOKEN' - Not Found ‼️")
        sys.exit()
    if not STRING_SESSION:
        LOGGER.info("❌ 'STRING_SESSION' - Not Found ‼️")
        sys.exit()

    if not MONGO_DB_URL:
        LOGGER.info("'MONGO_DB_URL' - Not Found !!")
        sys.exit()
    try:
        await mongo_async_cli.admin.command('ping')
    except Exception:
        LOGGER.info("❌ 'MONGO_DB_URL' - Not Valid !!")
        sys.exit()
    LOGGER.info("✅ Required Variables Are Collected.")
    await asyncio.sleep(1)
    LOGGER.info("🌀 Starting All Clients ...")
    try:
        await bot.start()
    except Exception as e:
        LOGGER.info(f"🚫 Bot Error: {e}")
        sys.exit()
    if LOG_GROUP_ID != 0:
        try:
            await bot.send_message(LOG_GROUP_ID, "**🤖 Bot Started.**")
        except Exception:
            pass
    LOGGER.info("✅ Bot Started.")
    try:
        await app.start()
    except Exception as e:
        LOGGER.info(f"🚫 Assistant Error: {e}")
        sys.exit()
    try:
        await app.join_chat("AdityaServer")
        await app.join_chat("AdityaDiscus")
    except Exception:
        pass
    if LOG_GROUP_ID != 0:
        try:
            await app.send_message(LOG_GROUP_ID, "**🦋 Assistant Started.**")
        except Exception:
            pass
    LOGGER.info("✅ Assistant Started.")
    try:
        await call.start()
    except Exception as e:
        LOGGER.info(f"🚫 PyTgCalls Error: {e}")
        sys.exit()
    LOGGER.info("✅ PyTgCalls Started.")
    await asyncio.sleep(1)
    LOGGER.info("✅ Sucessfully Hosted Your Bot !!")
    LOGGER.info("✅ Now Do Visit: @ATRINMUSIC_TM !!")
    await idle()









# Some Required Functions ...!!


def _netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096).decode("utf-8").strip("\n\x00")
        if not data:
            break
        return data
    s.close()

async def get_youtube_info(url):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception as e:
        print(f"خطا در دریافت اطلاعات ویدیو: {str(e)}")
        return None
async def paste_queue(content):
    loop = asyncio.get_running_loop()
    link = await loop.run_in_executor(None, partial(_netcat, "ezup.dev", 9999, content))
    return link

async def is_call_active(chat_id):
    try:
        # بررسی مستقیم از گروه‌های در حال پخش
        return await call.get_active_calls() and chat_id in [
            chat.chat_id for chat in call.active_calls
        ]
    except Exception:
        return False

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time





# Mongo Database Functions

chatsdb = mongodb.chatsdb
usersdb = mongodb.usersdb


async def generate_ai_response(prompt: str) -> str:
    try:
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2000
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(API_URL, json=data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    return "متاسفانه در دریافت پاسخ خطایی رخ داد."
                    
    except Exception as e:
        print(f"AI API Error: {str(e)}")
        return "متاسفانه در دریافت پاسخ خطایی رخ داد."
# Served Chats
async def save_subscription(chat_id: int, months: int):
    expiry_date = datetime.now() + timedelta(days=30*months)
    subscription_data = {
        "chat_id": chat_id,
        "is_installed": True,
        "install_date": datetime.now(),
        "expiry_date": expiry_date,
        "months": months
    }
    
    await subscriptions.update_one(
        {"chat_id": chat_id},
        {"$set": subscription_data},
        upsert=True
    )

async def get_subscription(chat_id: int):
    return await subscriptions.find_one({"chat_id": chat_id})

async def check_subscription(chat_id: int):
    subscription = await get_subscription(chat_id)
    if not subscription:
        return False
    
    if not subscription.get("is_installed", False):
        return False
        
    if datetime.now() > subscription["expiry_date"]:
        return False
        
    return True
async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True

async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False
async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


async def add_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    return await chatsdb.insert_one({"chat_id": chat_id})


async def add_referral(user_id: int, referrer_id: int):
    await referral_collection.update_one(
        {"user_id": user_id},
        {"$set": {"referrer_id": referrer_id, "date": datetime.now()}},
        upsert=True
    )
    # اضافه کردن 10 امتیاز به معرف
    await add_points(referrer_id, 10)

async def add_points(user_id: int, points: int):
    await points_collection.update_one(
        {"user_id": user_id},
        {"$inc": {"points": points}},
        upsert=True
    )

async def get_points(user_id: int):
    user = await points_collection.find_one({"user_id": user_id})
    return user["points"] if user else 0
# Served Users

async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return await usersdb.insert_one({"user_id": user_id})

async def is_call_active(chat_id: int) -> bool:
    return chat_id in calls and calls[chat_id].is_connected

async def set_call_volume(chat_id: int, volume: int):
    if chat_id in calls:
        await calls[chat_id].set_volume(volume)

async def play_audio(chat_id: int, audio_file: str):
    try:
        await start_call(chat_id)
        group_call = calls[chat_id]
        
        if not group_call.is_connected:
            await group_call.join(chat_id)
        
        await group_call.start_audio(AudioPiped(audio_file))
        return True
    except Exception as e:
        print(f"خطای پخش صوت: {str(e)}")
        return False

async def play_video(chat_id: int, video_file: str):
    try:
        await start_call(chat_id)
        group_call = calls[chat_id]
        
        if not group_call.is_connected:
            await group_call.join(chat_id)
        
        await group_call.start_video(AudioVideoPiped(video_file))
        return True
    except Exception as e:
        print(f"خطای پخش ویدیو: {str(e)}")
        return False

async def start_call(chat_id):
    if chat_id not in calls:
        group_call = GroupCallFactory().get_group_call()
        calls[chat_id] = group_call




CBUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("˹ گروه پشتیبانی ˼", url="https://t.me/ATRINMUSIC_TM1")
        ],
        [
            InlineKeyboardButton("˹ کانال ما ˼", url="https://t.me/ATRINMUSIC_TM"),
            InlineKeyboardButton("˹ همه ربات‌ها ˼", url="https://t.me/+")
        ],
        [
            InlineKeyboardButton("↺ بازگشت ↻", callback_data="back_to_home")
        ]
    ]
)

# Define ABUTTON outside of the HELP_X string
ABUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton("↺ ʙᴧᴄᴋ ↻", callback_data="back_to_home")
        ]
    ]
)

HELP_C = """```
⌬ ๏ ʟᴇᴛ's ɪɴᴛʀᴏᴅᴜᴄᴇ ᴍᴜsɪᴄ ʙᴏᴛ```

**⌬ [【◖ ʜᴀʀᴍᴏɴʏ ◗ 】 🚩](https://t.me/atrinmusic_tm) ɪs ᴏɴᴇ ᴏғ ᴛʜᴇ ʙᴇsᴛ ᴍᴜsɪᴄ | ᴠɪᴅᴇᴏ sᴛꝛᴇᴀᴍɪɴɢ ʙᴏᴛ ᴏɴ ᴛᴇʟᴇɢꝛᴧᴍ ғᴏꝛ ʏᴏᴜꝛ ɢꝛᴏᴜᴘs ᴀɴᴅ ᴄʜᴧɴɴᴇʟ**
```\n⌬ ʙᴇsᴛ ғᴇᴀsɪʙɪʟɪᴛʏ ᴏɴ ᴛᴏᴘ  ?```

**␥ بهترین کیفیت صدا
␥ پشتیبانی از صدای نسخه 2.0 
␥ بدون مشکل مسدودی IP یوتیوب
␥ بر پایه جدیدترین نسخه پایروگرام
␥ بدون تبلیغات | آپتایم بالا
␥ سرور با زیرساخت قدرتمند
␥ هسته بازنویسی شده | بهینه‌سازی شده
␥ بدون تاخیر و قطعی
␥ امکانات بیشتر........


ᴀʟʟ ᴛʜᴇ ғᴇᴀᴛᴜʀᴇs ᴀʀᴇ ᴡᴏʀᴋɪɴɢ ғɪɴᴇ

⌬ ᴍᴏʀᴇ ɪɴғᴏ. [ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ](https://t.me/ATRINMUSIC_TM)**"""

HELP_X = """```
    【◖ ʀᴀɴɢᴇʀ ◗ 】 🚩 ᴍᴇɴᴜ```
**ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴡɪᴛʜ : /**
␥ پخش - پخش موزیک مورد علاقه شما [صوتی]

␥ /vplay - پخش موزیک مورد علاقه شما [تصویری]

␥ /pause - توقف پخش [صوتی و تصویری]

␥ /resume - ادامه پخش [صوتی و تصویری]

␥ /skip - رد کردن آهنگ [صوتی و تصویری]

␥ /end - [اتمام]تمام کردن تصویری و صوتی


V ɪ s ɪ ᴛ - [ʜᴇʀᴇ](https://t.me/linkdonitehranasli)"""

# Callback query handler
@bot.on_callback_query(filters.regex("UTTAM_RATHORE"))
async def helper_cb(client, CallbackQuery):
    await CallbackQuery.edit_message_text(HELP_X, reply_markup=ABUTTON)

@bot.on_callback_query(filters.regex("UTTAM"))
async def helper_cb(client, CallbackQuery):
    await CallbackQuery.edit_message_text(HELP_C, reply_markup=CBUTTON)


# Callback & Message Queries





@bot.on_message(filters.command(["start", "help"]) & filters.private)
async def start_message_private(client, message):
    user_id = message.from_user.id
    mention = message.from_user.mention
    await add_served_user(user_id)

    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:5] == "verify":
            pass  # handle verification if needed
    else:
        # ارسال پیام موقت برای نمایش پیشرفت
        baby = await message.reply_text("[□□□□□□□□□□] 0%")

        # شبیه‌سازی نوار پیشرفت
        progress = ["[■□□□□□□□□□] 10%", "[■■□□□□□□□□] 20%", "[■■■□□□□□□□] 30%", "[■■■■□□□□□□] 40%", "[■■■■■□□□□□] 50%", 
                    "[■■■■■■□□□□] 60%", "[■■■■■■■□□□] 70%", "[■■■■■■■■□□] 80%", "[■■■■■■■■■□] 90%", "[■■■■■■■■■■] 100%"]
        for i, step in enumerate(progress):
            await baby.edit_text(f"**{step} ↺{10 * (i+1)}%**")
            await asyncio.sleep(0.005)

        await baby.edit_text("**❖ در حال بارگذاری هارمونی...**")
        await asyncio.sleep(1)
        await baby.delete()

        caption = """🎵 به ربات موزیک هارمونی خوش آمدید!

🌟 من یک ربات موزیک پیشرفته با امکانات فوق‌العاده هستم.

━━━━━━━━━━━━━━━━━━
☀️ ویژگی‌های منحصر به فرد:
• پخش موزیک با کیفیت بالا
• پشتیبانی از پلتفرم‌های مختلف
• سیستم صف پیشرفته
• مدیریت آسان ویدئوچت
• جستجوی هوشمند موزیک
• پخش موزیک بدون وقفه
━━━━━━━━━━━━━━━━━━

⚡️ سرعت فوق‌العاده بالا
🎯 دقت بالا در جستجو
🔊 کیفیت صدای عالی
⚙️ پنل مدیریتی پیشرفته

📱 برنامه‌نویسی شده توسط تیم رنجر
𝙍𝘼𝙉𝙂𝙀𝙍

╭─────────────╮
┅━─⊰ 𝙍𝘼𝙉𝙂𝙀𝙍 ™⊱─━┅ 
╰─────────────╯"""

        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="➕ افزودن به گروه ➕",
                        url=f"https://t.me/MusicHarmony12Bot?startgroup=true",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="👤 سازنده",
                        url="https://t.me/beblnn",
                    ),
                    InlineKeyboardButton(
                        text="🎵 کانال ما",
                        url="https://t.me/ATRINMUSIC_TM",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="💬 گروه پشتیبانی",
                        url="https://t.me/ATRINMUSIC_TM1",
                    ),
                    InlineKeyboardButton(
                        text="📢 راهنما ربات",
                        callback_data="UTTAM_RATHORE",
                    ),
                ]
            ]
        )

        if START_IMAGE_URL:
            try:
                return await message.reply_video(
                    video=START_IMAGE_URL, caption=caption, reply_markup=buttons
                )
            except Exception as e:
                LOGGER.info(f"🚫 خطا در ارسال تصویر: {e}")
                try:
                    return await message.reply_text(text=caption, reply_markup=buttons)
                except Exception as e:
                    LOGGER.info(f"🚫 خطا در ارسال پیام: {e}")
                    return
        else:
            try:
                return await message.reply_text(text=caption, reply_markup=buttons)
            except Exception as e:
                LOGGER.info(f"🚫 خطا در ارسال پیام: {e}")
                return




@bot.on_callback_query(rgx("force_close"))
async def delete_cb_query(client, query):
    try:
        return await query.message.delete()
    except Exception:
        return


# Thumbnail Generator Area


async def download_thumbnail(vidid: str):
    async with aiohttp.ClientSession() as session:
        links = [
            f"https://i.ytimg.com/vi/{vidid}/maxresdefault.jpg",
            f"https://i.ytimg.com/vi/{vidid}/sddefault.jpg",
            f"https://i.ytimg.com/vi/{vidid}/hqdefault.jpg",
            START_IMAGE_URL,
        ]
        thumbnail = f"cache/temp_{vidid}.png"
        for url in links:
            async with session.get(url) as resp:
                if resp.status != 200:
                    continue
                else:
                    f = await aiofiles.open(thumbnail, mode="wb")
                    await f.write(await resp.read())
                    await f.close()
                    return thumbnail


async def get_user_logo(user_id):
    try:
        user_chat = await bot.get_chat(user_id)
        userimage = user_chat.photo.big_file_id
        user_logo = await bot.download_media(userimage, f"cache/{user_id}.png")
    except:
        user_chat = await bot.get_me()
        userimage = user_chat.photo.big_file_id
        user_logo = await bot.download_media(userimage, f"cache/{bot.id}.png")
    return user_logo


def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage


def circle_image(image, size):
    size = (size, size)
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    output = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output


def random_color_generator():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return (r, g, b)


async def create_thumbnail(results, user_id):
    if not results:
        return START_IMAGE_URL
    title = results.get("title")
    title = re.sub("\W+", " ", title)
    title = title.title()
    vidid = results.get("id")
    duration = results.get("duration")
    views = results.get("views")
    channel = results.get("channel")
    image = await download_thumbnail(vidid)
    logo = await get_user_logo(user_id)
    image_string = "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"
    font_string_01 = "AAEAAAAPAIAAAwBwRkZUTW/cvroAATswAAAAHEdERUYQiRH/AAEQdAAAAIpHUE9T+agRQQABG/AAAB8+R1NVQrDeETsAAREAAAAK7k9TLzJsSv5PAAABeAAAAGBjbWFwKq2jxAAACngAAASuZ2FzcP//AAQAARBsAAAACGdseWYdPBKpAAATfAAA6PRoZWFkCFrkGQAAAPwAAAA2aGhlYQmdBOQAAAE0AAAAJGhtdHgT80YMAAAB2AAACJ5sb2NhN60AcAAADygAAARSbWF4cAIwAG8AAAFYAAAAIG5hbWVjUXMNAAD8cAAABEpwb3N07sx4QAABALwAAA+uAAEAAAABGZn/74CRXw889QALA+gAAAAA0hlDHQAAAADSGUMd/7j+0AVRBJEAAAAIAAIAAAAAAAAAAQAABJH+0AAABXL/uP56BVEAAQAAAAAAAAAAAAAAAAAAAicAAQAAAigAbgAHAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAEAl8DhAAFAAACigJYAAAASwKKAlgAAAFeADIBLAAAAQAAAAAAAAAAAKAAAC8AAAAAAAAAAAAAAABVS1dOAQAAIPsCBJH+0AAABJEBMAAAAAEAAAAAAfQCvAAAACAAAwH0AAAAAAAAAU0AAAEbAAAA9AAhAZQAIAKvACACsQAgA9oAIALYACEAywAgAWMAIQFkACABgAAgAhgAIQD0ACAB/AAhAOcAIQHzABgCrwAjAXUAFgJ+AB0CggAbAo0AFwJ5ACICjwAiAlgAIQKpACQCjwAeAOgAIQD1ACEB1AAhAhgAIAHUACECdwAhA9QAIwMYABgCsQBDAr8ALgLcAEMCWgBDAksAQgMGAC8C3wBDATMAQwIOABkCrwBDAkQAQwORAD4C0AA9AzYALgKmAEMDQwAtArUAQwKzACECoQAZAt0AQwMNABkESQAYAvQAGQMAABgCkgAhAVMAIQHzABgBUwAhApYAIQIwACABQgAhAjoAGQJ6ADACCwAeAnoAIAJQAB8BiAAUAlgAFgJdADYBGAA2ARn/yQJHADYBYAA2A4EAMAJlADACegAfAn8ANgJ6AB8BawAwAfgAFwGWABUCXwAsAlkADANUAA4CQwANAloAEAHzABQBfgAgAO8AIQF+ACACBwAfAPQAIQIHABwCiQAiAyQAAAMAABgA7wAhAkkAIQH6AC0DEQAhAbwALAJ4ACEDJAAAAxEAIQGBACEBlAAhAhgAIQGFACEBhwAgAUIAIQNFACEA5wAhAVkAIQD3ACAB7gAvAngAIQLtACIDIwAiA1AAIAJ3ACEDGAAZAxgAGAMYABgDGAAYAxgAGQMYABgDowAZAr8ALQJaAEMCWgBDAloARAJaAEMBMwAZATMAIAEz/+UBM//HAt7/8gLQADwDNgAuAzYALgM2AC0DNgAtAzYALgHuACADNgAuAt0AQwLdAEMC3QBEAt0AQwMAABgCtABDAp8AOAI6ABkCOgAaAjoAGgI6ABkCOgAZAjoAGgPjABgCCwAfAlAAHgJQAB8CUAAfAlAAHwENAAsBDQASAQ3/1gEN/7kCWAAXAmUAMAJ6AB8CegAgAnoAHwJ6AB4CegAfAhgAIAJ6ACACXwArAl8ALAJfACwCXwAsAloAEAJ/ADYCWgARAxgAGQI6ABkDGAAZAjoAGAMYABgCOgAZAr8ALgILAB4CvwAtAgsAHgK/AC4CCwAeAtwAQwMvACAC3v/yAnoAHwJaAEMCUAAeAloAQwJQAB4CWgBDAlAAHwJaAEQCUAAfAwYALgJYABUDBgAvAlgAFgMGAC8CWAAWAt8AAAJd//ABM//ZAQ3/zAEz//gBDf/qATMAAQEN/+4BMwBDAQ0ANQNAAEMCMQA2Aq8AQwJHADYCRABDAWAACwJEAEMBYAA2AkQAQwHKADYCRABDAeMANgI5/+AB2wAOAtAAPQJlADEC0AA9AmUAMALQAD4CZQAwAtAAPQJqADADNgAuAnoAHwM2AC0CegAeBHMALwPkAB8CtQBDAWsAMAK1AEMBawAwArUARAFrAA0CswAiAfgAGAKzACEB+AAXArMAIQH4ABgCoQAZAZYAFQKhABkB8AAUAqEAGQGWABUC3QBBAl8AKwLdAEMCXwArAt0AQwJfACwC3QBDAl8ALALdAEMCXwAsBEkAGANUAA4DAAAYAloAEAMAABcCkgAhAfMAEwKSACEB8wAUApIAIgHzABQBiAASAxgAGQI6ABoBM//mAQ3/1wM2AC4CegAfAt0ARAJfACwC3QBDAl8ALALdAEMCXwAsAt0ARAJfAC0C3QBDAl8ALAMYABkCOgAZAwYALwJYABkDNgAtAnoAHwKzACEB+AAXAqEAGQGWABUCWgBDAlAAHwGmACIBpgAiAZAAIQDnACABawAhAUUAIQHKAB8CRgAhAAAAIAAAACAAAAAiAAAAIQJYAAACWAAAAlgAAAJYAAACsQBDAnoAMALcAEMCegAgAtwAQwJ6ACAC3ABDAnoAIALfAEMCXQA2ATP/xgEN/7gCRABDAWAANgJEAEMBYP/YA5EAPgOBADAC0AA+AmUAMALQAD0CZQAwAtAAPQJlADADNgAtAnoAHgM2AC4CegAfAzYALgJ6AB8CswAhAfgAFwKhABkBlgAVAqEAGQGWABUCoQAZAZYAFQRJABgDVAAOBEkAGQNUAA4ESQAZA1QADwKSACEB8wAUAjoAGQMYABgCOgAaAloAQwJQAB8CWgBCAlAAHQJaAEQCUAAfATMAQwEYADYDNgAuAnoAHwM2AC0CegAfAt0AQwJfACwDAAAXAloAEQI3ACECpwAgAPQAIgD0ACEA9AAhAdIAIgHSACEB0gAhAjIAIQIyACEBWgAgArIAIQVyACEBbAAhAWwAIQJ5ABgCmAAgA7UAIQM7ACIDnQAgA5YAIANSACADJAAAAyQAAAMkAAADJAAAAhgAIAMkAAADJAAAAyQAAAIHAB0CGAAhAcMAIAHDACADJAAAAqAAFALoABUCeAAhAngAIQJ4ACECeAAhAngAIQJ4ACECeAAgAngAIAJ4ACECeAAgAngAIAJ4ACICeAAhAngAHwQBACECRAAeAkQAHgJEAB4CRAAeAkQAHAJEAB0CRAAdAkQAHgJEAB4CRAAeAkQAHgJEABwCRAAcAnoAIAJ6ACACegAhAnoAIQJ6ACAD1wAeBP4AGARoAB4DoQAeBAIAFAMQABQEJwAUBCkAFARwABQD5QAVAqEAFAPPABUEeAAXA44AGAKpACQCqQAkAp0AHgKdAB4CegAiAnoAIgKdADECnQAxAo0AFwKNABcCnQAjAp0AIwKPAB4CjwAeAp0AJgKdACcBdQAWAQ4ACAGDAC8B9ACDAlgAIQJYACECnQBEAp0ARAKPACICjwAiAp0AJgKdACcCggAbAoIAGwKdACsCnQArAn4AHQHfABUCnQAvAfQAIAKvACMCCQAcAp0AGgH0ABIBeQASAXkAEgFdAAsBXQALAWEACQFhAAkBaAAKAWgACgDUAAUA1AAFAT4ACgE+AAoBaAAUAWgAFAFhAAkBYQAJAVkACQFZAAkBfAASABIAAAAAAAMAAAADAAAAHAABAAAAAAKk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d3cuam9uYXRoYW5oaWxsLm1lLnVrAAAAAAIAAAAAAAD/agAyAAAAAAAAAAAAAAAAAAAAAAAAAAACKAAAAAEAAgADAAQABQAGAAcACAAJAAoACwAMAA0ADgAPABAAEQASABMAFAAVABYAFwAYABkAGgAbABwAHQAeAB8AIAAhACIAIwAkACUAJgAnACgAKQAqACsALAAtAC4ALwAwADEAMgAzADQANQA2ADcAOAA5ADoAOwA8AD0APgA/AEAAQQBCAEMARABFAEYARwBIAEkASgBLAEwATQBOAE8AUABRAFIAUwBUAFUAVgBXAFgAWQBaAFsAXABdAF4AXwBgAGEAowCEAIUAvQCWAOgAhgCOAIsAnQCpAKQAigDaAIMAkwECAQMAjQCIAMMA3gEEAJ4AqgD1APQA9gCiAK0AyQDHAK4AYgBjAJAAZADLAGUAyADKAM8AzADNAM4A6QBmANMA0ADRAK8AZwDwAJEA1gDUANUAaADrAO0AiQBqAGkAawBtAGwAbgCgAG8AcQBwAHIAcwB1AHQAdgB3AOoAeAB6AHkAewB9AHwAuAChAH8AfgCAAIEA7ADuALoBBQEGAQcBCAEJAQoA/QD+AQsBDAD/AQABDQEOAQ8BAQEQAREBEgETARQBFQEWARcA+AD5ARgBGQEaARsBHAEdAR4BHwEgASEBIgEjAPoA1wEkASUBJgEnASgBKQEqASsBLAEtAS4BLwDiAOMBMAExATIBMwE0ATUBNgE3ATgBOQE6ATsAsACxATwBPQE+AT8BQAFBAUIBQwD7APwA5ADlAUQBRQFGAUcBSAFJAUoBSwFMAU0BTgFPAVABUQFSAVMBVAFVAVYBVwC7AVgBWQFaAVsA5gDnAKYBXAFdAV4BXwFgAWEBYgFjAWQBZQFmAWcBaAFpAWoBawFsAW0BbgFvAXABcQFyAXMBdAF1AXYBdwDYAOEA2wDcAN0A4ADZAN8BeAF5AXoBewF8AX0BfgCbAX8BgAGBAYIBgwGEAYUBhgGHAYgBiQGKAYsBjAGNAY4BjwGQAZEBkgGTAZQBlQGWAZcBmAGZAZoBmwGcAZ0BngGfAaABoQGiAaMBpAGlAaYBpwGoAakBqgGrAawBrQGuAa8BsAGxAbIBswG0AbUBtgG3AbgBuQG6AbsBvAG9Ab4BvwCyALMAtgC3AMQAtAC1AMUAggDCAIcAqwDGAL4AvwC8AcAAjAHBAcIBwwHEAJgBxQCaAJkA7wClAJIAnACnAI8AlACVALkBxgHHAcgByQHKAcsBzAHNAc4BzwHQAdEB0gHTAdQB1QHWAdcB2AHZAdoB2wHcAd0B3gHfAeAB4QHiAeMB5AHlAeYB5wHoAekB6gHrAewB7QHuAe8B8AHxAfIB8wH0AfUB9gH3AfgB+QH6AfsB/AH9Af4B/wIAAgECAgIDAgQCBQIGAgcCCAIJAgoCCwIMAg0CDgIPAhACEQISAhMCFAIVAhYCFwIYAhkCGgIbAhwCHQIeAh8CIAIhAiICIwIkAiUCJgInAigCKQIqAisCLAItAi4CLwIwAjECMgd1bmkwMEIyB3VuaTAwQjMHdW5pMDBCOQdBbWFjcm9uB2FtYWNyb24GQWJyZXZlBmFicmV2ZQdBb2dvbmVrB2FvZ29uZWsKQ2RvdGFjY2VudApjZG90YWNjZW50BkRjYXJvbgZkY2Fyb24GRGNyb2F0B0VtYWNyb24HZW1hY3JvbgpFZG90YWNjZW50CmVkb3RhY2NlbnQHRW9nb25lawdlb2dvbmVrBkVjYXJvbgZlY2Fyb24KR2RvdGFjY2VudApnZG90YWNjZW50B3VuaTAxMjIHdW5pMDEyMwRIYmFyBGhiYXIGSXRpbGRlBml0aWxkZQdJbWFjcm9uB2ltYWNyb24HSW9nb25lawdpb2dvbmVrAklKAmlqB3VuaTAxMzYHdW5pMDEzNwZMYWN1dGUGbGFjdXRlB3VuaTAxM0IHdW5pMDEzQwZMY2Fyb24GbGNhcm9uBExkb3QEbGRvdAZOYWN1dGUGbmFjdXRlB3VuaTAxNDUHdW5pMDE0NgZOY2Fyb24GbmNhcm9uA0VuZwNlbmcHT21hY3JvbgdvbWFjcm9uDU9odW5nYXJ1bWxhdXQNb2h1bmdhcnVtbGF1dAZSYWN1dGUGcmFjdXRlB3VuaTAxNTYHdW5pMDE1NwZSY2Fyb24GcmNhcm9uBlNhY3V0ZQZzYWN1dGUHdW5pMDE2Mgd1bmkwMTYzBlRjYXJvbgZ0Y2Fyb24EVGJhcgR0YmFyBlV0aWxkZQZ1dGlsZGUHVW1hY3Jvbgd1bWFjcm9uBVVyaW5nBXVyaW5nDVVodW5nYXJ1bWxhdXQNdWh1bmdhcnVtbGF1dAdVb2dvbmVrB3VvZ29uZWsLV2NpcmN1bWZsZXgLd2NpcmN1bWZsZXgLWWNpcmN1bWZsZXgLeWNpcmN1bWZsZXgGWmFjdXRlBnphY3V0ZQpaZG90YWNjZW50Cnpkb3RhY2NlbnQHdW5pMDFDRAd1bmkwMUNFB3VuaTAxQ0YHdW5pMDFEMAd1bmkwMUQxB3VuaTAxRDIHdW5pMDFEMwd1bmkwMUQ0B3VuaTAxRDUHdW5pMDFENgd1bmkwMUQ3B3VuaTAxRDgHdW5pMDFEOQd1bmkwMURBB3VuaTAxREIHdW5pMDFEQwd1bmkwMURFB3VuaTAxREYGR2Nhcm9uBmdjYXJvbgtPc2xhc2hhY3V0ZQtvc2xhc2hhY3V0ZQd1bmkwMjE4B3VuaTAyMTkHdW5pMDIxQQd1bmkwMjFCB3VuaTAyMjgHdW5pMDIyOQxkb3RiZWxvd2NvbWIHdW5pMDMyNgd1bmkwMzJEB3VuaTAzMzEHdW5pMDM5NAd1bmkwM0E5B3VuaTAzQkMHdW5pMUUwNAd1bmkxRTA1B3VuaTFFMEMHdW5pMUUwRAd1bmkxRTBFB3VuaTFFMEYHdW5pMUUxMgd1bmkxRTEzB3VuaTFFMjQHdW5pMUUyNQd1bmkxRTJFB3VuaTFFMkYHdW5pMUUzNgd1bmkxRTM3B3VuaTFFM0MHdW5pMUUzRAd1bmkxRTNFB3VuaTFFM0YHdW5pMUU0NAd1bmkxRTQ1B3VuaTFFNDYHdW5pMUU0Nwd1bmkxRTRBB3VuaTFFNEIHdW5pMUU0Qwd1bmkxRTREB3VuaTFFNTAHdW5pMUU1MQd1bmkxRTUyB3VuaTFFNTMHdW5pMUU2Mgd1bmkxRTYzB3VuaTFFNkMHdW5pMUU2RAd1bmkxRTZFB3VuaTFFNkYHdW5pMUU3MAd1bmkxRTcxBldncmF2ZQZ3Z3JhdmUGV2FjdXRlBndhY3V0ZQlXZGllcmVzaXMJd2RpZXJlc2lzB3VuaTFFOTIHdW5pMUU5Mwd1bmkxRUExB3VuaTFFQUMHdW5pMUVBRAd1bmkxRUI4B3VuaTFFQjkHdW5pMUVCQwd1bmkxRUJEB3VuaTFFQzYHdW5pMUVDNwd1bmkxRUNBB3VuaTFFQ0IHdW5pMUVDQwd1bmkxRUNEB3VuaTFFRDgHdW5pMUVEOQd1bmkxRUU0B3VuaTFFRTUGWWdyYXZlBnlncmF2ZQRFdXJvCW9uZWVpZ2h0aAx0aHJlZWVpZ2h0aHMLZml2ZWVpZ2h0aHMMc2V2ZW5laWdodGhzCGVtcHR5c2V0B3VuaUZCMDEHdW5pRkIwMgZhLnNhbHQLYWFjdXRlLmFhbHQLYWJyZXZlLmFhbHQMdW5pMDFDRS5hYWx0EGFjaXJjdW1mbGV4LmFhbHQMdW5pMUVBRC5hYWx0DmFkaWVyZXNpcy5hYWx0DHVuaTAxREYuYWFsdAx1bmkxRUExLmFhbHQLYWdyYXZlLmFhbHQMYW1hY3Jvbi5hYWx0DGFvZ29uZWsuYWFsdAphcmluZy5hYWx0C2F0aWxkZS5hYWx0B2FlLmFhbHQGZS5hYWx0C2VhY3V0ZS5hYWx0C2VjYXJvbi5hYWx0DHVuaTAyMjkuYWFsdBBlY2lyY3VtZmxleC5hYWx0DHVuaTFFQzcuYWFsdA5lZGllcmVzaXMuYWFsdA9lZG90YWNjZW50LmFhbHQMdW5pMUVCOS5hYWx0C2VncmF2ZS5hYWx0DGVtYWNyb24uYWFsdAxlb2dvbmVrLmFhbHQMdW5pMUVCRC5hYWx0BmcuYWFsdAtnYnJldmUuYWFsdAtnY2Fyb24uYWFsdAx1bmkwMTIzLmFhbHQPZ2RvdGFjY2VudC5hYWx0B29lLmFhbHQIVF9oLmRsaWcIY19oLmRsaWcIY190LmRsaWcIZl9iLmRsaWcIZl9mLmxpZ2EKZl9mX2kubGlnYQpmX2Zfai5kbGlnCmZfZl9sLmxpZ2EIZl9oLmRsaWcIZl9qLmRsaWcIZl9rLmRsaWcIc19wLmRsaWcIc190LmRsaWcKZWlnaHQuY2FzZQ5laWdodC5vbGRzdHlsZQplaWdodC50bnVtE2VpZ2h0LnRudW0ub2xkc3R5bGUJZml2ZS5jYXNlDWZpdmUub2xkc3R5bGUJZml2ZS50bnVtEmZpdmUudG51bS5vbGRzdHlsZQlmb3VyLmNhc2UNZm91ci5vbGRzdHlsZQlmb3VyLnRudW0SZm91ci50bnVtLm9sZHN0eWxlCW5pbmUuY2FzZQ1uaW5lLm9sZHN0eWxlCW5pbmUudG51bRJuaW5lLnRudW0ub2xkc3R5bGUIb25lLmNhc2UMb25lLm9sZHN0eWxlCG9uZS50bnVtEW9uZS50bnVtLm9sZHN0eWxlCnNldmVuLmNhc2UOc2V2ZW4ub2xkc3R5bGUK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AfcAFwACAfcAFwABAfUAAgH7ABwAAgH7ABwAAQH5AAIB/wAUAAIB/wAUAAEB/QACAgMAGgACAgMAGgABAgEAAgIHABkAAgIHABkAAQIFAAICCwAWAAICCwAWAAECCQACAg8AFQACAg8AFQABAg0AAgITABMAAgITABMAAQIRAAIADAATABwAAABEAEQACgHtAe8ACwHxAfMADgH1AfcAEQH5AfsAFAH9Af8AFwIBAgMAGgIFAgcAHQIJAgsAIAINAg8AIwIRAhMAJgACAA4ABAFBAUIBQwFEAAEABAELAQwBDwEQAAIADgAEAUEBQgFDAUQAAQAEAQsBDAEPARAAAwAAAAIAFAAaAAEAIAABAAAAFQABAAEATwABAAEAdgABAAEATwADAAAAAgAUABoAAQAgAAEAAAAVAAEAAQAvAAEAAQB2AAEAAQAvAAIADAADAHgAcgBzAAEAAwAUABUAFgACABoACgInAh0CJQIjAhkCFwIhAh8CFQIbAAIAAQATABwAAAACABoACgImAhwCJAIiAhgCFgIgAh4CFAIaAAIAAQATABwAAAABAAYBlQABAAEAEgACABoACgInAh0CJQIjAhkCFwIhAh8CFQIbAAIAAQATABwAAAADAAEAKgABABIAAAABAAAAFgABAAoCFQIXAhkCGwIdAh8CIQIjAiUCJwABAAEBpwADAAEAKgABABIAAAABAAAAFgABAAoCFQIXAhkCGwIdAh8CIQIjAiUCJwABAAoCFAIWAhgCGgIcAh4CIAIiAiQCJgADAAEAGgABABIAAAABAAAAFgABAAIAJABEAAIAAQATABwAAAADAAEAGgABABIAAAABAAAAFgABAAIAMgBSAAIAAQATABwAAAACABoACgAbABgAFwAcABQAGgAZABYAFQATAAEACgHtAfEB9QH5Af0CAQIFAgkCDQIRAAIALgAUABsB7QAYAfEAFwH1ABwB+QAUAf0AGgIBABkCBQAWAgkAFQINABMCEQABABQB7gHvAfIB8wH2AfcB+gH7Af4B/wICAgMCBgIHAgoCCwIOAg8CEgITAAIALgAUAhIB/gIOAgoB9gHyAgYCAgHuAfoB7wHzAfcB+wH/AgMCBwILAg8CEwABABQAEwAUABUAFgAXABgAGQAaABsAHAHtAfEB9QH5Af0CAQIFAgkCDQIRAAIALgAUAhEB/QIN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AAAAAAAAAAAAAAAAADQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/6f/6gAA/+r/7gAA/+IAAP/z//EAAAAAAAAAAAAAAAAAAP/MAAAAAAAAAAD/+//iAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/9QAA//X//gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/+gAAAAAAAAAAAAAAAAAAAAA/+sAAAAAAAAAAAAAAAAAAP/QAAAAAP/aAAAAAAAA/+cAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/5D/of/Q/6H/swAAAAAAAP+0/8gAAP+1/9EAAP/RAAAAAAAA/9EAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/9P/+//T//v/9AAAAAAAA/9gAAAAAAAAAAAAA/9sAAAAAAAAAAAAAAAAAAAAAAAD/5wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/9wAAAAAAAAAAAAD/xQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/8cAAAAAAAD/8AAAAAD/8wAAAAAAAAAAAAAAAP/2AAAAAP+1AAAAAP/HAAD/0gAA/80AAP+r/9H/xQAAAAAAAAAAAAAAAAAAAAD/4gAA/+L/8wAA/+YAAAAAAAD/v/+/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/iAAD/4gAAAAAAAAAAAAAAAAAAAAAAAAAA//MAAAAAAAAAAAAAAAAAAAAA/+cAAAAAAAAAAAAAAAAAAP/MAAAAAAAAAAAAAAAA/+YAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/5H/a/96/2v/awAAAAD/av9r/3MAAP9t/90AAP97AAAAAAAA/93/9AAAAAAAAAAAAAD/UQAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/5//8/+cAAAAAAAAAAAAA/7AAAAAA/+IAAAAAAAD/5f90/+QAAP+MAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/+0AAAAAAAD/7wAA/+oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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"
    font_string_02 = "AAEAAAASAQAABAAgRFNJRwAAAAEAAlKwAAAACEdERUZ8Gn6BAAABLAAAAfRHUE9TI4GfPQAAAyAAAMKcR1NVQibw52gAAMW8AAAcTE9TLzJpK/hhAADiCAAAAGBjbWFwyOZhcQAA4mgAAAYWY3Z0IBxkDcYAAkMkAAAAnGZwZ22eNhXSAAJDwAAADhVnYXNwAAAAEAACQxwAAAAIZ2x5ZjGhbnoAAOiAAAEkbmhlYWQWknIRAAIM8AAAADZoaGVhB50GSgACDSgAAAAkaG10eEVmOA0AAg1MAAAMxGxvY2EbzmC3AAIaEAAABmRtYXhwBi0QaAACIHQAAAAgbmFtZfJ8cmkAAiCUAAAFDnBvc3Rw09rKAAIlpAAAHXVwcmVw+LWQAgACUdgAAADWAAEAAAAMAAAAAAHMAAIASgADAAoAAQAMAA4AAQAQABYAAQAYABgAAQAaACMAAQAlACoAAQAsAEIAAQBEAEcAAQBJAFQAAQBZAGIAAQBkAGQAAQBmAHMAAQB1AHkAAQB7AIMAAQCFAJgAAQCcAKUAAQCnAMMAAQDFAMYAAQDJAM0AAQDPAOgAAQDrAOsAAQDuAPoAAQD8AQAAAQECAQoAAQEMASEAAQEjAS4AAQEwATEAAQEzATcAAQE7AWEAAQFiAWcAAgFqAWoAAQFtAW4AAQFxAXQAAQF2AXoAAQF9AX4AAQGBAYQAAQGOAY4AAQGRAZEAAQGUAZYAAQGYAZkAAQGbAZsAAQGdAZ0AAQGkAaQAAQGnAacAAQGpAakAAQGsAa4AAQGwAbkAAQG9Ab0AAQG/AcAAAQHCAcMAAQHNAc0AAQHQAdAAAQHSAdgAAQHaAdoAAQHcAeMAAQHlAeUAAQHtAfAAAQH0AfUAAQH4AfkAAQH9AgQAAQIGAgYAAQIOAg4AAQIQAhcAAQIZAhkAAQIbAhwAAQIjAiMAAQKtAq0AAQKvAq8AAQKyArIAAQK3ArgAAQL4AwYAAwMUAysAAwMtAy4AAQMwAzAAAQACAAYC+AMDAAIDBAMFAAEDFAMdAAIDHgMeAAEDIAMmAAIDKAMrAAIAAQAAAAoBHAP2AANERkxUABRjeXJsACZsYXRuAEwABAAAAAD//wAEAAAADQAaACcACgABQkdSIAAYAAD//wAEAAEADgAbACgAAP//AAQAAgAPABwAKQA6AAlBWkUgAEhDQVQgAFZDUlQgAGRLQVogAHJNT0wgAIBOTEQgAI5ST00gAJxUQVQgAKpUUksgALgAAP//AAQAAwAQAB0AKgAA//8ABAAEABEAHgArAAD//wAEAAUAEgAfACwAAP//AAQABgATACAALQAA//8ABAAHABQAIQAuAAD//wAEAAgAFQAiAC8AAP//AAQACQAWACMAMAAA//8ABAAKABcAJAAxAAD//wAEAAsAGAAlADIAAP//AAQADAAZACYAMwA0Y3BzcAE6Y3BzcAFAY3BzcAFGY3BzcAFMY3BzcAFSY3BzcAFYY3BzcAFeY3BzcAFkY3BzcAFqY3BzcAFwY3BzcAF2Y3BzcAF8Y3BzcAGCa2VybgGIa2VybgGQa2VybgGYa2VybgGga2VybgGoa2VybgGwa2VybgG4a2VybgHAa2VybgHIa2VybgHQa2VybgHYa2VybgHga2VybgHobWFyawHwbWFyawH6bWFyawIEbWFyawIObWFyawIYbWFyawIibWFyawIsbWFyawI2bWFyawJAbWFyawJKbWFyawJUbWFyawJebWFyawJobWttawJybWttawJ6bWttawKCbWttawKKbWttawKSbWttawKabWttawKibWttawKqbWttawKybWttawK6bWttawLCbWttawLKbWttawLSAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAQAAAAAAAgABAAIAAAACAAEAAgAAAAIAAQACAAAAAgABAAIAAAACAAEAAgAAAAIAAQACAAAAAgABAAIAAAACAAEAAgAAAAIAAQACAAAAAgABAAIAAAACAAEAAgAAAAIAAQACAAAAAgABAAIAAAADAAMABAAFAAAAAwADAAQABQAAAAMAAwAEAAUAAAADAAMABAAFAAAAAwADAAQABQAAAAMAAwAEAAUAAAADAAMABAAFAAAAAwADAAQABQAAAAMAAwAEAAUAAAADAAMABAAFAAAAAwADAAQABQAAAAMAAwAEAAUAAAADAAMABAAFAAAAAgAGAAcAAAACAAYABwAAAAIABgAHAAAAAgAGAAcAAAACAAYABwAAAAIABgAHAAAAAgAGAAcAAAACAAYABwAAAAIABgAHAAAAAgAGAAcAAAACAAYABwAAAAIABgAHAAAAAgAGAAcACAASABoAKABAAEgAUABYAGAAAQAAAAEAVgACAAgABABYAHoAsgh2AAIACAAJDLA7JjwoTIxMtFkwbrxu3HKIAAQAAAABdqAABAAAAAF4ggAEAAAAAX7AAAYBAAABjjoABgIAAAGOmAABkLwABQAFAAoAAZDCAAQAAAACAA4AGAACASIASgEpACMAAgEiAAABKQAAAAKQqAAEAACYApgYAAQABQAAAAcAAAAAAAAAAAAA/+IAAAAAAAAAAAAA//wAAAAAAAAAAAAAAA4AApB+AAQAAJgCmOYAHQAiAAD/5P/W/+z/0P/fAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/2//zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//X/6//1AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/9P/zAAD//f/9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//f/0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//z/5v/0//wAAAAAAAD//QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/8f/wAAD/+//7AAAAAAAA//z//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/+wAAAAA/+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/5P/V/9n/8//9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/90AAAAAAAAAAAAAAAAAAAAAAAAAAP/W/8T/v//hAAD/7P/k/+8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/sAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/4AAA//YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/sAAD/6gAAAAAAAAAA/+3//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/2wAA/9AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/5P/c/+n/7AAAAAAAAP/0//D/7wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/j/+EAAP/s/+0AAAAAAAD/7v/uAAAAAAAAAAAAAAAAAAAAAAAA//kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/0/+kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/2AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//f/7/+0AAAAAAAAAAAAAAAAAAAAAAAD/7P/sAAAAAP/xAAAAAAAAAAAAAAAA/9D/v/+8/9MAAAAA//YAAAAAAAAAAAAAAAAAAP/2AAAAAAAAAAAAAAAAAAD/5AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/t//wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//D//AAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/2gAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA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AAUAtAArALoACgACALz/+AC9//kAAgC8//gAvf/5AAIAvP/4AL3/+QACALz/+AC9//kAAQC8//kAAQC8//kAAQC8//kAAQC8//kAAQC8//kAAQC8//kAAQC8//kAAQC8//kAAQC8//kAJgCv//oAsP/5ALH/+gC1//oAtv/6ALf/+gC5//oAuwBBALwAQQC9AEEAvgBBAMH/+QDI//kAyf/5AMr/+QDM//kAzf/5AM7/+QDP//kA3P/5AN//+QDg//kA4f/5AOL/+QEo//oBKf/6ASr/+QEr//oBM//5ATT/+QE1//kBNv/5AnUABQKaAAUCmwAFArEADgLX//kDLf/6AAYAswAfALQAHgC6ABQAvP/7AL3/+wC+AB8APAAQ//4AEf/+ABL//gAT//4AFP/+ABX//gAl//4AJv/+ACf//gAo//4AKf/+AEr//gBL//4ATP/+AE3//gBO//4AT//+AFD//gBR//4AUv/+AFP//gBU//4AVf/+AFj//gCE//4Akf/9AKf/8QCo//EAqf/xAKr/8QCr//EArP/9AK0AEwCu//0AswAfALQAHgC6ABQAvP/7AL3/+wC+AB8Av//9AMD//QDC//0Aw//9AMT//QDF//0Axv/9AN3//QDp//0BJP/xASX/8QEm//EBJ//xAS3//QEu//0BL//9ATD//QEx//0CfwAPAs///gAGALMAHwC0AB4AugAUALz/+wC9//sAvgAfAAYAswAfALQAHgC6ABQAvP/7AL3/+wC+AB8AAQC0AA4ABgCzAB8AtAAeALoAFAC8//sAvf/7AL4AHwAGALMAHwC0AB4AugAUALz/+wC9//sAvgAfAA4AswAfALQAHgC6ABQAvP/7AL3/+wC+AB8CVQAOAl8ADgJyAA4CgwAmAocADgKNABsCjwAZApEAGQALALMAHwC0AB4AugAUALz/+wC9//sAvgAfAlUADgJfAA4CcgAOAo0ADAKPAAoABgCzAB8AtAAeALoAFAC8//sAvf/7AL4AHwAGALMAHwC0AB4AugAUALz/+wC9//sAvgAfAAYAswAfALQAHgC6ABQAvP/7AL3/+wC+AB8ABwCzAB8AtAAeALoAFAC7ADQAvAA0AL0ANAC+ADQABgCzAB8AtAAeALoAFAC8//sAvf/7AL4AHwABALQADgABALQADgABALQADgACAGj/3gC0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AD8AtABjALYAKwC4ACwAugA4AmIAAAAIALsAIgC8ACIAvQAiAL4AIgEpAAABKgAAASsAAAEsAAAACAC7ACIAvAAiAL0AIgC+ACIBKQAAASoAAAErAAABLAAAAAgAuwAiALwAIgC9ACIAvgAiASkAAAEqAAABKwAAASwAAAAIALsAIgC8ACIAvQAiAL4AIgEpAAABKgAAASsAAAEsAAAACAC7ACIAvAAiAL0AIgC+ACIBKQAAASoAAAErAAABLAAAAAIAvAAAAL0AAAACALwAAAC9AAAAAgC8AAAAvQAAAAYAvAAAASkAAAEqAAABKwAAASwAGAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAABKQAAASoAAAErAAABLAAYAmIAAAKHAAkABwCtABsBKQAYASoAAAErABgBLAAwAocAGgLrAAkABQCtABsBKQAYASoAAAErABgBLAAwAFQADwAMABYADAAYAAwAGgAMABsADAAcAAwAHQAMAB4ADAAfAAwAIAAMACEADAAiAAwAIwAMACQADAAqAAwAKwAMACwADAAtAAwALgAMAC8ADAAwAAwAMQAMADIADAAzAAwANAAMADUADAA2AAwANwAMADsADAA8AAwAPQAMAD4ADAA/AAwAQAAMAEEADABDAAwARAAMAEUADABGAAwARwAMAEgADABJAAwAVgAMAFcADABZAAwAWgAMAFsADABcAAwAYwAMAGkADgBqAA4AawAOAGwADgBtAA4AbgAOAG8ADgBwAA4AcQAOAHIADgBzAA4ArQAbAMsABAELAAwBKQAYASoAAAErABgBLAAwAnkACwJ/ADICgwAMAocAHgKJACQCigAMAosAJwKdAAQCnwAEAqQAEAKlABAC0wAMAusAMALvAAwC8AAMAvUADAL2AAwABgC8AAABKQAAASoAAAErAAABLAAYAmIAAAAGALwAAAEpAAABKgAAASsAAAEsABgCYgAAAAYAvAAAASkAAAEqAAABKwAAASwAGAJiAAAABQCtABsBKQAYASoAAAErABgBLAAwACQArwAAALAAAACxAAAAtQAAALYAAAC3AAAAuQAAALsAOAC8ADgAvQA4AL4AOADBAAAAyAAAAMkAAADKAAAAzAAAAM0AAADOAAAAzwAAANwAAADfAAAA4AAAAOEAAADiAAABKAAAASkAAAEqAAABKwAAASwAGAEzAAABNAAAATUAAAE2AAACYgAAAtcAAAMtAAAACACtABsBKQAYASoAAAErABgBLAAwAn8ADwKJAAkCiwANAAkAuwAKALwACgC9AAoAvgAKASkAAAEqAAABKwAAASwAGAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABgC8AAABKQAAASoAAAErAAABLAAYAmIAAAAFAK0AGwEpABgBKgAAASsAGAEsADAABQADAAAADQAAAHoAAAC8AAAAvQAAAAUAAwAAAA0AAAB6AAAAvAAAAL0AAAAOAGQAIgBlAAAAdAAAAHUAAAB6AAAAgAAAAJQAEgCtAC8AtAB0ALYAVgDlABEA6QAZAQkAEALuABoABwADAAAADQAAAHoAAAC7AAoAvAAKAL0ACgC+AAoABQBkAAAAdQAAAHoAAACAAAACtAAUAAIAvAAAAL0AAAACALwAAAC9AAAAAgC8AAAAvQAAAAIAvAAAAL0AAAACALwAAAC9AAAAAgC8AAAAvQAAAAIAvAAAAL0AAAACALwAAAC9AAAAAQKH//IAEQCvAA4AsQAOALUADgC2AA4AtwAOALkADgC7AB0AvAAdAL0AHQC+AB0BKAAOASkAFwEqABcBKwAXASwAFwJiAAADLQAOAAYBIgAAATcAAAE4AAABOQAAAToAAAE7AAAABgEiAAABNwAAATgAAAE5AAABOgAAATsAAAAHASIAAAE3AAABOAAAATkAAAE6AAABOwAAAof/+gAGASIAAAE3AAABOAAAATkAAAE6AAABOwAAABIAoQAOAK0AUACxABsAsgCGALQAqgC2AHEAuABvALoAfgDUABUA4QAaAPQAIwEEAA4BBQA1AQ4ACAEQACsBEgAMARUADgEgACcADwC7AAAAvAAAAL0AAAC+AAAA+wAAAPwAAAEiAAABNwAAATgAAAE5AAABOgAAATsAAAJ0AAACdQAAAnwAAAAPALsAAAC8AAAAvQAAAL4AAAD7AAAA/AAAASIAAAE3AAABOAAAATkAAAE6AAABOwAAAnQAAAJ1AAACfAAAAAIArQA5ARAADQAtAK8AAACwAAAAsQAAALUAAAC2AAAAtwAAALkAAAC7ADMAvAAzAL0AMwC+ADMAwQAAAMgAAADJAAAAygAAAMwAAADNAAAAzgAAAM8AAADcAAAA3wAAAOAAAADhAAAA4gAAAPsAAAD8AAABIgAAASgAAAEpAAABKgAAASsAAAEzAAABNAAAATUAAAE2AAABNwAAATgAAAE5AAABOgAAATsAAAJ0AAACdQAAAnwAAALXAAADLQAAAC0ArwAAALAAAACxAAAAtQAAALYAAAC3AAAAuQAAALsAFwC8ABcAvQAXAL4AFwDBAAAAyAAAAMkAAADKAAAAzAAAAM0AAADOAAAAzwAAANwAAADfAAAA4AAAAOEAAADiAAAA+wAAAPwAAAEiAAABKAAAASkAAAEqAAABKwAAATMAAAE0AAABNQAAATYAAAE3AAABOAAAATkAAAE6AAABOwAAAnQAAAJ1AAACfAAAAtcAAAMtAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAABwC8AAAAvQAAASkAAAEqAAABKwAAASwAAAJiAAAACQC7AEMAvABDAL0AQwC+AEMBKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAACALwAAAC9AAAAAgC8AAAAvQAAAAIAvAAAAL0AAAACALwAAAC9AAAAAgC8AAAAvQAAAAIAvAAAAL0AAAACALwAAAC9AAAAEACvAAAAsQAAALUAAAC2AAAAtwAAALkAAAC7AEMAvABDAL0AQwC+AEMBKAAAASkAAAErAAACif/2Aov/9wMtAAAAAgC8AAAAvQAAAAIAvAAAAL0AAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHALwAAAC9AAABKQAAASoAAAErAAABLAAAAmIAAAAHAK0AGwCyAD8AtABjALYAKwC4ACwAugA4AmIAIgAHALwAAAC9AAABKQAXASoAFwErABcBLAAXAmIAeAAIALsAIgC8ACIAvQAiAL4AIgEpABcBKgAXASsAFwEsABcACAC7ACIAvAAiAL0AIgC+ACIBKQAXASoAFwErABcBLAAXAAgAuwAiALwAIgC9ACIAvgAiASkAFwEqABcBKwAXASwAFwAIALsAIgC8ACIAvQAiAL4AIgEpABcBKgAXASsAFwEsABcABgC8AAABKQAUASoAAAErAAABLAAYAmIAAAAQAK8AAACxAAAAtQAAALYAAAC3AAAAuQAAALsAAAC8AAAAvQAAASgAAAEpABcBKgAXASsAFwEsACECYgAqAy0AAAAHALwAAAC9AAABKQAXASoAFwErABcBLAAXAmIAAAAGALwAAAEpABcBKgAXASsAFwEsACECYgAAABkArQAbALAAAAC8AAAAwQAAAMgAAADJAAAAygAAAMwAAADNAAAAzgAAAM8AAADcAAAA3wAAAOAAAADhAAAA4gAAASkAIQEqABcBKwAhASwAOQEzAAABNAAAATUAAAE2AAAC1wAAAAUAAwAbAA0AGwB6AA4AvAAAAL0AAAAFAAMAAAANAAAAegAAALwAAAC9AAAADgBkACwAZQAsAHQAMgB1ACwAegAoAIAADgCUABIArQAvALQAdAC2AFYA5QARAOkAGQEJABAC7gAaAAUAAwAAAA0AAAB6AAAAvAAAAL0AAAAFAGT/7AB1//IAev/yAID/8gK0ABQABgEiAAoBNwAIATgACAE5AAgBOgAIATsACAAGASIACgE3AAgBOAAIATkACAE6AAgBOwAIAAYBIgAKATcACAE4AAgBOQAIAToACAE7AAgABgEiAAoBNwAIATgACAE5AAgBOgAIATsACAAPALsAAAC8AAAAvQAAAL4AAAD7AAcA/AAH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AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFAAAAAAAGAAAAAAAAAAAAAAAAAAYAAAAAAAAAAAAhAAAAGAAeAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAUAAAAEQAKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHgAUACUAAAAAABsAIgAAAAAAGAAwABAAGwAAAAAAHQAOAAAAGAAAAAAAAAAeABgAIgAAAAgABwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/+r/8wAA/+7/8QAAAAAAAAAAAAD/+QAA/77/5gAA/8L/9v/y//H/9gAAAAAAAP/7AAAAAAAA//sAAAAAAAD/+AAA//oAAAAAAAD//v/qAAD/9gAAAAD/9AAAAAAAAAAAAAAAAAAAAAAAAAAA/+n/8//4/+r/6//y/+j/4v/j//kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/2AAAAAAAAAAAAAAAAAAD/6v/7AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD//f/lAAAAAP/K/8EAAAAAAAD/+//+/7v/7f/L/7cABf/5/+z/8wAA/8MAAAAAAAAAAAAAAAAAAAAAAAD//AAAAAAAAAAAAAAAAAAAAAD/3//BAAAAAAAAAAD/1v/kAAAAAAAAAAAAAAAA/+EAAAAA//3/8//4AAD/7v/0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/oAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP/4//L/+wAA/+3/+gAAAAAAAAAAAAD//f+t/9L/+P+bAAD/4P/w//AAAAAAAAD/9wAA//3/+wAAAAD/9//3AAAAAP/x//b/+gAAAAD/4v/7/+n/+f/xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA//kAAAAAAAAAAAAA//kAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/+//3AAAAAP/3AAAABgAAAAAAAAAAAAD/uf/fAAD/vQAA/+4AAP/8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAD/+QAAAAAAAP/9AAAAAP/9//sAAAAAAAAAAAAA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AAAEagVOAAAFVAVaBWAFZgVsAAAFQgVsAAAFQgVyAAAFeAV+AAAFhAV+AAAFhAWKAAAFHgWQAAAFlgUSAAAEvgUYAAAFHgAAAAAFJAUqAAAFMAU2BTwFQgU2BTwFQgU2BTwFSAReAAAEagVOAAAFVAVaBWAFZgUSAAAEvgUYAAAFHgAAAAAFJAUqAAAFMAU2BTwFQgU2BTwFQgU2BTwFSAReAAAEagVOAAAFVAVsAAAFQgVsAAAFQgVyAAAFeAAB/6wAAAAB/z4AAAAB/z0AAAAB/8AAAAAB/8QAAAAB/8EAAAAB/wUB7gAB/3UB7gAB/wQB7gAB/1MB7gAB/u4B7gAB/wcB7gAB/ygB7gAB/0AB7gAB/w4B7gAB/yAB7gAB/3YB7gAB/wUCvAAB/3UCvAAB/48CvAAB/1MCvAAB/u4CvAAB/wcCvAAB/ycCvAAB/w4CvAAB/yACvAAB/wwB7gAB/roB7gABAYoAAAABAxoAAAABAYoCvAABAUQCvAABAUMDigABAUwAAAABAm0AAAABAWACvAABAWADigABAWADmQABAfkCvAABAYsAAAABAYwCvAABAYwDigABAWAAAAABAVQCvAABAVMDigABAYQAAAABAYUCvAABAZ4AAAABAukACgABAZ0CvAABAZwAAAABAY0CvAABATcAAAABATcCvAABAXYCvAABA0gAAAABA5kAAAABA0gCvAABAVAAAAABAUkCvAABAJ8AAAABAPAAAAABAJ8CvAABAJ4DmQABAV4AAAABAccCvAABAjACvAABAWEAAAABAXkCvAABAgQAAAABAikCvAABAXwAAAABAw0AAAABAXwCvAABAUEAAAABAkEAAAABAUEB7gABAP4B7gABAP4CvAABASYAAAABAZQAAAABASoB7gABASsCvAABASoCywABAY8B7gABAPYAAAABAPYB7gABATMB7gABATMCvAABARMAAAABARMB7gABARMCvAABAS4AAAABAh0ACgABAS4B7gABAT4AAAABAT4B7gABASkAAAABASMB7gABASAAAAABAR8B7gABAqkAAAABAvcAAAABAqkB7gABAQIAAAABAP0B7gABAQQB7gABAIoAAAABANgAAAABAIoCygABAIoCxQABAIr/KgABAIsCygABATUAAAABATUCvAABAaoB7gABAQ4AAAABAdoAAAABAeoB7gABAPgAAAABAUH/KgABASwB7gABAYsB7gABARAAAAABARAB7gABATMAAAABAisAAAABATAB7gABATECvAABATgAAAABAUkB7gABARsAAAABAgAAAAABARwB7gABATQAAAABAaoAAAABAb4B7gABASMAAAABATIB7gABAT7/KgABAQAAAAABAQAB7gABF4oYdAADAAwAqgAnAAIIGgACCCAAAggmAAIILAACCDIAAgg4AAIIOAACCD4AAghEAAIISgACCFAAAghWAAAH9gAAB/wAAQgIAAIIXAACCGIAAghoAAIIbgACCHQAAgh6AAIIegACCIAAAgiGAAIIjAAACAIAAQgOAAIIkgACCCYAAggsAAIIOAACCD4AAgiSAAIIUAABCBQAAgh6AAIIjAACCJgAAgh0ATkIAAgGCAwIAAgGCBIIAAgGCBgIAAgGCB4IAAgGCCQIAAgGCB4IAAgGCCoIAAgGCAwIAAgGCDAINgAACDwINgAACEIISAAACE4ISAAACFQISAAACFoIYAAACE4ISAAACGYISAAACGwIcgAACHgIcgAACH4IhAiKCJAIhAiKCJYIhAiKCJwIhAiKCKIIhAiKCJYIhAiKCKgIhAiKCK4IhAiKCJYIhAiKCKIIhAiKCJAItAAACLoItAAACMAItAAACMYIzAAACLoItAAACNII2AAACN4I2AAACOQI6gjwCPYI/AjwCQII6gjwCQgI6gjwCQ4I6gjwCRQI6gjwCRoI6gjwCSAI6gjwCRQI6gjwCSYI6gjwCPYI6gjwCSwJMgAACTgJMgAACT4JMgAACUQJSgAACVAJVgAACVAJXAAACWIJXAAACQgJaAAACW4JdAAACWIJXAAACWIJegAACYAJhgAACYwJhgAACZIJhgAACZgJngAACYwJhgAACaQJqgmwCbYJqgmwCbwJqgmwCcIJqgmwCbwJqgmwCcgJqgmwCbwJqgmwCc4JqgmwCdQJ2gAACeAJ2gAACeYJqgmwCewJ8gAACfgJ8gAACf4J8gAACgQKCgAACfgKEAAAChYKEAAAChwKEAAACiIKKAAAChYKEAAACi4KNAAAChYKOgAACkAKOgAACkYKTAAACkAKUgAACkAKWApeCmQKWApeCmoKWApeCnAKWApeCnYKWApeCnwKWApeCnYKWApeCnYKWApeCoIKWApeCmQKWApeCogKWApeCo4KlAAACpoKlAAACqAKlAAACqYKlAAACqwKlAAACqYKsgAACfgKsgAACf4KsgAACf4KsgAACrgKsgAACf4KvgAACsQKvgAACsoKvgAACtAKvgAACtYK3AriCugK3AriCu4K3AriCvQK3AriCvoK3AriCwAK3AriCvoK3AriCwYK3AriCugK3AriCwwK3AriCxILGAAACx4LGAAACyQLKgAACzALNgAACzwLNgAAC0ILNgAAC0ILSAAACzwLNgAAC0ILNgAAC04LVAAAC1oLYAtmC2wLYAtmC3ILYAtmC3gLYAtmC3ILYAtmC3ILYAtmC34LYAtmC4QLYAtmC4oLYAtmC5AAAAAAC5YLnAAAC6ILnAAAC6gLnAAAC64LnAAAC7QLnAAAC7oLwAAAC8YLwAAAC8wLwAAAC9IL2AveC+QL2AveC+oL2AveC/AL2AveC/YL2AveC/wL2AveDAIL2AveDAgL2AveC/wMDgveDBQL2AveDBoL2AveDAgL2AveDCAMJgAADCwMJgAADDIMJgAADDgMJgAADDgMPgAADEQMSgAADEQMPgAADFAL2AAAC/wL2AAADFYMXAAAC/wL2AAAC/wMYgAADGgMYgAADG4MdAAADHoMYgAAChYMgAAADGgMYgAADIYMjAySDJgMjAySDJ4MjAySDKQMjAySDKoMjAySDLAMjAySDKoMjAySDKoMjAySDLYAAAAADLwAAAAAC4oMjAySDMIMyAAADM4LKgAADNQLKgAACzALKgAADNQL2AAADNoL2AAADOAL2AAADOYMXAAADNoM7AAADPIM7AAADPgM7AAADP4NBAAADPIM7AAADP4NCgAADPINEAAADRYNHAAADRYNIgAADRYNKA0uDTQNKA0uDToNKA0uDUANKA0uDUYNKA0uDUwNKA0uDUYNKA0uDUYNKA0uDVINKA0uDTQNKA0uDVgNKA0uDV4J2gAADWQJ2gAACeAJ2gAACeAJ2gAADWoJ2gAACeANcAAADXYNcAAADXwNcAAADYINcAAADYgNcAAADYINjgAADZQNjgAADZoNjgAADPgNjgAADaANpg2sDbINpg2sDbgNpg2sDb4Npg2sDcQNpg2sDcoNpg2sDcQNpg2sDdANpg2sDbINpg2sDdYNpg2sDdwN4gAADegN4gAADe4N9AAADLwN9AAADfoN9AAA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AqMCpQF1AqcCpwF4AqkCqQF5ArECsQF6ArYCtgF7Ar8CwAF8AsICwgF+As8CzwF/AtIC0wGAAtUC1QGCAtcC1wGDAtwC3AGEAuAC4AGFAuIC4gGGAu8C8AGHAvYC9gGJAy0DLQGKAAEAGgFtAW4BbwFwAYMBhAGIAYoBnAGfAaMBpgGvAccByQHUAd8B5AHyAfkCAAIFAgYCEwIYAhkAAgAbAAMAhAAAAQsBCwCCAWoBagCDAWwBbACEAXEBggCFAYUBhwCXAYkBiQCaAYsBiwCbAY4BjgCcAZEBlgCdAZgBmQCjAZsBmwClAZ0BngCmAaABoQCoAaQBpQCqAacBqACsAikCKQCuAi4CLgCvAosCiwCwAq8CrwCxArQCtACyArYCtgCzAs8CzwC0AtIC0wC1AtUC1QC3Au8C8AC4AvYC9gC6AAEAAwLkAuUC9wACAA4CdAJ4AAACegKGAAUCiAKIABICigKKABMCjAKMABQCjgKOABUCkAKQABYCkgKpABcCvQK9AC8CvwLAADACwgLCADIC3ALcADMC4ALgADQC4gLiADUAAgAiAIUBCgAAAQwBZwCGAZcBlwDiAZoBmgDjAakBqgDkAbABswDmAbUBwADqAcIBxgD2AcgByAD7AcoBygD8Ac0BzQD9AdAB2gD+Ad0B3gEJAeAB4wELAeUB5gEPAegB6AERAewB8QESAfMB9gEYAfgB+AEcAfoB+wEdAf4B/wEfAgECBAEhAgcCBwElAgkCCQEmAg0CDgEnAhECEgEpAhQCFwErAhoCHAEvAh4CHgEyAiICJAEzAq0CrQE2ArECsQE3AtYC1wE4Ay0DLQE6AAEAAwABAAICqgABABIBawFtAW4BbwFwAYMBhAGIAYoBjAGNAY8BkAGcAZ8BogGjAaYAAQAqAasBrAGtAa4BrwG0AcEBxwHJAcsBzAHOAc8B2wHcAd8B5AHnAekB6gHrAfIB9wH5AfwB/QIAAgUCBgIIAgoCCwIMAg8CEAITAhgCGQIdAh8CIAIhAAIAAgL4AwYAAAMUAysADwABAAgCrQKvArICtwK4Ay0DLgMwAAEAYQFqAW0BbgFxAXIBcwF0AXYBdwF4AXkBegF9AX4BgQGCAYMBhAGOAZEBlAGVAZYBmAGZAZsBnQGkAacBqQGsAa0BrgGwAbEBsgGzAbQBtQG2AbcBuAG5Ab0BvwHAAcIBwwHNAdAB0gHTAdQB1QHWAdcB2AHaAdwB3QHeAd8B4AHhAeIB4wHlAe0B7gHvAfAB9AH1AfgB+QH9Af4B/wIAAgECAgIDAgQCBgIOAhACEQISAhMCFAIVAhYCFwIZAhsCHAIjAAIAHQADAAoAAAAMAA4ACAAQABYACwAYABgAEgAaACMAEwAlACoAHQAsAEIAIwBEAEcAOgBJAFQAPgBZAGIASgBkAGQAVABmAHMAVQB1AHkAYwB7AIMAaACFAJgAcQCcAKUAhQCnAMMAjwDFAMYArADJAM0ArgDPAOgAswDrAOsAzQDuAPoAzgD8AQAA2wECAQoA4AEMASEA6QEjAS4A/wEwATEBCwEzATcBDQE7AWEBEgABAAMDBAMFAx4AAQAHAv4DBAMFAwkDCgMaAx4AAgAEAvgDAwAAAxQDHQAMAyADJgAWAygDKwAdAAIABgL4AwMAAAMHAwkADAMLAxAADwMSAx0AFQMgAyYAIQMoAykAKAACAAMCswKzAAMCwQLBAAIC7ALsAAEAAgAFAioCKgACAi0CLQADAmICYgABArQCtAAEAr4CvgABAAECdABvABMACQAIAAgAEwAAAAAAAAAWABQABwAAAAAADgAaAAEAFQAAAA8AEQACAAQABQAAABAAEgADABwABgAAAAwADAAMAAwAGwANAA0ADQAJAAkAGAAZABgAGQAAAAoAAAAKABcAFwAAAAsAAAALAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABwAAAAwADAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKAAAAAAAAAAwAAAAKAAIALwImAiYABwInAicAGQIpAikAEAIqAioACAIsAiwABwItAi0AGAIuAi4ACgIvAi8ADwJ0AnQABAJ1AnUAAgJ2AncAAQJ4AngABAJ7AnsAEwJ9An0AIQJ+An4AFgJ/An8AEQKAAoAAEwKBAoEAFQKCAoIAIAKDAoMAEgKGAoYACQKHAocADQKIAogADgKJAokAGwKLAosADAKMAowACwKNAo0AHgKOAo4AGgKPAo8AHAKRApEAHQKSApUAAwKWApYABQKaApsAAgKcApwABgKeAp4ABgKgAqAAHwKiAqIAHwKkAqUAFAKmAqYAFwKoAqgAFwK9Ar0AFgK/AsAAAwLCAsIAAwLMAswAAwLcAtwAAwLgAuAAHwLiAuIAHwACAA0CJgImAAkCJwInAAMCKAIoAAgCKgIqAAECLAIsAAcCLQItAAUCLwIvAAkCTwJPAAQCVQJVAAYCWQJZAAQCXwJfAAYCYgJiAAICvgK+AAIAAgCFAAMADAABAA0ADgAPADgAOgAYAGQAaAAIAHQAeQADAHoAegAVAHsAfwAEAIUAkAAcAJIAmAAcAJoApQAcALAAsAAdALwAvAAdAMEAwQAdAMgAygAdAMwAzwAdANAA2wAcANwA3AAdAN4A3gAcAN8A4gAdAOMA6AAmAQEBAQAoARgBHAAcASMBIwAcASoBKgAdATMBNgAdAVgBXAAcAWoBagABAXABcAAXAXQBdAAyAXUBdQAxAXsBewACAYIBggAIAYMBhAAwAYYBhgAVAY0BjQAQAY8BjwACAZMBkwAHAZYBlgAYAZcBlwAIAZkBmQAvAZoBmgAIAZsBmwAPAZ0BnQABAZ8BnwAXAaABoAACAaIBogACAaQBpAABAacBpwABAakBqQAcAaoBqgAeAasBrgAdAa8BrwAgAbABsgAcAbQBtAApAbUBuQAdAboBugAhAbsBvAAdAb0BvQAcAb4BvwAdAcABwAAcAcEBwQAnAcQBxAAcAcUBxQAoAcYBxgAfAccBywAdAcwBzAAkAc0BzQAdAc4BzgAhAc8BzwAdAdAB0AAmAdEB0QAcAdcB1wAdAdgB2AAlAdoB2gAcAdwB3AAjAd0B3QAcAd8B3wAFAeQB5AAiAeUB5gAdAfIB8gAgAfMB8wAhAfYB9gAfAfcB9wAhAfgB+AAcAfkB+QAFAfoB+wAdAf0B/QAjAf4B/gAcAgACAAAFAgUCBQAiAgYCBwAdAhACEAAjAhECEQAcAhMCEwAFAhgCGAAiAhkCGgAdAiQCJAAdAioCKgAbAj4CPgAOAkgCSAAOAmICYgAWAnQCdAAsAnUCdQAaAnYCdwAZAngCeAAsAn0CfQAtAoECgQArAoICggAuAoMCgwAJAoQChAAUAocChwAMAokCiQAzAosCiwAKAo0CjQANAo8CjwA0ApECkQALApIClQASApYClgA1ApcCmQATApoCmwAaApwCnAAGAp4CngAGAq0CrQAcArYCtgAEAr4CvgAWAr8CwAASAsECwQAqAsICwgASAswCzAASAtIC0gABAtcC1wAdAtwC3AASAuwC7AARAAIASQANAA4AAwAPAA8AAQAQABUAAgAWABkADAAaACMAAwAkACQABAAlACkABQAqAC0ADgAuAC4AEQAvADcADgA4ADoAEQA7ADwABwA9AD4ACAA/AD8ACQBAAEIACABDAEkADgBKAFQADABVAFUAAwBWAFYACgBXAFcAEABYAFgADABZAFwACwBdAGIADQBjAGMABgBkAGgADwBpAHMAEQB0AHkAEgB6AHoAEwB7AH8AFACAAIMAFQCEAIQADAELAQsABgFsAWwAAQFxAXMAAwF0AXQABwF1AXUAAQF2AXgADgF5AXoABwF7AX0ADgF+AX4ADAF/AX8ADgGAAYAACgGBAYEAAgGCAYIADwGFAYUADAGGAYYAEwGHAYcADgGJAYkADgGLAYsADgGOAY4ADgGRAZEADQGSAZIAAgGTAZMADAGUAZUADgGWAZYAEQGYAZgADAGZAZkADgGbAZsAAwGeAZ4ADAGgAaEADgGlAaUADAGoAagADAIpAikAAQIuAi4AAQKLAosADgKvAq8ADQK0ArQACgK2ArYAFALPAs8ADALTAtMADgLVAtUAEgLvAvAADgL2AvYADgACAQcAAQACADUAAwAMADkADQAOAD4AEAAVAAUAJQApAAUAOAA6AAQASgBVAAUAWABYAAUAXQBiAAYAZABoAAcAaQBzAAgAdAB5AAoAegB6AEEAewB/AAsAgACDAFYAhACEAAUAhQCQABwAkQCRAFoAkgCYABwAmQCZACEAmgClABwApgCmACIApwCrACMArACuAFoArwCvAFMAsACwAEQAsQCxAFMAsgC0AFIAtQC3AFMAuAC4AFIAuQC5AFMAugC6AFIAuwC7AFMAvAC8AEQAvQC9AFMAvgC+AFIAvwDAAFoAwQDBAEQAwgDGAFoAxwDHAFcAyADKAEQAywDLADMAzADPAEQA0ADbABwA3ADcAEQA3QDdAFoA3gDeABwA3wDiAEQA4wDoACcA6QDpAFoA6gDqACIA6wDvACgA8AD6ACoA+wEAACsBAQEBAEkBAgEGACsBBwEKAEoBDAEXAB0BGAEcABwBHQEhACoBIgEiACIBIwEjABwBJAEnACMBKAEpAFMBKgEqAEQBKwErAFMBLAEsAFIBLQExAFoBMgEyAFcBMwE2AEQBNwE7ACgBPAFLACoBTAFXAB0BWAFcABwBXQFhACoBYgFnACIBaAFpAC8BagFqADkBcAFwADoBdAF0AEIBdQF1AAwBewF7AAIBfgF+AAUBgQGBAAUBggGCAAcBgwGEAAkBhQGFAAUBhgGGAEEBhwGHAAEBjQGNAAMBjwGPAAIBkQGRAAYBkgGSAAUBkwGTAEABlgGWAAQBlwGXAAcBmQGZAFEBmgGaAAcBmwGbAD4BnAGcAD8BnQGdADkBngGeAAUBnwGfADoBoAGgAAIBoQGhAAEBogGiAAIBowGjAD8BpAGkADkBpQGlAAUBpgGmAD8BpwGnADkBqAGoAAUBqQGpABwBqgGqAB4BqwGuAEQBrwGvAEUBsAGyABwBswGzAEsBtAG0ACwBtQG5AEQBugG6ACABuwG8AEQBvQG9ABwBvgG/AEQBwAHAABwBwQHBACkBwgHDACsBxAHEABwBxQHFAEkBxgHGAB8BxwHLAEQBzAHMACUBzQHNAEQBzgHOACABzwHPAEQB0AHQACcB0QHRABwB0gHSAEcB0wHTAFMB1AHUAFIB1QHVAFMB1gHWAFoB1wHXAEQB2AHYAEgB2QHZAFoB2gHaABwB2wHbABMB3AHcACQB3QHdABwB3gHeAEsB3wHfAC0B4AHiACoB4wHjAFoB5AHkAEYB5QHmAEQB5wHqACoB6wHrACYB7AHsAFoB7QHtAB0B7gHvACoB8AHwAB0B8gHyAEUB8wHzACAB9AH1ACoB9gH2AB8B9wH3ACAB+AH4ABwB+QH5AC0B+gH7AEQB/AH8ABMB/QH9ACQB/gH+ABwB/wH/AEsCAAIAAC0CAQIDACoCBAIEAFoCBQIFAEYCBgIHAEQCCAILACoCDAIMACYCDQINAFoCDgIOAB0CDwIPABMCEAIQACQCEQIRABwCEgISAEsCEwITAC0CFAIWACoCFwIXAFoCGAIYAEYCGQIaAEQCGwIgACoCIQIhACYCIgIiAFoCIwIjAB0CJAIkAEQCJgImADgCJwInAF4CKAIoAD0CKQIpADYCKgIqABcCKwIrABYCLAIsADgCLQItADQCLgIuABUCLwIvAC4CdAJ0AE4CdQJ1AEMCdgJ3AFwCeAJ4AE4CegJ6AF0CewJ7ADACfQJ9AFQCfgJ+AFsCfwJ/AA4CgAKAADACggKCAE8CgwKDABAChAKEAFUChwKHAEwCiQKJABECiwKLABICjQKNAE0CjwKPADsCkQKRADwCkgKVABoClgKWAFAClwKZABsCmgKbAEMCnAKcADICnQKdADMCngKeADICnwKfADMCoAKgABgCoQKhAFgCogKiABgCowKjAFgCpAKlADECpgKmABkCpwKnAFkCqAKoABkCqQKpAFkCqgKqADUCrQKtABwCrwKvAAYCtgK2AAsCvQK9AFsCvwLAABoCwgLCABoCzALMABoCzwLPAAUC0gLSADkC1gLWACEC1wLXAEQC3ALcABoC4ALgABgC4gLiABgC5ALkAA8C5QLlAA0C6ALqABQC6wLrADcC9wL3AA0DLQMtAFMAAQLkAAEAAQACAA8AAwAMAAUADQAOAAEAZABoAAIAdAB5AAMAewB/AAQBagFqAAUBggGCAAIBlwGXAAIBmgGaAAIBmwGbAAEBnQGdAAUBpAGkAAUBpwGnAAUCtgK2AAQC0gLSAAUAAQJ0AG8AFAAJAAgACAAUAAAACgAXABgAFQAGAAAAFwARABwAAQAWAAcAEgAAAAIAAAAEAAAAEwAAAAMAAAAFAAAADwAPAA8ADwAdABAAEAAQAAkACQAaABsAGgAbAAsADQALAA0AGQAZAAwADgAMAA4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGAAAADwAPAAAADwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA0AAAAAAAAADwAAAA0AAgDBAAMADAABAA0ADgACABAAFQAGACUAKQAGADgAOgAFAEoAVQAGAFgAWAAGAF0AYgAsAGQAaAAHAGkAcwAVAHQAeQAXAHoAegApAHsAfwAYAIAAgwAyAIQAhAAGAIUAkAAIAJEAkQA0AJIAmAAIAJkAmQANAJoApQAIAKYApgAcAKcAqwAOAKwArgA0ALAAsAAkALIAtAAPALgAuAAPALoAugAPALwAvAAkAL4AvgAPAL8AwAA0AMEAwQAkAMIAxgA0AMcAxwAzAMgAygAkAMsAywAxAMwAzwAkANAA2wAIANwA3AAkAN0A3QA0AN4A3gAIAN8A4gAkAOMA6AARAOkA6QA0AOoA6gAcAOsA7wAgAPAA+gAiAPsBAAAjAQEBAQAmAQIBBgAjAQcBCgAnAQwBFwAJARgBHAAIAR0BIQAiASIBIgAcASMBIwAIASQBJwAOASoBKgAkASwBLAAPAS0BMQA0ATIBMgAzATMBNgAkATcBOwAgATwBSwAiAUwBVwAJAVgBXAAIAV0BYQAiAWIBZwAcAWoBagABAXABcAADAXQBdAAqAXUBdQAwAXsBewAEAX4BfgAGAYEBgQAGAYIBggAHAYMBhAAWAYUBhQAGAYYBhgApAYcBhwAUAY0BjQAuAY8BjwAEAZEBkQAsAZIBkgAGAZMBkwAvAZYBlgAFAZcBlwAHAZkBmQATAZoBmgAHAZsBmwACAZwBnAAtAZ0BnQABAZ4BngAGAZ8BnwADAaABoAAEAaEBoQAUAaIBogAEAaMBowAtAaQBpAABAaUBpQAGAaYBpgAtAacBpwABAagBqAAGAakBqQAIAaoBqgAlAasBrgAkAa8BrwAKAbABsgAIAbMBswAoAbQBtAASAbUBuQAkAboBugALAbsBvAAkAb0BvQAIAb4BvwAkAcABwAAIAcEBwQAhAcIBwwAjAcQBxAAIAcUBxQAmAcYBxgAaAccBywAkAcwBzAAeAc0BzQAkAc4BzgALAc8BzwAkAdAB0AARAdEB0QAIAdIB0gAbAdQB1AAPAdYB1gA0AdcB1wAkAdgB2AAQAdkB2QA0AdoB2gAIAdsB2wAZAdwB3AAdAd0B3QAIAd4B3gAoAd8B3wArAeAB4gAiAeMB4wA0AeQB5AAMAeUB5gAkAecB6gAiAesB6wAfAewB7AA0Ae0B7QAJAe4B7wAiAfAB8AAJAfIB8gAKAfMB8wALAfQB9QAiAfYB9gAaAfcB9wALAfgB+AAIAfkB+QArAfoB+wAkAfwB/AAZAf0B/QAdAf4B/gAIAf8B/wAoAgACAAArAgECAwAiAgQCBAA0AgUCBQAMAgYCBwAkAggCCwAiAgwCDAAfAg0CDQA0Ag4CDgAJAg8CDwAZAhACEAAdAhECEQAIAhICEgAoAhMCEwArAhQCFgAiAhcCFwA0AhgCGAAMAhkCGgAkAhsCIAAiAiECIQAfAiICIgA0AiMCIwAJAiQCJAAkAp0CnQAxAp8CnwAxAq0CrQAIAq8CrwAsArYCtgAYAs8CzwAGAtIC0gABAtYC1gANAtcC1wAkAAIAhwCFAI4AAgCPAJAABgCRAJEAAQCSAJcABACZAJkABwCaAJoABQCcAKUABgCmAKYACACnAKsACQCsAK4AAwCvAK8ACwCwALAAAgCxALEACwCyALQADAC1ALcACwC4ALgADAC5ALkACwC6ALoADAC7ALsACwC8ALwAAgC9AL0ACwC+AL4ADAC/AMEADQDEAMQABQDGAMYADgDHAMcADwDIAM8AAwDQANoAAQDbANsABgDcAN0AAQDeAN4AAgDfAOIAEADjAOgAEQDpAOkACgDqAOoAGADrAOwAEgDtAO0AEwDuAO8AEgDwAPoAAgD7AQAAFQEBAQEAFgECAQYAFQEHAQoAFwEMARUAAwEWARcABgEYASEAAgEiASIACAEjASMAAgEkAScACQEoASkACwEqASoAAgErASsACwEsASwADAEvAS8ABQExATEADgEyATIADwEzATYAEAE3ATgAEgE5ATkAFAE6ATsAEgE8AUsAAgFMAVUAAwFWAVcABgFYAWEAAgFiAWIACAFjAWMACwFlAWUACAFmAWYACwGXAZcAAwGaAZoAAQGpAakAAgGqAaoAAQGwAbIABgGzAbMADQG1AbcAAgG4AbkADQG6AbwAAgG9Ab0AAQG+Ab4AAgG/Ab8AAQHAAcAABAHCAcMAFQHEAcQAAQHFAcUAFgHGAcYAAgHIAcgAAgHKAcoAAgHNAc0AAgHQAdAAEQHRAdEABAHSAdIAAQHTAdMACwHUAdQADAHVAdUACwHWAdYAAwHXAdcAAQHYAdkAAgHaAdoABgHdAd0AAgHeAd4ADQHgAeIAAgHjAeMADQHlAeYAAwHoAegAAgHsAewAAQHtAe0AAwHuAe8AAgHwAfAABgHxAfEAAQHzAfYAAgH4AfgAAgH6AfsAAgH+Af4AAgH/Af8ADQIBAgMAAgIEAgQADQIHAgcAAwIJAgkAAgINAg0AAQIOAg4AAwIRAhEAAgISAhIADQIUAhYAAgIXAhcADQIaAhoAAwIbAhwAAgIeAh4AAgIiAiIAAQIjAiMABgIkAiQAAgKtAq0ABAKxArEACALWAtYABwLXAtcAAgMtAy0ACwABAAEDLQBXAFcABgAGAAYABgAGAAYABgAGAAYABgAHAAcADAABAAEAAQABAAEAAQAMAAAADAAAAAwADAAMAAwADAAMAAwADAAMAAwADAABAAEAAQABAAEADAAMAAwADAAMAAwADAAMAAwADAAMAAwADAAMADcANwA3AAwADAAMAAwADAAMAAwAAAAMAAwADAAMAAwADAAMAAEAAQABAAEAAQABAAEAAQABAAEAAQABAAwADAABAAwADAAMAAwACwALAAsACwALAAsADAANAA0ADQANAA0AAgACAAIAAgACAAIAAgACAAIAAgACAA4ADgAOAA4ADgAOAA8AEAAQABAAEAAQAAMAAwADAAMAAQA7ADsAOwA7ADsAOwA7ADsAOwA7ADsAOwBKADsAOwA7ADsAOwA7ADsAPgA7ADsAOwA7ADsAOwA7ADsAOwA7ADsAOwAdAD8APwA/AD8APwBKAEoASgBMAEsATABNAE0ATQBMAEwATABNAEwATQBMAEsATABNAEoASgBLAEoASgBKAEoASgBcAEsASwBLAC4ASwBLAEsASwA7ADsAOwA7ADsAOwA7ADsAOwA7ADsAOwBLAEoAOwBLAEsASwBLACAAIAAgACAAIAAgAEoAHQAhACEAIQAhACEAYABgAGAAYABgAGAAYABgAGAAYABgACMAIwAjACMAIwAjACQAIwAjACMAIwAjACUAJQAlACUADAA8ADwAPAA8ADwAPAA8ADwAPAA8ADwAPAA7ADsAOwA7ADsAYABgAGAAYABgAB0AOwA/AD8APwA/AEwATABLAEwATQBKAEoASgBKAEoAXABLAEsASwBLACEAIQAhACEAIQBgAGAAYABgAGAAYABgAGAAYABgAGAAYABgAGAAYABgADwAPAA8ADwAPAA8ADwAPAA8ADwAPAA8ADsAOwA7ADsAOwBgAGAAYABgAGAAHQAdAB0AHQAdAB0AUgBSAAYADAAMAAwADAAMAAAADAAMAAwAMwAyAAwADAAMAAwADAAJAAwADAABAAwADAABAA0AMQAxAAEADwAIAAwADAAMAAwADAAKAAwACQAMAAsAAQAAAAwADAA3AA0ADAA2AA0ABwAAAAYAAQAAAAkACAAJAAAABgABAAAABgABADsAPQBLAEsASwBLABkAOwA7ADsAKAAmAEsASwBLAEsASwAaAEsASwA7AEsASwA7ACIAIwAjADsAJAAYAEsASwBLAEsASwAeAEsAGgBLACAAOwAcAEwATQBMAEoASwBBAEoAOwA4AEAAOwAoACcAYABgAGAASgAbAEsASwBgAGAAYABgAB8ASgA8AGAAYAA8AAwAGQAaAGAAYAAYABoAOwAnAEsASwA4AEAAOwAoACcAYABgAGAASgAbAEsASwBgAGAAYABgAB8ASgA8ADgAQAA7ACgAJwBgAGAAYABKABsASwBLAGAAYABgAGAAYABgAB8ASgA8AEsAAAAAAFAAAAAAAGcARwAAAFUAAABdAAAAAAAAAAAAAAAAAAAAAAAAAAAAbABpAGsAagBoAGYAbAAAAAAAAABsAGkAawBqAGgAZgBsAAAAAAAAAFsAUQBaAFkASQBIAFsAZQBFAE8AWwBRAFoAWQBJAEgAWwBlAEUATwBiAFEAUQBaAFEAWQBRAFoAWQBJAFEASABRAFEAWQBIAGUAUQAqABYAFQAVACoARgAAACsAZAAEAF8AEQArAAAALwASAAAAAAAAACkAAAATAAwAFAAAADUAAAA0AAAAAAA6ADoAOgA6ADAAAAAAAAAAFgAWAC0ALgAtAC4AOQAXADkAFwAsACwAAAAAAAAAAABXAAAAAAA7AAAACwAAAAAAAABjAFQAAAAQAAAAAAAAAAAAAAAAAF8AYgA6ADoAAAA6AAAAAAAAAAAAAAAAAAAAAAAAADoAAAAAAAEAAAAAAAYADABYAGEAPgBLAFMAUwAAAAAAOgBWAAAAAAA5AAAAOQAAAAAAQgBeAG0AQwBDAEMABQBEAE4ATgAMAAwAAAAAAAAAAAAMAAwAQgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAATAACAAAAAgAVAAMADAABAGQAaAACAHQAeQADAHoAegAEAHsAfwAFAMsAywAHAPsBAAAGAQIBBgAGAWoBagABAYIBggACAYYBhgAEAZcBlwACAZoBmgACAZ0BnQABAaQBpAABAacBpwABAcIBwwAGAp0CnQAHAp8CnwAHArYCtgAFAtIC0gABAAIADAFtAW8AAwFwAXAAAQGDAYQABQGIAYgAAQGKAYoAAQGMAY0ABAGPAZAABAGcAZwAAgGfAZ8AAQGiAaIABAGjAaMAAgGmAaYAAgACAMsAAQACAEAAAwAMAAEADQAOAEEAEAAVADAAJQApADAAOAA6AEIASgBVADAAWABYADAAXQBiAAgAZABoAAkAegB6AAsAhACEADAAhQCQADQAkgCYADQAmgClADQAsACwADUAvAC8ADUAwQDBADUAyADKADUAywDLACsAzADPADUA0ADbADQA3ADcADUA3gDeADQA3wDiADUA4wDoAEYA8AD6ADkA+wEAAB8BAQEBACABAgEGAB8BDAEXADYBGAEcADQBHQEhADkBIwEjADQBKgEqADUBMwE2ADUBPAFLADkBTAFXADYBWAFcADQBXQFhADkBagFqAAEBcAFwAAMBdAF0AA0BdQF1AAwBewF7AAUBfgF+ADABgQGBADABggGCAAkBgwGEAAoBhQGFADABhgGGAAsBhwGHAAIBjQGNAAcBjwGPAAUBkQGRAAgBkgGSADABkwGTAAYBlgGWAEIBlwGXAAkBmQGZAC8BmgGaAAkBmwGbAEEBnAGcAAQBnQGdAAEBngGeADABnwGfAAMBoAGgAAUBoQGhAAIBogGiAAUBowGjAAQBpAGkAAEBpQGlADABpgGmAAQBpwGnAAEBqAGoADABqQGpADQBqgGqADcBqwGuADUBrwGvABcBsAGyADQBswGzACMBtAG0ACEBtQG5ADUBugG6ABgBuwG8ADUBvQG9ADQBvgG/ADUBwAHAADQBwQHBAB4BwgHDAB8BxAHEADQBxQHFACABxgHGABYBxwHLADUBzAHMABsBzQHNADUBzgHOABgBzwHPADUB0AHQAEYB0QHRADQB0gHSABoB1wHXADUB2AHYAB0B2gHaADQB2wHbADEB3AHcADgB3QHdADQB3gHeACMB3wHfACIB4AHiADkB5AHkABkB5QHmADUB5wHqADkB6wHrABwB7QHtADYB7gHvADkB8AHwADYB8gHyABcB8wHzABgB9AH1ADkB9gH2ABYB9wH3ABgB+AH4ADQB+QH5ACIB+gH7ADUB/AH8ADEB/QH9ADgB/gH+ADQB/wH/ACMCAAIAACICAQIDADkCBQIFABkCBgIHADUCCAILADkCDAIMABwCDgIOADYCDwIPADECEAIQADgCEQIRADQCEgISACMCEwITACICFAIWADkCGAIYABkCGQIaADUCGwIgADkCIQIhABwCIwIjADYCJAIkADUCJgImADsCJwInACQCKAIoAEgCKQIpAC0CKgIqAEUCLAIsADsCLQItACwCLgIuAEMCLwIvAEsCdAJ0ACcCdQJ1ABUCdgJ3ABQCeAJ4ACcCegJ6AEQCewJ7ACgCfAJ8ACkCfQJ9AD4CfgJ+ADwCfwJ/AA4CgAKAACgCgQKBAEwCggKCAEcCgwKDAA8ChAKEAD8ChQKFAD0ChwKHACUCiQKJABACiwKLABICjQKNACYCjwKPABECkQKRABMCkgKVADIClgKWAC4ClwKZADMCmgKbABUCnAKcADoCnQKdACsCngKeADoCnwKfACsCoQKhAEkCowKjAEkCpAKlACoCpwKnAEoCqQKpAEoCqgKqAEACrQKtADQCrwKvAAgCvQK9ADwCvwLAADICwgLCADICzALMADICzwLPADAC0gLSAAEC1wLXADUC3ALcADIAAgAeAasBqwAJAawBrgADAa8BrwABAbQBtAAJAcEBwQAHAccBxwABAckByQABAcsBzAAFAc4BzwAFAdwB3AAEAd8B3wAKAeQB5AACAecB5wAIAekB6QAIAeoB6wAGAfIB8gABAfcB9wAFAfkB+QAKAf0B/QAEAgACAAAKAgUCBgACAggCCAAIAgoCCgAIAgsCDAAGAhACEAAEAhMCEwAKAhgCGQACAh0CHQAIAh8CHwAIAiACIQAGAAIAdgABAAIAJQCFAJAAHACSAJgAHACaAKUAHADLAMsAFgDQANsAHADeAN4AHADjAOgACwDwAPoAKgD7AQAADQEBAQEADgECAQYADQEMARcAHQEYARwAHAEdASEAKgEjASMAHAE8AUsAKgFMAVcAHQFYAVwAHAFdAWEAKgGpAakAHAGqAaoAHgGvAa8AIAGwAbIAHAGzAbMAEQG0AbQADwG6AboALgG9Ab0AHAHAAcAAHAHBAcEADAHCAcMADQHEAcQAHAHFAcUADgHGAcYAHwHMAcwACAHOAc4ALgHQAdAACwHRAdEAHAHSAdIABwHYAdgACgHaAdoAHAHbAdsAGgHcAdwAIQHdAd0AHAHeAd4AEQHfAd8AEAHgAeIAKgHkAeQABgHnAeoAKgHrAesACQHtAe0AHQHuAe8AKgHwAfAAHQHyAfIAIAHzAfMALgH0AfUAKgH2AfYAHwH3AfcALgH4AfgAHAH5AfkAEAH8AfwAGgH9Af0AIQH+Af4AHAH/Af8AEQIAAgAAEAIBAgMAKgIFAgUABgIIAgsAKgIMAgwACQIOAg4AHQIPAg8AGgIQAhAAIQIRAhEAHAISAhIAEQITAhMAEAIUAhYAKgIYAhgABgIbAiAAKgIhAiEACQIjAiMAHQImAiYAJgIqAioALQIsAiwAJgItAi0ALAIuAi4AKAIvAi8AKwJ0AnQAEwJ1AnUABQJ2AncABAJ4AngAEwJ7AnsAJAJ9An0AIgJ+An4AGAJ/An8AAQKAAoAAJAKCAoIAFwKDAoMAAgKEAoQAIwKFAoUAGQKHAocAEgKJAokAAwKLAosAJwKSApUAGwKWApYALwKXApkAKQKaApsABQKcApwAFQKdAp0AFgKeAp4AFQKfAp8AFgKkAqUAFAKqAqoAJQKtAq0AHAK9Ar0AGAK/AsAAGwLCAsIAGwLMAswAGwLcAtwAGwABAAAACgKsDwAAA0RGTFQAFGN5cmwARGxhdG4AqAAEAAAAAP//ABMAAAANABoAJwA0AEEATgBgAG0AegCHAJQAoQCuALsAyADVAOIA7wAKAAFCR1IgADYAAP//ABMAAQAOABsAKAA1AEIATwBhAG4AewCIAJUAogCvALwAyQDWAOMA8AAA//8AFAACAA8AHAApADYAQwBQAFsAYgBvAHwAiQCWAKMAsAC9AMoA1wDkAPEAOgAJQVpFIABmQ0FUIACSQ1JUIADAS0FaIADsTU9MIAEYTkxEIAFGUk9NIAF0VEFUIAGgVFJLIAHMAAD//wATAAMAEAAdACoANwBEAFEAYwBwAH0AigCXAKQAsQC+AMsA2ADlAPIAAP//ABMABAARAB4AKwA4AEUAUgBkAHEAfgCLAJgApQCyAL8AzADZAOYA8wAA//8AFAAFABIAHwAsADkARgBTAFwAZQByAH8AjACZAKYAswDAAM0A2gDnAPQAAP//ABMABgATACAALQA6AEcAVABmAHMAgACNAJoApwC0AMEAzgDbAOgA9QAA//8AEwAHABQAIQAuADsASABVAGcAdACBAI4AmwCoALUAwgDPANwA6QD2AAD//wAUAAgAFQAiAC8APABJAFYAXQBoAHUAggCPAJwAqQC2AMMA0ADdAOoA9wAA//8AFAAJABYAIwAwAD0ASgBXAF4AaQB2AIMAkACdAKoAtwDEANEA3gDrAPgAAP//ABMACgAXACQAMQA+AEsAWABqAHcAhACRAJ4AqwC4AMUA0gDfAOwA+QAA//8AEwALABgAJQAyAD8ATABZAGsAeACFAJIAnwCsALkAxgDTAOAA7QD6AAD//wAUAAwAGQAmADMAQABNAFoAXwBsAHkAhgCTAKAArQC6AMcA1ADhAO4A+wD8YWFsdAXqYWFsdAXyYWFsdAX6YWFsdAYCYWFsdAYKYWFsdAYSYWFsdAYaYWFsdAYiYWFsdAYqYWFsdAYyYWFsdAY6YWFsdAZCYWFsdAZKY2FsdAZSY2FsdAZYY2FsdAZeY2FsdAZkY2FsdAZqY2FsdAZwY2FsdAZ2Y2FsdAZ8Y2FsdAaCY2FsdAaIY2FsdAaOY2FsdAaUY2FsdAaaY2FzZQagY2FzZQamY2FzZQasY2FzZQayY2FzZQa4Y2FzZQa+Y2FzZQbEY2FzZQbKY2FzZQbQY2FzZQbWY2FzZQbcY2FzZQbiY2FzZQboY2NtcAbuY2NtcAb2Y2NtcAb+Y2NtcAcGY2NtcAcOY2NtcAcWY2NtcAceY2NtcAcmY2NtcAcuY2NtcAc2Y2NtcAc+Y2NtcAdGY2NtcAdOZG5vbQdWZG5vbQdcZG5vbQdiZG5vbQdoZG5vbQduZG5vbQd0ZG5vbQd6ZG5vbQeAZG5vbQeGZG5vbQeMZG5vbQeSZG5vbQeYZG5vbQeeZnJhYwekZnJhYweuZnJhYwe4ZnJhYwfCZnJhYwfMZnJhYwfWZnJhYwfgZnJhYwfqZnJhYwf0ZnJhYwf+ZnJhYwgIZnJhYwgSZnJhYwgcbGlnYQgmbGlnYQgsbGlnYQgybGlnYQg4bGlnYQg+bGlnYQhEbGlnYQhKbGlnYQhQbGlnYQhWbGlnYQhcbGlnYQhibGlnYQhobGlnYQhubG9jbAh0bG9jbAh6bG9jbAiAbG9jbAiGbG9jbAiMbnVtcgiSbnVtcgiYbnVtcgiebnVtcgikbnVtcgiqbnVtcgiwbnVtcgi2bnVtcgi8bnVtcgjCbnVtcgjIbnVtcgjObnVtcgjUbnVtcgjab3Jkbgjgb3Jkbgjob3Jkbgjwb3Jkbgj4b3JkbgkAb3JkbgkIb3JkbgkQb3JkbgkYb3Jkbgkgb3Jkbgkob3Jkbgkwb3Jkbgk4b3JkbglAcG51bQlIcG51bQlOcG51bQlUcG51bQlacG51bQlgcG51bQlmcG51bQlscG51bQlycG51bQl4cG51bQl+cG51bQmEcG51bQmKcG51bQmQc2FsdAmWc2FsdAmcc2FsdAmic2FsdAmoc2FsdAmuc2FsdAm0c2FsdAm6c2FsdAnAc2FsdAnGc2FsdAnMc2FsdAnSc2FsdAnYc2FsdAnec2luZgnkc2luZgnqc2luZgnwc2luZgn2c2luZgn8c2luZgoCc2luZgoIc2luZgoOc2luZgoUc2luZgoac2luZgogc2luZgomc2luZgosc3MwMQoyc3MwMQo4c3MwMQo+c3MwMQpEc3MwMQpKc3MwMQpQc3MwMQpWc3MwMQpcc3MwMQpic3MwMQpoc3MwMQpuc3MwMQp0c3MwMQp6c3MwMgqAc3MwMgqGc3MwMgqMc3MwMgqSc3MwMgqYc3MwMgqec3MwMgqkc3MwMgqqc3MwMgqwc3MwMgq2c3MwMgq8c3MwMgrCc3MwMgrIc3MwMwrOc3MwMwrUc3MwMwrac3MwMwrgc3MwMwrmc3MwMwrsc3MwMwryc3MwMwr4c3MwMwr+c3MwMwsEc3MwMwsKc3MwMwsQc3MwMwsWc3MwNAscc3MwNAsic3MwNAsoc3MwNAsuc3MwNAs0c3MwNAs6c3MwNAtAc3MwNAtGc3MwNAtMc3MwNAtSc3MwNAtYc3MwNAtec3MwNAtkc3Vicwtqc3Vicwtwc3Vicwt2c3Vicwt8c3VicwuCc3VicwuIc3VicwuOc3VicwuUc3Vicwuac3Vicwugc3Vicwumc3Vicwusc3Vicwuyc3Vwcwu4c3Vwcwu+c3VwcwvEc3VwcwvKc3VwcwvQc3VwcwvWc3Vwcwvcc3Vwcwvic3Vwcwvoc3Vwcwvuc3Vwcwv0c3Vwcwv6c3VwcwwAdG51bQwGdG51bQwMdG51bQwSdG51bQwYdG51bQwedG51bQwkdG51bQwqdG51bQwwdG51bQw2dG51bQw8dG51bQxCdG51bQxIdG51bQxOAAAAAgAAAAEAAAACAAAAAQAAAAIAAAABAAAAAgAAAAEAAAACAAAAAQAAAAIAAAABAAAAAgAAAAEAAAACAAAAAQAAAAIAAAABAAAAAgAAAAEAAAACAAAAAQAAAAIAAAABAAAAAgAAAAEAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABsAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAABABUAAAACAAIAAwAAAAIAAgADAAAAAgACAAMAAAACAAIAAwAAAAIAAgADAAAAAgACAAMAAAACAAIAAwAAAAIAAgADAAAAAgACAAMAAAACAAIAAwAAAAIAAgADAAAAAgACAAMAAAACAAIAAwAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAEADQAAAAMADgAPABAAAAADAA4ADwAQAAAAAwAOAA8AEAAAAAMADgAPABAAAAADAA4ADwAQAAAAAwAOAA8AEAAAAAMADgAPABAAAAADAA4ADwAQAAAAAwAOAA8AEAAAAAMADgAPABAAAAADAA4ADwAQAAAAAwAOAA8AEAAAAAMADgAPABAAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABABYAAAABAAgAAAABAAYAAAABAAUAAAABAAcAAAABAAQAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAABAAwAAAACABEAEgAAAAIAEQASAAAAAgARABIAAAACABEAEgAAAAIAEQASAAAAAgARABIAAAACABEAEgAAAAIAEQASAAAAAgARABIAAAACABEAEgAAAAIAEQASAAAAAgARABIAAAACABEAEgAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAEwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEAFwAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEACgAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGAAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGQAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAGgAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEAHAAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACQAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEACwAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAAAAEAFAAjAEgAUABYAGYAcAB4AIAAigCUAJwApACsALQAvADEAMwA1ADeAOgA8AD4AQABCAEQARgBIAEoATABOgFCAUoBUgFaAWIBagABAAAAAQUQAAMAAAABBeAABgAAAAQBGgEsAUABUgAGAAAAAgFWAWgAAQAAAAEBcAABAAAAAQFuAAYAAAACAXQBiAAGAAAAAgGSAaQAAQAAAAEBrAABAAAAAQHUAAEAAAABAdIAAQAAAAEB0AABAAAAAQHOAAEAAAABAcwAAQAAAAEBygABAAAAAQHIAAYAAAACAcYB2AAGAAAAAgHgAfIABAAAAAEB+gABAAAAAQIGAAEAAAABAiQAAQAAAAECQgAEAAgAAQJ6AAEAAAABApQAAQAAAAECyAABAAAAAQL8AAEAAAABA3QABgAAAAIDnAOwAAEAAAABA7oAAQAAAAEHkAAEAAAAAQesAAEAAAABB8IAAQAAAAEHxAABAAAAAQfCAAEAAAABB8gAAwAAAAEHxgABB84AAQAAAB0AAwAAAAEHtAACB8YHvAABAAAAHQADAAEHugABB7oAAAABAAAAHQADAAEHxAABB6gAAAABAAAAHQADAAAAAQeWAAEHwgABAAAAHQADAAEHsAABB4QAAAABAAAAHQABB64ABgACB64ABABiAGgA6ADvAAMAAAACB6wHsgABB6wAAQAAAB4AAwAAAAIHpAeeAAEHpAABAAAAHgADAAEHlgABB5wAAAABAAAAHwADAAEHkAABB5YAAAABAAAAHwACB4oAFQGcAZ0BngHbAdwB3QHeAd8B4AHhAeIB4wHkAeUB5gHnAegB6QHqAesB7AABB4gAFAABB4IAFAABB3wAMgABB3YAKAABB3AAHgABB3T/4AABB2QAKAADAAEHbgABB3QAAAABAAAAIAADAAEHbAABB2IAAAABAAAAIAADAAEHOgABB2QAAAABAAAAIQADAAEHKAABB1oAAAABAAAAIQABB1AAAQAIAAEABAL1AAMA0AJ0AAIHQgAQAiYCJwIoAikCKgIrAiwCLQIuAi8CrQKvArACsQK1ArYAAgcsABACMAIxAjICMwI0AjUCNgI3AjgCOQK3ArgCuQK6ArsCvAACByIAHQKEAoUCjAKNAo4CjwKQApEClwKYApkCpgKnAqgCqQL2AxQDFQMWAxcDGAMZAxoDGwMcAx0DHgMfAysAAQcgAAEACAADAAgADgAUAWIAAgCmAWMAAgCvAWQAAgDCAAIHBAAbAQwBDQEOAQ8BEAERARIBEwEUARUBFgEXARgBGQEaARsBHAEdAR4BHwEgASEB7QHuAe8B8AL3AAIGyAAbAQwBDQEOAQ8BEAERARIBEwEUARUBFgEXARgBGQEaARsBHAEdAR4BHwEgASEB7QHuAe8B8AL3AAIGugA9AIQBIgEjASQBJQEmAScBKAEpASoBKwEsAS0BLgEvATABMQEyATMBNAE1ATYBNwE4ATkBOgE7ATwBPQE+AT8BQAFBAUIBQwFEAUUBRgFHAUgBSQFKAUsBZQFmAWcBnwGgAaEBogHxAfIB8wH0AfUB9gH3AfgB+QH6AfsAAgUuABUBowGkAaUB/AH9Af4B/wIAAgECAgIDAgQCBQIGAgcCCAIJAgoCCwIMAg0AAwABBKIAAQaIAAEEogABAAAAIgADAAIEjgSOAAEGdAAAAAEAAAAiAAIGZgAvAUwBTQFOAU8BUAFRAVIBUwFUAVUBVgFXAVgBWQFaAVsBXAFdAV4BXwFgAWEBpgGnAagCDgIPAhACEQISAhMCFAIVAhYCFwIYAhkCGgIbAhwCHQIeAh8CIAIhAiICIwACBmQAaQFoADkBaQCEAGIAaAEiALUBKAEqASsBLAEtAS4BLwEwATEBMgFpATMBNAE1ATYA6AELATcBOAE5ATsBPAE9AT4BPwFAAUEBQgFDAUQBRQFGAWUBZgFnAaEBogHxAfYB9wH4AfkB+gH7AkQCRQJGAkcCSAJJAkoCSwJMAk0ChAKFAmICjAKNAo4CjwKQApEClwKYApkCpgKnAqgCqQK3ArgCuQK6ArsCvAKtAq8CsAKxArUCtgL3AvYDFAMVAxYDFwMYAxkDGgMbAxwDHQMeAx8DKwABBmIARQCQAJgAngCkAKoAsAC2ALwAwgDIAM4A1ADaAOIA6gDyAPoBAgEIAQ4BFgEeASYBLgE2AUABSgFSAVgBYAFoAXIBegGCAYoBkgGaAaIBrAG0AbwBxAHMAdQB3AHkAewB9AH8AgICDgIaAiYCMgI+AkoCVgJiAm4CegJ+AoIChgKKAo4CkgKWApoCngADAWgBDAFMAAIBDQFNAAIBDgFOAAIBDwFPAAIBEAFQAAIBEQFRAAIBEgFSAAIBEwFTAAIBFAFUAAIBFQFVAAIBFgFWAAIBFwFXAAMBGAEjAVgAAwEZASQBWQADARoBJQFaAAMBGwEmAVsAAwEcAScBXAACAL0BKQACAO8BOgADAR0BRwFdAAMBHgFIAV4AAwEfAUkBXwADASABSgFgAAMBIQFLAWEABAGcAZ8BowGmAAQBnQGgAaQBpwADAZ4BpQGoAAIB7QIOAAMB2wH8Ag8AAwHcAf0CEAAEAd0B8gH+AhEAAwHeAf8CEgADAd8CAAITAAMB4AIBAhQAAwHhAgICFQADAeICAwIWAAMB4wIEAhcABAHkAfMCBQIYAAMB5QIGAhkAAwHmAgcCGgADAe4B9AIbAAMB7wH1AhwAAwHnAggCHQADAegCCQIeAAMB6QIKAh8AAwHqAgsCIAADAesCDAIhAAMB7AINAiIAAgHwAiMABQI6AlgCTgJEAjAABQI7AlkCTwJFAjEABQI8AloCUAJGAjIABQI9AlsCUQJHAjMABQI+AlwCUgJIAjQABQI/Al0CUwJJAjUABQJAAl4CVAJKAjYABQJBAl8CVQJLAjcABQJCAmACVgJMAjgABQJDAmECVwJNAjkAAQImAAECJwABAigAAQIpAAECKgABAisAAQIsAAECLQABAi4AAQIvAAIEPAAPALAAvAMUAxUDFgMXAxgDGQMaAxsDHAMdAx4DHwMrAAEEOgACAAoAFAABAAQAQQACAn0AAQAEAMYAAgJ9AAIEJAACADkAvQABAPD/9gACBBwABAFoAWkBaAFpAAECIgAiAAEAAgCvALsAAgABAvgDAwAAAAEAAgMFAwYAAgAEAvgC/wAAAwEDAgAIAwUDBgAKAyoDKgAMAAIAAgADAIQAAAFqAagAggACAAIDFAMfAAADKwMrAAwAAQABAK8AAQAEAGAAZwDmAO4AAQABAMIAAQABAn0AAQABAD0AAQABALEAAQABALsAAQABAC8AAQABADgAAQAVAXABewGFAasBrAGvAbMBtAG1AbYBtwG4AboBvgHBAccByAHJAcsBzAHXAAIAAQImAi8AAAABAAECggABAAECYgACAAECTgJXAAAAAgABAkQCTQAAAAEAAgADAIUAAQACAEoA0AABAAEARAACAAICMAI5AAACtwK8AAoAAgAEAiYCLwAAAq0CrQAKAq8CsQALArUCtgAOAAEAHQJ9An4ChgKHAogCiQKKAosCkgKUApUCoAKhAqICowLvAvgC+QL6AvsC/AL9Av4C/wMBAwIDBQMGAyoAAQABAKYAAgAHAIUAkAAAAKcAqwAMAQIBBgARAakBqQAWAcIBwwAXAdoB2gAZAuUC5QAaAAEAPQBYAKYApwCoAKkAqgCrALcAuwC8AL0AvgDCAMMAxADFAMYAxwDfAOAA4QDiAOsA7ADtAO4A7wDwAPEA8gDzAPQA9QD2APcA+AD5APoBAgEDAQQBBQEGAWIBYwFkAXABewGHAY8BqgGvAboBwgHDAcYBzgHdAd8B5QHmAAEAAQDpAAEALwCFAIYAhwCIAIkAigCLAIwAjQCOAI8AkACnAKgAqQCqAKsBAgEDAQQBBQEGAXABewGFAakBqwGsAa8BswG0AbUBtgG3AbgBugG+AcEBwgHDAccByAHJAcsBzAHXAdoAAQBpAAMAOABKAFgAYABnAKYArwC3ALwAvQC+AMIAwwDEAMUAxgDHANAA3wDgAOEA4gDmAOkA6wDsAO0A7wDwAPEA8gDzAPQA9QD2APcA+AD5APoBYgFjAWQBhwGPAaoBxgHOAd0B3wHlAeYCTgJPAlACUQJSAlMCVAJVAlYCVwJ9An4CggKGAocCiAKJAooCiwKSApQClQKgAqECogKjAq0CrwKwArECtQK2ArcCuAK5AroCuwK8AuUC7wL4AvkC+gL7AvwC/QL+Av8DAQMCAwUDBgMqAAIAFACFAJAAAACnAKsADAC7ALsAEQDuAO4AEgECAQYAEwFwAXAAGAF7AXsAGQGFAYUAGgGpAakAGwGrAawAHAGvAa8AHgGzAbgAHwG6AboAJQG+Ab4AJgHBAcMAJwHHAckAKgHLAcwALQHXAdcALwHaAdoAMAImAjkAMQABAA8ArwC7AvgC+QL6AvsC/AL9Av4C/wMBAwIDBQMGAyoAAQACAD0AwgABAAIAOAC7AAEABAADAEoAhQDQAAQCZQOEAAUABAKKAlgAAABLAooCWAAAAV4AMgEoAAAAAAoAAAAAAAAAgAACBwAAAHMAAAAAAAAAAEZCUkMAwAAA+wID5v7WANwD5gEqIAAAlwAAAAAB7gK8AAAAIAADAAAAAgAAAAMAAAAUAAMAAQAAABQABAYCAAAAnACAAAYAHAAAAA0ALwA5AH4BfwGSAf8CGwI3AscC3QMEAwgDDAMSAygDvAPABBoEIwQvBDMENQQ5BDoEQwRfBJEE1R6FHp4e8yAJIAsgFCAaIB4gIiAmIDAgMyA6ID0gRCBwIHkgiSCsILQguiC9IRMhFyEiISYhLiFRIVQhWiFeIZMhmSICIgYiDyISIhUiGiIeIisiSCJgImUlyvj/+wL//wAAAAAADQAgADAAOgCgAZIB/AIYAjcCxgLYAwADBgMKAxIDJgO8A8AEAAQbBCQEMAQ0BDYEOgQ7BEQEkATUHoAenh7yIAkgCyATIBggHCAgICYgMCAyIDkgPSBEIHAgdCCAIKwgtCC6IL0hEyEWISIhJiEuIVAhUyFVIVshkCGWIgIiBSIPIhEiFSIZIh4iKyJIImAiZCXK+P/7Af//Ayz/9AAAAfYAAAAAAR8AAAAA/oUAAAAAAAAAAAAA//H/3v5o/mUAAP1gAAD9eQAA/X0AAP1/AAAAAAAAAADhxQAA4qLioeKBAAAAAAAA4lLiqeK74mniQ+Ie4ejh6OG64gTh/uH54ffh3wAA4cnhq+HGAAAAAOET4RQAAAAA4NQAAODEAADgqQAA4LDgpeCC4GQAAN0YCeQGYgABAAAAAACYAAAAtAE8AAAC+AL+AAADAgMEAw4DFgMaAAAAAAAAAAADFgAAA0gAAANcAAADXAAAA1oDkAOSA5QAAAOcAAAAAAAAA5gDnAOgAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOIAAAAAAAAA4QDhgAAAAADhAOKAAADjgAAA44AAAOOAAAAAAAAAAADiAAAAAAAAAAAAAICeQKkAoECrwLYAuUCpQKGAocCfwK/AnUCkgJ0AoICdgJ3AsYCwwLFAnsC5AADAA8AEAAWABoAJAAlACoALQA4ADsAPQBDAEQASgBWAFgAWQBdAGQAaQB0AHUAegB7AIACigKDAosCzQKWAw4AhQCRAJIAmACcAKYApwCsAK8AuwC/AMIAyADJANAA3ADeAN8A4wDrAPAA+wD8AQEBAgEHAogC7wKJAssCqgJ6Aq0CtQKuArYC8ALnAwwC6AFoAqACzAKTAukDEALsAskCWgJbAwcC1wLmAn0DCgJZAWkCoQJmAmMCZwJ8AAgABAAGAAwABwALAA0AEwAhABsAHgAfADQALwAxADIAFwBJAE8ASwBNAFQATgLBAFIAbgBqAGwAbQB8AFcA6QCKAIYAiACOAIkAjQCPAJUAowCdAKAAoQC2ALEAswC0AJkAzwDVANEA0wDaANQCwgDYAPUA8QDzAPQBAwDdAQUACQCLAAUAhwAKAIwAEQCTABQAlgAVAJcAEgCUABgAmgAZAJsAIgCkABwAngAgAKIAIwClAB0AnwAnAKkAJgCoACkAqwAoAKoALACuACsArQA3ALoANQC4ADAAsgA2ALkAMwCwAC4AtwA6AL4APADAAMEAPgDDAEAAxQA/AMQAQQDGAEIAxwBFAMoARwDNAEYAzADLAEgAzgBRANcATADSAFAA1gBVANsAWgDgAFwA4gBbAOEAXgDkAGEA5wBgAOYAXwDlAGcA7gBmAO0AZQDsAHMA+gBwAPcAawDyAHIA+QBvAPYAcQD4AHcA/gB9AQQAfgCBAQgAgwEKAIIBCQDqAA4AkABTANkAYgDoAGgA7wMLAwkDCAMNAxIDEQMTAw8C+gL7Av0DAQMCAv8C+QL4AwAC/AL+AXIBcwGaAW4BkgGRAZQBlQGWAY8BkAGXAXoBeAGEAYsBagFrAWwBbQFwAXEBdAF1AXYBdwF5AYUBhgGIAYcBiQGKAY0BjgGMAZMBmAGZAa8BsAG4AcQBxQHHAcYByAHJAcwBzQHLAdIB1wHYAbEBsgHZAa0B0QHQAdMB1AHVAc4BzwHWAbkBtwHDAcoBbwGuAZsB2gB5AQAAdgD9AHgA/wB/AQYCngKfApoCnAKdApsC8QLzAn4C9QLqAm4CcwJkAmUC4ALaAtwC3gLhAtsC3QLfAs8C0gLUAsACvQLVAsgCxwAAAAMAJwAAAlECvAADACAALABEQEEABAIDAgQDgAADBQIDBX4AAAACBAACaQAFAAYHBQZpCAEHAQEHWQgBBwcBXwABBwFPISEhLCErJRkiEykREAkGHSsTIREhATQ2NzY2NTQmIyIGBhczNDYzMhYVFAYHBgYVFTMGNjU0JiMiBhUUFjMnAir91gE8Fxk1MWVYOFUtAmctJyYqHyErKGcYISEaGiIiGgK8/UQBABYcCRI/L0dTKUgvICYiHhYeCw83LhagIBkZICAZGSAAAAL/+QAAAxoCvAAHAAoARkuwL1BYQBUABAAAAQQAaAACAjJNBQMCAQEzAU4bQBUABAAAAQQAaAACAjJNBQMCAQE2AU5ZQA4AAAoJAAcABxEREQYJGSshJyEHIwEzAQEDMwJpNP6nNK8BOq8BOP5wc+R+fgK8/UQCH/7sAP////kAAAMaA4sAIgADAAAAAwMXAjYAAP////kAAAMaA40AIgADAAAAAwMbAmIAAP////kAAAMaA4sAIgADAAAAAwMZAoIAAP////kAAAMaA5sAIgADAAAAAwMUAoQAAP////kAAAMaA4sAIgADAAAAAwMWAfsAAP////kAAAMaA3UAIgADAAAAAwMdAmoAAAAC//n/NwNIArwAFwAaAIJACxcBBQEBTBABAQFLS7AhUFhAHgAGAAIBBgJoAAQEMk0DAQEBM00ABQUAYQAAADcAThtLsC9QWEAbAAYAAgEGAmgABQAABQBlAAQEMk0DAQEBMwFOG0AbAAYAAgEGAmgABQAABQBlAAQEMk0DAQEBNgFOWVlAChMlERERFCIHCR0rBQYGIyImNTQ3IychByMBMwEGFRQWMzI3AQMzA0gbPCU0OzElNP6nNK8BOq8BOD4ODRIQ/nFz5JwYFTQuOS5+fgK8/UQjHwsNCwJu/uwAAAP/+QAAAxoDdQAQABwAHwBgtg4EAgYEAUxLsC9QWEAdAAIHAQUEAgVpAAYAAAEGAGgABAQ4TQMBAQEzAU4bQB0AAgcBBQQCBWkABgAAAQYAaAAEBDhNAwEBATYBTllAEBERHx4RHBEbJRUlERAICRsrJSEHIwEmNTQ2MzIWFRQHASMCBhUUFjMyNjU0JiMTAzMCNf6nNK8BLShOPT5OJwEssfMXFxMTFxcTAXPkfn4CnyM3N0VFNzch/V8DIhcSERcWEhIX/v3+7AAA////+QAAAxoDjQAiAAMAAAADAxwCfAAAAAL/4gAAA9cCvAAPABQAbbUTAQYFAUxLsC9QWEAmAAYABwgGB2cACAACAQgCZwAFBQRfAAQEMk0AAAABXwMBAQEzAU4bQCYABgAHCAYHZwAIAAIBCAJnAAUFBF8ABAQyTQAAAAFfAwEBATYBTllADBEREREREREREAkJHyslIRUhNSEHIwEhFSEVIRUhBTM1NwcChQFS/hX+/1G4AcMCJ/65ATL+zv6+qQFAiop+fgK8iY6EEqtnbP///+IAAAPXA4sAIgANAAAAAwMXAtYAAAADAEwAAAKvArwADgAXACAAZ7UOAQQCAUxLsC9QWEAfAAIABAUCBGcGAQMDAV8AAQEyTQcBBQUAXwAAADMAThtAHwACAAQFAgRnBgEDAwFfAAEBMk0HAQUFAF8AAAA2AE5ZQBQYGA8PGCAYHx4cDxcPFichJAgJGSsAFhUUBiMhESEyFhUUBgclFTMyNjU0JiMSNjU0JiMjFTMCczyNfP6mAVpxgi8q/q28JyorJjQxMSzExAFYWzlcaAK8ZFYzTRTHiyQhISX+VSolJimeAAAAAQAk//ACrgLMABoAV0APCQEBABcKAgIBGAEDAgNMS7AvUFhAFgABAQBhAAAAOE0AAgIDYQQBAwM5A04bQBYAAQEAYQAAADhNAAICA2EEAQMDPANOWUAMAAAAGgAZJiMmBQkZKwQmJjU0NjYzMhcHJiMiBgYVFBYWMzI2NxcGIwEsq11fqm2bb2VDXj9hNTVhPzJcImBxoBBcpmxsp1ttZUA3ZEFBZDckImtt//8AJP/wAq4DiwAiABAAAAADAxcCOQAA//8AJP/wAq4DjgAiABAAAAADAxoChgAAAAEAJP8JAq4CzAAxAGtAGx8BBAMtIAIFBDEuFRQEAgUTCQIBAggBAAEFTEuwIVBYQB0ABQACAQUCaQAEBANhAAMDOE0AAQEAYQAAAD0AThtAGgAFAAIBBQJpAAEAAAEAZQAEBANhAAMDOAROWUAJJiMqJCQkBgkcKwQWFRQGIyImJzcWMzI2NTQmIyIHJzcuAjU0NjYzMhcHJiMiBgYVFBYWMzI2NxcGBwcB6jVMPSpGFzUhKBUYGRUZCh4YYZBOX6ptm29lQ14/YTU1YT8yXCJgYoQLLDYrLzsbGj0bEA4PEQccQAthnWJsp1ttZUA3ZEFBZDckImtdDhoA//8AJP/wAq4DiwAiABAAAAADAxkChQAA//8AJP/wAq4DlwAiABAAAAADAxUCGAAAAAIATAAAAtMCvAAKABQATkuwL1BYQBcAAgIBXwQBAQEyTQUBAwMAXwAAADMAThtAFwACAgFfBAEBATJNBQEDAwBfAAAANgBOWUASCwsAAAsUCxMSEAAKAAkmBgkXKwAWFhUUBgYjIREhEjY1NCYmIyMRMwHXo1lZo2z+4QEfWGwxWTp7ewK8Vp9paZ9WArz903BfP10z/mIAAgALAAAC3gK8AA4AGwBoS7AvUFhAIQUBAgYBAQcCAWcABAQDXwgBAwMyTQkBBwcAXwAAADMAThtAIQUBAgYBAQcCAWcABAQDXwgBAwMyTQkBBwcAXwAAADYATllAGA8PAAAPGw8aGRgXFhUTAA4ADRERJgoJGSsAFhYVFAYGIyERIzUzESESNjU0JiMjFTMVIxUzAeKjWVmjbP7gS0sBIFppaVx6jo56ArxWn2lpn1YBIH8BHf3Rcl9fcpB/kwD//wBMAAAC0wOOACIAFgAAAAMDGgJSAAD//wALAAAC3gK8AAIAFwAAAAEATAAAAm0CvAALAFFLsC9QWEAdAAQABQAEBWcAAwMCXwACAjJNAAAAAV8AAQEzAU4bQB0ABAAFAAQFZwADAwJfAAICMk0AAAABXwABATYBTllACREREREREAYJHCs3IRUhESEVIRUhFSHrAYL93wIW/okBY/6diooCvImOhAD//wBMAAACbQOLACIAGgAAAAMDFwINAAD//wBMAAACbQONACIAGgAAAAMDGwI5AAD//wBMAAACbQOOACIAGgAAAAMDGgJZAAD//wBMAAACbQOLACIAGgAAAAMDGQJYAAD//wBMAAACbQObACIAGgAAAAMDFAJbAAD//wBMAAACbQOXACIAGgAAAAMDFQHrAAD//wBMAAACbQOLACIAGgAAAAMDFgHRAAD//wBMAAACbQN1ACIAGgAAAAMDHQJAAAAAAQBM/zcCmwK8ABsAnkALGwEHAQFMFAEBAUtLsCFQWEAnAAQABQYEBWcAAwMCXwACAjJNAAYGAV8AAQEzTQAHBwBhAAAANwBOG0uwL1BYQCQABAAFBgQFZwAHAAAHAGUAAwMCXwACAjJNAAYGAV8AAQEzAU4bQCQABAAFBgQFZwAHAAAHAGUAAwMCXwACAjJNAAYGAV8AAQE2AU5ZWUALJRERERERFCIICR4rBQYGIyImNTQ3IREhFSEVIRUhFSEVBhUUFjMyNwKbGzwlNDsx/msCFv6JAWP+nQGCPg4NEhCcGBU0LjkuAryJjoSXiiMfCw0LAAEATAAAAlECvAAJAEVLsC9QWEAYAAEAAgMBAmcAAAAEXwAEBDJNAAMDMwNOG0AYAAEAAgMBAmcAAAAEXwAEBDJNAAMDNgNOWbcREREREAUJGysBIRUhFSEVIxEhAlH+nwFN/rOkAgUCLaeL+wK8AAABACT/8ALCAs0AHwBsQBIPAQIBEAEFAhwBAwQBAQADBExLsC9QWEAeBgEFAAQDBQRnAAICAWEAAQE4TQADAwBhAAAAOQBOG0AeBgEFAAQDBQRnAAICAWEAAQE4TQADAwBhAAAAPABOWUAOAAAAHwAfEiUlJiMHCRsrAREGBiMiJiY1NDY2MzIWFwcmJiMiBhUUFhYzMjc1IzUCwjWbXW+nW2CtcFGDN2MhWS9ldTRgP2M7vgGe/sg5PVqmbmunXTg5YiEkeWhDZjgza4MAAAD//wAk//ACwgONACIAJQAAAAMDGwJxAAD//wAk//ACwgOLACIAJQAAAAMDGQKRAAD//wAk/vUCwgLNACIAJQAAAAMDBAH3AAD//wAk//ACwgOXACIAJQAAAAMDFQIkAAAAAQBMAAACvAK8AAsAQUuwL1BYQBUABQACAQUCZwQBAAAyTQMBAQEzAU4bQBUABQACAQUCZwQBAAAyTQMBAQE2AU5ZQAkRERERERAGCRwrATMRIxEhESMRMxEhAhmjo/7XpKQBKQK8/UQBGf7nArz+8QAAAAACABQAAAMEArwAEwAXAGhLsC9QWEAiDAkHAwULBAIACgUAZwAKAAIBCgJnCAEGBjJNAwEBATMBThtAIgwJBwMFCwQCAAoFAGcACgACAQoCZwgBBgYyTQMBAQE2AU5ZQBYAABcWFRQAEwATERERERERERERDQkfKwEVIxEjESERIxEjNTM1MxUhNTMVBSE1IQMEQKT+2KRAQKQBKKT+NAEo/tgCZWL9/QEQ/vACA2JXV1dXxWUAAAD//wBMAAACvAOLACIAKgAAAAMDGQJ9AAAAAQBMAAAA8AK8AAMAKEuwL1BYQAsAAAAyTQABATMBThtACwAAADJNAAEBNgFOWbQREAIJGCsTMxEjTKSkArz9RAAAAP//AEz/8gPAArwAIgAtAAAAAwA4AT0AAP//AEwAAAFMA4sAIgAtAAAAAwMXAUsAAP////kAAAFDA40AIgAtAAAAAwMbAXcAAP///+AAAAFeA4sAIgAtAAAAAwMoAZcAAP///9YAAAFnA5sAIgAtAAAAAwMUAZkAAP//AEgAAAD2A5cAIgAtAAAAAwMVASoAAP////EAAADwA4sAIgAtAAAAAwMWARAAAP////8AAAE+A3UAIgAtAAAAAwMpAX8AAAABADP/NwEeArwAEwBjQAsTAQMBAUwMAQEBS0uwIVBYQBUAAgIyTQABATNNAAMDAGEAAAA3AE4bS7AvUFhAEgADAAADAGUAAgIyTQABATMBThtAEgADAAADAGUAAgIyTQABATYBTllZtiURFCIECRorBQYGIyImNTQ3IxEzEQYVFBYzMjcBHhs8JTQ7MRikPg4NEhCcGBU0LjkuArz9RCMfCw0L////6QAAAVEDjQAiAC0AAAADAxwBkQAAAAEAFP/yAoMCvAASAFdLsC9QWEAeAAEDAgMBAoAAAwMEXwUBBAQyTQACAgBhAAAAOQBOG0AeAAEDAgMBAoAAAwMEXwUBBAQyTQACAgBhAAAAPABOWUANAAAAEgASEyISJAYJGisBERQGBiMiJiczFhYzMjY1ESM1AoNNjl6SowGgAU5HRk/MArz+bV+MTKKUT1VXUAEDjgD//wAU//ICgwOLACIAOAAAAAMDFwJ0AAD//wAU//IChwOLACIAOAAAAAMDKALAAAAAAQBMAAACugK8AAoAN7cKBwIDAAIBTEuwL1BYQA0DAQICMk0BAQAAMwBOG0ANAwECAjJNAQEAADYATlm2EhESEAQJGishIwMRIxEzERMzAQK61fajo+bK/tkBFv7qArz+7gES/qkAAP//AEz+9QK6ArwAIgA7AAAAAwMEAbQAAAABAEwAAAJQArwABQAzS7AvUFhAEAAAADJNAAEBAmAAAgIzAk4bQBAAAAAyTQABAQJgAAICNgJOWbURERADCRkrEzMRIRUhTKQBYP38Arz92JQAAP//AEwAAAJQA4sAIgA9AAAAAwMXAUsAAAACAEwAAAJQArwABQAJAEFLsC9QWEAWAAQEAF8DAQAAMk0AAQECYAACAjMCThtAFgAEBABfAwEAADJNAAEBAmAAAgI2Ak5ZtxEREREQBQkbKxMzESEVIQEzByNMpAFg/fwBUo5ObgK8/dWRArzcAAD//wBM/vUCUAK8ACIAPQAAAAMDBAGpAAAAAgBMAAACUAK8AAUAEQBVS7AvUFhAGgADBgEEAAMEaQUBAgIyTQAAAAFgAAEBMwFOG0AaAAMGAQQAAwRpBQECAjJNAAAAAWAAAQE2AU5ZQBMGBgAABhEGEAwKAAUABRERBwkYKxMRIRUhEQAmNTQ2MzIWFRQGI/ABYP38ATU2NikpNjYpArz92JQCvP5XMycnMjInJzMAAAABAA4AAAJYArwADQBCQA0NDAsKBwYFBAgAAgFMS7AvUFhAEAACAjJNAAAAAWAAAQEzAU4bQBAAAgIyTQAAAAFgAAEBNgFOWbUVERADCRkrNyEVITUHNTcRMxE3FQf4AWD9/EZGpGxskZHhIn4jAVz+9jaBNQAAAAABAEwAAANQArwADABItwwHBAMCAAFMS7AvUFhAFQACAAEAAgGABAEAADJNAwEBATMBThtAFQACAAEAAgGABAEAADJNAwEBATYBTlm3ERISERAFCRsrATMRIxEHIycRIxEzEwK9k6POINCjk+8CvP1EAbb8/f5JArz+1gAAAQBMAAACvQK8AAsANrYKBAIBAAFMS7AvUFhADQMBAAAyTQIBAQEzAU4bQA0DAQAAMk0CAQEBNgFOWbYRExEQBAkaKwEzESMBFxUjETMBJwIao5P+wwKjkwE9AgK8/UQBsb30Arz+TbsAAAD//wBMAAACvQOLACIARAAAAAMDFwI1AAD//wBMAAACvQOOACIARAAAAAMDGgKCAAD//wBM/vUCvQK8ACIARAAAAAMDBAHfAAAAAQBM/x4CvQK8ABUAlUAQEw0MAwIDBwEBAgYBAAEDTEuwCVBYQBcFBAIDAzJNAAICM00AAQEAYgAAADcAThtLsCFQWEAXBQQCAwMyTQACAjNNAAEBAGIAAAA9AE4bS7AvUFhAFAABAAABAGYFBAIDAzJNAAICMwJOG0AUAAEAAAEAZgUEAgMDMk0AAgI2Ak5ZWVlADQAAABUAFREVIyMGCRorAREUBiMiJzcWMzI1NQEXFSMRMwEnNQK9U05BRhweFjX+0wKjkgE/AwK8/SpiZh9yDkgtAZu99AK8/k25+v//AEwAAAK9A40AIgBEAAAAAwMcAnsAAAACACT/7wMWAs0ADwAfAE5LsC9QWEAXAAICAGEAAAA4TQUBAwMBYQQBAQE5AU4bQBcAAgIAYQAAADhNBQEDAwFhBAEBATwBTllAEhAQAAAQHxAeGBYADwAOJgYJFysEJiY1NDY2MzIWFhUUBgYjPgI1NCYmIyIGBhUUFhYzASyrXV2rcXGrXV2rcT9hNTVhPz9gNTVgPxFbpm5upltbpm5upluSN2RCQmQ3N2RCQmQ3//8AJP/vAxYDiwAiAEoAAAADAxcCSgAA//8AJP/vAxYDjQAiAEoAAAADAxsCdgAA//8AJP/vAxYDiwAiAEoAAAADAxkClQAA//8AJP/vAxYDmwAiAEoAAAADAxQCmAAA//8AJP/vAxYDiwAiAEoAAAADAxYCDgAA//8AJP/vAxYDigAiAEoAAAADAxgCrwAA//8AJP/vAxYDdQAiAEoAAAADAx0CfgAAAAMAJP+5AxoDAwAXACEAKgB4QBMXFAIEAignHx4EBQQLCAIABQNMS7AvUFhAIQADAgOFAAEAAYYGAQQEAmEAAgI4TQcBBQUAYQAAADkAThtAIQADAgOFAAEAAYYGAQQEAmEAAgI4TQcBBQUAYQAAADwATllAEyIiGBgiKiIpGCEYIBInEiUICRorABYVFAYGIyInByM3JiY1NDY2MzIXNzMHBAYGFRQWFxMmIxI2NjU0JwMWMwLZQV6rclA/L5NUPUFerHFLRDCUVv7CYzcbGOggIEFkNjLoHiECS5JbbqZbFkyGMJRbbqZbFkyHPThmQy5OHQFyCP4+OGZDXD3+jggAAAD//wAk/7kDGgOLACIAUgAAAAMDFwJMAAD//wAk/+8DFgONACIASgAAAAMDHAKQAAAAAgAk//ED1wLLABYAIgEuQAodAQUEHAEHBgJMS7ARUFhAIQAFAAYHBQZnCQEEBAJhAwECAjhNCAEHBwBhAQEAADMAThtLsCFQWEA1AAUABgcFBmcJAQQEAmEAAgI4TQkBBAQDXwADAzJNCAEHBwBfAAAAM00IAQcHAWEAAQE5AU4bS7AtUFhAMwAFAAYHBQZnCQEEBAJhAAICOE0JAQQEA18AAwMyTQAHBwBfAAAAM00ACAgBYQABATkBThtLsC9QWEAxAAUABgcFBmcACQkCYQACAjhNAAQEA18AAwMyTQAHBwBfAAAAM00ACAgBYQABATkBThtAMQAFAAYHBQZnAAkJAmEAAgI4TQAEBANfAAMDMk0ABwcAXwAAADZNAAgIAWEAAQE8AU5ZWVlZQA4gHiMRERERESYhEAoJHyshIQYjIiYmNTQ2NjMyFyEVIRUhFSEVISQWFjMyNxEmIyIGFQPX/jc9OnGnW1uncTRFAbz+wQEs/tQBSvzyNmJAMiotMmF0D1qlb2+kWQ+Ij4SXk2Q2DwGXEHdkAAAAAAIATAAAAqcCvAAMABUAVUuwL1BYQBoGAQQAAAEEAGcAAwMCXwUBAgIyTQABATMBThtAGgYBBAAAAQQAZwADAwJfBQECAjJNAAEBNgFOWUATDQ0AAA0VDRQTEQAMAAsRJgcJGCsAFhYVFAYGIyMVIxEhEjY1NCYjIxUzAex5QkJ5UaukAU8sPT00pKQCvD1yTExyPcYCvP6ZOjExOtYAAAACAEwAAAKnArwADgAXAFxLsC9QWEAdBgEDAAQFAwRnBwEFAAABBQBnAAICMk0AAQEzAU4bQB0GAQMABAUDBGcHAQUAAAEFAGcAAgIyTQABATYBTllAFA8PAAAPFw8WFRMADgANEREmCAkZKwAWFhUUBgYjIxUjETMVMxI2NTQmIyMVMwHseUJCeVGrpKSrLTw8M6amAls+ckxMcj5jArxh/pk7MDA71gACACT/ugMxAs0AEgAiAFNACxEBAwISAQIAAwJMS7AvUFhAFgACAgFhAAEBOE0EAQMDAGEAAAA5AE4bQBYAAgIBYQABAThNBAEDAwBhAAAAPABOWUAMExMTIhMhLSYiBQkZKwUnBiMiJiY1NDY2MzIWFhUUBxckNjY1NCYmIyIGBhUUFhYzAr9hU25xq11dq3Fxq10+Wf6rYTU1YT8/YDU1YD9GYCtbpm5upltbpm5/WlpWN2RCQmQ3N2RCQmQ3AAACAEwAAALEArwADgAXAFC1DAEABQFMS7AvUFhAGQAFAAABBQBnAAQEAl8AAgIyTQMBAQEzAU4bQBkABQAAAQUAZwAEBAJfAAICMk0DAQEBNgFOWUAJISIXIREQBgkcKyUjFSMRITIWFhUUBgcXIwImIyMVMzI2NQFPX6QBVUxyPlNMxsMGOTSfnzU45+cCvDtsRlByGPUB/DTFMy8AAAD//wBMAAACxAOLACIAWQAAAAMDFwIPAAD//wBMAAACxAOOACIAWQAAAAMDGgJbAAD//wBM/vUCxAK8ACIAWQAAAAMDBAHKAAAAAQAg//ACdgLMACUAV0APFQECARYDAgACAgEDAANMS7AvUFhAFgACAgFhAAEBOE0AAAADYQQBAwM5A04bQBYAAgIBYQABAThNAAAAA2EEAQMDPANOWUAMAAAAJQAkJCskBQkZKxYmJzcWMzI2NTQmJyYmNTQ2NjMyFhcHJiMiBhUUFhcWFhUUBgYj+Z86VV18PklESo+FSIJVSYs1TVJjPUk/So6MSoZXEDQvd0kqJCImCBBmX0BiNiomczkoIiEkCRBtX0JlN///ACD/8AJ2A4sAIgBdAAAAAwMXAfYAAP//ACD/8AJ2A44AIgBdAAAAAwMaAkMAAAABACD/CQJ2AswAOwBrQBsvAQUEMB0CAwUcGRgDBAIDFw0CAQIMAQABBUxLsCFQWEAdAAMAAgEDAmkABQUEYQAEBDhNAAEBAGEAAAA9AE4bQBoAAwACAQMCaQABAAABAGUABQUEYQAEBDgFTllACSQrKCQkKAYJHCskBgcHFhYVFAYjIiYnNxYzMjY1NCYjIgcnNyYmJzcWMzI2NTQmJyYmNTQ2NjMyFhcHJiMiBhUUFhcWFhUCdohyCy01TD0qRhc1ISgVGBkVGAseGEeAMFVdfD5JREqPhUiCVUmLNU1SYz1JP0qOjHR3CxoENisvOxsaPRsQDg8RBxxACDEnd0kqJCImCBBmX0BiNiomczkoIiEkCRBtXwD//wAg//ACdgOLACIAXQAAAAMDGQJCAAD//wAg/vUCdgLMACIAXQAAAAMDBAGkAAAAAQBM//gCxgK8AB8As0uwHVBYQBMeAQMFHxICAgMJAQECCAEAAQRMG0ATHgEDBR8SAgIDCQEBAggBBAEETFlLsB1QWEAeAAIDAQMCAYAAAwMFXwAFBTJNAAEBAGEEAQAAPABOG0uwL1BYQCIAAgMBAwIBgAADAwVfAAUFMk0ABAQzTQABAQBhAAAAPABOG0AiAAIDAQMCAYAAAwMFXwAFBTJNAAQENk0AAQEAYQAAADwATllZQAkiEyIjIyUGCRwrABYVFAYGIyInNxYzMjY1NCMjJzcjIgYVESMRNDMhFQcCZ189ckxNRx4sLzc8dD0cbHE0LaTcAWBxAa13WEZoOBeGDjEtW0enLjT+NAHe3laoAAAAAQAQAAACXwK8AAcAPkuwL1BYQBICAQAAA18EAQMDMk0AAQEzAU4bQBICAQAAA18EAQMDMk0AAQE2AU5ZQAwAAAAHAAcREREFCRkrARUjESMRIzUCX9ak1QK8j/3TAi2PAAAAAAEAEAAAAl8CvAAPAE9LsC9QWEAbBQEBBAECAwECZwYBAAAHXwAHBzJNAAMDMwNOG0AbBQEBBAECAwECZwYBAAAHXwAHBzJNAAMDNgNOWUALERERERERERAICR4rASMVMxUjESMRIzUzNSM1IQJf1nt7pHt71QJPAjCbev7lARt6m4wA//8AEAAAAl8DjgAiAGQAAAADAxoCMAAAAAEAEP8JAl8CvAAfAKJAEBYBAgIDFQsCAQIKAQABA0xLsCFQWEAlAAIDAQMCAYAGAQQEBV8ABQUyTQgHAgMDM00AAQEAYQAAAD0AThtLsC9QWEAiAAIDAQMCAYAAAQAAAQBlBgEEBAVfAAUFMk0IBwIDAzMDThtAIgACAwEDAgGAAAEAAAEAZQYBBAQFXwAFBTJNCAcCAwM2A05ZWUAQAAAAHwAfEREREyQkJgkJHSshBxYWFRQGIyImJzcWMzI2NTQmIyIHJzcjESM1IRUjEQFoEC01TD0qRhc1ISgVGBkVGAseHR7VAk/WKAQ2Ky87Gxo9GxAODxEHHE0CLY+P/dMAAAD//wAQ/vUCXwK8ACIAZAAAAAMDBAGLAAAAAQBB//ECvAK8ABEAPkuwL1BYQBICAQAAMk0AAQEDYQQBAwM5A04bQBICAQAAMk0AAQEDYQQBAwM8A05ZQAwAAAARABATIxMFCRkrFiY1ETMRFBYzMjY1ETMRFAYj6KekUUlHUqSmlw+nlgGO/nJQXFxQAY7+cpanAAAA//8AQf/xArwDiwAiAGkAAAADAxcCKwAA//8AQf/xArwDjQAiAGkAAAADAxsCVwAA//8AQf/xArwDiwAiAGkAAAADAxkCdwAA//8AQf/xArwDmwAiAGkAAAADAxQCeQAA//8AQf/xArwDiwAiAGkAAAADAxYB8AAA//8AQf/xArwDigAiAGkAAAADAxgCkAAA//8AQf/xArwDdQAiAGkAAAADAx0CXwAAAAEAQf83ArwCvAAhAFlACxQLAgADDAEBAAJMS7AhUFhAGgADAgACAwCABQQCAgIyTQAAAAFiAAEBNwFOG0AXAAMCAAIDAIAAAAABAAFmBQQCAgIyAk5ZQA0AAAAhACEjGCQoBgkaKwERFAYHBhUUFjMyNxcGBiMiJjU0NyYmNREzERQWMzI2NRECvGljPQ4NEhAvGzwlNDskhZKkUUlHUgK8/nJ3mxwjHwsNC00YFTQuMSkLpIwBjv5yUFxcUAGO//8AQf/xArwD4AAiAGkAAAEHAwACPgDOAAixAQKwzrA1KwAA//8AQf/xArwDjQAiAGkAAAADAxwCcQAAAAH/+wAAAugCvAAIADK1BwEBAAFMS7AvUFhADAIBAAAyTQABATMBThtADAIBAAAyTQABATYBTlm1EREQAwkZKwEzASMBMxcTEwIztf7grf7gtV5jZQK8/UQCvO7+8AEQAAEACQAABEoCvAAQADq3DwwFAwEAAUxLsC9QWEAOBAMCAAAyTQIBAQEzAU4bQA4EAwIAADJNAgEBATYBTlm3ExEUERAFCRsrATMDIycnBwcjAzMTFxMzEzcDl7P1m0JQTkOY9rNYOZ92oz0CvP1Ew+vrwwK8/unHAd7+H8oAAAD//wAJAAAESgOLACIAdQAAAAMDFwLTAAD//wAJAAAESgOLACIAdQAAAAMDGQMfAAD//wAJAAAESgObACIAdQAAAAMDFAMiAAD//wAJAAAESgOLACIAdQAAAAMDFgKYAAAAAf/+AAACuAK8AA8AN7cMCAQDAAIBTEuwL1BYQA0DAQICMk0BAQAAMwBOG0ANAwECAjJNAQEAADYATlm2FBIUEQQJGisBEyMnJwcHIxMDMxcXNzczAcfxx1FFQ1HJ7eDBSkJFTMIBZf6benFwewFeAV52cnJ2AAAAAf/6AAACzQK8AAgAPLcHBAEDAAEBTEuwL1BYQA0DAgIBATJNAAAAMwBOG0ANAwICAQEyTQAAADYATllACwAAAAgACBISBAkYKwEBESMRATMTEwLN/uOj/u3ApqoCvP5W/u4BEgGq/vABEAD////6AAACzQOLACIAewAAAAMDFwIPAAD////6AAACzQOLACIAewAAAAMDGQJaAAD////6AAACzQObACIAewAAAAMDFAJdAAD////6AAACzQOLACIAewAAAAMDFgHTAAAAAQAZAAACVQK8AAkASkAKCQECAwQBAQACTEuwL1BYQBUAAgIDXwADAzJNAAAAAV8AAQEzAU4bQBUAAgIDXwADAzJNAAAAAV8AAQE2AU5ZthESERAECRorNyEVITUBITUhFf4BV/3EAVT+wgIgj489AfSLO///ABkAAAJVA4sAIgCAAAAAAwMXAe8AAP//ABkAAAJVA44AIgCAAAAAAwMaAjsAAP//ABkAAAJVA5cAIgCAAAAAAwMVAc0AAAADACT/QgMWAs0ADwAfACMArUuwFVBYQCEAAgIAYQAAAB9NBwEDAwFhBgEBASBNAAQEBV8ABQUeBU4bS7AtUFhAHgAEAAUEBWMAAgIAYQAAAB9NBwEDAwFhBgEBASABThtLsC9QWEAcAAAAAgMAAmkABAAFBAVjBwEDAwFhBgEBASABThtAHAAAAAIDAAJpAAQABQQFYwcBAwMBYQYBAQEiAU5ZWVlAFhAQAAAjIiEgEB8QHhgWAA8ADiYIBxcrBCYmNTQ2NjMyFhYVFAYGIz4CNTQmJiMiBgYVFBYWMwchFSEBLKtdXatxcatdXatxP2E1NWE/P2A1NWA/DgFD/r0RW6ZubqZbW6ZubqZbkjdkQkJkNzdkQkJkN7uEAAIAH//2AkEB+AARAB0ApUuwGVBYQAoQAQQCAwEABQJMG0AKEAEEAwMBAAUCTFlLsBlQWEAZAAQEAmEGAwICAjtNBwEFBQBhAQEAADMAThtLsC9QWEAhBgEDAzVNAAQEAmEAAgI7TQAAADNNBwEFBQFhAAEBPAFOG0AhBgEDAzVNAAQEAmEAAgI7TQAAADZNBwEFBQFhAAEBPAFOWVlAFBISAAASHRIcGBYAEQARJiIRCAkZKwERIycGIyImJjU0NjYzMhYXNwI2NTQmIyIGFRQWMwJBiAo/ZUVrPDxrRTJUHgpVQkI0NEFBNAHu/hI7RUF1S0t1QSMhOv6MRTg4RUY3N0b//wAf//YCQQK8ACIAhQAAAAMC+wHtAAD//wAf//YCQQK8ACIAhQAAAAMC/wIZAAD//wAf//YCQQK8ACIAhQAAAAMC/QI5AAD//wAf//YCQQLFACIAhQAAAAMC+AI8AAD//wAf//YCQQK8ACIAhQAAAAMC+gI9AAD//wAf//YCQQKnACIAhQAAAAMDAgIhAAAAAgAf/0QCcAH4ACEALQCIS7AZUFhAEBUBBQIYCAcDAQYhAQQBA0wbQBAVAQUDGAgHAwEGIQEEAQNMWUuwGVBYQB4ABAAABABmAAUFAmEDAQICO00HAQYGAWEAAQE8AU4bQCIABAAABABmAAMDNU0ABQUCYQACAjtNBwEGBgFhAAEBPAFOWUAPIiIiLSIsJyYTJiYhCAkcKwUGIyImNTQ3JwYjIiYmNTQ2NjMyFhc3MxEXBhUUFjMyNjcmNjU0JiMiBhUUFjMCcDVIMjkxCj9lRWs8PGtFMlQeCogBRRANChcJ4EJCNDRBQTSNLzAqOCs6RUF1S0t1QSMhOv4TAR8fCw8JB8JFODhFRjc3RgAAAP//AB//9gJBAxIAIgCFAAAAAwMAAgAAAP//AB//9gJBAsMAIgCFAAAAAwMBAjMAAAADAB//9gO4AfgAJgAtADkBp0uwGVBYQBEkIQIJBQwBAQAVEg0DAgEDTBtLsC1QWEARJCECCQYMAQEAFRINAwMBA0wbQBEkIQIJBgwBCwAVEg0DAwEDTFlZS7ARUFhAJgAIAAABCABnCg0CCQkFYQwHBgMFBTtNDgsCAQECYQQDAgICPAJOG0uwGVBYQDIACAAAAQgAZw0BCQkFYQwHBgMFBTtNAAoKBWEMBwYDBQU7TQ4LAgEBAmEEAwICAjwCThtLsC1QWEA5AAgAAAEIAGcABgY1TQ0BCQkFYQwHAgUFO00ACgoFYQwHAgUFO00AAwMzTQ4LAgEBAmEEAQICPAJOG0uwL1BYQEMACAAACwgAZwAGBjVNDQEJCQVhDAcCBQU7TQAKCgVhDAcCBQU7TQ4BCwsCYQQBAgI8TQADAzNNAAEBAmEEAQICPAJOG0BDAAgAAAsIAGcABgY1TQ0BCQkFYQwHAgUFO00ACgoFYQwHAgUFO00OAQsLAmEEAQICPE0AAwM2TQABAQJhBAECAjwCTllZWVlAIC4uJycAAC45Ljg0MictJywqKQAmACUSJiISJSIVDwkdKwAWFhUUByEWFjMyNjcXBgYjIicHIycGIyImJjU0NjYzMhc3Mxc2MwYGBzMmJiMANjU0JiMiBhUUFjMDFmk5Bv6dCEQ0JkQXUyhuPGk6B3wFPl9Eajw8akRhPgZ5Bz1lQDoH2gE7L/6jQEAzM0BAMwH4PG5IHiMlKxYUWSYqPzU2QEF1S0t1QUE3NT92LigmMP74Rjc3RkY3N0YA//8AH//2A7gCvAAiAI8AAAADAvsClwAAAAIAO//2Al4CvAAQABwAqUuwGVBYQAoOAQQDCQEABQJMG0AKDgEEAwkBAQUCTFlLsBlQWEAdAAICMk0ABAQDYQYBAwM7TQcBBQUAYQEBAAA8AE4bS7AvUFhAIQACAjJNAAQEA2EGAQMDO00AAQEzTQcBBQUAYQAAADwAThtAIQACAjJNAAQEA2EGAQMDO00AAQE2TQcBBQUAYQAAADwATllZQBQREQAAERwRGxcVABAADxESJggJGSsAFhYVFAYGIyInByMRMxU2MxI2NTQmIyIGFRQWMwG2bDw8bEVlPwqInT5bD0JCNDRBQTQB+EF1S0t1QUU7Arz9Of6CRTg4RUY3N0YAAQAf//UB9gH5ABgANEAxCgEBABULAgIBFgEDAgNMAAEBAGEAAAA7TQACAgNhBAEDAzwDTgAAABgAFyQkJgUJGSsWJiY1NDY2MzIWFwcmIyIGFRQWMzI3FwYj3XtDRHpQN2QnVyo5NkRDNz0rWVNzCz90Tk11QScmXydFODhFK15SAAD//wAf//UB9gK8ACIAkgAAAAMC+wHQAAD//wAf//UB9gK8ACIAkgAAAAMC/gIcAAAAAQAf/wkB9gH5AC4As0AdHwEEAyogAgUEKxUCBgUUAQIGEwkCAQIIAQABBkxLsAtQWEAlBwEGBQIBBnIABQACAQUCaQAEBANhAAMDO00AAQEAYgAAAD0AThtLsCFQWEAmBwEGBQIFBgKAAAUAAgEFAmkABAQDYQADAztNAAEBAGIAAAA9AE4bQCMHAQYFAgUGAoAABQACAQUCaQABAAABAGYABAQDYQADAzsETllZQA8AAAAuAC4kJCkkJCQICRwrBBYVFAYjIiYnNxYzMjY1NCYjIgcnNyYmNTQ2NjMyFhcHJiMiBhUUFjMyNxcGBwcBdDVLPSpGFjUgKBQYGBUVDh4bYnBEelA3ZCdXKjk2REM3PStZR1sNKzYsLzsbGT0bEQ4PEggcRxGFZk11QScmXydFODhFK15GCh8A//8AH//1AfYCvAAiAJIAAAADAv0CGwAA//8AH//1AfYCxgAiAJIAAAADAvkBrgAAAAIAH//2AkECvAAQABwAlkAKDwEEAgMBAAUCTEuwGVBYQB0GAQMDMk0ABAQCYQACAjtNBwEFBQBhAQEAADMAThtLsC9QWEAhBgEDAzJNAAQEAmEAAgI7TQAAADNNBwEFBQFhAAEBPAFOG0AhBgEDAzJNAAQEAmEAAgI7TQAAADZNBwEFBQFhAAEBPAFOWVlAFBERAAARHBEbFxUAEAAQJiIRCAkZKwERIycGIyImJjU0NjYzMhc1AjY1NCYjIgYVFBYzAkGICj9lRWs8PGtFWz5AQkI0NEFBNAK8/UQ7RUF1S0t1QTn9/b5FODhFRjc3RgAAAAACAB//9QIpAssAGQAlAFVADxABAgEBTBkYFxYUEwYBSkuwIVBYQBYAAgIBYQABATVNBAEDAwBhAAAAPABOG0AUAAEAAgMBAmkEAQMDAGEAAAA8AE5ZQAwaGholGiQvJiUFCRkrABYVFAYGIyImJjU0NjYzMhcmJic3Fhc3FwcCNjU0JiMiBhUUFjMB1lNBdk5OdkE8bUcuICBxQhpOOy1XJzc9PS8vPT0vAh+5b011QD1xSkduPREsQQt0Chs2Qi3+G0I0M0JCMzRCAAADAB//9gMOArwAEAAUACAAoUAKEAEGBQQBAQcCTEuwGVBYQCIABQUAXwQBAAAyTQAGBgNhAAMDO00IAQcHAWECAQEBMwFOG0uwL1BYQCYABQUAXwQBAAAyTQAGBgNhAAMDO00AAQEzTQgBBwcCYQACAjwCThtAJgAFBQBfBAEAADJNAAYGA2EAAwM7TQABATZNCAEHBwJhAAICPAJOWVlAEBUVFSAVHyUREiYiERAJCR0rATMRIycGIyImJjU0NjYzMhc3MwcjAjY1NCYjIgYVFBYzAaSdiAo/ZUVrPDxrRVs+5oRJaPlCQjQ0QUE0Arz9RDtFQXVLS3VBOf3S/pBFODhFRjc3RgACACL/9gKDArwAGAAkAK9AChABCAMEAQEJAkxLsBlQWEAmBwEFBAEAAwUAZwAGBjJNAAgIA2EAAwM7TQoBCQkBYQIBAQEzAU4bS7AvUFhAKgcBBQQBAAMFAGcABgYyTQAICANhAAMDO00AAQEzTQoBCQkCYQACAjwCThtAKgcBBQQBAAMFAGcABgYyTQAICANhAAMDO00AAQE2TQoBCQkCYQACAjwCTllZQBIZGRkkGSMlEREREiYiERALCR8rASMRIycGIyImJjU0NjYzMhc1IzUzNTMVMwA2NTQmIyIGFRQWMwKDP4gKP2VFazw8a0VbPlpanT/+5EJCNDRCQjQCKP3YO0VBdUtLdUE5aVw4OP32RTg4RUY3N0YAAAIAH//0Ai8B+QAYAB8AQEA9DAEBAA0BAgECTAAEAAABBABnBwEFBQNhBgEDAztNAAEBAmEAAgI8Ak4ZGQAAGR8ZHhwbABgAFyUiFQgJGSsAFhYVFAchFhYzMjY3FwYGIyImJjU0NjYzBgYHMyYmIwF6dj8F/pUHRDUlRhlSKnNBVn5EQ3hPKjsE2gM5MAH5PW9KGCMmLxYUWCcqP3RPTHZBfDArKzAA//8AH//0Ai8CvAAiAJwAAAADAvsB1wAA//8AH//0Ai8CvAAiAJwAAAADAv8CAgAA//8AH//0Ai8CvAAiAJwAAAADAv4CIwAA//8AH//0Ai8CvAAiAJwAAAADAv0CIgAA//8AH//0Ai8CxQAiAJwAAAADAvgCJQAA//8AH//0Ai8CxgAiAJwAAAADAvkBtQAA//8AH//0Ai8CvAAiAJwAAAADAvoCJwAA//8AH//0Ai8CpwAiAJwAAAADAwICCgAAAAIAH/9EAjAB+QAmAC0ATEBJDAEBAB8VDQMCARYBAwIDTAABAAIAAQKAAAUAAAEFAGcAAgADAgNmCAEGBgRhBwEEBDsGTicnAAAnLScsKikAJgAlJCgiFQkJGisAFhYVFAchFhYzMjY3FwYHBhUUMzI3FwYGIyImNTQ2NyYmNTQ2NjMGBgczJiYjAXp3PwX+lAdENChEGVMxRkQaERArGD4gMDcUE299SXlIKTsF2QM6LwH5PXBKGSEmLxYUWCobGiQaDEUUFzAqFy4TDIhsU3U7fDArLS4AAAEAFQAAAcQCzAAXAFxAChABBgURAQAGAkxLsC9QWEAcAAYGBWEABQU4TQMBAQEAXwQBAAA1TQACAjMCThtAHAAGBgVhAAUFOE0DAQEBAF8EAQAANU0AAgI2Ak5ZQAokJBEREREQBwkdKwEzFSMRIxEjNTM1NDY2MzIXByYmIyIGFQELhoafV1c5XDVTOzUSHRIfJAHufv6QAXB+GkJYKi5jCwojJQAAAAIAH/7kAksCKwAoADQAeUAQIyIgAwUEKAEDBgJMIQEESkuwL1BYQCUAAQMCAwECgAACAAACAGUABQUEYQAEBDtNBwEGBgNhAAMDMwNOG0AlAAEDAgMBAoAAAgAAAgBlAAUFBGEABAQ7TQcBBgYDYQADAzYDTllADykpKTQpMy4mJCIVJQgJHCskFhUUBgYjIiYmNTQ3MwYWMzI2NTQmIyImJjU0NjYzMhc3FwcWFRQGByY2NTQmIyIGFRQWMwIIN0R8UlB4QQGXAjs4Mj45NVJ7Q0V7Tz0zOnNCMjUwdEA/NTRAQDQ6UTU+XzM0YD8QCDE2LSUmKT5xS0hxPxhIU005TzddHj1ANTU/PzU0QQD//wAf/uQCSwK8ACIApwAAAAMC/wILAAD//wAf/uQCSwLTACIApwAAAQcC/QIsABcACLECAbAXsDUrAAAAAwAf/uQCSwMZAA0ANgBCAJlAES8HAgEAMTAuAwcGNgEFCANMS7AvUFhALgADBQQFAwSAAAAJAQEGAAFpAAQAAgQCZQAHBwZhAAYGO00KAQgIBWEABQUzBU4bQC4AAwUEBQMEgAAACQEBBgABaQAEAAIEAmUABwcGYQAGBjtNCgEICAVhAAUFNgVOWUAcNzcAADdCN0E9Oy0rJSMfHRsaFRMADQAMFQsJFysAJjU0NjczBxYWFRQGIxIWFRQGBiMiJiY1NDczBhYzMjY1NCYjIiYmNTQ2NjMyFzcXBxYVFAYHJjY1NCYjIgYVFBYzAQ0sGCJKGBYaLCLZN0R8UlB4QQGXAjs4Mj45NVJ7Q0V7Tz0zOnNCMjUwdEA/NTRAQDQCJSwiHEBKZwcjGCEq/hVRNT5fMzRgPxAIMTYtJSYpPnFLSHE/GEhTTTlPN10ePUA1NT8/NTRBAP//AB/+5AJLAsYAIgCnAAAAAwL5Ab4AAAABADsAAAI1ArwAEgBQtRABAQQBTEuwL1BYQBcAAwMyTQABAQRhBQEEBDtNAgEAADMAThtAFwADAzJNAAEBBGEFAQQEO00CAQAANgBOWUANAAAAEgARERMjEwYJGisAFhURIxE0JiMiBhURIxEzETYzAcprnS8qLjmdnTleAfl6aP7pAQ4wNj4y/vwCvP78QQABAAIAAAI1ArwAGgBotRgBAQgBTEuwL1BYQCEGAQQHAQMIBANnAAUFMk0AAQEIYQkBCAg7TQIBAAAzAE4bQCEGAQQHAQMIBANnAAUFMk0AAQEIYQkBCAg7TQIBAAA2AE5ZQBEAAAAaABkRERERERMjEwoJHisAFhURIxE0JiMiBhURIxEjNTM1MxUzFSMVNjMBxm+dMycsOp05OZ1xcThbAflzd/7xAQ4yND00/v0CKFw4OFxqOwD////CAAACNQOKACIArAAAAQcC/QGAAM4ACLEBAbDOsDUrAAAAAgAuAAAA5gLKAAsADwBIS7AvUFhAFgQBAQEAYQAAADhNAAICNU0AAwMzA04bQBYEAQEBAGEAAAA4TQACAjVNAAMDNgNOWUAOAAAPDg0MAAsACiQFCRcrEiY1NDYzMhYVFAYjBzMRI2EzNCgoNDMpT52dAh8wJSYwMCYlMDH+EgABADsAAADYAe4AAwAoS7AvUFhACwAAADVNAAEBMwFOG0ALAAAANU0AAQE2AU5ZtBEQAgkYKxMzESM7nZ0B7v4SAAAA//8AOwAAARoCvAAiALAAAAADAyIBNgAA////7wAAASYCvAAiALAAAAADAyQBYgAA////0AAAAUMCvAAiALAAAAADAyMBggAA////0wAAAT8CxQAiALAAAAADAyABfgAA//8ANQAAAN4CxgAiALAAAAADAvkBFQAA////+QAAANgCvAAiALAAAAADAyEBhgAA//8ALv8TAfsCygAiAK8AAAADALsBEwAA/////wAAARQCpwAiALAAAAADAyYBagAAAAIAKf9EAQACxgALACAAZ0ALIAEFAwFMGQEDAUtLsC9QWEAdAAUAAgUCZQYBAQEAYQAAADhNAAQENU0AAwMzA04bQB0ABQACBQJlBgEBAQBhAAAAOE0ABAQ1TQADAzYDTllAEgAAHx0YFxYVEA4ACwAKJAcJFysSJjU0NjMyFhUUBiMTBgYjIiY1NDY3IxEzEQYGFRQzMjdlMDAlJS8vJXYXPiAuNBwYIp0fHBgRDwIqLCIiLCwiIiz9RRQXLiccNRYB7v4SECARGQwA////3gAAATYCwwAiALAAAAADAyUBfgAAAAL/tf8TAOgCygALABkAY0AKDgECAw0BBAICTEuwIVBYQBwFAQEBAGEAAAA4TQADAzVNAAICBGIGAQQEPQROG0AZAAIGAQQCBGYFAQEBAGEAAAA4TQADAzUDTllAFAwMAAAMGQwYFRQRDwALAAokBwkXKxImNTQ2MzIWFRQGIwInNxYzMjY1ETMRFAYjYzQ0KCk0NCmZPSMcFxkYnVtSAh8wJSUxMSUlMPz0IHEOIyUCEP3wYWoAAAAB/7X/EwDZAe4ADQBEQAoCAQABAQECAAJMS7AhUFhAEQABATVNAAAAAmIDAQICPQJOG0AOAAADAQIAAmYAAQE1AU5ZQAsAAAANAAwTIwQJGCsGJzcWMzI2NREzERQGIw49IxwXGRidW1LtIHEOIyUCEP3wYWoAAP///7X/EwEcArwAIgC8AAAAAwMiATgAAP///7X/EwFEArwAIgC8AAAAAwMjAYMAAAABADsAAAIwArwACgA/twoHAgMAAwFMS7AvUFhAEQACAjJNAAMDNU0BAQAAMwBOG0ARAAICMk0AAwM1TQEBAAA2AE5ZthIREhAECRorISMnFSMRMxE3MwcCMMKXnJyJs7LExAK8/ne76gAAAP//ADv+9QIwArwAIgC/AAAAAwMEAWcAAP//ADsAAAIwAe4AAgG4AAAAAQA7AAAA2AK8AAMAKEuwL1BYQAsAAAAyTQABATMBThtACwAAADJNAAEBNgFOWbQREAIJGCsTMxEjO52dArz9RAAAAP//ADsAAAEpA4oAIgDCAAABBwL7ATYAzgAIsQEBsM6wNSsAAAACADsAAAGmArwAAwAHADZLsC9QWEARAAMDAF8CAQAAMk0AAQEzAU4bQBEAAwMAXwIBAAAyTQABATYBTlm2EREREAQJGisTMxEjEzMHIzudneeESWcCvP1EArzS//8AO/71ANgCvAAiAMIAAAADAwQA3gAA//8AOwAAAcICvAAiAMIAAAEHAn0A3gAqAAixAQGwKrA1KwAAAAEAEQAAATACvAALADdADQsIBwYFAgEACAABAUxLsC9QWEALAAEBMk0AAAAzAE4bQAsAAQEyTQAAADYATlm0FRMCCRgrARUHESMRBzU3ETMVATBBnUFBnQHldCD+rwEFIHQgAUP3AAAAAQA7AAADXwH5ACEAebYfGQIBBQFMS7AVUFhAFgMBAQEFYQgHBgMFBTVNBAICAAAzAE4bS7AvUFhAGgAFBTVNAwEBAQZhCAcCBgY7TQQCAgAAMwBOG0AaAAUFNU0DAQEBBmEIBwIGBjtNBAICAAA2AE5ZWUAQAAAAIQAgIxETIxMjEwkJHSsAFhURIxE0JiMiBhURIxE0JiMiBhURIxEzFzY2MzIWFzYzAvNsnSklKTCcKCUpMZ2ICRpJKjBMFjxuAfluYP7VARcsMTgu/vIBFywxOC7+8gHuNyAiKSRNAAABADsAAAI1AfkAEwBstRABAQMBTEuwFVBYQBMAAQEDYQUEAgMDNU0CAQAAMwBOG0uwL1BYQBcAAwM1TQABAQRhBQEEBDtNAgEAADMAThtAFwADAzVNAAEBBGEFAQQEO00CAQAANgBOWVlADQAAABMAEhETIxMGCRorABYVESMRNCYjIgYVESMRMxc2NjMByG2dMCouOJ2ICh1RMQH5eGr+6QEOMDY+Mv78Ae46ISQA//8AOwAAAjUCvAAiAMkAAAADAvsB9QAA//8APwAAAt4CwwAjAMkAqQAAAAICnwAA//8AOwAAAjUCvAAiAMkAAAADAv4CQgAA//8AO/71AjUB+QAiAMkAAAADAwQBjAAAAAEAO/8fAjUB+QAcALRADhkBAgQJAQEDCAEAAQNMS7AVUFhAHAACAgRhBgUCBAQ1TQADAzNNAAEBAGEAAAA3AE4bS7AhUFhAIAAEBDVNAAICBWEGAQUFO00AAwMzTQABAQBhAAAANwBOG0uwL1BYQB0AAQAAAQBlAAQENU0AAgIFYQYBBQU7TQADAzMDThtAHQABAAABAGUABAQ1TQACAgVhBgEFBTtNAAMDNgNOWVlZQA4AAAAcABsREyQjJQcJGysAFhURFAYjIic3FjMyNRE0JiMiBhURIxEzFzY2MwHIbV1ROj0lGRgyMCouOJ2ICh1RMQH5eGr+0GFnIHAOSAElMDY+Mv78Ae46ISQAAAD//wA7AAACNQLDACIAyQAAAAMDAQI7AAAAAgAf//UCPgH5AA8AGwAsQCkAAgIAYQAAADtNBQEDAwFhBAEBATwBThAQAAAQGxAaFhQADwAOJgYJFysWJiY1NDY2MzIWFhUUBgYjNjY1NCYjIgYVFBYz3HtCQntSUnxCQnxSNEBANDNAQDMLQXRNTXRBQXRNTXRBhUY3N0ZGNzdGAAD//wAf//UCPgK8ACIA0AAAAAMC+wHbAAD//wAf//UCPgK8ACIA0AAAAAMC/wIGAAD//wAf//UCPgK8ACIA0AAAAAMC/QInAAD//wAf//UCPgLFACIA0AAAAAMC+AIpAAD//wAf//UCPgK8ACIA0AAAAAMC+gIrAAD//wAf//UCPgK8ACIA0AAAAAMC/AJAAAD//wAf//UCPgKnACIA0AAAAAMDAgIPAAAAAwAf/8MCOgIpABcAHwAnAEpARxcUAgQCJSQdHAQFBAsIAgAFA0wAAwIDhQABAAGGBgEEBAJhAAICO00HAQUFAGEAAAA8AE4gIBgYICcgJhgfGB4SJxIlCAkaKwAWFRQGBiMiJwcjNyYmNTQ2NjMyFzczBwYGFRQXNyYjFjY1NCcHFjMCCDJCe1ExKiRoOy8yQnpRNSgkZzvfPxN0DggzPxNzDgYBpGtCTXRBDD5lImpDTHVBDT1jUkY3KSHFAvpGNykgxAIAAP//AB//wwI6ArwAIgDYAAAAAwL7AdgAAP//AB//9QI+AsMAIgDQAAAAAwMBAiEAAAADAB//9QOgAfkAJAArADcA6kuwLVBYQA8hAQcEDAEBABMNAgIBA0wbQA8hAQcEDAEJABMNAgIBA0xZS7AVUFhAJAAGAAABBgBnCAsCBwcEYQoFAgQEO00MCQIBAQJhAwECAjwCThtLsC1QWEAvAAYAAAEGAGcLAQcHBGEKBQIEBDtNAAgIBGEKBQIEBDtNDAkCAQECYQMBAgI8Ak4bQDkABgAACQYAZwsBBwcEYQoFAgQEO00ACAgEYQoFAgQEO00MAQkJAmEDAQICPE0AAQECYQMBAgI8Ak5ZWUAeLCwlJQAALDcsNjIwJSslKignACQAIyYkJSIVDQkbKwAWFhUUByEWFjMyNjcXBgYjIiYnBgYjIiYmNTQ2NjMyFhc2NjMGBgczNiYjADY1NCYjIgYVFBYzAvNwPQb+lglILShEF1MobT1BbSQiYz9Mcz4+c0xAZSEjZzsyPgbXAjku/r1AQDMzPz8zAfk9bUYgIScsFxVZKikqKigsQXVMTHVBLCkqK3oxLCsy/vtGNzdGRzY2RwAAAAIAO/8qAl4B+AAQABwAlkAKDgEEAgkBAAUCTEuwGVBYQB0ABAQCYQYDAgICNU0HAQUFAGEAAAA8TQABATcBThtLsCFQWEAhAAICNU0ABAQDYQYBAwM7TQcBBQUAYQAAADxNAAEBNwFOG0AhAAQEA2EGAQMDO00HAQUFAGEAAAA8TQABAQJfAAICNQFOWVlAFBERAAARHBEbFxUAEAAPERImCAkZKwAWFhUUBgYjIicRIxEzFzYzEjY1NCYjIgYVFBYzAbZsPDxsRVw9nYgKPmYPQkI0NEFBNAH4QXVLS3VBOv76AsQ6RP6CRTg4RUY3N0YAAAACADv/KgJcArwAEAAcAHBACg4BBAMJAQAFAkxLsCFQWEAhAAICMk0ABAQDYQYBAwM7TQcBBQUAYQAAADxNAAEBNwFOG0AhAAQEA2EGAQMDO00HAQUFAGEAAAA8TQABAQJfAAICMgFOWUAUEREAABEcERsXFQAQAA8REiYICRkrABYWFRQGBiMiJxEjETMVNjMSNjU0JiMiBhUUFjMBs2w9PWxGYDWdnTVgEkJCNDRCQjQB+EF1S0t1QTv++QOS/zv+gkU4OEVFODhFAAACAB7/KgJBAfgAEAAcAKlLsBlQWEAKDwEEAgMBAQUCTBtACg8BBAMDAQEFAkxZS7AZUFhAHQAEBAJhBgMCAgI7TQcBBQUBYQABATxNAAAANwBOG0uwIVBYQCEGAQMDNU0ABAQCYQACAjtNBwEFBQFhAAEBPE0AAAA3AE4bQCEABAQCYQACAjtNBwEFBQFhAAEBPE0AAAADXwYBAwM1AE5ZWUAUEREAABEcERsXFQAQABAmIhEICRkrAREjEQYjIiYmNTQ2NjMyFzcCNjU0JiMiBhUUFjMCQZ09XEVsPDxsRWY+ClVBQTQ0QkI0Ae79PAEGOkF1S0t1QUQ6/oxGNzdGRTg4RQAAAAABADsAAAHTAfkAEABuQAsOAgIAAgMBAQACTEuwFVBYQBIAAAACYQQDAgICNU0AAQEzAU4bS7AvUFhAFgACAjVNAAAAA2EEAQMDO00AAQEzAU4bQBYAAgI1TQAAAANhBAEDAztNAAEBNgFOWVlADAAAABAADxETJQUJGSsAFhcHJiYjIgYVFSMRMxc2MwF2RBlCFSQUMjqdiQwwVAH5GRhzDQxAPvAB7j5JAAD//wA7AAAB0wK8ACIA3wAAAAMC+wGeAAD//wAsAAAB0wK8ACIA3wAAAAMC/gHrAAD//wA7/vUB0wH5ACIA3wAAAAMDBADeAAAAAQAX//MB4QH7ACEAkkASEwEDAhQBAQMCAQABAQEEAARMS7ALUFhAHgABAwADAQCAAAMDAmEAAgI7TQAAAARhBQEEBDwEThtLsA1QWEAeAAEDAAMBAIAAAwMCYQACAjtNAAAABGEFAQQEOQROG0AeAAEDAAMBAIAAAwMCYQACAjtNAAAABGEFAQQEPAROWVlADQAAACEAICQkFCQGCRorFic3FhYzMjU0JicmJjU0NjMyFhcHJiMiFRQWFxYWFRQGI3hhPCRfL0EkKl5veGY6aSY9OE1MHyVqb3psDUJsFhgjEhIDBVRESlccGWkgJA8QBAhQSExXAP//ABf/8wHhArwAIgDjAAAAAwL7AaoAAP//ABf/8wHhArwAIgDjAAAAAwL+AfcAAAABABf/CQHhAfsAOADHQCAtAQcGLgEFBxwBBAUbGQIABBgBAwAXDQICAwwBAQIHTEuwC1BYQCwABQcEBwUEgAAABAMCAHIABAADAgQDaQAHBwZhAAYGO00AAgIBYgABAT0BThtLsCFQWEAtAAUHBAcFBIAAAAQDBAADgAAEAAMCBANpAAcHBmEABgY7TQACAgFiAAEBPQFOG0AqAAUHBAcFBIAAAAQDBAADgAAEAAMCBANpAAIAAQIBZgAHBwZhAAYGOwdOWVlACyQkFCgkJCQTCAkeKyQGBwcWFhUUBiMiJic3FjMyNjU0JiMiByc3Jic3FhYzMjU0JicmJjU0NjMyFhcHJiMiFRQWFxYWFQHhXlYMLTVLPSpGFjUgKBQYGBUVDh4aZE88JF8vQSQqXm94ZjppJj04TUwfJWpvU1MKHgM2LC87Gxk9GxEODxIIHEMKNWwWGCMSEgMFVERKVxwZaSAkDxAECFBIAAD//wAX//MB4QK8ACIA4wAAAAMC/QH2AAD//wAX/vUB4QH7ACIA4wAAAAMDBAFWAAAAAQA7//UCTgLGACgAqkuwFVBYQA4oAQIDCAEBAgcBAAEDTBtADigBAgMIAQECBwEABQNMWUuwFVBYQB4AAwACAQMCaQAEBAZhAAYGOE0AAQEAYQUBAAA8AE4bS7AvUFhAIgADAAIBAwJpAAQEBmEABgY4TQAFBTNNAAEBAGEAAAA8AE4bQCIAAwACAQMCaQAEBAZhAAYGOE0ABQU2TQABAQBhAAAAPABOWVlACiMSJCEkIyQHCR0rABYVFAYjIic1FjMyNjU0JiMjNTMyNjU0JiMiFREjETQ2MzIWFhUUBgcCCkR7byA2Hh4yNj89IBkqLi8oWJ1/dEhtOysmAWtiRGJuCYsJLy0uL4EjHh8kWP4aAfZjbS5VNzBKEgABABUAAAHCAswAEwBdQAoCAQAEAwEDAAJMS7AvUFhAGwAAAARhBQEEBDhNAAICA18AAwM1TQABATMBThtAGwAAAARhBQEEBDhNAAICA18AAwM1TQABATYBTllADQAAABMAEhEREyQGCRorABYXByYjIgYVESMRIzUzNTQ2NjMBXkkbMyAmHCKfV1c5XDUCzBgYZRkkJP34AXB+GkJYKgAAAQAX//YBnQJ6ABUALkArFQEFAQFMCwoCAkoEAQEBAl8DAQICNU0ABQUAYQAAADwATiMRExETIQYJHCslBiMiJjU1IzUzNTcVMxUjFRQWMzI3AZ06SVFeVFSce3seGh0cEx1bZbt9exGMfbseHQ4AAAEAF//2AZ0CegAdAD1AOh0BCQEBTA8OAgRKBwECCAEBCQIBZwYBAwMEXwUBBAQ1TQAJCQBhAAAAPABOHBoRERETEREREyEKCR8rJQYjIiY1NSM1MzUjNTM1NxUzFSMVMxUjFRQWMzI3AZ06SVFeRERUVJx7e1paHhogGRMdW2UcYEV3exGMd0VgHB4dEQAAAAIAF//2AjgChwADABkAQkA/ERACBAAFAQcDBgECBwNMAAAAAQMAAWcGAQMDBF8FAQQENU0IAQcHAmEAAgI8Ak4EBAQZBBgRExETJBEQCQkdKwEzByMCNxcGIyImNTUjNTM1NxUzFSMVFBYzAa2LTGslHCU6SVFeVFScX18eGgKH2f7NDnYdW2W7fXsRjH27Hh0AAAABABf/CQGdAnoAKwDNQB0nAQcDKBUCCAcUAQIIEwkCAQIIAQABBUwdHAIESkuwC1BYQC0ABwMIAwcIgAkBCAIBCHAAAgEDAgF+BgEDAwRfBQEEBDVNAAEBAGIAAAA9AE4bS7AhUFhALgAHAwgDBwiACQEIAgMIAn4AAgEDAgF+BgEDAwRfBQEEBDVNAAEBAGIAAAA9AE4bQCsABwMIAwcIgAkBCAIDCAJ+AAIBAwIBfgABAAABAGYGAQMDBF8FAQQENQNOWVlAEQAAACsAKyMRExEWJCQkCgkeKwQWFRQGIyImJzcWMzI2NTQmIyIHJzcmNTUjNTM1NxUzFSMVFBYzMjcXBgcHAVY1Sz0qRhY1ICgUGBgVFQ4eHWpUVJx7ex4aHRwlLzgNKzYsLzsbGT0bEQ4PEggcTSGVu317EYx9ux4dDnYXBR///wAX/vUBnQJ6ACIA6wAAAAMDBAFfAAAAAQA1//UCKwHuABMAbLUDAQADAUxLsBVQWEATBQQCAgI1TQADAwBiAQEAADMAThtLsC9QWEAXBQQCAgI1TQAAADNNAAMDAWIAAQE8AU4bQBcFBAICAjVNAAAANk0AAwMBYgABATwBTllZQA0AAAATABMjEyMRBgkaKwERIycGBiMiJjURMxEUFjMyNjURAiuIChxRMFtsnS8pLTcB7v4SOSEjeGoBF/7yMDY/MgEDAP//ADX/9QIrArwAIgDwAAAAAwL7Ad0AAP//ADX/9QIrArwAIgDwAAAAAwL/AggAAP//ADX/9QIrArwAIgDwAAAAAwL9AikAAP//ADX/9QIrAsUAIgDwAAAAAwL4AisAAP//ADX/9QIrArwAIgDwAAAAAwL6Ai0AAP//ADX/9QI2ArwAIgDwAAAAAwL8AkIAAP//ADX/9QIrAqcAIgDwAAAAAwMCAhEAAAABADX/RAJZAe4AIgAwQC0aCAcDAQMiAQUBAkwABQAABQBlBAECAjVNAAMDAWIAAQE8AU4lEyMTJyEGCRwrBQYjIiY1NDcnBgYjIiY1ETMRFBYzMjY1ETMRBhUUFjMyNjcCWTVIMjkyChxRMFtsnS8pLTedRRANChcJjS8wKjgsNyEjeGoBF/7yMDY/MgED/hIfHwsPCQcA//8ANf/1AisDEgAiAPAAAAADAwAB8AAA//8ANf/1AisCwwAiAPAAAAADAwECIwAAAAEAAgAAAkUB7gAIADK1BwEBAAFMS7AvUFhADAIBAAA1TQABATMBThtADAIBAAA1TQABATYBTlm1EREQAwkZKwEzAyMDMxcXNwGep9Gg0qs7PT0B7v4SAe6Vs7MAAQACAAADOwHuABAAOrcPDAUDAQABTEuwL1BYQA4EAwIAADVNAgEBATMBThtADgQDAgAANU0CAQEBNgFOWbcTERQREAUJGysBMwMjJycHByMDMxcXEzMTNwKVpqWVKTk5KZalpiwmcWhxJgHu/hJ5n595Ae6YmAEw/s+Z//8AAgAAAzsCvAAiAPwAAAADAvsCTAAA//8AAgAAAzsCvAAiAPwAAAADAv0ClwAA//8AAgAAAzsCxQAiAPwAAAADAvgCmgAA//8AAgAAAzsCvAAiAPwAAAADAvoCmwAAAAEAAwAAAiIB7gAPADe3DAgEAwACAUxLsC9QWEANAwECAjVNAQEAADMAThtADQMBAgI1TQEBAAA2AE5ZthQSFBEECRorJRcjJycHByM3JzMXFzc3MwF8prQrMTEtsaaZsS4kJi6t+/tHU1NH+/NLRERLAAAAAQAC/yoCPQHuAAkAM7YIBAIBAAFMS7AhUFhADAIBAAA1TQABATcBThtADAABAQBfAgEAADUBTlm1EhEQAwkZKwEzASM3AzMXFzcBk6r+zKdgwKk5NjoB7v083QHnnKGhAAAA//8AAv8qAj0CvAAiAQIAAAADAvsBywAA//8AAv8qAj0CvAAiAQIAAAADAv0CFwAA//8AAv8qAj0CxQAiAQIAAAADAvgCGQAA//8AAv8qAj0CvAAiAQIAAAADAvoCGwAAAAEAGQAAAdMB7gAJAEpACgkBAgMEAQEAAkxLsC9QWEAVAAICA18AAwM1TQAAAAFfAAEBMwFOG0AVAAICA18AAwM1TQAAAAFfAAEBNgFOWbYREhEQBAkaKzczFSE1EyM1IRX52v5G1MEBoImJNAE1hTIAAAD//wAZAAAB0wK8ACIBBwAAAAMC+wGpAAD//wAZAAAB0wK8ACIBBwAAAAMC/gH2AAD//wAZAAAB0wLGACIBBwAAAAMC+QGIAAD//wBM//gCxgK8AAIAYwAAAAIAG//3AgAB+QAYACQArEAWFgEDBBUBAgMPAQUCGwEGBQUBAAYFTEuwG1BYQCAAAgAFBgIFaQADAwRhBwEEBCFNCAEGBgBhAQEAABsAThtLsC9QWEAkAAIABQYCBWkAAwMEYQcBBAQhTQAAABtNCAEGBgFhAAEBIgFOG0AkAAIABQYCBWkAAwMEYQcBBAQhTQAAAB1NCAEGBgFhAAEBIgFOWVlAFRkZAAAZJBkjHx0AGAAXIyQiEwkHGisAFhURIycGIyImNTQ2MzIXJiYjIgYHJzYzEjY3JiYjIgYVFBYzAX+BiAo5ZFBmcVpMMQE5NSZXIhVaaCM7BBI6GCEoKB4B+V1m/so8RVhNTloXLCgSD20s/ncsIwsPGxoZGwAA//8AG//3AgACvAAiAQwAAAADAvsByAAA//8AG//3AgACvAAiAQwAAAADAv8B9AAA//8AG//3AgACvAAiAQwAAAADAv0CFAAA//8AG//3AgACxQAiAQwAAAADAvgCFgAA//8AG//3AgACvAAiAQwAAAADAvoCGAAA//8AG//3AgACpwAiAQwAAAADAwIB/AAAAAIAG/9EAi4B+QAnADMAVEBRGQEDBBgBAgMSAQYCKgEHBh8IBwMBBycBBQEGTAACAAYHAgZpAAUAAAUAZQADAwRhAAQEIU0IAQcHAWEAAQEiAU4oKCgzKDInJyQjJCYhCQcdKwUGIyImNTQ3JwYjIiY1NDYzMhcmJiMiBgcnNjMyFhURBhUUFjMyNjcmNjcmJiMiBhUUFjMCLjVIMjkyCjlkUGZxWkwxATk1JlciFVpofYFFEA0KFwndOwQSOhghKCgejS8wKjgsOkVYTU5aFywoEg9tLF1m/sofHwsPCQe4LCMLDxsaGRsAAAD//wAb//cCAAMSACIBDAAAAAMDAAHbAAD//wAb//cCAALDACIBDAAAAAMDAQIOAAAAAwAb//cDWQH5ACwAMwA/AQFLsC1QWEAZKSMCBQYiAQQFHQEIBDYLAgEAEQwCAgEFTBtAGSkjAgUGIgEEBR0BCAQ2CwIBABEMAgILBUxZS7APUFhAKwAECAAEWQAICgEAAQgAaQ0JAgUFBmEMBwIGBiFNDgsCAQECYQMBAgIiAk4bS7AtUFhALAAEAAoABAppAAgAAAEIAGcNCQIFBQZhDAcCBgYhTQ4LAgEBAmEDAQICIgJOG0A2AAQACgAECmkACAAAAQgAZw0JAgUFBmEMBwIGBiFNAAEBAmEDAQICIk0OAQsLAmEDAQICIgJOWVlAIDQ0LS0AADQ/ND46OC0zLTIwLwAsACskJCQjJSIUDwcdKwAWFRQHIRYWMzI2NxcGBiMiJwYGIyImNTQ2MzIWFzU0IyIHJzY2MzIWFzY2MwYGBzM2JiMANjcmJiMiBhUUFjMC33oG/q8IQjAePBhSJ2k3hEQkbkBbaW5dI0UZe0dQFTBYMUdkFRplPTg3BcUBMiv+vjsFFjcYJCgnIQH4gWwgIyYtFRNYJSlTJyxaTE1aDg0BWCJuFhUuKigvejEsKzL+8i0iDA4cGRkbAAAA//8AG//3A1kCvAAiARYAAAADAvsCagAAAAIAH/8LAkAB+AAcACgAwEuwGVBYQBIbAQUDDQECBgcBAQIGAQABBEwbQBIbAQUEDQECBgcBAQIGAQABBExZS7AZUFhAHwABAAABAGUABQUDYQcEAgMDIU0IAQYGAmEAAgIbAk4bS7AvUFhAIwABAAABAGUHAQQEHE0ABQUDYQADAyFNCAEGBgJhAAICGwJOG0AjAAEAAAEAZQcBBAQcTQAFBQNhAAMDIU0IAQYGAmEAAgIdAk5ZWUAVHR0AAB0oHScjIQAcABwmJSMjCQcaKwERFAYjIic3FjMyNjU1BgYjIiYmNTQ2NjMyFhc3AjY1NCYjIgYVFBYzAkCUgYRoOVNQRkUcUC9Fazw8a0UyVB4KVEFBNTRBQTQB7v4Td39CcC87PzEeH0FzSkp0QCMhOv6PRDc3RUU3N0QAAP//AB//CwJAArwAIgEYAAAAAwL/AgQAAP//AB//CwJAArwAIgEYAAAAAwL9AiQAAAADAB//CwJAAxUADQAqADYA7kuwGVBYQBYHAQEAKQEHBRsBBAgVAQMEFAECAwVMG0AWBwEBACkBBwYbAQQIFQEDBBQBAgMFTFlLsBlQWEAoAAAJAQEFAAFpAAMAAgMCZQAHBwVhCgYCBQUhTQsBCAgEYQAEBBsEThtLsC9QWEAsAAAJAQEFAAFpAAMAAgMCZQoBBgYcTQAHBwVhAAUFIU0LAQgIBGEABAQbBE4bQCwAAAkBAQUAAWkAAwACAwJlCgEGBhxNAAcHBWEABQUhTQsBCAgEYQAEBB0ETllZQCArKw4OAAArNis1MS8OKg4qJyUfHRgWExEADQAMFQwHFysSJjU0NjczBxYWFRQGIwURFAYjIic3FjMyNjU1BgYjIiYmNTQ2NjMyFhc3AjY1NCYjIgYVFBYz+SwYIkoYFhosIgEllIGEaDlTUEZFHFAvRWs8PGtFMlQeClRBQTU0QUE0AiEsIhxASmcHJBggKjP+E3d/QnAvOz8xHh9Bc0pKdEAjITr+j0Q3N0VFNzdEAAD//wAf/wsCQALGACIBGAAAAAMC+QG3AAAAAQA1/wsCKwHuAB0AXkAODgECBAgBAQIHAQABA0xLsC9QWEAZAAEAAAEAZQYFAgMDHE0ABAQCYgACAhsCThtAGQABAAABAGUGBQIDAxxNAAQEAmIAAgIdAk5ZQA4AAAAdAB0jEyQkIwcHGysBERQGIyImJzcWMzI2NTUGIyImNREzERQWMzI2NTUCK4h/RHIyO1RNPUA3YmFmnTApLDcB7v4NdXsfI3AvODdBQXpwAQf++C84PzP9//8ANf8LAisCvAAiAR0AAAADAvsB3QAA//8ANf8LAisCvAAiAR0AAAADAv0CKQAA//8ANf8LAisCxQAiAR0AAAADAvgCKwAA//8ANf8LAisCvAAiAR0AAAADAvoCLQAAAAEAFQAAAaYCyAANAHFLsClQWEAcAAAABl8ABgYaTQQBAgIBXwUBAQEcTQADAxsDThtLsC9QWEAaAAYAAAEGAGcEAQICAV8FAQEBHE0AAwMbA04bQBoABgAAAQYAZwQBAgIBXwUBAQEcTQADAx0DTllZQAoREREREREQBwcdKwEjFTMVIxEjESM1MzUhAaadg4OdV1cBOgJDVX7+kAFwftoAAAAAAgAf/yoCQQH4ABQAIADmS7AZUFhAChMBBQMFAQIGAkwbQAoTAQUEBQECBgJMWUuwGVBYQCIABQUDYQcEAgMDIU0IAQYGAmEAAgIbTQABAQBgAAAAHgBOG0uwL1BYQCYHAQQEHE0ABQUDYQADAyFNCAEGBgJhAAICG00AAQEAYAAAAB4AThtLsDFQWEAmBwEEBBxNAAUFA2EAAwMhTQgBBgYCYQACAh1NAAEBAGAAAAAeAE4bQCQIAQYAAgEGAmkHAQQEHE0ABQUDYQADAyFNAAEBAGAAAAAeAE5ZWVlAFRUVAAAVIBUfGxkAFAAUJiMREQkHGisBESE1ITUGBiMiJiY1NDY2MzIWFzcCNjU0JiMiBhUUFjMCQf42AS8dUTBEajs7akQ2WhsCUUJCNDNCQjMB7v08hZsfIUBwR0dwQCgjQf6dQjIzQkIzMkIAAAD//wAf/yoCQQK8ACIBIwAAAAMC/wIEAAD//wAf/yoCQQK8ACIBIwAAAAMC/QIkAAAAAwAf/yoCQQMVAA0AIgAuAR1LsBlQWEAOBwEBACEBBwUTAQQIA0wbQA4HAQEAIQEHBhMBBAgDTFlLsBlQWEArAAAJAQEFAAFpAAcHBWEKBgIFBSFNCwEICARhAAQEG00AAwMCYAACAh4CThtLsC9QWEAvAAAJAQEFAAFpCgEGBhxNAAcHBWEABQUhTQsBCAgEYQAEBBtNAAMDAmAAAgIeAk4bS7AxUFhALwAACQEBBQABaQoBBgYcTQAHBwVhAAUFIU0LAQgIBGEABAQdTQADAwJgAAICHgJOG0AtAAAJAQEFAAFpCwEIAAQDCARpCgEGBhxNAAcHBWEABQUhTQADAwJgAAICHgJOWVlZQCAjIw4OAAAjLiMtKScOIg4iHx0XFRIREA8ADQAMFQwHFysSJjU0NjczBxYWFRQGIwURITUhNQYGIyImJjU0NjYzMhYXNwI2NTQmIyIGFRQWM/MrGSFJFxYaLCIBK/42AS8dUTBEajs7akQ2WhsCUUJCNDNCQjMCISojHURGZwgjGCAqM/08hZsfIUBwR0dwQCgjQf6dQjIzQkIzMkIAAP//AB//KgJBAsYAIgEjAAAAAwL5AbcAAP//AC7/KgIIAsoAIgCvAAAAAwEpARMAAAAC/9T/KgD1AsoACwARAFJLsC1QWEAbBQEBAQBhAAAAH00AAwMcTQACAgRgAAQEHgROG0AZAAAFAQEDAAFpAAMDHE0AAgIEYAAEBB4ETllAEAAAERAPDg0MAAsACiQGBxcrEiY1NDYzMhYVFAYjAzMRMxEhcDQ0KCk0NCnEdZ3+7gIfMCUlMTElJTD9kAI//TwAAAAAAf/U/yoA5gHuAAUAGUAWAAEBHE0AAAACYAACAh4CThEREAMHGSsHMxEzESEsdZ3+7lECP/08AP///9T/KgEoArwAIgEqAAAAAwMiAUQAAP///9T/KgFRArwAIgEqAAAAAwMjAZAAAAABADsAAAEoArwABQBMS7AtUFhAEAACAhpNAAAAAWAAAQEbAU4bS7AvUFhAEAACAAKFAAAAAWAAAQEbAU4bQBAAAgAChQAAAAFgAAEBHQFOWVm1EREQAwcZKzczFSMRM9hQ7Z2FhQK8//8AOwAAASgDigAiAS0AAAEHAvsBNADOAAixAQGwzrA1KwAAAAIAOwAAAaYCvAAFAAkAZ0uwLVBYQBcABAQCXwMFAgICGk0AAAABYAABARsBThtLsC9QWEAVAwUCAgAEAAIEZwAAAAFgAAEBGwFOG0AVAwUCAgAEAAIEZwAAAAFgAAEBHQFOWVlADwAACQgHBgAFAAUREQYHGCsTETMVIxEzMwcj2FDt54RJZwK8/cmFArzS//8AO/71ASgCvAAiAS0AAAADAwQBBgAA//8AOwAAAcICvAAiAS0AAAEHAn0A3gAqAAixAQGwKrA1KwAAAAEAEQAAAT8CvAANAFtADQ0MCwoHBgUECAACAUxLsC1QWEAQAAICGk0AAAABYAABARsBThtLsC9QWEAQAAIAAoUAAAABYAABARsBThtAEAACAAKFAAAAAWAAAQEdAU5ZWbUVERADBxkrNzMVIxEHNTcRMxU3FQfvUO1BQZ1BQYWFAQUgdCABQ/cgdCAAAQA7AAABkQHuAAUAM0uwL1BYQBAAAQEAXwAAABxNAAICGwJOG0AQAAEBAF8AAAAcTQACAh0CTlm1EREQAwcZKxMhFSMRIzsBVrqcAe6H/pkAAAD//wA7AAABkQK8ACIBMwAAAAMC+wGQAAD//wAeAAABqgK8ACIBMwAAAAMC/gHdAAD//wA7/vUBkQHuACIBMwAAAAMDBADgAAAAAQAXAAABcAJ2AAsATEuwL1BYQBgCAQAAA18GBQIDAxxNAAQEAV8AAQEbAU4bQBgCAQAAA18GBQIDAxxNAAQEAV8AAQEdAU5ZQA4AAAALAAsREREREQcHGysBFSMRIxEjNTM1MxUBcGmcVFScAe59/o8BcX2IiAAAAQAXAAABcAJ2ABMAXkuwL1BYQCEFAQEEAQIDAQJnBgEAAAdfCQEHBxxNAAgIA18AAwMbA04bQCEFAQEEAQIDAQJnBgEAAAdfCQEHBxxNAAgIA18AAwMdA05ZQA4TEhEREREREREREAoHHysBIxUzFSMVIzUjNTM1IzUzNTMVMwFwaVdXnEREVFScaQFxP2DS0mA/fYiIAAACABcAAAI7AocAAwAPAIZLsA9QWEAfAAEDAAFXBQEDAwJfBgECAhxNCAcCAAAEXwAEBBsEThtLsC9QWEAgAAAAAQMAAWcFAQMDAl8GAQICHE0IAQcHBF8ABAQbBE4bQCAAAAABAwABZwUBAwMCXwYBAgIcTQgBBwcEXwAEBB0ETllZQBAEBAQPBA8REREREhEQCQcdKwEzByMnFTMVIxEjESM1MzUBsItMan5paZxUVAKH2ciIff6PAXF9iAAAAAACABf+/AFwAnYACwAdAG5LsC9QWEAnCgEJAAgHCQhpAAcABgcGYwMBAQEAXwQBAAAcTQAFBQJfAAICGwJOG0AnCgEJAAgHCQhpAAcABgcGYwMBAQEAXwQBAAAcTQAFBQJfAAICHQJOWUASDAwMHQwcJCElEREREREQCwcfKwEzFSMRIxEjNTM1MwIWFRQGIyM3MzI2NTQmIyM3MwEHaWmcVFScGDU+OFsITw8TDg1BCEYB7n3+jwFxfYj9WDooLkJSEgwLDUoA//8AF/71AXACdgAiATcAAAADAwQBDQAAAAEANf/1AioB7gARACFAHgIBAAAcTQABAQNiBAEDAyIDTgAAABEAEBMjEwUHGSsWJjURMxEUFjMyNjURMxEUBiO5hJwyLCwynYN3C3ltARP+7i8zMy8BEv7tbXn//wA1//UCKgK8ACIBPAAAAAMC+wHcAAD//wA1//UCKgK8ACIBPAAAAAMC/wIHAAD//wA1//UCKgK8ACIBPAAAAAMC/QIoAAD//wA1//UCKgLFACIBPAAAAAMC+AIqAAD//wA1//UCKgK8ACIBPAAAAAMC+gIsAAD//wA1//UCNQK8ACIBPAAAAAMC/AJBAAD//wA1//UCKgKnACIBPAAAAAMDAgIQAAAAAQA1/0QCKgHuACEAMkAvFAwCAAMNAQEAAkwAAwIAAgMAgAAAAAEAAWYFBAICAhwCTgAAACEAISMYJCgGBxorAREUBgcGFRQWMzI2NxcGIyImNTQ3JiY1ETMRFBYzMjY1EQIqU05EEA0KFwksNUgyOShdZpwyLCwyAe7+7VdxFB0gCw8JB0UvMCoxKg50YAET/u4vMzMvARIAAAD//wA1//UCKgMSACIBPAAAAAMDAAHvAAD//wA1//UCKgLDACIBPAAAAAMDAQIiAAAAAQA1/yoCKAHuABQAWbUFAQIEAUxLsC1QWEAcBgUCAwMcTQAEBAJiAAICG00AAQEAXwAAAB4AThtAGgAEAAIBBAJqBgUCAwMcTQABAQBfAAAAHgBOWUAOAAAAFAAUIxMiEREHBxsrAREhNSE1BiMiJjURMxUUFjMyNjU1Aij+TgEYN2BaaJwwKis2Ae79PIiYP3ppAQD5Lzc/Mu7//wA1/yoCKAK8ACIBRwAAAAMC+wHfAAD//wA1/yoCKAK8ACIBRwAAAAMC/QIrAAD//wA1/yoCKALFACIBRwAAAAMC+AItAAD//wA1/yoCKAK8ACIBRwAAAAMC+gIvAAD//wAb//cCAAH5AAIBDAAA//8AG//3AgACvAAiAQwAAAADAvsByAAA//8AG//3AgACvAAiAQwAAAADAv8B9AAA//8AG//3AgACvAAiAQwAAAADAv0CFAAA//8AG//3AgACxQAiAQwAAAADAvgCFgAA//8AG//3AgACvAAiAQwAAAADAvoCGAAA//8AG//3AgACpwAiAQwAAAADAwIB/AAAAAIAG/9EAi4B+QAnADMAVEBRGQEDBBgBAgMSAQYCKgEHBh8IBwMBBycBBQEGTAACAAYHAgZpAAUAAAUAZQADAwRhAAQEIU0IAQcHAWEAAQEiAU4oKCgzKDInJyQjJCYhCQcdKwUGIyImNTQ3JwYjIiY1NDYzMhcmJiMiBgcnNjMyFhURBhUUFjMyNjcmNjcmJiMiBhUUFjMCLjVIMjkyCjlkUGZxWkwxATk1JlciFVpofYFFEA0KFwndOwQSOhghKCgejS8wKjgsOkVYTU5aFywoEg9tLF1m/sofHwsPCQe4LCMLDxsaGRsAAAD//wAb//cCAAMSACIBDAAAAAMDAAHbAAD//wAb//cCAALDACIBDAAAAAMDAQIOAAD//wAb//cDWQH5AAIBFgAA//8AG//3A1kCvAAiARYAAAADAvsCagAA//8AH/8LAkAB+AACARgAAP//AB//CwJAArwAIgEYAAAAAwL/AgQAAP//AB//CwJAArwAIgEYAAAAAwL9AiQAAAADAB//CwJAAxUADQAqADYA7kuwGVBYQBYHAQEAKQEHBRsBBAgVAQMEFAECAwVMG0AWBwEBACkBBwYbAQQIFQEDBBQBAgMFTFlLsBlQWEAoAAAJAQEFAAFpAAMAAgMCZQAHBwVhCgYCBQUhTQsBCAgEYQAEBBsEThtLsC9QWEAsAAAJAQEFAAFpAAMAAgMCZQoBBgYcTQAHBwVhAAUFIU0LAQgIBGEABAQbBE4bQCwAAAkBAQUAAWkAAwACAwJlCgEGBhxNAAcHBWEABQUhTQsBCAgEYQAEBB0ETllZQCArKw4OAAArNis1MS8OKg4qJyUfHRgWExEADQAMFQwHFysSJjU0NjczBxYWFRQGIwURFAYjIic3FjMyNjU1BgYjIiYmNTQ2NjMyFhc3AjY1NCYjIgYVFBYz/isYIkkXFhkrIgEflIGEaDlTUEZFHFAvRWs8PGtFMlQeClRBQTU0QUE0AiErIx1CR2cHIxkgKjP+E3d/QnAvOz8xHh9Bc0pKdEAjITr+j0Q3N0VFNzdEAAD//wAf/wsCQALGACIBGAAAAAMC+QG3AAD//wA1/wsCKwHuAAIBHQAA//8ANf8LAisCvAAiAR0AAAADAvsB3QAA//8ANf8LAisCvAAiAR0AAAADAv0CKQAA//8ANf8LAisCxQAiAR0AAAADAvgCKwAA//8ANf8LAisCvAAiAR0AAAADAvoCLQAAAAEAFQAAAzsC0QApAR1LsA1QWEAMIxQCCAckFQIACAJMG0AMIxQCCwckFQIACAJMWUuwC1BYQCELAQgIB2EKAQcHGk0FAwIBAQBfCQYCAAAcTQQBAgIbAk4bS7ANUFhAKwsBCAgKYQAKCh9NCwEICAdhAAcHGk0FAwIBAQBfCQYCAAAcTQQBAgIbAk4bS7AtUFhAKQALCwphAAoKH00ACAgHYQAHBxpNBQMCAQEAXwkGAgAAHE0EAQICGwJOG0uwL1BYQCUACgALCAoLaQAHAAgABwhpBQMCAQEAXwkGAgAAHE0EAQICGwJOG0AlAAoACwgKC2kABwAIAAcIaQUDAgEBAF8JBgIAABxNBAECAh0CTllZWVlAEiclIiAcGyMkEREREREREAwHHysBMxUjESMRIxEjESM1MzU0NjYzMhcHJiMiBhUVMzU0NjYzMhcHJiMiBhUCgYeHndudV1c5XDdPNjYbGyIm2zhcNVQ6NSIfHyUB7n7+kAFw/pABcH4JQlgqImILJCUNIUJYKi5jFSMlAAAAAgAVAAAChALNABgAJACAQAoQAQYFEQEJBgJMS7AvUFhAKgAGBgVhCAEFBThNCgEJCQVhCAEFBThNAwEBAQRfBwEEBDVNAgEAADMAThtAKgAGBgVhCAEFBThNCgEJCQVhCAEFBThNAwEBAQRfBwEEBDVNAgEAADYATllAEhkZGSQZIyUTIyQREREREAsJHyshIxEjESMRIzUzNTQ2NjMyFwcmIyIGFRUhJiY1NDYzMhYVFAYjAnad0J1XVzhdN0IwLhwUHyQBbXczNCgoNDMpAXD+kAFwfhpCWSocagolIxsxMCUmMDAmJTAAAAABABUAAAJzAs0AGgCUtQMBAgEBTEuwDVBYQB8AAQEHYQkIAgcHOE0FAQMDAl8GAQICNU0EAQAAMwBOG0uwL1BYQCMJAQgIMk0AAQEHYQAHBzhNBQEDAwJfBgECAjVNBAEAADMAThtAIwkBCAgyTQABAQdhAAcHOE0FAQMDAl8GAQICNU0EAQAANgBOWVlAEQAAABoAGSQREREREyIRCgkeKwERIxEmIyIGFRUzFSMRIxEjNTM1NDY2MzIXNQJznSs8NTF7e51XVz1sRUM5Arz9RAI3GiwvCnz+kAFwfhc8WzEVBAABABUAAAMeAt4AFwCaS7AtUFhAJwALAAAJCwBnAAkJCF8ACAgaTQYEAgICAV8KBwIBARxNBQEDAxsDThtLsC9QWEAlAAsAAAkLAGcACAAJAQgJZwYEAgICAV8KBwIBARxNBQEDAxsDThtAJQALAAAJCwBnAAgACQEICWcGBAICAgFfCgcCAQEcTQUBAwMdA05ZWUASFxYVFBMSEREREREREREQDAcfKwEjFTMVIxEjESMRIxEjNTM1IRUjFTM1IQMenYKCndudV1cBKYzbAToCWWt+/pABcP6QAXB+zYJN8gAAAAACABUAAAKEAsoACwAbAKhLsC1QWEArAAgIAGEHAQAAH00KAQEBAGEHAQAAH00FAQMDBl8LCQIGBhxNBAECAhsCThtLsC9QWEAkAAgBAAhXBwEACgEBBgABaQUBAwMGXwsJAgYGHE0EAQICGwJOG0AkAAgBAAhXBwEACgEBBgABaQUBAwMGXwsJAgYGHE0EAQICHQJOWVlAHgwMAAAMGwwbGhkYFxYVFBMSERAPDg0ACwAKJAwHFysAJjU0NjMyFhUUBiMXESMRIxEjESM1MzUhFSMVAf8zNCgoNDMpTp3QnVdXASmMAh8wJSYwMCYlMDH+EgFw/pABcH7ag1cAAAAAAQAVAAACwwLIABEAhUuwKVBYQCIAAgIIXwAICBpNBgEEBANfBwEDAxxNAAAAAV8FAQEBGwFOG0uwL1BYQCAACAACAwgCZwYBBAQDXwcBAwMcTQAAAAFfBQEBARsBThtAIAAIAAIDCAJnBgEEBANfBwEDAxxNAAAAAV8FAQEBHQFOWVlADBEREREREREREAkHHyslMxUjESMVMxUjESMRIzUzNSECc1DtzXp6nVdXAgeFhQJGWnz+kAFwftoAAAAAAwAnANkBmQLCAA4AGgAeAMVLsCdQWEAKBwEFAAwBAgQCTBtACgcBBQEMAQIEAkxZS7AiUFhAJAEBAAkBBQQABWkABAgDAgIGBAJpAAYHBwZXAAYGB18ABwYHTxtLsCdQWEApCQEFBAAFWQEBAAACAwACZwAECAEDBgQDaQAGBwcGVwAGBgdfAAcGB08bQCoAAAkBBQQABWkAAQACAwECZwAECAEDBgQDaQAGBwcGVwAGBgdfAAcGB09ZWUAYDw8AAB4dHBsPGg8ZFRMADgANERIkCgsZKxImNTQ2MzIXNzMRIycGIyYGFRQWMzI2NTQmIwMhFSF8VVVIRicFYmIFJ0YIJiYfHyYmH6ABXv6iAWxcT09cLSf+tyUs8icgICcnICAn/txhAAADACcA2QGQAsIACwAXABsAO0A4AAAAAgMAAmkHAQMGAQEEAwFpAAQFBQRXAAQEBV8ABQQFTwwMAAAbGhkYDBcMFhIQAAsACiQICxcrEiY1NDYzMhYVFAYjNjY1NCYjIgYVFBYzByEVIYdgYFRUYWFUICUlIB8mJh+rAVf+qQFsW1BQW1xPT1xkJiEhJiYhISaWYQD////5AAADGgK8AAIAAwAAAAIATAAAAq4CvAAMABQAhEuwLVBYQB8GAQMABAUDBGcAAgIBXwABARpNBwEFBQBfAAAAGwBOG0uwL1BYQB0AAQACAwECZwYBAwAEBQMEZwcBBQUAXwAAABsAThtAHQABAAIDAQJnBgEDAAQFAwRnBwEFBQBfAAAAHQBOWVlAFA0NAAANFA0TEhAADAALEREkCAcZKwAWFRQGIyERIRUhFTMSNjU0IyMVMwIohod+/qMCI/59vTUyY8HBAbVwaWxwAryNev7WKihRowAA//8ATAAAAq8CvAACAA8AAAABAEwAAAItArwABQBRS7AtUFhAEQAAAAJfAwECAhpNAAEBGwFOG0uwL1BYQA8DAQIAAAECAGcAAQEbAU4bQA8DAQIAAAECAGcAAQEdAU5ZWUALAAAABQAFEREEBxgrARUhESMRAi3+w6QCvI/90wK8AAAA//8ATAAAAi0DiwAiAW0AAAADAxcB8AAAAAEATAAAAi0DWAAHAHdLsAlQWEAWAAADAwBwAAEBA18AAwMaTQACAhsCThtLsC1QWEAVAAADAIUAAQEDXwADAxpNAAICGwJOG0uwL1BYQBMAAAMAhQADAAECAwFoAAICGwJOG0ATAAADAIUAAwABAgMBaAACAh0CTllZWbYREREQBAcaKwEzESERIxEhAZSZ/sOkAUgDWP7X/dECvAAAAAACAAz/cAM6ArwADgAVAKlLsBVQWEAeAgEAAwBTAAcHBF8ABAQaTQYIBQMDAwFfAAEBGwFOG0uwLVBYQB8IBQIDAgEAAwBjAAcHBF8ABAQaTQAGBgFfAAEBGwFOG0uwL1BYQB0ABAAHAwQHZwgFAgMCAQADAGMABgYBXwABARsBThtAHQAEAAcDBAdnCAUCAwIBAAMAYwAGBgFfAAEBHQFOWVlZQBIAABUUExIADgAOFBEREREJBxsrJREjNSEVIxEzNjY3EyERJQYGByERIwM6m/4Im1EmIQUSAg/+gAQcGQEX1ZT+3JCQASQgZWgBO/3Y3VdtJAGf//8ATAAAAm0CvAACABoAAP//AEwAAAJtA4sAIgFxAAAAAwMWAdEAAP//AEwAAAJtA5sAIgFxAAAAAwMUAlsAAAAB//IAAAQBArwAEQBaQAsRDgsIBQIGAAMBTEuwLVBYQA8FBAIDAxpNAgECAAAbAE4bS7AvUFhADwUEAgMDAF8CAQIAABsAThtADwUEAgMDAF8CAQIAAB0ATllZQAkSEhISEhAGBxwrISMDESMRAyMBATMTETMREzMBBAHM7J/szAEt/uzG2Z/Zxf7qARr+5gEa/uYBZAFY/uwBFP7sART+qwAAAAEAEP/vAlkCzQApAItAFh8BBAUeAQMEKQECAwoBAQIJAQABBUxLsC1QWEAdAAMAAgEDAmcABAQFYQAFBR9NAAEBAGEAAAAgAE4bS7AvUFhAGwAFAAQDBQRpAAMAAgEDAmcAAQEAYQAAACAAThtAGwAFAAQDBQRpAAMAAgEDAmcAAQEAYQAAACIATllZQAkkJCEkJSUGBxwrABYVFAYGIyImJzcWFjMyNjU0JiMjNTMyNjU0JiMiByc2NjMyFhYVFAYHAiA5RYBXVZ85TjVpOz5GOjGenCoxPTdpYE45lVJOd0EtKQFVWTtAXjQ4MXEnJS4oJSuCKSMmLERrLzQzXDwzTxUAAQBMAAACvQK8AAsATLYLBQIBAAFMS7AtUFhADQMBAAAaTQIBAQEbAU4bS7AvUFhADQMBAAABXwIBAQEbAU4bQA0DAQAAAV8CAQEBHQFOWVm2ERMREAQHGisBMxEjNTcBIxEzFQcCKZSjA/7ElaMCArz9RPTA/kwCvPi+//8ATAAAAr0DowAiAXYAAAADAysCngAA//8ATAAAAr0DiwAiAXYAAAADAxYB/QAA//8ATAAAAroCvAACADsAAP//AEwAAAK6A4sAIgF5AAAAAwMXAgAAAAABABL/9ALIArwADwBdQAoKAQABAUwJAQBJS7AtUFhAEQABAQJfAwECAhpNAAAAGwBOG0uwL1BYQA8DAQIAAQACAWcAAAAbAE4bQA8DAQIAAQACAWcAAAAdAE5ZWUALAAAADwAPEREEBxgrAREjESMHDgIHJz4CNxMCyKPgCgZDb1IfMDYfBRICvP1EAibOd5JLEJQLLF9XAUcAAP//AEwAAANQArwAAgBDAAD//wBMAAACvAK8AAIAKgAA//8AJP/vAxYCzQACAEoAAAABAEwAAALCArwABwBMS7AtUFhAEQACAgBfAAAAGk0DAQEBGwFOG0uwL1BYQA8AAAACAQACZwMBAQEbAU4bQA8AAAACAQACZwMBAQEdAU5ZWbYREREQBAcaKxMhESMRIREjTAJ2qf7dqgK8/UQCJf3bAAAA//8ATAAAAqcCvAACAFYAAP//ACT/8AKuAswAAgAQAAD//wAQAAACXwK8AAIAZAAAAAEAB//vAtgCvAAUAGdADBIOCQMBAggBAAECTEuwLVBYQBIEAwICAhpNAAEBAGIAAAAgAE4bS7AvUFhAEgQDAgIBAoUAAQEAYgAAACAAThtAEgQDAgIBAoUAAQEAYgAAACIATllZQAwAAAAUABQTJCQFBxkrAQEOAiMiJic3FjMyNzcBMxcXNzcC2P71I0JPOChIGzgeIDcdBv7hwG9EQmQCvP3rR08iERB/DzUKAf3PjY3P//8AB//vAtgDowAiAYMAAAADAysCiAAAAAMAJP/XA2oC5wAVABwAIwB0S7APUFhAKwAEAwMEcAABAAABcQUBAwgBBwYDB2oKCQIGAAAGWQoJAgYGAGECAQAGAFEbQCkABAMEhQABAAGGBQEDCAEHBgMHagoJAgYAAAZZCgkCBgYAYQIBAAYAUVlAEh0dHSMdIxcRFRERFhEREgsHHysABgYHFSM1LgI1NDY2NzUzFR4CFQQWFxEGBhUENjU0JicRA2pSmGekZ5hSUphnpGeYUv1WYllVZgGrY2ZWAQeKTAJYWAJMilxaiEwBVVUBTIhaUFoBAVMBW0yqWlBMWwH+rf////4AAAK4ArwAAgB6AAAAAQA5AAACkwK8ABEAarUDAQEDAUxLsC1QWEAVAAMAAQADAWoFBAICAhpNAAAAGwBOG0uwL1BYQBUAAwABAAMBagUEAgICAF8AAAAbAE4bQBUAAwABAAMBagUEAgICAF8AAAAdAE5ZWUANAAAAEQARIhMiEQYHGisBESM1BiMiJjU1MxUUMzI2NTUCk6RKZICIo4VFSQK8/UT0L5aL1sucSkXYAAABAEz/cAMrArwACwBlS7AtUFhAFwABAAFUBQEDAxpNBAEAAAJgAAICGwJOG0uwL1BYQBcFAQMAA4UAAQABVAQBAAACYAACAhsCThtAFwUBAwADhQABAAFUBAEAAAJgAAICHQJOWVlACREREREREAYHHCslMxEjNSERMxEhETMCvG+b/byjASuilP7ckAK8/dgCKAAAAQBMAAAEKgK8AAsAWUuwLVBYQBMEAgIAABpNBQEDAwFgAAEBGwFOG0uwL1BYQBMEAgIAAwCFBQEDAwFgAAEBGwFOG0ATBAICAAMAhQUBAwMBYAABAR0BTllZQAkRERERERAGBxwrATMRIREzETMRMxEzA4mh/CKi/p/+Arz9RAK8/dgCKP3YAAEATP9wBJgCvAAPAG1LsC1QWEAZAAEAAVQHBQIDAxpNBgQCAAACYAACAhsCThtLsC9QWEAZBwUCAwADhQABAAFUBgQCAAACYAACAhsCThtAGQcFAgMAA4UAAQABVAYEAgAAAmAAAgIdAk5ZWUALERERERERERAIBx4rJTMRIzUhETMRMxEzETMRMwQqbpv8T6L+n/6hlP7ckAK8/dgCKP3YAigAAQBM/3ACvAK8AAsAj0uwCVBYQBkAAQAAAXEGBQIDAxpNAAQEAGACAQAAGwBOG0uwLVBYQBgAAQABhgYFAgMDGk0ABAQAYAIBAAAbAE4bS7AvUFhAGAYFAgMEA4UAAQABhgAEBABgAgEAABsAThtAGAYFAgMEA4UAAQABhgAEBABgAgEAAB0ATllZWUAOAAAACwALEREREREHBxsrAREjFSM1IxEzESERArzonuqkASkCvP1EkJACvP3YAigAAAAAAgBMAAACqAK8AAoAEwB+S7AtUFhAHAABARpNAAMDAl8FAQICHE0GAQQEAGAAAAAbAE4bS7AvUFhAHAABAgGFAAMDAl8FAQICHE0GAQQEAGAAAAAbAE4bQBwAAQIBhQADAwJfBQECAhxNBgEEBABgAAAAHQBOWVlAEwsLAAALEwsSEQ8ACgAJESQHBxgrABYVFAYjIREzFTMSNjU0JiMjFTMCHIyPhP63pKouPT06n58B5nxzdoECvNb+qzQvLzPFAAAAAAIAEAAAAxwCvAAMABUAikuwLVBYQCEAAQECXwACAhpNAAQEA18GAQMDHE0HAQUFAF8AAAAbAE4bS7AvUFhAHwACAAEDAgFnAAQEA18GAQMDHE0HAQUFAF8AAAAbAE4bQB8AAgABAwIBZwAEBANfBgEDAxxNBwEFBQBfAAAAHQBOWVlAFA0NAAANFQ0UExEADAALEREkCAcZKwAWFRQGIyERIzUhFTMSNjU0JiMjFTMCj42QhP64sAFTqi49PTqfnwHmfHN2gQIvjdb+qzQvLzPFAAD//wBMAAADmQK8ACIBjAAAAAMALQKpAAAAAgAS//QEaAK8ABYAHwCWQAoOAQAFAUwNAQBJS7AtUFhAIQABAQJfAAICGk0ABAQDXwYBAwMcTQcBBQUAXwAAABsAThtLsC9QWEAfAAIAAQMCAWcABAQDXwYBAwMcTQcBBQUAXwAAABsAThtAHwACAAEDAgFnAAQEA18GAQMDHE0HAQUFAF8AAAAdAE5ZWUAUFxcAABcfFx4dGwAWABUbESQIBxkrABYVFAYjIREjBw4CByc+AjcTIRUzEjY1NCYjIxUzA9yMj4T+xNQKBkNvUh8wNh8FEgIPnS49PTqSkgHmfHN2gQImzneSSxCUCyxfVwFH1v6rNC8vM8UAAgBMAAAERwK8ABIAGwD5S7APUFhAHgkGAgQHAQEIBAFnBQEDAxpNCgEICABgAgEAABsAThtLsBVQWEAjAAcBBAdXCQYCBAABCAQBZwUBAwMaTQoBCAgAYAIBAAAbAE4bS7AtUFhAJAkBBgAHAQYHZwAEAAEIBAFnBQEDAxpNCgEICABgAgEAABsAThtLsC9QWEAqCQEGAAcBBgdnAAQAAQgEAWcFAQMDAF8CAQAAG00KAQgIAGACAQAAGwBOG0AqCQEGAAcBBgdnAAQAAQgEAWcFAQMDAF8CAQAAHU0KAQgIAGACAQAAHQBOWVlZWUAXExMAABMbExoZFwASABERERERESQLBxwrABYVFAYjIREhESMRMxUhNTMVMxI2NTQmIyMVMwO9io18/sT+7qSkARKhoCk4ODWUlAHQdm1wfQEw/tACvPj47P7BLSwrK6///wAg//ACdgLMAAIAXQAAAAEAJP/wAq4CzAAbAINADgwBAgENAQMCGwEFBANMS7AtUFhAHQADAAQFAwRnAAICAWEAAQEfTQAFBQBhAAAAIABOG0uwL1BYQBsAAQACAwECaQADAAQFAwRnAAUFAGEAAAAgAE4bQBsAAQACAwECaQADAAQFAwRnAAUFAGEAAAAiAE5ZWUAJIhESIyYhBgccKyUGIyImJjU0NjYzMhcHJiMiBgchFSEWFjMyNjcCrnGjb6pdXqpunHBmRF1LbxYBK/7SEnFQMloiXW1bpm1splxvYEJRRI1JVyUjAAABABP/8AKcAswAGwCPQBIZAQQFGAEDBAoBAQIJAQABBExLsC1QWEAeAAMAAgEDAmcABAQFYQYBBQUfTQABAQBhAAAAIABOG0uwL1BYQBwGAQUABAMFBGkAAwACAQMCZwABAQBhAAAAIABOG0AcBgEFAAQDBQRpAAMAAgEDAmcAAQEAYQAAACIATllZQA4AAAAbABoiERIkJgcHGysAFhYVFAYGIyInNxYWMzI2NyE1ISYmIyIHJzYzAZSqXl2qb6NwYCJaMlByEv7RASwWb0xdRGZymgLMXKZsbaZbbWgiJldJjURRQmBvAAAA//8ATAAAAPACvAACAC0AAP///9YAAAFnA5sAIgAtAAAAAwMUAZkAAP//ABT/8gKDArwAAgA4AAAAAQAQAAAC/wK8ABYAsLUUAQEGAUxLsCFQWEAbBwEGAAEABgFpBQEDAwRfAAQEGk0CAQAAGwBOG0uwLVBYQCEABQQDAwVyBwEGAAEABgFpAAMDBGAABAQaTQIBAAAbAE4bS7AvUFhAHwAFBAMDBXIABAADBgQDZwcBBgABAAYBaQIBAAAbAE4bQB8ABQQDAwVyAAQAAwYEA2cHAQYAAQAGAWkCAQAAHQBOWVlZQA8AAAAWABURERETIxMIBxwrABYVFSM1NCYjIgYVFSMRIzUhFSMVNjMCjXKkNTEvPKPXAk/VP1oB0Xlw6OcwNT8x3AIwjIWdNwAAAAACAEz/7wQ8As0AFgAmAM5LsA9QWEAhAAQAAQcEAWcABgYDYQgFAgMDGk0JAQcHAGECAQAAIABOG0uwLVBYQCkABAABBwQBZwADAxpNAAYGBWEIAQUFH00AAgIbTQkBBwcAYQAAACAAThtLsC9QWEAnCAEFAAYEBQZpAAQAAQcEAWcAAwMCXwACAhtNCQEHBwBhAAAAIABOG0AnCAEFAAYEBQZpAAQAAQcEAWcAAwMCXwACAh1NCQEHBwBhAAAAIgBOWVlZQBYXFwAAFyYXJR8dABYAFRERERMmCgcbKwAWFhUUBgYjIiYmJyMRIxEzETM+AjMSNjY1NCYmIyIGBhUUFhYzAzeoXV2ob2ScYg1opaVqD2OaYT1eNDRePT1eNDRePQLNW6ZubqZbSohb/uQCvP7yWIFG/bU3ZEFBZDc3ZEFBZDcAAAAAAgASAAACjwK8AA4AFwB/tQcBAQQBTEuwLVBYQBsABAABAAQBZwcBBQUDXwYBAwMaTQIBAAAbAE4bS7AvUFhAGQYBAwcBBQQDBWcABAABAAQBZwIBAAAbAE4bQBkGAQMHAQUEAwVnAAQAAQAEAWcCAQAAHQBOWVlAFA8PAAAPFw8WFRMADgANERERCAcZKwERIzUjByM3JiY1NDY2MwYGFRQWMzM1IwKPpGmvwcJKUUF1TCU6OjWhoQK8/UTn5/kZcE1GazyMNC8vNMYAAQAQ//ADEwK8ABoAtEAOGAEABQYBAQACTAUBAUlLsCFQWEAaBgEFAAABBQBpBAECAgNfAAMDGk0AAQEbAU4bS7AtUFhAIAACBAUEAnIGAQUAAAEFAGkABAQDXwADAxpNAAEBGwFOG0uwL1BYQB4AAgQFBAJyAAMABAIDBGcGAQUAAAEFAGkAAQEbAU4bQB4AAgQFBAJyAAMABAIDBGcGAQUAAAEFAGkAAQEdAU5ZWVlADgAAABoAGRERERMrBwcbKwAWFRQGByc2NjU0JiMiBhUVIxEjNSEVIxU2MwKcd4F5HTc5OTE3QaTWAk/VQ2QB0XZrc4MKiAc3Ly41PTTXAi6Oh5s3AAD////iAAAD1wK8AAIADQAAAAIAFv9wA0wCvAALAA4AjUuwIVBYQBgDAQEAAVQABQUaTQYEAgAAAmAAAgIbAk4bS7AtUFhAGQQBAAMBAQABYwAFBRpNAAYGAmAAAgIbAk4bS7AvUFhAGQAFAAWFBAEAAwEBAAFjAAYGAmAAAgIbAk4bQBkABQAFhQQBAAMBAQABYwAGBgJgAAICHQJOWVlZQAoSEREREREQBwcdKyUzESM1IRUjETMTMwcDIQLyWpv+AJtZ7apXmgE0lP7ckJABJAIop/54AAAAAf/5AAADAAK8AAcAULUDAQACAUxLsC1QWEANAwECAhpNAQEAABsAThtLsC9QWEANAwECAAKFAQEAABsAThtADQMBAgAChQEBAAAdAE5ZWUALAAAABwAHExEEBxgrAQEjAwcDIwEB1AEstc9GirMBLAK8/UQCCLD+qAK8AAMAJP+eA58DGAARABgAHwDAS7ANUFhAJgAEAwMEcAABAAABcQgBBwcDYQUBAwMaTQoJAgYGAGECAQAAGwBOG0uwLVBYQCQABAMEhQABAAGGCAEHBwNhBQEDAxpNCgkCBgYAYQIBAAAbAE4bS7AvUFhAIgAEAwSFAAEAAYYFAQMIAQcGAwdqCgkCBgYAYQIBAAAbAE4bQCIABAMEhQABAAGGBQEDCAEHBgMHagoJAgYGAGECAQAAHQBOWVlZQBIZGRkfGR8XERQRERQRERELBx8rJAYHFSM1JiY1NDY3NTMVFhYVBBYXEQYGFQQ2NTQmJxEDn8Cso6zAwKyjrMD9I21oaG0B0m1taL26B15eB7qhoboHWFgHuqFmcAQBtQVvZ9ZwZmdvBf5LAAAAAAIADP9wAzoCvAALAA8Ap0uwFVBYQB4DAQEAAVMABgYFXwAFBRpNCAcEAwAAAl8AAgIbAk4bS7AtUFhAHwQBAAMBAQABYwAGBgVfAAUFGk0IAQcHAl8AAgIbAk4bS7AvUFhAHQAFAAYABQZnBAEAAwEBAAFjCAEHBwJfAAICGwJOG0AdAAUABgAFBmcEAQADAQEAAWMIAQcHAl8AAgIdAk5ZWVlAEAwMDA8MDxIRERERERAJBx0rJTMRIzUhFSMRMxMhAxEjAwLLb5v+CJttSgIIo9I3lP7ckJABJAIo/c0Bnf5jAAEAEgAAArgCvAAJAFxLsC1QWEAWAAICAF8AAAAaTQAEBAFfAwEBARsBThtLsC9QWEAUAAAAAgQAAmcABAQBXwMBAQEbAU4bQBQAAAACBAACZwAEBAFfAwEBAR0BTllZtxEREREQBQcbKxMhESMRIwMjNTOpAg+j2D/sWwK8/UQCJv3akAAAAAABADkAAAKLArwADgBjS7AtUFhAFQADAAEAAwFoBQQCAgIaTQAAABsAThtLsC9QWEAVAAMAAQADAWgFBAICAgBfAAAAGwBOG0AVAAMAAQADAWgFBAICAgBfAAAAHQBOWVlADQAAAA4ADiITIREGBxorAREjNSMiJjU1MxUUMzMRAoukpoCIo4WGArz9RNeWi8S5mwFUAAAAAAIAEgAABFgCvAAQABkAkkuwLVBYQCMAAQEEXwAEBBpNAAYGBV8IAQUFHE0JBwIDAwBfAgEAABsAThtLsC9QWEAhAAQAAQUEAWcABgYFXwgBBQUcTQkHAgMDAF8CAQAAGwBOG0AhAAQAAQUEAWcABgYFXwgBBQUcTQkHAgMDAF8CAQAAHQBOWVlAFhERAAARGREYFxUAEAAPERERESQKBxsrABYVFAYjIREjAyM1MxMhFTMSNjU0JiMjFTMDy42Qg/7EzD/sWzwCBJwuPTw6k5MB5nxzdoECJv3akAIs1v6rNC8vM8UAAP//ABb/cANMArwAAgGcAAD////5AAADAAK8AAIBnQAA//8AJP+eA58DGAACAZ4AAP//ABb/cANMArwAAgGcAAD////5AAADAAK8AAIBnQAA//8AJP+eA58DGAACAZ4AAP//AB//9gJBAfgAAgCFAAAAAgAg//UCPwLvABkAJQBZQAsWAQIBAUwQDwIBSkuwIVBYQBcAAgIBYQQBAQEcTQUBAwMAYQAAACIAThtAFQQBAQACAwECaQUBAwMAYQAAACIATllAEhoaAAAaJRokIB4AGQAYJAYHFysAFhUUBiMiJjU1NDY3NjY3FwYGBwYGBzY2MxI2NTQmIyIGFRQWMwHCfZJ9gJCglz48JT4pUkRdWAoaUjAWPT02Nj09NgHfgGt2iaKcFKC/FwoTFXchHAgLQUMcH/6YQDY2Pz82NkAAAAMAOwAAAhAB7gAOABcAHgBftQ4BBAMBTEuwL1BYQB4AAwAEBQMEZwACAgFfAAEBHE0GAQUFAF8AAAAbAE4bQB4AAwAEBQMEZwACAgFfAAEBHE0GAQUFAF8AAAAdAE5ZQA4YGBgeGB0lISchJAcHGyskFhUUBiMhESEyFhUUBgcmJiMjFTMyNjUWNTQjIxUzAecpX1L+3AEiS1kgHV8YFmVlFhgONG1t7z4lQUsB7kg8JjgObBZPFRLnKilTAAAAAAEAOwAAAbEB7gAFADNLsC9QWEAQAAEBAF8AAAAcTQACAhsCThtAEAABAQBfAAAAHE0AAgIdAk5ZtREREAMHGSsTIRUjESM7AXbanAHuh/6ZAAAA//8AOwAAAbECvAAiAawAAAADAvsBqwAAAAEAOwAAAbECWAAHAF1LsAtQWEAWAAADAwBwAAEBA18AAwMcTQACAhsCThtLsC9QWEAVAAADAIUAAQEDXwADAxxNAAICGwJOG0AVAAADAIUAAQEDXwADAxxNAAICHQJOWVm2EREREAQHGisBMxUjESMRMwEpiNqc7gJY8f6ZAe4AAgAN/4QCZQHuAA4AFQBjtQ8BAwcBTEuwL1BYQB4CAQADAFMABwcEXwAEBBxNBggFAwMDAV8AAQEbAU4bQB4CAQADAFMABwcEXwAEBBxNBggFAwMDAV8AAQEdAU5ZQBIAABUUExIADgAOFBEREREJBxsrJREjNSEVIxEzNjY3NyERJQYGBzM1IwJllP7RlTQTEgUUAZ7+5QMQD6J4h/79fHwBAxc5Od7+mYIwPhjqAP//AB//9AIvAfkAAgCcAAD//wAf//QCLwK8ACIBsAAAAAMC+gInAAD//wAf//QCLwLFACIBsAAAAAMC+AIlAAAAAf/3AAADIwHuABEAQkALEQ4LCAUCBgADAUxLsC9QWEAPBQQCAwMcTQIBAgAAGwBOG0APBQQCAwMcTQIBAgAAHQBOWUAJEhISEhIQBgccKyEjJxUjNQcjNyczFzUzFTczBwMju4+YlbW+o7B/mH6uocjIyMj88sDAv7/rAAEAFf/vAc0B/wAmAGlAFh4BBAUdAQMEJgECAwkBAQIIAQABBUxLsC9QWEAdAAMAAgEDAmcABAQFYQAFBSFNAAEBAGEAAAAgAE4bQB0AAwACAQMCZwAEBAVhAAUFIU0AAQEAYQAAACIATllACSQkISMlJAYHHCskFhUUBiMiJic3FhYzMjU0JiMjNTMyNjU0JiMiBgcnNjMyFhUUBgcBoyp4Z0F0JD4lQylNHBpkVhwdIiAhPyQ8YHReaCIe8T8oSFMmIGgZFS8SFG4UExQWFBVlQE1DJTkPAAEAOwAAAioB7gALADa2CwUCAQABTEuwL1BYQA0DAQAAHE0CAQEBGwFOG0ANAwEAABxNAgEBAR0BTlm2ERMREAQHGisBMxEjNTcHIxEzFQcBooidAsuJnAIB7v4SnF/7Ae6dX///ADsAAAIqAskAIgG1AAAAAwMqAnkAAP//ADsAAAIqArwAIgG1AAAAAwL6Ai8AAAABADsAAAIwAe4ACgA3twoHAgMAAgFMS7AvUFhADQMBAgIcTQEBAAAbAE4bQA0DAQICHE0BAQAAHQBOWbYSERIQBAcaKyEjJxUjETMVNzMHAjDCl5ycibOwwsIB7rq66v//ADsAAAIwArwAIgG4AAAAAwL7AcAAAAABABb/9wIqAe4ADwBHQAoKAQABAUwJAQBJS7AvUFhAEQABAQJfAwECAhxNAAAAGwBOG0ARAAEBAl8DAQICHE0AAAAdAE5ZQAsAAAAPAA8REQQHGCsBESMRIwcOAgcnPgI3NwIqnH0IBy9bSxcfIxMFEwHu/hIBZ2lXbDoKhQYbPDjdAAABADsAAAKXAe4ADABItwwHBAMCAAFMS7AvUFhAFQACAAEAAgGABAEAABxNAwEBARsBThtAFQACAAEAAgGABAEAABxNAwEBAR0BTlm3ERISERAFBxsrATMRIxEHIycRIxEzFwIDlJqIF4malJsB7v4SAQujpP70Ae68AAAAAQA7AAACKwHuAAsAQUuwL1BYQBUABQACAQUCZwQBAAAcTQMBAQEbAU4bQBUABQACAQUCZwQBAAAcTQMBAQEdAU5ZQAkRERERERAGBxwrATMRIzUjFSMRMxUzAY6dnbadnbYB7v4SuroB7q3//wAf//UCPgH5AAIA0AAAAAEAOwAAAisB7gAHADZLsC9QWEARAAICAF8AAAAcTQMBAQEbAU4bQBEAAgIAXwAAABxNAwEBAR0BTlm2EREREAQHGisTIREjESMRIzsB8J22nQHu/hIBZ/6ZAAD//wA7/yoCXgH4AAIA3AAA//8AH//1AfYB+QACAJIAAAABABYAAAHgAe4ABwA+S7AvUFhAEgIBAAADXwQBAwMcTQABARsBThtAEgIBAAADXwQBAwMcTQABAR0BTllADAAAAAcABxEREQUHGSsBFSMRIxEjNQHgl5yXAe6H/pkBZ4cAAAD//wAC/yoCPQHuAAIBAgAA//8AAv8qAj0CyQAiAcIAAAADAyoCZQAAAAMAH/8kAugCvAAVAB4AJgBoS7AtUFhAJAAEBBpNCAEHBwNhBQEDAyFNCgkCBgYAYQIBAAAiTQABAR4BThtAJAAEAwSFCAEHBwNhBQEDAyFNCgkCBgYAYQIBAAAiTQABAR4BTllAEh8fHyYfJhciFRERFhEREgsHHyskBgYHFSM1LgI1NDY2NzUzFR4CFQQWMzMRIyIGFQQ2NTQmIyMRAuhEflScVX5ERX5UnFR+RP3RRzwBATxHAU5HRzwBqnRBAdDQAUB1TU10QAHDwwFBc008RgEDRjuCRjw7Rv79AAD//wADAAACIgHuAAIBAQAAAAEAJgAAAgAB7gASAEy1AwEBAwFMS7AvUFhAFQADAAEAAwFqBQQCAgIcTQAAABsAThtAFQADAAEAAwFqBQQCAgIcTQAAAB0ATllADQAAABIAEiMTIhEGBxorAREjNQYjIiY1NTMVFBYzMjY1NQIAmDhHW2iXKispLQHu/hKjIm5inYwzMi8rlwABADv/hAJ0Ae4ACwBFS7AvUFhAFwABAAFUBQEDAxxNBAEAAAJgAAICGwJOG0AXAAEAAVQFAQMDHE0EAQAAAmAAAgIdAk5ZQAkRERERERAGBxwrJTMRIzUhETMRMxEzAitJlf5cnbadh/79fAHu/pkBZwAAAAEAOwAAAxUB7gALAD1LsC9QWEATBAICAAAcTQUBAwMBYAABARsBThtAEwQCAgAAHE0FAQMDAWAAAQEdAU5ZQAkRERERERAGBxwrATMRIREzETMRMxEzAnyZ/SaYi5SKAe7+EgHu/pkBZ/6ZAAEAO/+EA10B7gAPAEtLsC9QWEAZAAEAAVQHBQIDAxxNBgQCAAACYAACAhsCThtAGQABAAFUBwUCAwMcTQYEAgAAAmAAAgIdAk5ZQAsREREREREREAgHHislMxEjNSERMxEzETMRMxEzAxVIlf1zmIuUipmH/v18Ae7+mQFn/pkBZwAAAAEAO/+EAioB7gALAG5LsAtQWEAZAAEAAAFxBgUCAwMcTQAEBABgAgEAABsAThtLsC9QWEAYAAEAAYYGBQIDAxxNAAQEAGACAQAAGwBOG0AYAAEAAYYGBQIDAxxNAAQEAGACAQAAHQBOWVlADgAAAAsACxERERERBwcbKwERIxUjNSMRMxEzEQIqrZWtnLYB7v4SfHwB7v6ZAWcAAAIAOwAAAgQB7gAKABMAVUuwL1BYQBoFAQIAAwQCA2gAAQEcTQYBBAQAXwAAABsAThtAGgUBAgADBAIDaAABARxNBgEEBABfAAAAHQBOWUATCwsAAAsTCxIRDwAKAAkRJAcHGCsAFhUUBiMhETMVMxY2NTQmIyMVMwGeZmVX/vOccQEhIB5ZWQFmYFJXXQHuiOseHBodcQAAAgATAAACZAHuAAwAFQBgS7AvUFhAHwYBAwAEBQMEZwABAQJfAAICHE0HAQUFAF8AAAAbAE4bQB8GAQMABAUDBGcAAQECXwACAhxNBwEFBQBfAAAAHQBOWUAUDQ0AAA0VDRQTEQAMAAsRESQIBxkrABYVFAYjIREjNSEVMxY2NTQmIyMVMwH+ZmVX/vOIASRxASEgHllZAWZgUlddAWmFiOseHBodcQD//wA7AAAC9wHuACIBywAAAAMAsAIfAAAAAgAW//cDUgHuABYAHwBsQAoOAQUEAUwNAQBJS7AvUFhAHwYBAwAEBQMEZwABAQJfAAICHE0HAQUFAF8AAAAbAE4bQB8GAQMABAUDBGcAAQECXwACAhxNBwEFBQBfAAAAHQBOWUAUFxcAABcfFx4dGwAWABUbESQIBxkrABYVFAYjIREjBw4CByc+Ajc3IRUzBjY1NCYjIxUzAuxmY1n+9XoIBy9bSxcfIxMFEwGgcwIhIR5WVgFmYVFWXgFnaVdsOgqFBhs8ON2I6x0cGh1wAAIAOwAAA0cB7gASABsAwEuwDVBYQB4JBgIEBwEBCAQBaAUBAwMcTQoBCAgAXwIBAAAbAE4bS7AdUFhAIwAHAQQHWAkGAgQAAQgEAWgFAQMDHE0KAQgIAF8CAQAAGwBOG0uwL1BYQCQJAQYABwEGB2gABAABCAQBZwUBAwMcTQoBCAgAXwIBAAAbAE4bQCQJAQYABwEGB2gABAABCAQBZwUBAwMcTQoBCAgAXwIBAAAdAE5ZWVlAFxMTAAATGxMaGRcAEgAREREREREkCwccKwAWFRQGIyE1IxUjETMVMzUzFTMGNjU0JiMjFTMC4WZkWP76rpycrpxqAiEgHk9PAWBgT1Zb0dEB7paWjuUdGRgbaQAA//8AF//zAeEB+wACAOMAAAABAB//9QH4AfkAHAA3QDQNAQIBDgEDAhwBBQQDTAADAAQFAwRnAAICAWEAAQEhTQAFBQBhAAAAIgBOIhESJCYhBgccKyUGIyImJjU0NjYzMhYXByYjIgYHMxUjFhYzMjY3AfhVdlF7QkR7UTdiJ1MpPyk+D660DkEtIjgUR1I/dE5NdUEnJlkpJCBzJywYFwABABD/9QHoAfkAGwBBQD4YAQQFFwEDBAoBAQIJAQABBEwAAwACAQMCZwAEBAVhBgEFBSFNAAEBAGEAAAAiAE4AAAAbABoiERIjJgcHGysAFhYVFAYGIyInNxYzMjY3IzUzJiYjIgcnNjYzASl7REJ7UXVVUTBCLUEOs60PPik9LFEnYTcB+UF1TU50P1JYLSwncyAkJ1cmJwAAAP//AC4AAADmAsoAAgCvAAD////TAAABPwLFACIAsAAAAAMDIAF+AAD///+1/xMA6ALKAAIAuwAA//8AAgAAAjUCvAACAK0AAAACADv/9QMuAfkAFAAgAKBLsBVQWEAhAAQAAQcEAWcABgYDYQgFAgMDHE0JAQcHAGECAQAAIgBOG0uwL1BYQCkABAABBwQBZwADAxxNAAYGBWEIAQUFIU0AAgIbTQkBBwcAYQAAACIAThtAKQAEAAEHBAFnAAMDHE0ABgYFYQgBBQUhTQACAh1NCQEHBwBhAAAAIgBOWVlAFhUVAAAVIBUfGxkAFAATEREREiYKBxsrABYWFRQGBiMiJicjFSMRMxUzNjYzEjY1NCYjIgYVFBYzAnR5QUF5UGWIEU+cnFEUh2AzPDwyMT4+MQH5QXRNTXRBa1u7Ae6wVmX+gUY3N0ZHNjZHAAIAFAAAAfYB7gANABYAX7UHAQEEAUxLsC9QWEAbAAQAAQAEAWcHAQUFA18GAQMDHE0CAQAAGwBOG0AbAAQAAQAEAWcHAQUFA18GAQMDHE0CAQAAHQBOWUAUDg4AAA4WDhUUEgANAAwREREIBxkrAREjNSMHIzcmJjU0NjMGBhUUFjMzNSMB9pw7Yql3LTJrVQceHx1aWgHu/hKOjqQWTzRRYH8fFhceagAAAAABAAL/HwI1ArwAJACxQA4iAQIJCQEBAwgBAAEDTEuwLVBYQCoHAQUIAQQJBQRnAAYGGk0AAgIJYQoBCQkhTQADAxtNAAEBAGEAAAAeAE4bS7AvUFhAJwcBBQgBBAkFBGcAAQAAAQBlAAICCWEKAQkJIU0ABgYDXwADAxsDThtAJwcBBQgBBAkFBGcAAQAAAQBlAAICCWEKAQkJIU0ABgYDXwADAx0DTllZQBIAAAAkACMRERERERMlIyULBx8rABYVERQGIyInNxYzMjY1ETQmIyIGFREjESM1MzUzFTMVIxU2MwHGb11ROj0lGhYbGDMnLDqdOTmdcXE4WwH5c3f+2GFnIHAOJCQBJTI0PTT+/QIoXDg4XGo7AAAA//8AH//2A7gB+AACAI8AAAADACz/9AIzAs0AFQAgAC0AakALGRUCAwIpAQQDAkxLsC1QWEAfAAMCBAIDBIAFAQICAWEAAQEfTQYBBAQAYQAAACIAThtAHQADAgQCAwSAAAEFAQIDAQJpBgEEBABhAAAAIgBOWUATISEWFiEtISwnJRYgFh8mJQcHGCsAFhUUBgYjIiY1NTQ2NjMyFhYVFAYHJgYVFTc2NjU0JiMSNjU0JiMiBwcVFBYzAgAzQXVLfIpBeFBFaTooJdA4YS4vLiYtOC4sFRNNODIBZ1c6Q2Y5kYK9UHhBMFY4LkgYzUA4PBQKLSMgJv4nNy4rMAQQMjpAAAAAAQAa//MB5AH5ACQAdkAPDgEAASANAgIAIQEDAgNMS7ALUFhAFgAAAAFhAAEBIU0AAgIDYQQBAwMiA04bS7ANUFhAFgAAAAFhAAEBIU0AAgIDYQQBAwMgA04bQBYAAAABYQABASFNAAICA2EEAQMDIgNOWVlADAAAACQAIyolKQUHGSsWJjU0NzY2NTQmIyIGByc2NjMyFhUUBgcGBhUUFjMyNjcXBgYjknjPKSQgHyJOJTYrZjZmd2RiLyciIC1fJjwtfEINVUqLFAQUEhASERBrFxtTSEJPCQQWEhMTGhZrICT//wAf/wsCQAH4AAIBGAAAAAH/9wAAAyQCvAARAHRACxEOCwgFAgYAAwFMS7AtUFhAEwAEBBpNBQEDAxxNAgECAAAbAE4bS7AvUFhAGgAEBABfAgECAAAbTQUBAwMcTQIBAgAAGwBOG0AaAAQEAF8CAQIAAB1NBQEDAxxNAgECAAAdAE5ZWUAJEhISEhIQBgccKyEjJxUjNQcjNyczFxEzETczBwMkvI+Xlba+oa6Al3+uosnJyMj788ABjv5ywOsAAQAT/xkB/wH+ACkAZkAWIAEEBR8BAwQpAQIDCgEBAgkBAAEFTEuwHVBYQB0AAwACAQMCZwAEBAVhAAUFIU0AAQEAYQAAAB4AThtAGgADAAIBAwJnAAEAAAEAZQAEBAVhAAUFIQROWUAJJCQhJCUlBgccKyQWFRQGBiMiJic3FhYzMjY1NCYjIzUzMjY1NCYjIgYHJzYzMhYWFRQGBwHKNUJ3TkR5KEUlSSg2PzMudWwqMDUvJEQmPmZ+RGg5Kyd+VjRAZDcoJGwZGDIrKS2DKycmKxcaZlAxWjs0VBgAAP//ADX/9QIrAe4AAgDwAAD//wA1//UCKwLJACIB4AAAAAMDKgJ2AAD//wA1//UCKwK8ACIB4AAAAAMC+gItAAD//wA7AAACMAK8AAIAvwAAAAEAAgAAAj0B7gAIADq1BAEAAgFMS7AvUFhADQMBAgIcTQEBAAAbAE4bQA0DAQICHE0BAQAAHQBOWUALAAAACAAIFBEEBxgrARMjJycHByMTAXDNqT82NUCozQHu/hKkoqKkAe4AAAD//wA7AAACNQH5AAIAyQAA//8AOwAAA18B+QACAMgAAAABADX/hAKEAe4AGwAqQCcJBgICAAFMAAEAAVQFAQMDHE0EAQAAAmIAAgIiAk4TIxMmERIGBxwrJBYWMxUjNSYmJwYGIyImNREzERQWMzI2NREzEQIrECYjjBgfCCJhOV9pnS4nLjmdrycP9Y8IHRctLXlvARH+8jA2PjIBBP7nAAEANf/1A1kB7gAhAHm2CQMCAAQBTEuwFVBYQBYIBwUDAwMcTQYBBAQAYgIBAgAAGwBOG0uwL1BYQBoIBwUDAwMcTQAAABtNBgEEBAFiAgEBASIBThtAGggHBQMDAxxNAAAAHU0GAQQEAWICAQEBIgFOWVlAEAAAACEAISMTIxMjIxEJBx0rAREjJwYGIyImJwYjIiY1ETMRFBYzMjY1ETMRFBYzMjY1EQNZiAkaSSowTBY8bl5snSklKDGcKCUpMQHu/hI3ICIpJE1uYAEr/uksMTguAQ7+6SwxOC4BDgAAAQA1/4QDsgHuACgAMUAuDggGAwIAAUwAAQABVAgGAgQEHE0HBQIAAAJiAwECAiICThMjEyMTIyUREgkHHyskFhYzFSM1JicGBiMiJicGIyImNREzERQWMzI2NREzERQWMzI2NREzEQNZESUjjC8PHlkzMk4WOXBebJ0pJSgxnCglKDKdrycP9Y8NLCotKiZQbmABK/7pLDE4LgEO/uksMTUrART+6AAAAgA1/+8CCAHuAA0AGQBctQsBAwIBTEuwL1BYQBoFAQIAAwQCA2kAAQEcTQYBBAQAYgAAACAAThtAGgUBAgADBAIDaQABARxNBgEEBABiAAAAIgBOWUATDg4AAA4ZDhgUEgANAAwTJAcHGCsAFhUUBiMiJjURMxU2MxI2NTQmIyIGFRQWMwGcbH5ua3ycMEAELy8mJi8vJgGMa11kcXprARqBH/7iLyUlLi4lJi4AAAACAAr/7wJTAe4ADwAbAGe1DQEEAQFMS7AvUFhAHwYBAwAEBQMEaQABAQJfAAICHE0HAQUFAGEAAAAgAE4bQB8GAQMABAUDBGkAAQECXwACAhxNBwEFBQBhAAAAIgBOWUAUEBAAABAbEBoWFAAPAA4REyQIBxkrABYVFAYjIiY1NSM1IRU2MxI2NTQmIyIGFRQWMwHnbH1va3x2ARIwQAQvLyYmLy8mAYxrXWRxemufe4Ef/uIvJSUuLiUmLgAAAAACADv/9QMuArwAFAAgANZLsBVQWEAlAAQAAQcEAWcAAwMaTQAGBgVhCAEFBSFNCQEHBwBhAgEAACIAThtLsC1QWEApAAQAAQcEAWcAAwMaTQAGBgVhCAEFBSFNAAICG00JAQcHAGEAAAAiAE4bS7AvUFhAKQAEAAEHBAFnAAYGBWEIAQUFIU0AAwMCXwACAhtNCQEHBwBhAAAAIgBOG0ApAAQAAQcEAWcABgYFYQgBBQUhTQADAwJfAAICHU0JAQcHAGEAAAAiAE5ZWVlAFhUVAAAVIBUfGxkAFAATEREREiYKBxsrABYWFRQGBiMiJicjFSMRMxEzNjYzEjY1NCYjIgYVFBYzAnR5QUF5UGWIEU+cnFEUh2AzPDwyMT4+MQH5QXRNTXRBa1u7Arz+glZl/oFGNzdGRzY2RwD//wAb//cCAAH5AAIBDAAA//8ANf8LAisB7gACAR0AAP//ADX/CwIrAskAIgHuAAAAAwMqAnYAAP//ABv/9wNZAfkAAgEWAAAAAgA6//UCWQLqABQAIADPtREBBQQBTEuwE1BYQCcAAgEBAnAAAwMBXwABARpNAAUFBGEHAQQEHE0IAQYGAGEAAAAiAE4bS7AZUFhAJgACAQKFAAMDAV8AAQEaTQAFBQRhBwEEBBxNCAEGBgBhAAAAIgBOG0uwH1BYQCQAAgEChQABAAMEAQNoAAUFBGEHAQQEHE0IAQYGAGEAAAAiAE4bQCIAAgEChQABAAMEAQNoBwEEAAUGBAVpCAEGBgBhAAAAIgBOWVlZQBUVFQAAFSAVHxsZABQAExEREyYJBxorABYWFRQGBiMiJjURITUzFSEVNjYzEjY1NCYjIgYVFBYzAbdpOUJ6UoSNAWaO/qQbUTMRPT01Nj4+NgHeO2pFTnM+nJoBfULEhB0f/plANjY/PzY2QAACAA3/hAJlAe4ACwAPAFpLsC9QWEAeAwEBAAFTAAYGBV8ABQUcTQgHBAMAAAJfAAICGwJOG0AeAwEBAAFTAAYGBV8ABQUcTQgHBAMAAAJfAAICHQJOWUAQDAwMDwwPEhEREREREAkHHSslMxEjNSEVIxEzEyEDNSMHAh1IlP7RlUopAZ2beBqH/v18fAEDAWf+lerqAAAAAAEAFgAAAiUB7gAJAEFLsC9QWEAWAAICAF8AAAAcTQAEBAFfAwEBARsBThtAFgACAgBfAAAAHE0ABAQBXwMBAQEdAU5ZtxEREREQBQcbKxMhESMRIwMjNTOBAaScfCDXSAHu/hIBZ/6ZggAA//8ANf8qAigB7gACAUcAAP//ADX/KgIoAskAIwMqAnEAAAACAUcAAAABACYAAAIAAe4ADwBFS7AvUFhAFQADAAEAAwFoBQQCAgIcTQAAABsAThtAFQADAAEAAwFoBQQCAgIcTQAAAB0ATllADQAAAA8ADyMTIREGBxorAREjNSMiJjU1MxUUFjMzNQIAmHFhcJkpK1UB7v4SkHRkhnYzMdoAAAAAAgAWAAADTQHuABAAGQCkS7AhUFhAIQgBBQAGAwUGZwABAQRfAAQEHE0JBwIDAwBfAgEAABsAThtLsC9QWEArCAEFAAYDBQZnAAEBBF8ABAQcTQADAwBfAgEAABtNCQEHBwBfAgEAABsAThtAKwgBBQAGAwUGZwABAQRfAAQEHE0AAwMAXwIBAAAdTQkBBwcAXwIBAAAdAE5ZWUAWEREAABEZERgXFQAQAA8RERERJAoHGysAFhUUBiMhESMDIzUzEyEVMwY2NTQmIyMVMwLoZWNZ/vV5INdIIwGecgIhIB5XVwFmYVFWXgFn/pmCAWyI6x0cGh1wAP//AB//KgJBAfgAAgEjAAAAAQAT/yoB7QH+AB8AN0A0FgEEBRUBAwQfAQIDA0wAAwACAQMCZwAEBAVhAAUFIU0AAQEAXwAAAB4ATiQkISIREwYHHCskFhUHITUhNTQjIzUzMjY1NCYjIgYHJzYzMhYWFRQGBwG6MwH+OAEtX3VsKjA1LyREJj5kgERoOSsnf11Bt4U+ZoMrJicrFxpmUDFaOzRUGAAAAAABADsAAAIrAe4ABwA2S7AvUFhAEQACAgBfAAAAHE0DAQEBGwFOG0ARAAICAF8AAAAcTQMBAQEdAU5ZthERERAEBxorEyERIxEjESM7AfCdtp0B7v4SAWf+mQAAAAEAOwAAAy8B7gALAD1LsC9QWEATBAECAgBfAAAAHE0FAwIBARsBThtAEwQBAgIAXwAAABxNBQMCAQEdAU5ZQAkRERERERAGBxwrEyERIxEjESMRIxEjOwL0m5OXk5wB7v4SAWf+mQFn/pkA//8ALP/0AjMCzQACAdsAAP//ABr/8wHkAfkAAgHcAAD//wAf/wsCQAH4AAIB3QAA////9wAAAyQCvAACAd4AAP//ABP/GQH/Af4AAgHfAAD//wA1//UCKwHuAAIB4AAA//8ANf/1AisCyQAiAgEAAAADAyoCdgAA//8ANf/1AisCvAAiAgEAAAADAvoCLQAA//8AOwAAAjACvAACAeMAAP//AAIAAAI9Ae4AAgHkAAD//wA7AAACNQH5AAIB5QAA//8AOwAAA18B+QACAMgAAP//ADX/hAKEAe4AAgHnAAD//wA1//UDWQHuAAIB6AAA//8ANf+EA7IB7gACAekAAP//ADX/7wIIAe4AAgHqAAD//wAK/+8CUwHuAAIB6wAA//8AO//1Ay4CvAACAewAAP//ABv/9wIAAfkAAgEMAAD//wAs//QCMwLNAAIB2wAA//8AGv/zAeQB+QACAdwAAP//AB//CwJAAfgAAgHdAAD////3AAADJAK8AAIB3gAA//8AE/8ZAf8B/gACAd8AAP//ADX/9QIrAe4AAgHgAAD//wA1//UCKwLJACICFAAAAAMDKgJ2AAD//wA1//UCKwK8ACICFAAAAAMC+gItAAD//wA7AAACMAK8AAIB4wAA//8AAgAAAj0B7gACAeQAAP//ADsAAAI1AfkAAgHlAAD//wA7AAADXwH5AAIAyAAA//8ANf8LAisB7gACAR0AAP//ADX/CwIrAskAIgHuAAAAAwMqAnYAAP//ADX/hAKEAe4AAgHnAAD//wA1//UDWQHuAAIB6AAA//8ANf+EA7IB7gACAekAAP//ADX/7wIIAe4AAgHqAAD//wAK/+8CUwHuAAIB6wAA//8AO//1Ay4CvAACAewAAP//ABv/9wNZAfkAAgEWAAAAAQA7/yoCMQHuABMAX7YHAwIABAFMS7AqUFhAHAYFAgMDKE0AAAApTQAEBAFhAAEBKU0AAgIqAk4bQB8AAAQBBAABgAYFAgMDKE0ABAQBYQABASlNAAICKgJOWUAOAAAAEwATIxESIhEHCBsrAREjJwYjIicVIxEzERQWMzI2NRECMYIMN0koI52dMCgsOAHu/hI1PhLfAsT+7iw0PjEBAwAAAAABABP/9AKWAe4AFQBgtAcBAwFLS7AqUFhAHQcGBAMCAgVfAAUFKE0AAwMpTQAAAAFhAAEBKQFOG0AgAAMAAQADAYAHBgQDAgIFXwAFBShNAAAAAWEAAQEpAU5ZQA8AAAAVABURERETJRIICBwrARUUMzI2NxcGIyImNTUjESMRIzUhFQIzLgcVBQ0wJkhYhp5iAoMBbNAxBAFwDE9Q2f6UAWyCggAAAAACADL/8gKpAsgAEQAfAE5LsC9QWEAXAAICAGEAAAA4TQUBAwMBYQQBAQE5AU4bQBcAAgIAYQAAADhNBQEDAwFhBAEBATwBTllAEhISAAASHxIeGRcAEQAQJwYJFysEJiY1NTQ2NjMyFhYVFRQGBiM2NjU1NCYjIgYVFRQWMwEOj01Nj2Bfj01Nj19FUVBGRlBQRg5Mi11uXYtMTItdbl2LTJJYSm5LV1dLbktXAAAAAAEAKwAAAbUCxAAKAD+3CAcGAwADAUxLsC9QWEARAAMDMk0CAQAAAWAAAQEzAU4bQBEAAwMyTQIBAAABYAABATYBTlm2FBEREAQJGislMxUhNTMRBzUlMwFHbv52e28BABCGhoYBeyGKWgAAAAEAMgAAAnkCxQAdAI9LsA9QWEAkAAQDAgMEcgACAAYAAgZpAAMDBWEABQU4TQAAAAFfAAEBMwFOG0uwL1BYQCUABAMCAwQCgAACAAYAAgZpAAMDBWEABQU4TQAAAAFfAAEBMwFOG0AlAAQDAgMEAoAAAgAGAAIGaQADAwVhAAUFOE0AAAABXwABATYBTllZQAokIhIkIxEQBwkdKzchFSE1NDYzMjY1NCYjIgYHIzY2MzIWFhUUISIGFdUBof28l405RT83O0EDpAKbhlaARf7gP0WMjKdydzInJiwsKml3NWNC4TEuAAABACr/9AJ4AscALABBQD4sAQMEAUwABgUEBQYEgAABAwIDAQKAAAQAAwEEA2cABQUHYQAHBzhNAAICAGEAAAA8AE4jEiQhJCITJQgJHisAFhUUBgYjIiYmNTMUFjMyNjU0JiMjNTMyNjU0JiMiBhUjNDY2MzIWFhUUBgcCPzlLhlhYhEmkSj04RD45fnM6PkA3OEOgR39VUn5HNCsBUlE4P2E1OmlFKTIuJycqfSYjIystJUNkNzVfPTFOEQAAAAACABQAAAJ/ArwACgANAFC1CwEEAwFMS7AvUFhAFgUGAgQCAQABBABoAAMDMk0AAQEzAU4bQBYFBgIEAgEAAQQAaAADAzJNAAEBNgFOWUAPAAANDAAKAAoSERERBwkaKwEVIxUjNSEnATMRJwczAn9Nn/6ODQF4pp7S0gEIin5+kAGu/kzw8gAAAQAx//UCbwK8ABoAaEuwDVBYQCUAAQMCAgFyBwEGAAMBBgNnAAUFBF8ABAQyTQACAgBiAAAAPABOG0AmAAEDAgMBAoAHAQYAAwEGA2cABQUEXwAEBDJNAAICAGIAAAA8AE5ZQA8AAAAaABkRESQiEiUICRwrABYVFAYGIyImNTMUFjMyNjU0JiMhESEVIRUzAd6RR4FUjJamQjg3QD46/vQCBf6abQHGdnJFajp4cCoxMyssMAGAj2cAAAACADT/9QKMAscAHgAqAHe1GwEFBAFMS7ARUFhAJgACAwQDAnIHAQQABQYEBWkAAwMBYQABAThNCAEGBgBhAAAAPABOG0AnAAIDBAMCBIAHAQQABQYEBWkAAwMBYQABAThNCAEGBgBhAAAAPABOWUAVHx8AAB8qHyklIwAeAB0iEicmCQkaKwAWFhUUBgYjIiYmNTU0NjYzMhYXIyYmIyIGFRU2NjMSNjU0JiMiBhUUFjMB13VAS4dZWolKSoZYiZgBowNENzpIIFw0EUpKPD1JST0BxThnQ0dsOzpsR/dHbDtvYyInOS5GGRv+vjUrKzY1LCw0AAAAAAEAGQAAAjoCvAAGADq1AgECAAFMS7AvUFhAEAACAgBfAAAAMk0AAQEzAU4bQBAAAgIAXwAAADJNAAEBNgFOWbUREhADCRkrEyEVASMBIRkCIf7OugEZ/rICvFH9lQIsAAMAL//yAokCyQAZACUAMQBothkLAgQCAUxLsC9QWEAfAAIABAUCBGkGAQMDAWEAAQE4TQcBBQUAYQAAADkAThtAHwACAAQFAgRpBgEDAwFhAAEBOE0HAQUFAGEAAAA8AE5ZQBQmJhoaJjEmMCwqGiUaJCsrJAgJGSsAFhUUBiMiJjU0NjcmJjU0NjYzMhYWFRQGByQGFRQWMzI2NTQmIxI2NTQmIyIGFRQWMwJTNp6PjaA2KyQnRX5UVX5EJyT+/kJCNjZCQjY+SEg+PkhIPgFWWDRncXNlNFgVG0stPVwyMlw9LEwb2y4mJS4uJSYu/jYwKCgwMCgoMAAAAAIAKf/1An0CxwAdACkAd7UTAQMGAUxLsBFQWEAmAAEDAgIBcggBBgADAQYDaQAFBQRhBwEEBDhNAAICAGIAAAA8AE4bQCcAAQMCAwECgAgBBgADAQYDaQAFBQRhBwEEBDhNAAICAGIAAAA8AE5ZQBUeHgAAHikeKCQiAB0AHCQiEicJCRorABYWFRUUBgYjIiYnMxYWMzI2NTUGIyImJjU0NjYzEjY1NCYjIgYVFBYzAamITEqIWYqZAaQCRTc5TUJmT3ZASYZYPklJOzxISDwCxzxrRvVJbDtuZSIoOzBAMjdnREdsO/6xNSwrNTUrLDUAAP//AC//8gKmAsgAAgIm/QAAAQBlAAACcwLEAAoAM7YJCAcGBABKS7AvUFhADAIBAAABXwABARsBThtADAIBAAABXwABAR0BTlm1EREQAwcZKyUzFSE1MxEHNSUzAcCz/fK6nQE3B4aGhgF7MItoAAD//wA/AAAChgLFAAICKA0A//8ANv/0AoQCxwACAikMAP//ACQAAAKPArwAAgIqEAD//wBM//UCigK8AAICKxsA//8AOf/1ApECxwACAiwFAP//AFcAAAJ4ArwAAgItPgD//wAu//ICiALJAAICLv8A//8ALv/1AoICxwACAi8FAP//ACP/qQFwASgBBgJEALAACbEAArj/sLA1KwD//wAe/7ABAQEmAQYCRQCwAAmxAAG4/7CwNSsA//8AJP+wAVMBKAEGAkYAsAAJsQABuP+wsDUrAP//AB3/qQFaASgBBgJHALAACbEAAbj/sLA1KwD//wAW/7ABZQEhAQYCSACwAAmxAAK4/7CwNSsA//8AKP+pAVoBIQEGAkkAsAAJsQABuP+wsDUrAP//ACn/qQFfASgBBgJKALAACbEAArj/sLA1KwD//wAb/7ABOQEhAQYCSwCwAAmxAAG4/7CwNSsA//8AIf+pAWcBKAEGAkwAsAAJsQADuP+wsDUrAP//ACH/qQFXASgBBgJNALAACbEAArj/sLA1KwAAAgAj//kBcAF4ABEAHwAqQCcAAAACAwACaQUBAwMBYQQBAQEiAU4SEgAAEh8SHhkXABEAECcGBxcrFiYmNTU0NjYzMhYWFRUUBgYjNjY1NTQmIyIGFRUUFjObTCwsTC8uTCwsTC4dKSkeHicoHQcpSjA5MEopKUowOTBKKVwoIDchKCghNyAoAAEAHgAAAQEBdgAKAD+3CAcGAwADAUxLsC9QWEARAAMAA4UCAQAAAWAAAQEbAU4bQBEAAwADhQIBAAABYAABAR0BTlm2FBEREAQHGis3MxUjNTM1BzU3M8I/40I0jApVVVW3DVQjAAAAAQAkAAABUwF4AB0Ae0uwJVBYQBsAAwIAAgNyAAQAAgMEAmkFAQAAAV8AAQEbAU4bS7AvUFhAHAADAgACAwCAAAQAAgMEAmkFAQAAAV8AAQEbAU4bQBwAAwIAAgMAgAAEAAIDBAJpBQEAAAFfAAEBHQFOWVlAEQEAFRMREA4MAwIAHQEdBgcWKzczFSE1NDY3NjY1NCYjIgYHIzQ2MzIWFRQGBwYGFYnG/tVEQCUiHBcWHgJgVEBHUkA7KiVbW186OggEEREQEhIQNENAOTU1BgUUFwABAB3/+QFaAXgAJACntSQBAwQBTEuwI1BYQCkABgUEBQZyAAEDAgIBcgAHAAUGBwVpAAQAAwEEA2kAAgIAYgAAACIAThtLsCZQWEAqAAYFBAUGBIAAAQMCAgFyAAcABQYHBWkABAADAQQDaQACAgBiAAAAIgBOG0ArAAYFBAUGBIAAAQMCAwECgAAHAAUGBwVpAAQAAwEEA2kAAgIAYgAAACIATllZQAsiEiMhIyESJAgHHiskFhUUBiMiJjUzFjMyNjU0IyM1MzI1NCYjIgYHIzY2MzIWFRQHAT4cVklEWmkDNBofODw5Nx4aFyEDWwFUQUFWKrQrGzY/RTQhExEkSyAQFBQQM0FBMjAXAAAAAAIAFgAAAWUBcQAKAA0AVUAKDQEEAwcBAAQCTEuwL1BYQBYAAwQDhQUGAgQCAQABBABoAAEBGwFOG0AWAAMEA4UFBgIEAgEAAQQAaAABAR0BTllADwAADAsACgAKEhEREQcHGislFSMVIzUjJzczFSMzNQFlK2K+BKd9vFqUVT8/U9/deAAAAAABACj/+QFaAXEAGQBkS7AhUFhAIwABAwICAXIABAAFBgQFZwcBBgADAQYDZwACAgBiAAAAIgBOG0AkAAEDAgMBAoAABAAFBgQFZwcBBgADAQYDZwACAgBiAAAAIgBOWUAPAAAAGQAYEREkIhIkCAccKyQWFRQGIyImNTMWFjMyNjU0JiMjNSEVIxUzAQpQU0NHVWICHhYZHRwakwETtjbyPj46Q0E8EhQVEhMW0VYpAAIAKf/5AV8BeAAYACQAc7UWAQUEAUxLsCdQWEAkAAIDBAMCcgABAAMCAQNpBwEEAAUGBAVpCAEGBgBhAAAAIgBOG0AlAAIDBAMCBIAAAQADAgEDaQcBBAAFBgQFaQgBBgYAYQAAACIATllAFRkZAAAZJBkjHx0AGAAXIRIlJAkHGiskFhUUBiMiJjU1NDYzMhYXIyYjIgYVFTYzFjY1NCYjIgYVFBYzARBPV0VDV1RDQVMCXgMyGx0gKAoeHhoaHh4a70Q1N0ZGN4o1Qz4zIBQTIhGiFhMTFRUTExYAAAAAAQAbAAABOQFxAAYAN0uwL1BYQA8DAQIAAQACAWcAAAAbAE4bQA8DAQIAAQACAWcAAAAdAE5ZQAsAAAAGAAYREgQHGCsBFwMjEyM1ATQFm26InQFxKv65ARdaAAADACH/+QFnAXgAFwAjAC8AO0A4FwsCBAIBTAABBgEDAgEDaQACAAQFAgRpBwEFBQBhAAAAIgBOJCQYGCQvJC4qKBgjGCIqKiQIBxkrJBYVFAYjIiY1NDY3JiY1NDYzMhYVFAYHJgYVFBYzMjY1NCYjFjY1NCYjIgYVFBYzAUscWUpLWBwXExVURERTFROIHR0ZGRwcGR4hIR4eIiIety8dND4+NB0wDAsmFzE7OzEXJgtpFBERExMRERTjFRMTFRUTExUAAgAh//kBVwF4ABkAJQBztREBAwYBTEuwJVBYQCQAAQMCAgFyBwEEAAUGBAVpCAEGAAMBBgNpAAICAGIAAAAiAE4bQCUAAQMCAwECgAcBBAAFBgQFaQgBBgADAQYDaQACAgBiAAAAIgBOWUAVGhoAABolGiQgHgAZABgkIhIlCQcaKwAWFRUUBiMiJiczFhYzMjY1NQYjIiY1NDYzFjY1NCYjIgYVFBYzAQFWVkRHTwJgAh0XGh8gJz5OVkYaHh4aGh4eGgF4RTaLNkM9OBASFRMhEUQ1N0SiFBMSFBQSExQAAAD//wAjAUQBcALDAQcCRAAAAUsACbEAArgBS7A1KwAAAP//AB4BSwEBAsEBBwJFAAABSwAJsQABuAFLsDUrAAAA//8AJAFLAVMCwwEHAkYAAAFLAAmxAAG4AUuwNSsAAAD//wAdAUQBWgLDAQcCRwAAAUsACbEAAbgBS7A1KwAAAP//ABYBSwFlArwBBwJIAAABSwAJsQACuAFLsDUrAAAA//8AKAFEAVoCvAEHAkkAAAFLAAmxAAG4AUuwNSsAAAD//wApAUQBXwLDAQcCSgAAAUsACbEAArgBS7A1KwAAAP//ABsBSwE5ArwBBwJLAAABSwAJsQABuAFLsDUrAAAA//8AIQFEAWcCwwEHAkwAAAFLAAmxAAO4AUuwNSsAAAD//wAhAUQBVwLDAQcCTQAAAUsACbEAArgBS7A1KwAAAP//ACMBtwFwAzYBBwJEAAABvgAJsQACuAG+sDUrAAAA//8AHgG+AQEDNAEHAkUAAAG+AAmxAAG4Ab6wNSsAAAD//wAkAb4BUwM2AQcCRgAAAb4ACbEAAbgBvrA1KwAAAP//AB0BtwFaAzYBBwJHAAABvgAJsQABuAG+sDUrAAAA//8AFgG+AWUDLwEHAkgAAAG+AAmxAAK4Ab6wNSsAAAD//wAoAbcBWgMvAQcCSQAAAb4ACbEAAbgBvrA1KwAAAP//ACkBtwFfAzYBBwJKAAABvgAJsQACuAG+sDUrAAAA//8AGwG+ATkDLwEHAksAAAG+AAmxAAG4Ab6wNSsAAAD//wAhAbcBZwM2AQcCTAAAAb4ACbEAA7gBvrA1KwAAAP//ACEBtwFXAzYBBwJNAAABvgAJsQACuAG+sDUrAAAAAAH/XgAAAU8CvAADAChLsC9QWEALAAAAMk0AAQEzAU4bQAsAAAAyTQABATYBTlm0ERACCRgrEzMBI+Bv/n1uArz9RAD//wAeAAADPgLBACICTwAAACMCYgE+AAAAAwJGAesAAP//AB7/+QNFAsEAIgJPAAAAIwJiAT4AAAADAkcB6wAA//8AJP/5A30CwwAiAlAAAAAjAmIBdgAAAAMCRwIjAAD//wAeAAADMgLBACICTwAAACMCYgE+AAAAAwJIAc0AAP//AB0AAANuAsMAIgJRAAAAIwJiAXoAAAADAkgCCQAA//8AHv/5A0UCwQAiAk8AAAAjAmIBPgAAAAMCSQHrAAD//wAk//kDfQLDACICUAAAACMCYgF2AAAAAwJJAiMAAP//AB3/+QOBAsMAIgJRAAAAIwJiAXoAAAADAkkCJwAA//8AFv/5A5ACvAAiAlIAAAAjAmIBiQAAAAMCSQI2AAD//wAe//kDSgLBACICTwAAACMCYgE+AAAAAwJKAesAAP//ACj/+QODArwAIgJTAAAAIwJiAXcAAAADAkoCJAAA//8AHgAAAyQCwQAiAk8AAAAjAmIBPgAAAAMCSwHrAAD//wAe//kDUgLBACICTwAAACMCYgE+AAAAAwJMAesAAP//AB3/+QOOAsMAIgJRAAAAIwJiAXoAAAADAkwCJwAA//8AKP/5A4sCvAAiAlMAAAAjAmIBdwAAAAMCTAIkAAD//wAb//kDQAK8ACICVQAAACMCYgEsAAAAAwJMAdkAAP//AB7/+QNCAsEAIgJPAAAAIwJiAT4AAAADAk0B6wAAAAEAK//2AOAAoAALABlAFgAAAAFhAgEBATwBTgAAAAsACiQDCRcrFiY1NDYzMhYVFAYjXjMzKCczMycKMCUlMDAlJTAAAQAs/4YA4ACgAA0AJUAiBwEAAQFMAgEBAAABWQIBAQEAXwAAAQBPAAAADQAMFQMJFys2FhUUBgcjNyYmNTQ2M64yHCdVHBoeMiigMSghTVN4BykdJi8A//8AK//2AOABuAAiAnQAAAEHAnQAAAEYAAmxAQG4ARiwNSsA//8ALP+GAOEBuAAiAnUAAAEHAnQAAQEYAAmxAQG4ARiwNSsA//8AK//2AtcAoAAiAnQAAAAjAnQA/AAAAAMCdAH3AAAAAgA///YA8wK8AAMADwAlQCIAAQEAXwAAADJNAAICA2EEAQMDPANOBAQEDwQOJREQBQkZKxMzAyMWJjU0NjMyFhUUBiNEqg2QITMzJyczMycCvP4c4jAlJTAwJSUwAAAAAgA2/zgA6gH+AAsADwBFS7AhUFhAFgAAAAFhBAEBATtNAAICA18AAwM3A04bQBMAAgADAgNjAAAAAWEEAQEBOwBOWUAOAAAPDg0MAAsACiQFCRcrEhYVFAYjIiY1NDYzBzMTI7czMycoMjIoSZENqwH+MCUlMC8mJTDi/hwAAAACAB3/9gI2AsMAHQApADZAMwABAAMAAQOAAAMEAAMEfgAAAAJhAAICMk0ABAQFYQYBBQU8BU4eHh4pHigmGiMSJwcJGysSNjc2NjU0JiMiBhUjJjY2MzIWFhUUBgcGBhUVIzUSJjU0NjMyFhUUBiPKNTosKzYvMDmhBEB7T1N6QkNEJSCgKTMzJygyMycBP00SDycaIicvKEFoOjRhQjxSGg4mHxkm/vgwJSUwLyYlMAAAAAACACH/NAI6AgEACwApAGdLsCFQWEAlAAUAAwAFA4AAAwIAAwJ+AAAAAWEGAQEBO00AAgIEYgAEBDcEThtAIgAFAAMABQOAAAMCAAMCfgACAAQCBGYAAAABYQYBAQE7AE5ZQBIAACgnHRsYFxUTAAsACiQHCRcrABYVFAYjIiY1NDYzEgYHBgYVFBYzMjY1MxYGBiMiJiY1NDY3NjY1NTMVAWUzMygnMzMnUTU6LSo2LzA5oARAek9Te0JDRSUgoAIBMCUmMDElJTD+t00TDicaIicvKEFoOjRhQjxSGQ4nHxkmAP//AC8AzQDkAXcBBwJ0AAQA1wAIsQABsNewNSsAAQBGALEBYgG7AAsAHkAbAAABAQBZAAAAAWECAQEAAVEAAAALAAokAwkXKzYmNTQ2MzIWFRQGI5ZQUD4+UFA+sUo7O0pKOztKAAAAAAEAKQGHAX0CvAAOABxAGQ4NCgkIBwYFBAMCAQwASQAAADIAThsBCRcrAQcXBycHJzcnNxcnMwc3AX1cQV0yMWBAWSFWBnQNXQIdEUNCUlJCQhJrI1dZJQAC//j/9gIpAsMAHQApAEdARA4BAAMBTAADAQABAwCAAAICBGEHAQQEMk0AAAABXwABATVNCAEGBgVhAAUFPAVOHh4AAB4pHigkIgAdABwSKBEaCQkaKwAWFhUUBgcGBhUVIwMzBzY3NjY1NCYjIgYHIzY2MxIWFRQGIyImNTQ2MwFwez4/PyckhAeHAgkMFhJBPD1IAZwDmYYuMzMnJzMzJwLDNl07PlwbESQcFwEaXggHDSEZJS4xLGx3/d0wJSUwMCUlMAAAAAIAJAAAAqsCvAAbAB8AeEuwL1BYQCYNCwIJDggCAAEJAGgQDwcDAQYEAgIDAQJnDAEKCjJNBQEDAzMDThtAJg0LAgkOCAIAAQkAaBAPBwMBBgQCAgMBAmcMAQoKMk0FAQMDNgNOWUAeHBwcHxwfHh0bGhkYFxYVFBMSEREREREREREQEQkfKwEjBzMVIwcjNyMHIzcjNTM3IzUzNzMHMzczBzMBNyMHAqtiKUhnIZYhaiGVIUhnKExrJJUkbCSVJEP+4ilwKQGqpX+GhoaGf6V/k5OTk/7aqakAAAABABj/sQHvAvQAAwARQA4AAAEAhQABAXYREAIJGCsBMwEjAVqV/r6VAvT8vQAAAAABABj/sQHvAvQAAwARQA4AAQABhQAAAHYREAIJGCsFIwEzAe+U/r2VTwND//8ANwD0AOwBngEHAnQADAD+AAixAAGw/rA1K///AEUAuwFhAcUBBgJ+/woACLEAAbAKsDUrAAAAAQAg/2gBWwMUAA0ABrMNBQEyKxYmNTQ2NxcGBhUUFhcHmHh4bVZOWlpOVkb1j4/1UmE+yG9vyD9gAAAAAQAR/2gBTAMUAA0ABrMNBwEyKxc2NjU0Jic3FhYVFAYHEU9ZWk5XbXd3bTg/x3BvyD5hUvWPj/VSAAAAAQAd/2YBWgLMACIAPEA5GwEFBBwBAwUCAQIDCwEAAgwBAQAFTAADAAIAAwJpAAAAAQABZQAFBQRhAAQEOAVOIyMREyMoBgkcKxIGBxYWFRUUFjMyNxUGIyI1NTQjNTI1NTQzMhcVJiMiBhUV9yMnJyMbHxcSJzCkQkKkKC8ZEB8bAWk/ERFAMnogHAJzCaOZP3A/maMJdAMcIHsAAQAb/2YBWALMACIAPEA5HQEEBRwBAAQTAQEACgEDAQkBAgMFTAAAAAEDAAFpAAMAAgMCZQAEBAVhAAUFOAROIywjIxEQBgkcKwAzFSIVFRQjIic1FjMyNjU1NDY3JiY1NTQmIyIHNTYzMhUVARZCQqQwJxIXHxsjJycjGx8QGS8opAFRcD+ZowlzAhwgejJAERE/MnsgHAN0CaOZAAAAAAEARv9gAUcCwQAHABxAGQACAAMCA2MAAQEAXwAAADIBThERERAECRorEyEVIxEzFSFGAQFvb/7/AsGB/aCAAAABACP/YAEkAsEABwAcQBkAAQAAAQBjAAICA18AAwMyAk4REREQBAkaKwUhNTMRIzUhAST+/29vAQGggAJggQD//wAl/4gBYAM0AQYChgUgAAixAAGwILA1KwAAAAEAGv+IAVUDNAANAAazDQcBMisXNjY1NCYnNxYWFRQGBxpOWlpOV213d20XPshvb8g+YVL1j4/1UgAA//8AI/+gAWADBgEGAogGOgAIsQABsDqwNSsAAAABACD/oAFdAwYAIgBCQD8dAQQFHAEABBMBAQAKAQMBCQECAwVMAAUABAAFBGkAAAABAwABaQADAgIDWQADAwJhAAIDAlEjLCMjERAGBxwrADMVIhUVFCMiJzUWMzI2NTU0NjcmJjU1NCYjIgc1NjMyFRUBG0JCpCotGw4fGiMnJyMaHxkQKC+kAYtwP5mjCXQDHCB7Mj8REUAyeyAbAnQIopoA//8ATf+rAU4DDAEGAooHSwAIsQABsEuwNSsAAAABACv/qwEsAwsABwAiQB8AAwACAQMCZwABAAABVwABAQBfAAABAE8REREQBAcaKwUhNTMRIzUhASz+/29vAQFVgAJggAAAAAABADoA4QG/AWIAAwAYQBUAAAEBAFcAAAABXwABAAFPERACCRgrEyEVIToBhf57AWKBAAD//wA6AOEBvwFiAAICkgAAAAEAOQDhAiQBYgADAB9AHAIBAQAAAVcCAQEBAF8AAAEATwAAAAMAAxEDCRcrARUhNQIk/hUBYoGBAAAAAAEAOQDhAn4BYgADAB9AHAIBAQAAAVcCAQEBAF8AAAEATwAAAAMAAxEDCRcrARUhNQJ+/bsBYoGBAAAAAAEAG/94AgD/+AADACCxBmREQBUAAAEBAFcAAAABXwABAAFPERACCRgrsQYARBchFSEbAeX+GwiAAAAA//8AOgEOAb8BjwEGApIALQAIsQABsC2wNSsAAAABADkBDgIkAY8AAwAfQBwCAQEAAAFXAgEBAQBfAAABAE8AAAADAAMRAwcXKwEVITUCJP4VAY+BgQAAAAABADkBDgJ+AY8AAwAfQBwCAQEAAAFXAgEBAQBfAAABAE8AAAADAAMRAwcXKwEVITUCfv27AY+BgQAAAP//ACz/hgDgAKAAAgJ1AAAAAgAs/5IBmwCQAA0AGwAzQDAVBwIAAQFMBQMEAwEAAAFZBQMEAwEBAF8CAQABAE8ODgAADhsOGhQTAA0ADBUGCRcrNhYVFAYHIzcmJjU0NjMyFhUUBgcjNyYmNTQ2M6ItGSRNGRcbLiPxLRojTBkXGy0kkCwkHkNNawglGSIrLCQeRkprCCUZIisAAAACAD0B0AGTAr0ADQAbAB5AGxsNAgABAUwCAQAAAV8DAQEBMgBOFSYVJAQJGisSFhUUBiMiJjU0NjczBxYWFRQGIyImNTQ2NzMHvBkrISIqGCFHF9QZKiEiKhchSBcCUiIYHykpIhxARmQHIhggKCkiHD9HZAAAAP//AD4BxQGtAsMBBwKbABICMwAJsQACuAIzsDUrAAAAAAEAQAG+AOICvAANABlAFg0BAAEBTAAAAAFfAAEBMgBOFSQCCRgrEhYVFAYjIiY1NDY3MwfHGy0kJC0aI0wZAkklGSIrLSQeRUprAAABAD8BxQDhAsMADQAfQBwHAQABAUwAAAABYQIBAQEyAE4AAAANAAwVAwkXKxIWFRQGByM3JiY1NDYztC0aI0wZFxstJALDLSQeRUprCCUZIisAAAACACAARgIsAgYABQALAFFACQoHBAEEAAEBTEuwFVBYQA8CAQAAAV8FAwQDAQE1AE4bQBcFAwQDAQAAAVcFAwQDAQEAXwIBAAEAT1lAEgYGAAAGCwYLCQgABQAFEgYJFysBBxcjJzchBxcjJzcBToyMooyMAYCMjKKMjAIG4ODg4ODg4OAAAAAAAgAjAEYCLwIGAAUACwBRQAkKBwQBBAABAUxLsBVQWEAPAgEAAAFfBQMEAwEBNQBOG0AXBQMEAwEAAAFXBQMEAwEBAF8CAQABAE9ZQBIGBgAABgsGCwkIAAUABRIGCRcrExcHIzcnIRcHIzcnxYyMooyMAYCMjKKMjAIG4ODg4ODg4OAAAQAgAEYBUwIGAAUAPrYEAQIAAQFMS7AVUFhADAAAAAFfAgEBATUAThtAEgIBAQAAAVcCAQEBAF8AAAEAT1lACgAAAAUABRIDCRcrAQcXIyc3AVOPj6eMjAIG4ODg4AAAAQAjAEYBVQIGAAUAPrYEAQIAAQFMS7AVUFhADAAAAAFfAgEBATUAThtAEgIBAQAAAVcCAQEBAF8AAAEAT1lACgAAAAUABRIDCRcrExcHIzcnyouLp46OAgbg4ODgAAD//wA+Aa4BgwK8ACICpQAAAAMCpQDBAAAAAQA+Aa4AwgK8AAMAE0AQAAEBAF8AAAAyAU4REAIJGCsTMxEjPoSEArz+8v//ADAAcgI8AjIBBgKgECwACLEAArAssDUrAAAAAgA4AHICRQIyAAUACwA1QDIKBwQBBAABAUwFAwQDAQAAAVcFAwQDAQEAXwIBAAEATwYGAAAGCwYLCQgABQAFEgYHFysTFwcjNychFwcjNyfbjIyjjY0BgYyMo42MAjLg4ODg4ODh3///ADAAcAFjAjABBgKiECoACLEAAbAqsDUrAAAAAQA4AHEBawIwAAUAJkAjBAECAAEBTAIBAQAAAVcCAQEBAF8AAAEATwAAAAUABRIDBxcrExcHIzcn4IuLqI6OAjDf4ODfAAAAAQAf/6IB9gJKABsANUAyDw0KAwIBGhACAwIbBAEDAAMDTAABAAIDAQJpAAMAAANZAAMDAF8AAAMATyQlGBIECRorJAcVIzUmJjU0Njc1MxUWFwcmIyIGFRQWMzI3FwG3UoBdaWtbgE48Vyo5NkRDNz0rWQkPWFoUg2NihRRZVg85XydFODhFK14AAAACADQANAI9AjwAGwAnAGZAHQ4NCwcFBAYCABsZFRMSBQEDAkwMBgIAShoUAgFJS7AdUFhAEwQBAwABAwFlAAICAGEAAAA7Ak4bQBoAAAACAwACaQQBAwEBA1kEAQMDAWEAAQMBUVlADBwcHCccJigsKAUJGSs3JjU0Nyc3FzYzMhc3FwcWFRQHFwcnBiMiJwcnJDY1NCYjIgYVFBYzbhQVO2tCKC8uKkJrORUVOGpBKy4vKEBrASsxMSkoMDEn1ys0My47akIQEEJqOS02MDA3akAPDkBrPzApKjEyKSgxAAEAIP+VAnYDKAApADVAMh0aFwMDAh4JAgEDCAUCAwABA0wAAgADAQIDaQABAAABWQABAQBfAAABAE8mHCYTBAkaKyQGBxUjNSYmJzcWMzI2NTQmJyYmNTQ2NzUzFRYWFwcmIyIGFRQWFxYWFQJ2emeIRHovVV18PklESo+FcF+IO2srTVJjPUk/So6MeXQQYF8IMSZ3SSokIiYIEGZfUHARY18HJx9zOSgiISQJEG1fAAAAAAEAFP/1AlUCxwAoAIRADhQBBgUVAQQGKAELAQNMS7AtUFhAKwkBAgoBAQsCAWcABgYFYQAFBThNCAEDAwRfBwEEBDVNAAsLAGEAAAA8AE4bQCkHAQQIAQMCBANnCQECCgEBCwIBZwAGBgVhAAUFOE0ACwsAYQAAADwATllAEiclJCMiIRESIyIRFBESIQwJHyslBiMiJicjNzMmNTQ3IzczNjYzMhcHJiMiBgczByMGFRQXMwcjFjMyNwJVPEmIryBlGTsBAVQZTiOve0U/Ky0sNFQZyhnPAQHCGI02giYqCRR0b2oJExEJa2t5F30OMy1nCRMUCWhcDAAAAAH/6v81AewCzAAjAGxAEh0BBwYeAQAHCwEDAQoBAgMETEuwIVBYQCEABwcGYQAGBjhNBAEBAQBfBQEAADVNAAMDAmEAAgI3Ak4bQB4AAwACAwJlAAcHBmEABgY4TQQBAQEAXwUBAAA1AU5ZQAskJBETJSMREAgJHisBMxUjERQGIyImJzcWFjMyNjURIzUzNTQ2NjMyFhcHJiMiBhUBNIaGalIlSh8zDhsRHSJXVzhcNShKGzQgJhsjAe19/o9haRcVaQoIKCUBa34aQlgqGRdlGSQkAAAAAAIADv/wAqECywAWACsAvEASDQECAwwBAQIiAQcGIwEIBwRMS7AXUFhAKgAFCQEGBwUGZwACAgNhAAMDOE0AAAABXwoEAgEBNU0ABwcIYQAICDkIThtLsC9QWEAoCgQCAQAABQEAZwAFCQEGBwUGZwACAgNhAAMDOE0ABwcIYQAICDkIThtAKAoEAgEAAAUBAGcABQkBBgcFBmcAAgIDYQADAzhNAAcHCGEACAg8CE5ZWUAXAAArKiYkIB4aGRgXABYAFiUkERELCRorARUhNSE2NTQmIyIGByc2NjMyFhYVFAcFIRUhBhUUFjMyNjcXBiMiJjU0NyMCof1tAacJPDIsVxtOOnFGUXtDA/2tApP+Vgk+Nz1kK1l2roiWBT0B2F9fDxMkJR0XaysmM18+EhGCXxMUJSsoKW9ydmYVFgAAAQAQAAACXgK8AB0Ah0AYFhUUExIREA0MCwoJCA0DARcHBgMCAwJMS7AJUFhAGAQBAwECAgNyAAEBMk0AAgIAYAAAADMAThtLsC9QWEAZBAEDAQIBAwKAAAEBMk0AAgIAYAAAADMAThtAGQQBAwECAQMCgAABATJNAAICAGAAAAA2AE5ZWUAMAAAAHQAdKRkjBQkZKwEVFAYjITUHNTc1BzU3NTMVNxUHFTcVBxUzMjY1NQJefGn+8ltbW1uluLi4uEkyMAEiNW9+5CJ5IkEieSKlaER5REJEeUSGLDIqAAACAAEAAAKAArwAFwAgAG1LsC9QWEAlCQEGCwgCBQAGBWcEAQADAQECAAFnAAoKB18ABwcyTQACAjMCThtAJQkBBgsIAgUABgVnBAEAAwEBAgABZwAKCgdfAAcHMk0AAgI2Ak5ZQBUAACAeGhgAFwAWIREREREREREMCR4rNxUzFSMVIzUjNTM1IzUzESEyFhYVFAYjJzMyNjU0JiMj+JCQq0xMTEwBMU51P4t3iH0vNTUvfewza05OazOCAU45akdqfIIyLCwyAAEANAAAAmsCxQAjAKa1AwEACAFMS7APUFhAJwAEBQIFBHIGAQIHAQEIAgFnAAUFA2EAAwM4TQkBCAgAXwAAADMAThtLsC9QWEAoAAQFAgUEAoAGAQIHAQEIAgFnAAUFA2EAAwM4TQkBCAgAXwAAADMAThtAKAAEBQIFBAKABgECBwEBCAIBZwAFBQNhAAMDOE0JAQgIAF8AAAA2AE5ZWUARAAAAIwAjERQiEiURFREKCR4rJRUhNTY2NTUjNTMmNTQ2NjMyFgcjJiYjIgYVFBczFSMWFRQHAmv9ySwtWT8NPXRQc4cElwExKS4xDMmxASuLi4kJRSsMejQqQ2Q4bm0qKjMvGjp6BQpILAABABgAAALrArwAFgBrtRUBAAkBTEuwL1BYQCEIAQAHAQECAAFoBgECBQEDBAIDZwsKAgkJMk0ABAQzBE4bQCEIAQAHAQECAAFoBgECBQEDBAIDZwsKAgkJMk0ABAQ2BE5ZQBQAAAAWABYUExEREREREREREQwJHysBAzMVIxUzFSMVIzUjNTM1IzUzAzMTEwLr3V6enp6jnp6eYNW/p6oCvP62ay1rb29rLWsBSv7wARAAAP//AG//ogJGAkoAAgKtUAD//wA1/5UCiwMoAAICrxUA//8APv/1An8CxwACArAqAAABAFT/NQJsAswAJABqQBIeAQcGHwEABwwBAwELAQIDBExLsC1QWEAhAAcHBmEABgYfTQQBAQEAXwUBAAAcTQADAwJhAAICHgJOG0AcAAYABwAGB2kAAwACAwJlBAEBAQBfBQEAABwBTllACyQkERMlJBEQCAceKwEzFSMRFAYGIyImJzcWFjMyNjURIzUzNTQ2NjMyFhcHJiMiBhUBq5CQM1g3KE0gMhEdEyAmeXk6XTcpTBwzIikeJQHtff6TQl0vFxVpCggpJwFofhpCWCoYGGUZJCQAAP//AEwAAAKDAsUAAgK1GAD////9AAAC0AK8AAICtuUAAAEAMADiAOsBkwALAB5AGwAAAQEAWQAAAAFhAgEBAAFRAAAACwAKJAMGFys2JjU0NjMyFhUUBiNlNTUoKTU1KeIyJiYzMyYmMgAAAAAB/+8AAAH7ArwAAwARQA4AAAEAhQABAXYREAIGGCsBMwEjAW+M/oCMArz9RAAAAAABADoAdgHnAhYACwAsQCkABAMBBFcGBQIDAgEAAQMAZwAEBAFfAAEEAU8AAAALAAsREREREQcJGysBFSMVIzUjNTM1MxUB54+Qjo6QAYqEkJCEjIwAAAAAAQA6AQUB0gGKAAMAGEAVAAABAQBXAAAAAV8AAQABTxEQAgYYKxMhFSE6AZj+aAGKhQAAAAEALwB/AaQB9gALAAazCQMBMisBBxcHJwcnNyc3FzcBpF1dX1tcX11dX1xbAZheXl1cXF1eXl5dXQAAAAMAOgA4AgECWAALAA8AGwA7QDgAAAYBAQIAAWkAAgADBAIDZwAEBQUEWQAEBAVhBwEFBAVREBAAABAbEBoWFA8ODQwACwAKJAgJFysSJjU0NjMyFhUUBiMHIRUhFiY1NDYzMhYVFAYj+DIxJiYxMiXjAcf+Ob0xMiUlMjEmAbksIyQsLCQjLC+A0iwkIywsIyQsAAACADoAiwHqAeEAAwAHAD5LsCdQWEASAAIAAwIDYwABAQBfAAAANQFOG0AYAAAAAQIAAWcAAgMDAlcAAgIDXwADAgNPWbYREREQBAkaKxMhFSEVIRUhOgGw/lABsP5QAeGBVIEAAQA6ACkB/QJDABMANUAyERACBkoHBgICSQcBBgUBAAEGAGcEAQECAgFXBAEBAQJfAwECAQJPExERERMRERAIBh4rASMHMxUhByc3IzUzNyM1ITcXBzMB/Zcuxf70Nk8eUJcuxQEMNk4eUQFgVIFiLDaBVIFiLDYAAQA2AEABdQIuAAYABrMDAAEyKxMXFQcnNyeZ3Nxjm5sCLtw13WGVlwAAAAABADQAQAFzAi4ABgAGswYDATIrAQcXByc1NwFzm5tj3NwBzZeVYd013AAAAAIANgAIAZYCdAAGAAoAIUAeBgUEAwIBBgBKAAABAQBXAAAAAV8AAQABTxEXAgYYKzcnNyc3FxUFIRUhm1CdnVD2/qUBYP6gwWR1dmTELP1/AAAAAAIAOAAIAZcCdAAGAAoAIUAeBgUEAwIBBgBKAAABAQBXAAAAAV8AAQABTxEXAgYYKwEHJzU3FwcDIRUhAYJQ9vZQna0BX/6hASVkwyzEZHb+7X8AAAIAOgAIAe0CXgALAA8AXEuwL1BYQB4DAQEEAQAFAQBnAAIIAQUGAgVnAAYGB18ABwczB04bQB4DAQEEAQAFAQBnAAIIAQUGAgVnAAYGB18ABwc2B05ZQBIAAA8ODQwACwALEREREREJCRsrNzUjNTM1MxUzFSMVBSEVIcmMjJSMjP7dAbP+TcaDiYyMiYM9gQAAAAACADQAgwHnAdkAFwAvAGFAXhMBAgEUCAIAAgcBAwArAQYFLCACBAYfAQcEBkwAAQAAAwEAaQACCAEDBQIDaQAGBAcGWQAFAAQHBQRpAAYGB2EJAQcGB1EYGAAAGC8YLiooJCIeHAAXABYkJCQKBhkrACYnJiYjIgcnNjYzMhYXFhYzMjcXBgYjBiYnJiYjIgcnNjYzMhYXFhYzMjcXBgYjAUMoGRQbDSkXUhdKLBYmGxYaDSkYURdKLBcoGRQbDSkXUhdKLBYmGxYaDSgZURdKLAFBDQwJCigwLzUNDAoJKTEvNb4NDAkKKTEvNQ0MCgkoMS80AAAAAAEANADKAjgBkAAXADyxBmREQDEUEwICAQgHAgMAAkwAAgADAlkAAQAAAwEAaQACAgNhBAEDAgNRAAAAFwAWJCQkBQkZK7EGAEQkJicmJiMiByc2NjMyFhcWFjMyNxcGBiMBfzAgGiMQJh5qDlE9HDQnHiAOJRVrDFNAyhQTDxA2J0JNFBQPDjcoQU8AAQA6AI4B2wGFAAUAPkuwCVBYQBYAAgAAAnEAAQAAAVcAAQEAXwAAAQBPG0AVAAIAAoYAAQAAAVcAAQEAXwAAAQBPWbURERADCRkrASE1IRUjAVP+5wGhiAENePcAAAAAAQAgAVYCWgK8AAYAIbEGZERAFgIBAAIBTAACAAKFAQEAAHYREhADCRkrsQYARAEjJwcjEzMCWqJ9fJ/sXwFWv78BZgADADEAmQL3AeQAFwAjAC8ASkBHFAEFAiwdAgQFCAEABANMCAMCAgYBBQQCBWkJBwIEAAAEWQkHAgQEAGEBAQAEAFEkJAAAJC8kLiooIR8bGQAXABYkJCQKBhkrABYVFAYjIiYnBgYjIiY1NDYzMhYXNjYzBBYzMjY3JiYjIgYVBDY1NCYjIgYHFhYzApleXko3WSwsVzdKXl5KN1csLFk3/lQhGh02Hh42HRohAcAhIRoeNh4eNh4B5FxJSlwzLCwzXEpJXDMsLDO/Ih8dHB8hGjwiGhohHxwdHwAAAwAf/9ACkgJ6ABcAIAApAE5ASxcUAgQCJyYeHQQFBAsIAgAFA0wAAwIDhQABAAGGAAIGAQQFAgRpBwEFAAAFWQcBBQUAYQAABQBRISEYGCEpISgYIBgfEicSJQgGGisAFhUUBgYjIicHIzcmJjU0NjYzMhc3MwcEBgYVFBcTJiMSNjY1NCcDFjMCWjhRj1o7NyN9QzI4UI9aQDMifkP+/k8tKrAXFTJQLSqwFhUB5nlIV4tOEzhsKXhIV4tOEzhrOy1QMkYwASAF/qItUDJGL/7hBQAB//3/NQH+AwAAGgA3QDQQAQIBEQMCAAICAQMAA0wAAQACAAECaQAAAwMAWQAAAANhBAEDAANRAAAAGgAZJCUlBQYZKxYmJzcWFjMyNjURNDYzMhYXByYjIgYVERQGI2VKHjIQGhAeIW9aKUkbNB4nHSJlVssXFWkKCCkkAjdaahkXZBglI/3DXG4AAAEAMgAAAxACzAAjAC5AKxQGAgEAAUwABQACAAUCaQQBAAEBAFcEAQAAAV8DAQEAAU8mERcnERIGBhwrAAYHMxUhNTY2NTQmJiMiBgYVFBYXFSE1MyYmNTQ2NjMyFhYVAxA2MFf+2kZQNV88PF81T0b+21cvN1ynbGynXAEseimJhxh2UD9iNzhiPlB2GIeJKXtFZp1XV51mAAAAAAL/+QAAAxQCvAADAAYAJUAiAwEBAgGFAAIAAAJXAAICAF8AAAIATwAABgUAAwADEQQGFysBASEBFwMhAdwBOPzlATdWpQFKArz9RAK8q/56AAAAAAEATP9JAmkCvAAHACBAHQMBAQIBhgAAAgIAVwAAAAJfAAIAAk8REREQBAYaKxMhESMRIxEjTAIdpNWkArz8jQLj/R0AAQArAAACMgK8AAwAMkAvBgEDAgwLBQMAAwQBAQADTAACAAMAAgNnAAABAQBXAAAAAV8AAQABTxEUERAEBhorJSEVITUTAzUhFSEXFQEFAS39+cnAAfj+44KPj1kBDgEHTom3KQAAAAABAAUAAAJvAusACAAUQBEIBwYFBAEGAEoAAAB2EgEGFysBFwMjAwcnNxMCAW7tcJlQJM15Ause/TMBOyVUXf7+AAAAAAIAH//1AikCugAVACEANEAxEQECAQFMFRQCAUoAAQACAwECaQQBAwAAA1kEAQMDAGEAAAMAURYWFiEWIComJgUGGSsAFhYVFAYGIyImJjU0NjYzMhcmJic3EjY1NCYjIgYVFBYzARaxYj92UE52QTxrRTgmIXlHHLE7OzExOzsxAq14wXVReEE9cUpHbj0XLkMKd/29QTU1QEA1NUEAAP//ADv/KgIxAe4AAgIkAAAABQAk//kDMwLDAAsADwAbACcAMwDUS7AhUFhALQAGAAgJBghqAAQEAGECAQAAMk0KAQEBBWELAQUFNU0NAQkJA2EMBwIDAzMDThtLsC9QWEA1AAYACAkGCGoAAgIyTQAEBABhAAAAMk0KAQEBBWELAQUFNU0AAwMzTQ0BCQkHYQwBBwc8B04bQDUABgAICQYIagACAjJNAAQEAGEAAAAyTQoBAQEFYQsBBQU1TQADAzZNDQEJCQdhDAEHBzwHTllZQCYoKBwcEBAAACgzKDIuLBwnHCYiIBAbEBoWFA8ODQwACwAKJA4JFysSJjU0NjMyFhUUBiMBMwEjEjY1NCYjIgYVFBYzACY1NDYzMhYVFAYjNjY1NCYjIgYVFBYzgl5eS01dXkwBeJT+OJRpHx8ZGR4eGQFxXl5LTF5dTRkfHxkZHh4ZAYBaSEhZWElJWQE8/UQB6h8ZGR8fGRkf/g9ZSEhaWUlJWGkfGRkfHxkZHwAHACT/+QTAAsMACwAPABsAJwAzAD8ASwD2S7AhUFhAMwgBBgwBCgsGCmoABAQAYQIBAAAyTQ4BAQEFYQ8BBQU1TRMNEgMLCwNhEQkQBwQDAzMDThtLsC9QWEA7CAEGDAEKCwYKagACAjJNAAQEAGEAAAAyTQ4BAQEFYQ8BBQU1TQADAzNNEw0SAwsLB2ERCRADBwc8B04bQDsIAQYMAQoLBgpqAAICMk0ABAQAYQAAADJNDgEBAQVhDwEFBTVNAAMDNk0TDRIDCwsHYREJEAMHBzwHTllZQDZAQDQ0KCgcHBAQAABAS0BKRkQ0PzQ+OjgoMygyLiwcJxwmIiAQGxAaFhQPDg0MAAsACiQUCRcrEiY1NDYzMhYVFAYjATMBIxI2NTQmIyIGFRQWMwAmNTQ2MzIWFRQGIyAmNTQ2MzIWFRQGIyQ2NTQmIyIGFRQWMyA2NTQmIyIGFRQWM4JeXktNXV5MAXuU/jiUZh8fGRkeHhkBd15eTExdXUwBPF9fS0xdXUz+kh4eGRkfHxkBoB4eGRkfHxkBgFpISFlYSUlZATz9RAHqHxkZHx8ZGR/+D1lISFpZSUlYWUhIWllJSVhpHxkZHx8ZGR8fGRkfHxkZHwAAAAABAB4AVgH+AngACAAUQBEIBwYFAgEGAEoAAAB2EwEGFysBBycRIxEHJzcB/k1neGdN8AGITmf+tQFLZ07wAAAAAQAiAHcBzwIkAAgAKUAmBAEBAgFMBgUCAUkAAQIBhgAAAgIAVwAAAAJfAAIAAk8UERADBhkrEyURBzUHJzcjfAFTbupV65ICIwH+rAGS6lTrAAAAAQA6AG4CXAJOAAgAJ0AkAQEAAQFMCAEBSgMCAgBJAAEAAAFXAAEBAF8AAAEATxEUAgYYKwEXByc3ITUhJwFs8PBOZ/61AUtnAk7w8E1neGcAAAAAAQAiAKoBzwJXAAgAKUAmCAECAAFMBwYCAEoAAAIAhQACAQECVwACAgFfAAECAU8RERADBhkrARcRJSczJzcXAWFu/q0BkutV6gH/Af6sAW3rVOoAAQAeAFUB/gJ4AAgAFEARCAUEAwIBBgBJAAAAdhYBBhcrARcHJzcXETMRAbFN8PBNZ3gBk07w8E5nAUz+tAAAAAEAOQCqAeYCVwAIAChAJQcBAAIBTAgBAkoAAgAChQAAAQEAVwAAAAFfAAEAAU8REREDBhkrAQczByERMxU3AebqkQH+rW3rAgLqbgFUkusAAQAgAG4CQwJOAAgAL0AsBQEAAQFMBwYCAUoEAwIASQIBAQAAAVcCAQEBAF8AAAEATwAAAAgACBEDBhcrARUhFwcnNxcHAkP+tGdO8PBOZwGaeGdN8PBNZwAAAAABADgAdgHlAiMACAAoQCUCAQACAUwBAQBJAAACAIYAAQICAVcAAQECXwACAQJPERETAwYZKyUHJxUnESEVIwHlVepuAVSSy1XqkQEBU20AAAIAIAAAAlICvAAFAAkAIUAeCQgHBAEFAAEBTAIBAQABhQAAAHYAAAAFAAUSAwYXKwETAyMDExM3JwcBftTUi9PTRnd3eAK8/qL+ogFeAV793MbGxgAAAAASADL//ARWAjkAEgAeACoAPABKAFEAXQBvAHsAjgCSAKEAsADJANYA2gDmAPIFvkAaMQEQCUYBFRRfMAIICsupmQMiHq6UAiMyBUxLsAlQWEDJABQCFQoUchIBEQAKAhFyACgfIB8oIIAAMCIzIjAzgAAzMiIzMn4HAQEACRABCWlDARATAQIUEAJpQQEKQAEIGQoIahcBFQAZBBUZaUUbDAMEABwNCz8GBQQOAARnGhhCDwQFFg4FV0YdAg5EARYfDhZpACAmHyBZJQEfACYpHyZnLysCKTUiKVkANR4iNVk9OzYxRyQGIjAeIllNPkw8BDIjKjJZOUs4LCEFHjo3LScEIyoeI2dNPkw8BDIyKmFKNEkuSAUqMipRG0uwClBYQNMAFAIVChRyEgERAAoTEXIAKB8gHygggAAwIjMiMDOAADMyIjMyfgAJEAEJWUMBEAATAhATZwcBAQACFAECaRcBFQALFVlBAQpAAQgLCghqHBkNAwsEAAtZRRsMAwQAPwYCBA4ABGcADhoYQg8EBRYOBWdGAR1EARYfHRZpACAmHyBZJQEfACYpHyZnLysCKTUiKVkANR4iNVk9OzYxRyQGIjAeIllNPkw8BDIjKjJZOUs4LCEFHjo3LScEIyoeI2dNPkw8BDIyKmFKNEkuSAUqMipRG0uwC1BYQL8AFAIVChRyEgERAAoCEXIAKB8gHygggAAwIjMiMDOAADMyIjMyfgcBAQAJEAEJaUMBEBMBAhQQAmlBAQpAAQgZCghqFwEVABkEFRlpRRsMAwQAHA0LPwYFBA4ABGcaGEIPBAUWDgVXRh0CDkQBFh8OFmkAICYfIFklAR8AJikfJmcvKwIpHiIpWTlLODUsIQYePTs2MUckBiIwHiJpTT5MPAQyIyMyWU0+TDwEMjIjXzo3SjRJLi1IKicKIzIjTxtLsB1QWEDJABQCFQoUchIBEQAKAhFyACgfIB8oIIAAMCIzIjAzgAAzMiIzMn4HAQEACRABCWlDARATAQIUEAJpQQEKQAEIGQoIahcBFQAZBBUZaUUbDAMEABwNCz8GBQQOAARnGhhCDwQFFg4FV0YdAg5EARYfDhZpACAmHyBZJQEfACYpHyZnLysCKTUiKVkANR4iNVk9OzYxRyQGIjAeIllNPkw8BDIjKjJZOUs4LCEFHjo3LScEIyoeI2dNPkw8BDIyKmFKNEkuSAUqMipRG0uwH1BYQMoAFAIVAhQVgBIBEQAKAhFyACgfIB8oIIAAMCIzIjAzgAAzMiIzMn4HAQEACRABCWlDARATAQIUEAJpQQEKQAEIGQoIahcBFQAZBBUZaUUbDAMEABwNCz8GBQQOAARnGhhCDwQFFg4FV0YdAg5EARYfDhZpACAmHyBZJQEfACYpHyZnLysCKTUiKVkANR4iNVk9OzYxRyQGIjAeIllNPkw8BDIjKjJZOUs4LCEFHjo3LScEIyoeI2dNPkw8BDIyKmFKNEkuSAUqMipRG0DLABQCFQIUFYASAREACgARCoAAKB8gHygggAAwIjMiMDOAADMyIjMyfgcBAQAJEAEJaUMBEBMBAhQQAmlBAQpAAQgZCghqFwEVABkEFRlpRRsMAwQAHA0LPwYFBA4ABGcaGEIPBAUWDgVXRh0CDkQBFh8OFmkAICYfIFklAR8AJikfJmcvKwIpNSIpWQA1HiI1WT07NjFHJAYiMB4iWU0+TDwEMiMqMlk5SzgsIQUeOjctJwQjKh4jZ00+TDwEMjIqYUo0SS5IBSoyKlFZWVlZWUC35+fb28rKsbGiopOTfHxwcF5eUlI+PSsrHx8TEwAA5/Ln8e3r2+bb5eHf2tnY18rWytbV1NHPzsyxybHIxsXDwb27urm3taKwoq+trKuqqKaToZOgnJqYl5aVkpGQj3yOfI6NjIuKiYiGhIOBfn1we3B6dnReb15vbm1qaGZlYmBSXVJcWFZRUE9OSUhFRD1KPkorPCs7Ojg2NTQzLy4fKh8pJSMTHhMdGRcAEgASERESISMRTgYcKxM1MzU0NjMzFSMiFRUzFSMVIzUkJjU0NjMyFhUUBiM2NjU0JiMiBhUUFjMEJjU1IzU3MxUzFSMVFDMzFSMlMhYVFAYHFyMnIxUjNRY1NCMjFTMEJjU0NjMyFhUUBiM3FzYzMhYVFSM1NCMiBhUVIzUGNjU0JiMiBhUUFjMHNTM1NDYzMxUjIhUVMxUjFSM1JTMVIwQnByMRMxU2MzIWFRQGIyAmNTQ2MzIXNzMVIycGIyAmNTQ2MzIWFyMmIyIGFRQWMzI2NzMGBiMlFzYzMxUjIgYVFSM1MzMVIyQ2NTQmIyIGFRQWMyA2NTQmIyIGFRQWMzIhHh0mHRQxLzQDuB4eFhceHhcSGBoQERgYEf6hJSFLCDUyHBYjAUMJDAcFDg4MBg4eBwkJ/No7OywrOjorrQkZJSAmMyETFjN1HR0VFxwcF/YhHh0mHRQxLzQC6jMz/socBCg1FR0rODgr/tQ3OComGAclKAQZJQKoOjorJDYGMg0hFhsdFA8YBzIGNiT+1wkUIw8WFRIzjzMz/gQeHhcWHR0WAQ8eHhcWHR0WAcIqEhsgKhMQKpCQCx4XFx4eFxYfDBgRERgYEREYpyUfTwtPMSlJHC7rCggFCQEVExM2GQcHDtc4Kys6OisrOMEWGyskcmsqHBdivJEcFxceHhcXHMwqEhsgKhQPKpGRdS7cFBABAU8SOisrODgrKzoYEb0SFjopKzosIx4dFxYdEA8jLMEWGDAVF2O9vSwdFhcdHRcWHR0WFx0dFxYdAAAAAAIAKP9HA4UCeQA3AEMBgEuwEVBYQBIWAQkCCQEABCwBBgAtAQcGBEwbS7AnUFhAEhYBCQMJAQAELAEGAC0BBwYETBtAEhYBCQMJAQEELAEGAC0BBwYETFlZS7ARUFhAJwsBCAAFAggFaQMBAgAJBAIJaQAGAAcGB2UMCgIEBABiAQEAADMAThtLsCdQWEAuAAMCCQIDCYALAQgABQIIBWkAAgAJBAIJaQAGAAcGB2UMCgIEBABiAQEAADMAThtLsClQWEA5AAMCCQIDCYALAQgABQIIBWkAAgAJBAIJaQAGAAcGB2UMCgIEBAFiAAEBM00MCgIEBABiAAAAMwBOG0uwL1BYQDMAAwIJAgMJgAsBCAAFAggFaQACAAkEAglpAAEABAFaAAYABwYHZQwKAgQEAGIAAAAzAE4bQDMAAwIJAgMJgAsBCAAFAggFaQACAAkEAglpAAEABAFaAAYABwYHZQwKAgQEAGIAAAA2AE5ZWVlZQBk4OAAAOEM4Qj48ADcANiMmJCMSJiMmDQkeKwAWFhUUBgYjIicGBiMiJiY1NDY2MzIXNzMVFBYzMjY1NCYjIgYGFRQWFjMyNxcGIyImJjU0NjYzEjY1NCYjIgYVFBYzAlPCcDhaNFElGEQzOFkxMlo8Ti0IYREVGiKih1mKTUiCVUk3KUpodbtrcMd+HDErJycvKicCeV6qb1ByOkIfHTZgOz5hNjAh3SUjPkF+h0qFVVWCRxpsJ2i5d3a7af4IMiosMy8rLjMAAwAw//MCrwLKAB4AKgAyAIJAEy0sJB0bGhgXCQkDAh4BAgADAkxLsAtQWEAXBAECAgFhAAEBOE0FAQMDAGEAAAA8AE4bS7ANUFhAFwQBAgIBYQABAThNBQEDAwBhAAAAOQBOG0AXBAECAgFhAAEBOE0FAQMDAGEAAAA8AE5ZWUARKysfHysyKzEfKh8pKyIGCRgrBScGIyImJjU0NyYmNTQ2NjMyFhYVFAYHFzY3FwYHFwAGFRQWFzY2NTQmIxI3JwYVFBYzAmBZXIlLbTqPKyQ3ZEE5WTJEQmoWDXsQKVb+cicYIi0mJB8xNJNONS0LUVMvVDV1UitIKzRVMS1QMTViKWArQCJfRE4B/yUbGS4iHjIbGyP+HSuGKD0hKwAAAQAg/zYDRwK8ABEASkuwIVBYQBoABAABAAQBgAIBAAAFXwAFBTJNAwEBATcBThtAGQAEAAEABAGAAwEBAYQCAQAABV8ABQUyAE5ZQAkmERERERAGCRwrASMRIxEjESMRLgI1NDY2MyEDR2KelZ5Ibz1Ee08CGQIq/QwC9P0MAYcCRHJHRnZEAAIAKv/vAkACzQAuADoAt0AaIAEEAyEBBQQXAQYFLgECBwoBAQIJAQABBkxLsC1QWEAoCAEHAAIBBwJpAAQEA2EAAwM4TQAGBgVhAAUFO00AAQEAYQAAADkAThtLsC9QWEAmAAUABgcFBmkIAQcAAgEHAmkABAQDYQADAzhNAAEBAGEAAAA5AE4bQCYABQAGBwUGaQgBBwACAQcCaQAEBANhAAMDOE0AAQEAYQAAADwATllZQBAvLy86LzkqIyQqIiUlCQkdKyQWFRQGBiMiJic3FhYzMjU0IyYmNTQ2NyYmNTQ2MzIWFwcmIyIVFBYzFhYVFAYHJjY1NCYjIgYVFBYzAh4iQndNUo4wSi5fNmxpd4cpIiEliXhGeiZUMVxpLzR5hSIdjzg4MzQ4OTPsPCIvSCguK2giISknAk5DJToMEDomTFYpJFgqKBQRAk9GIzsQMxkXFxoaFxcZAAMAKv/xAwgCywAPAB8ANwBksQZkREBZKQEFBDQqAgYFNQEHBgNMAAAAAgQAAmkABAAFBgQFaQAGCgEHAwYHaQkBAwEBA1kJAQMDAWEIAQEDAVEgIBAQAAAgNyA2MzEtKyclEB8QHhgWAA8ADiYLCRcrsQYARAQmJjU0NjYzMhYWFRQGBiM+AjU0JiYjIgYGFRQWFjMmJjU0NjYzMhYXByYjIgYVFBYzMjcXBiMBLqddXadsbKZcXKZsT3lCQnlPT3lDQ3lPSW4zWzwoSR1DHigoMzMnKyBFQVEPW6ZsbKZbW6ZsbKZbXER7UlJ7RER8UVF8RFNnVzhYMB4dRx4zKSgyIEY+AAAAAAQAEAGpATYCzQALABcAJQAtAS+xBmREtRoBBQkBTEuwC1BYQDcACAcJAghyAAkFAwlwAAUEBAVwCgEBAAIHAQJpAAcGAQQDBwRnCwEDAAADWQsBAwMAYgAAAwBSG0uwEVBYQDgACAcJAghyAAkFBwkFfgAFBAQFcAoBAQACBwECaQAHBgEEAwcEZwsBAwAAA1kLAQMDAGIAAAMAUhtLsB1QWEA5AAgHCQcICYAACQUHCQV+AAUEBAVwCgEBAAIHAQJpAAcGAQQDBwRnCwEDAAADWQsBAwMAYgAAAwBSG0A6AAgHCQcICYAACQUHCQV+AAUEBwUEfgoBAQACBwECaQAHBgEEAwcEZwsBAwAAA1kLAQMDAGIAAAMAUllZWUAeDAwAACopKCYjISAfHh0cGwwXDBYSEAALAAokDAkXK7EGAEQSFhUUBiMiJjU0NjMWNjU0JiMiBhUUFjM2BgcXIycjFSM1MzIWFSYjIxUzMjY15VFSQUFSUUIuODguLjc3LkQPDh8yFgssQxogLBEVFQgJAs1QQkFRUUFCUPo5LzA6OjAvOW8XBjAqKo4bFwwcCAcAAAAEACr/8QMIAssADwAfACoAMwBcQFkABQQDBAUDgAkBAQACBgECaQsBBgAHCAYHZwwBCAAEBQgEZwoBAwAAA1kKAQMDAGEAAAMAUSsrICAQEAAAKzMrMjEvICogKSgnJiQQHxAeGBYADwAOJg0GFysAFhYVFAYGIyImJjU0NjYzEjY2NTQmJiMiBgYVFBYWMxIWFRQGIyMVIxEzFjY1NCYjIxUzAgamXFymbGynXV2nbE95QkJ5T095Q0N5T2hNTTtOYK4PGRkVSEgCy1umbGymW1umbGymW/2CRHtSUntERHxRUXxEAb1JOThJZgFpsRkUFBlaAAAAAAIAPQGQAvwCvAAHABYARUBCFhANAwYBAUwABgECAQYCgAcFAgIChAgEAgABAQBXCAQCAAABXwkDAgEAAU8AABUUExIPDgsKCQgABwAHERERCgYZKxM1IRUjFSM1JTMRIzU3ByMnFxUjETMXPQElXWsB+2dpA0MZQQNqZ04CXl5ezs5e/tRHU1pZUkcBLGwAAAIAJgGyAU4CwwALABcAOLEGZERALQAAAAIDAAJpBQEDAQEDWQUBAwMBYQQBAQMBUQwMAAAMFwwWEhAACwAKJAYJFyuxBgBEEiY1NDYzMhYVFAYjNjY1NCYjIgYVFBYzeVNTQUFTU0EWHBwWFhwcFgGyTTw8TEw8PE1ZGxUUHBwUFRsAAAEAJgHAANgCvAADABNAEAABAQBfAAAAMgFOERACCRgrEzMHIzudNX0CvPz//wAmAcABrgK8ACMC7QDWAAAAAgLtAAAAAQBM/7MA5wLqAAMAGEAVAAABAQBXAAAAAV8AAQABTxEQAgkYKxMzESNMm5sC6vzJAAAAAAIATP+zAOcC6gADAAcAIkAfAAAAAQIAAWcAAgMDAlcAAgIDXwADAgNPEREREAQJGisTMxEjFTMRI0ybm5ubAur+kU/+hwAAAAEAIf+cAi4CvAALAEpLsBVQWEAYAgEAAANfBgUCAwM1TQABAQRfAAQEMgFOG0AWBgUCAwIBAAEDAGcAAQEEXwAEBDIBTllADgAAAAsACxERERERBwkbKwEVIxEjESM1MzUzFQIuuZu5uZsCBYn+IAHgibe3AAAAAAIAF//6AdYCxwAaACMAOUA2GxcNCwcBBgIDAgEAAgJMAAEAAwIBA2kEAQIAAAJZBAECAgBhAAACAFEAACEfABoAGSsjBQYYKyQ3FwYjIiYnBwYjNTY3NTQ2MzIWFRQGBxYWMyc2NjU0IyIGFQFxLydNTmRoAhUuBB0qZFdZZHZ5BSsrXjkwMxocfhN3IFtXAwaFAwjqT1tiWHafKikn3RpSP0EfHgAAAAEAMv+SAkQCvAATADBALQkBBwYBAAEHAGcFAQEEAQIDAQJnAAMDCF8ACAgyA04TEhEREREREREREAoJHysBIxUzFSMVIzUjNTM1IzUzNTMVMwJEurq6nrq6urqeugGKvYK5uYK9grCwAAAAAAIAOv/5AkwCSgAXAB4AQUA+HhsCBQQHBgEDAAMCTAACAAQFAgRpAAUGAQMABQNnAAABAQBZAAAAAWEAAQABUQAAHRwaGAAXABcmJSIHBhkrExUWMzI2NxcGBiMiJiY1NDY2MzIWFRQHAiMiBxUhNbk8UUBcIiUpbkxQekJCeVCBhgGsWlQ4ARsBB7AvLTAdOjVJhllZh0mRixoNARQvtrwAAAAABABMAAAERgLDAAsAFwAjACcA9kAKEQEIARcBCQgCTEuwIVBYQCgACAwBCQMICWcLAQcHAF8FAgIAABpNCgEBAQZhAAYGIU0EAQMDGwNOG0uwLVBYQCwACAwBCQMICWcFAQICGk0LAQcHAGEAAAAaTQoBAQEGYQAGBiFNBAEDAxsDThtLsC9QWEAqAAALAQcGAAdpAAgMAQkDCAlnCgEBAQZhAAYGIU0FAQICA18EAQMDGwNOG0AqAAALAQcGAAdpAAgMAQkDCAlnCgEBAQZhAAYGIU0FAQICA18EAQMDHQNOWVlZQCIkJBgYAAAkJyQnJiUYIxgiHhwWFRQTEA8ODQALAAokDQcXKwAmNTQ2MzIWFRQGIyU1MxEjARcVIxEzAQAGFRQWMzI2NTQmIwM1IRUDYldXRkdXV0f+cqmO/r4Dqo4BQgF1Hh4XGB4dGY8BHwGhT0FBUVFBQU8j+P1EAZ+r9AK8/l4BTB0YFx0dFxgd/q9cXAAA//8ATP+7AOcC8gEGAu8ACAAIsQABsAiwNSsAAAACAC3/9QKtAscAKAAzARpADxABBgUCAQgGBwMCAAgDTEuwD1BYQCcAAwQFBANyAAUHAQYIBQZnAAQEAmEAAgIfTQkBCAgAYQEBAAAbAE4bS7AhUFhAKAADBAUEAwWAAAUHAQYIBQZnAAQEAmEAAgIfTQkBCAgAYQEBAAAbAE4bS7AtUFhALAADBAUEAwWAAAUHAQYIBQZnAAQEAmEAAgIfTQAAABtNCQEICAFhAAEBIgFOG0uwL1BYQCoAAwQFBAMFgAACAAQDAgRpAAUHAQYIBQZnAAAAG00JAQgIAWEAAQEiAU4bQCoAAwQFBAMFgAACAAQDAgRpAAUHAQYIBQZnAAAAHU0JAQgIAWEAAQEiAU5ZWVlZQBEpKSkzKTIlESQiEiwiJAoHHiskFjcVBiMiJwYjIiYmNTQ2NyYmNTQ2NjMyFhUjJiYjIgYVFBYzIRUjFQY2NTUjIgYVFBYzAmQlJBUTWSRMi052QDsxKC5FfFF/j5kBPTg3PkA3AU9B40mDPEJCOrAnBI4DRk0xWz03WxcTTTI9XTRtYiYpKyYnLX9KXzUsSi0oKS0AAAL+RgIq/8UCxQALABcAMrEGZERAJwIBAAEBAFkCAQAAAWEFAwQDAQABUQwMAAAMFwwWEhAACwAKJAYJFyuxBgBEACY1NDYzMhYVFAYjMiY1NDYzMhYVFAYj/nUvMCAhLy8hvS8wICEwMCECKiklJCkpJCUpKSUkKSkkJSkAAAAAAf8gAir/yQLGAAsAJrEGZERAGwAAAQEAWQAAAAFhAgEBAAFRAAAACwAKJAMJFyuxBgBEAiY1NDYzMhYVFAYjsDAwJSUvLyUCKiwiIiwsIiIsAAAAAf5kAij/UAK8AAMAJrEGZERAGwAAAQEAVwAAAAFfAgEBAAFPAAAAAwADEQMJFyuxBgBEASczF/7NaalDAiiUlAAAAAAB/wcCKP/zArwAAwAgsQZkREAVAAABAQBXAAAAAV8AAQABTxEQAgkYK7EGAEQDMwcjtqlpgwK8lAAAAAAC/kMCKP/0ArwAAwAHACWxBmREQBoCAQABAQBXAgEAAAFfAwEBAAFPEREREAQJGiuxBgBEATMHIyUzByP+h5tegQEVnGyDAryUlJQAAf5CAib/zgK8AAYAIbEGZERAFgIBAAIBTAACAAKFAQEAAHYREhADCRkrsQYARAMjJwcjNzMyjTo4jZVhAiY1NZYAAAAB/kECJv/NArwABgAhsQZkREAWBgEBAAFMAgEAAQCFAAEBdhEREAMJGSuxBgBEAzMHIyczF8CNlmGVjTgCvJaWNQAAAAH+gwIn/80CvAANAFGxBmRES7AbUFhAGAIBAAEBAHAAAQMDAVkAAQEDYgQBAwEDUhtAFwIBAAEAhQABAwMBWQABAQNiBAEDAQNSWUAMAAAADQAMEiISBQkZK7EGAEQAJjUzFBYzMjY1MxQGI/7bWHYaFRYadVhNAidPRhYaGhZGTwAAAAL+tQIb/8wDEgALABcAOLEGZERALQAAAAIDAAJpBQEDAQEDWQUBAwMBYQQBAQMBUQwMAAAMFwwWEhAACwAKJAYJFyuxBgBEAiY1NDYzMhYVFAYjNjY1NCYjIgYVFBYz/U5OPT5OTj4TFxcTExcXEwIbRTY3RUU3NkVTFhISFxcSERcAAAH+WgIs/74CwwATAD+xBmREQDQPAQIBEAYCAAIFAQMAA0wAAgADAlkAAQAAAwEAaQACAgNhBAEDAgNRAAAAEwASIiQiBQkZK7EGAEQCJyYjIgcnNjYzMhcWMzI3FwYGI9ImHxIeDlEPPSYiIhgaHg5QDjkmAiwVESE3KzAUESI0MDAAAAH+igI2/7YCpwADACCxBmREQBUAAAEBAFcAAAABXwABAAFPERACCRgrsQYARAEhFSH+igEs/tQCp3EAAAH/FgIO/8oDKAANACaxBmREQBsNAQABAUwAAQAAAVcAAQEAYQAAAQBRFSQCCRgrsQYARAIWFRQGIyImNTQ2NzMHUx0yKCkxHCdVGwKpKRwmMDIoIUxTdwAB/2D+9f/4/8wADQAtsQZkREAiBwEAAQFMAgEBAAABWQIBAQEAXwAAAQBPAAAADQAMFQMJFyuxBgBEBhYVFAYHIzcmJjU0NjMyKhQdTBMWGCshNCceFztAXAQdFx0mAAAB/rH/Cf+/ABYAFwBvsQZkREAUFAECAxMJAgECCAEAAQNMFhUCA0pLsAtQWEAcBAEDAgEDcAACAQKFAAEAAAFZAAEBAGIAAAEAUhtAGwQBAwIDhQACAQKFAAEAAAFZAAEBAGIAAAEAUllADAAAABcAFyQkJAUJGSuxBgBEBhYVFAYjIiYnNxYzMjY1NCYjIgcnNxcHdjVLPSpGFjUgKBQYGBUVDh4mYRYrNiwvOxsZPRsRDg8SCBxjCDYAAAH/B/9E/+8ALgARADKxBmREQCcPAQEAAUwOBgUDAEoAAAEBAFkAAAABYQIBAQABUQAAABEAECoDCRcrsQYARAYmNTQ2NxcGFRQWMzI2NxcGI8A5Qzo9RRANChcJLDVIvDAqLU0WLh8fCw8JB0UvAP//ADYCKAEiArwAAwL7AS8AAAAA//8AHQInAWcCvAADAv8BmgAAAAD//wATAiYBnwK8AAMC/gHSAAAAAP//ACn/CQE3ABYAAwMFAXgAAAAA//8ADQImAZkCvAADAv0BywAAAAD//wAyAioBsQLFAAMC+AHsAAAAAP//ACUCKgDOAsYAAwL5AQUAAAAA////jAIoAHgCvAADAvoBKAAAAAD//wBEAigB9QK8AAMC/AIBAAAAAP//AEMCNgFvAqcAAwMCAbkAAAAA//8Aff9EAWUALgADAwYBdgAAAAD//wAyAhsBSQMSAAMDAAF9AAAAAP//ACoCLAGOAsMAAwMBAdAAAAAAAAL+PQL4/84DmwALABcAKkAnAgEAAQEAWQIBAAABYQUDBAMBAAFRDAwAAAwXDBYSEAALAAokBgcXKwAmNTQ2MzIWFRQGIzImNTQ2MzIWFRQGI/5uMTEjIjIyIscyMiIjMTEjAvgsJiYrKyYmLCwmJisrJiYsAAAAAAH/HgL1/8wDlwALAB5AGwAAAQEAWQAAAAFhAgEBAAFRAAAACwAKJAMHFysCJjU0NjMyFhUUBiOxMTEmJjExJgL1LiMkLS0kIy4AAAAB/uEC+//bA4sAAwAeQBsAAAEBAFcAAAABXwIBAQABTwAAAAMAAxEDBxcrAyczF69wsEoC+5CQAAH/BwL7AAEDiwADABhAFQAAAQEAVwAAAAFfAAEAAU8REAIHGCsDMwcjr7BwigOLkAAAAAAC/kEC9v/0A4oAAwAHAB1AGgIBAAEBAFcCAQAAAV8DAQEAAU8REREQBAcaKwEzByMlMwcj/oieYYQBGplshAOKlJSUAAH+RwL7/8kDiwAGACBAHQIBAAIBTAACAAACVwACAgBfAQEAAgBPERIQAwcZKwMjJwcjNzM3kDExkIxrAvsuLpAAAAAAAf5GAv7/yAOOAAYAIUAeBgEBAAFMAgEAAQEAVwIBAAABXwABAAFPEREQAwcZKwMzByMnMxfIkItrjJAxA46QkC4AAAAB/oIC+P/MA40ADQBJS7AbUFhAGAIBAAEBAHAAAQMDAVkAAQEDYgQBAwEDUhtAFwIBAAEAhQABAwMBWQABAQNiBAEDAQNSWUAMAAAADQAMEiISBQcZKwAmNTMUFjMyNjUzFAYj/tpYdhoVFhp1WE0C+E9GFhoaFkZPAAAAAf5YAvb/wAONABMAN0A0DwECARAGAgACBQEDAANMAAIAAwJZAAEAAAMBAGkAAgIDYQQBAwIDUQAAABMAEiIkIgUHGSsCJyYjIgcnNjYzMhcWMzI3FwYGI9ImHxQeDlEPPSYkIhwYHg5QDjolAvYVESE3KzAUESI0LzEAAAH+ewME/8QDdQADABhAFQAAAQEAVwAAAAFfAAEAAU8REAIHGCsBIRUh/nsBSf63A3VxAAAB/rD/Cf/AABYAFwAwQC0TCQIBAggBAAECTBcWFRQEAkoAAgEChQABAAABWQABAQBhAAABAFEkJCQDBxkrBhYVFAYjIiYnNxYzMjY1NCYjIgcnNxcHdTVMPSpGFzUhKBUYGRUZCh4lYxYsNisvOxsaPRsQDg8RBxxjCDYAAf8H/zf/8gAwABEAQ0AMDgEBAAFMDQYFAwBKS7AnUFhADAAAAAFhAgEBAR4BThtAEQAAAQEAWQAAAAFhAgEBAAFRWUAKAAAAEQAQKgMHFysGJjU0NjcXBhUUFjMyNxcGBiO+O0Y5Pj4ODRIQLxs8Jck0LjFPFzAjHwsNC00YFQAC/lUCKv/BAsUACwAXACRAIQUDBAMBAQBhAgEAADgBTgwMAAAMFwwWEhAACwAKJAYJFysAJjU0NjMyFhUUBiMyJjU0NjMyFhUUBiP+gy4uHyAtLSCyLS0gIC0tIAIqKiQjKiojJCoqJCMqKiMkKgAAAf5zAij/TwK8AAMAGUAWAgEBAQBfAAAAMgFOAAAAAwADEQMJFysBJzMX/stYqTMCKJSUAAH/CAIo/+QCvAADABNAEAABAQBfAAAAMgFOERACCRgrAzMHI8WpWIQCvJQAAf5OAib/wQK8AAYAG0AYAgEAAgFMAQEAAAJfAAICMgBOERIQAwkZKwMjJwcjNzM/iy8ui4dmAiY1NZYAAf6NAif/xAK8AA0AHkAbAAEEAQMBA2YCAQAAMgBOAAAADQAMEiISBQkZKwAmNTMUFjMyNjUzFAYj/t9SchYTFBVzUkoCJ09GFxkZF0ZPAAAB/mACLP+4AsMAEwAxQC4PAQIBEAYCAAIFAQMAA0wAAgQBAwIDZQAAAAFhAAEBMgBOAAAAEwASIiQiBQkZKwInJiMiByc2NjMyFxYzMjcXBgYj1iIbEB0RTw89JiAeGRMdEE8OOSYCLBURIDYrMBQRIDIwMAAAAAAB/pUCNv+qAqcAAwAtS7AXUFhACwABAQBfAAAAMgFOG0AQAAABAQBXAAAAAV8AAQABT1m0ERACCRgrASEVIf6VARX+6wKncQAB/xH/RP/oACYAEQAqQCcOAQEAAUwNBgUDAEoAAAEBAFkAAAABYQIBAQABUQAAABEAECoDBhcrBiY1NDY3FwYGFRQzMjcXBgYjuzRCMjsfHBgRDysXPiC8LictTRMmECARGQxDFBcAAAH+SQL7/8cDiwAGACBAHQIBAAIBTAACAAACVwACAgBfAQEAAgBPERIQAwkZKwMjJwcjNzM5kC8vkIZxAvstLZAAAAAAAf6AAwT/vwN1AAMAGEAVAAABAQBXAAAAAV8AAQABTxEQAgkYKwEhFSH+gAE//sEDdXEAAAH+GAIc/14CyQANACVAIgoJAwIEAEoAAAEBAFkAAAABYQIBAQABUQAAAA0ADCUDBxcrACYnNxYWMzI2NxcGBiP+d1INYAcfHR0fB2AOUkMCHEdKHCMeHiMcSkcAAf46AvH/owOjAAsAJUAiCQgCAQQASgAAAQEAWQAAAAFhAgEBAAFRAAAACwAKJAMHFysAJzcWFjMyNjcXBiP+WB5jBygjIycIYhyYAvGWHCMgICMclgAA//8AO/8TAi8CvAAiALEAAAADAL0BEwAA//8ATP/yA8ADiwAiAC8AAAADADkBPQAA//8ALQIOAOEDKAADAwMBFwAAAAAAAQAAAAIAQVyWBlJfDzz1AAcD6AAAAADaTw5QAAAAANpPH9j+GP7kBMAD4AAAAAcAAgAAAAAAAAABAAAD5v7WANwE5P4Y/14EwAABAAAAAAAAAAAAAAAAAAADMQKSACcBQgAAAOoAAAMT//kDE//5AxP/+QMT//kDE//5AxP/+QMT//kDE//5AxP/+QMT//kEBP/iBAT/4gLWAEwCwAAkAsAAJALAACQCwAAkAsAAJALAACQC9wBMAwIACwL3AEwDAgALApoATAKaAEwCmgBMApoATAKaAEwCmgBMApoATAKaAEwCmgBMApoATAJ8AEwC8AAkAvAAJALwACQC8AAkAvAAJAMJAEwDGAAUAwkATAE9AEwEAQBMAT0ATAE9//kBPf/gAT3/1gE9AEgBPf/xAT3//wE9ADMBPf/pAsQAFALEABQCxAAUAqwATAKsAEwCYQBMAmEATAJhAEwCYQBMAmEATAJpAA4DnABMAwkATAMJAEwDCQBMAwkATAMJAEwDCQBMAzoAJAM6ACQDOgAkAzoAJAM6ACQDOgAkAzoAJAM6ACQDPgAkAz4AJAM6ACQEBAAkAroATAK6AEwDOAAkAtQATALUAEwC1ABMAtQATAKTACACkwAgApMAIAKTACACkwAgApMAIALeAEwCbgAQAm4AEAJuABACbgAQAm4AEAL+AEEC/gBBAv4AQQL+AEEC/gBBAv4AQQL+AEEC/gBBAv4AQQL+AEEC/gBBAuP/+wRTAAkEUwAJBFMACQRTAAkEUwAJArb//gLG//oCxv/6Asb/+gLG//oCxv/6AncAGQJ3ABkCdwAZAncAGQM6ACQCfAAfAnwAHwJ8AB8CfAAfAnwAHwJ8AB8CfAAfAnwAHwJ8AB8CfAAfA9MAHwPTAB8CfAA7AgYAHwIGAB8CBgAfAgYAHwIGAB8CBgAfAn0AHwJKAB8CxwAfAn8AIgJLAB8CSwAfAksAHwJLAB8CSwAfAksAHwJLAB8CSwAfAksAHwJLAB8BoAAVAmYAHwJmAB8CZgAfAmYAHwJmAB8CagA7AmoAAgJq/8IBEwAuARMAOwETADsBE//vARP/0AET/9MBEwA1ARP/+QIoAC4BE///ARMAKQET/94BFf+1ARX/tQEV/7UBFf+1AicAOwInADsCJwA7ARMAOwETADsBcwA7ARMAOwG3ADsBQQARA5QAOwJqADsCagA7AxMAPwJqADsCagA7AmoAOwJqADsCXQAfAl0AHwJdAB8CXQAfAl0AHwJdAB8CXQAfAl0AHwJZAB8CWQAfAl0AHwO9AB8CfAA7AnsAOwJ9AB4BzQA7Ac0AOwHNACwBzQA7AfoAFwH6ABcB+gAXAfoAFwH6ABcB+gAXAmwAOwFaABUBqAAXAagAFwH6ABcBqAAXAagAFwJmADUCZgA1AmYANQJmADUCZgA1AmYANQJmADUCZgA1AmYANQJmADUCZgA1AkcAAgM9AAIDPQACAz0AAgM9AAIDPQACAiUAAwI/AAICPwACAj8AAgI/AAICPwACAfUAGQH1ABkB9QAZAfUAGQLeAEwCNQAbAjUAGwI1ABsCNQAbAjUAGwI1ABsCNQAbAjUAGwI1ABsCNQAbA3UAGwN1ABsCewAfAnsAHwJ7AB8CewAfAnsAHwJmADUCZgA1AmYANQJmADUCZgA1AZ8AFQJ8AB8CfAAfAnwAHwJ8AB8CfAAfAjUALgEi/9QBIv/UASL/1AEi/9QBKwA7ASsAOwF9ADsBKwA7AbcAOwFIABEBmgA7AZoAOwGaAB4BmgA7AXsAFwF7ABcB/QAXAXsAFwF7ABcCYAA1AmAANQJgADUCYAA1AmAANQJgADUCYAA1AmAANQJgADUCYAA1AmAANQJjADUCYwA1AmMANQJjADUCYwA1AjUAGwI1ABsCNQAbAjUAGwI1ABsCNQAbAjUAGwI1ABsCNQAbAjUAGwN1ABsDdQAbAnsAHwJ7AB8CewAfAnsAHwJ7AB8CZgA1AmYANQJmADUCZgA1AmYANQMXABUCsQAVAq4AFQMXABUCsQAVAsYAFQHUACcBuQAnAxP/+QLUAEwC1gBMAkgATAJIAEwCSABMA08ADAKaAEwCmgBMApoATAPz//ICgQAQAwoATAMKAEwDCgBMAqwATAKsAEwDFAASA5wATAMJAEwDOgAkAw4ATAK6AEwCwAAkAm4AEALRAAcC0QAHA44AJAK2//4C3wA5A0AATAR3AEwErQBMAwkATALaAEwDTQAQA+YATASaABIEeABMApMAIALAACQCwAATAT0ATAE9/9YCxAAUAzQAEARgAEwC2wASAykAEAQE/+IDYgAWAvj/+QPDACQDTwAMAwUAEgLXADkEiQASA2IAFgL4//kDwwAkA2IAFgL4//kDwwAkAnwAHwJeACACMgA7Ac8AOwHPADsBzwA7AnMADQJLAB8CSwAfAksAHwMa//cB7gAVAmUAOwJlADsCZQA7AicAOwInADsCZQAWAtIAOwJmADsCXQAfAmYAOwJ8ADsCBgAfAfYAFgI/AAICPwACAwcAHwIlAAMCOwAmAoIAOwNQADsDawA7AmUAOwIfADsCfwATAzIAOwNtABYDYgA7AfoAFwIHAB8CBwAQARMALgET/9MBFf+1AmoAAgNMADsCMQAUAmoAAgPTAB8CVQAsAfoAGgJ7AB8DG//3Ah8AEwJmADUCZgA1AmYANQInADsCQAACAmoAOwOUADsCkAA1A5QANQO+ADUCJAA1AnAACgNMADsCNQAbAmYANQJmADUDdQAbAngAOgJzAA0CYAAWAmMANQJjADUCOwAmA2kAFgJ8AB8CFAATAmYAOwNqADsCVQAsAfoAGgJ7AB8DG//3Ah8AEwJmADUCZgA1AmYANQInADsCQAACAmoAOwOUADsCkAA1A5QANQO+ADUCJAA1AnAACgNMADsCNQAbAlUALAH6ABoCewAfAxv/9wIfABMCZgA1AmYANQJmADUCJwA7AkAAAgJqADsDlAA7AmYANQJmADUCkAA1A5QANQO+ADUCJAA1AnAACgNMADsDdQAbAmwAOwK3ABMC1QAyAc0AKwKtADICpQAqAqoAFAKVADECtAA0AkcAGQK4AC8CsQApAssALwLLAGUCywA/AssANgLLACQCywBMAssAOQLLAFcCywAuAssALgGTACMBIAAeAXYAJAF6AB0BiQAWAXcAKAF/ACkBRQAbAYcAIQF/ACEBkwAjASAAHgF2ACQBegAdAYkAFgF3ACgBfwApAUUAGwGHACEBfwAhAZMAIwEgAB4BdgAkAXoAHQGJABYBdwAoAX8AKQFFABsBhwAhAX8AIQGTACMBIAAeAXYAJAF6AB0BiQAWAXcAKAF/ACkBRQAbAYcAIQF/ACEArf9eA2IAHgNmAB4DngAkA1YAHgOSAB0DYgAeA5oAJAOeAB0DrQAWA2sAHgOkACgDMAAeA3IAHgOuAB0DqwAoA2AAGwNrAB4BCwArAQwALAELACsBDAAsAwMAKwEyAD8BHgA2AlgAHQJUACEBEwAvAagARgGmACkCWP/4AtAAJAIHABgCBwAYASUANwGmAEUBbAAgAWwAEQF1AB0BdQAbAWoARgFqACMBegAlAXoAGgF/ACMBfwAgAXkATQF5ACsB+QA6AfkAOgJeADkCtwA5AhsAGwH5ADoCXgA5ArcAOQEMACwBxgAsAcgAPQHgAD4BGABAARMAPwJPACACTwAjAXUAIAF2ACMBwAA+AP8APgJ0ADACdQA4AZsAMAGbADgA6gAAAK8AAAAAAAACBgAfAnEANAKTACACegAUAcf/6gK1AA4CZgAQApQAAQKYADQDAwAYAssAbwLLADUCywA+AssAVALLAEwCy//9ARsAMAHr/+8CIQA6AgwAOgHTAC8COgA6AiQAOgI3ADoBqQA2AakANAHNADYBzQA4AiYAOgIaADQCawA0Ah8AOgJ5ACADKAAxArEAHwH7//0DQQAyAwz/+QK1AEwCZAArAngABQJKAB8CbAA7A1YAJATkACQCHAAeAggAIgJ8ADoCBwAiAhwAHgIIADkCfAAgAgcAOAJyACAEiAAyA5cAKAK4ADADaAAgAnEAKgMzACoBRgAQAzMAKgNDAD0BdQAmAPEAJgHHACYBMwBMATMATAJPACECBQAXAnYAMgJ7ADoEbQBMATMATALaAC0AAP5GAAD/IAAA/mQAAP8HAAD+QwAA/kIAAP5BAAD+gwAA/rUAAP5aAAD+igAA/xYAAP9gAAD+sQAA/wcBCwA2AX4AHQGwABMBVgApAbkADQISADIA/QAlAQ//jAHnAEQBvABDAYsAfQGMADIBvwAqAAD+PQAA/x4AAP7hAAD/BwAA/kEAAP5HAAD+RgAA/oIAAP5YAAD+ewAA/rAAAP8HAAD+VQAA/nMAAP8IAAD+TgAA/o0AAP5gAAD+lQAA/xEAAP5JAAD+gAAA/hgAAP46AlgAAAIoADsEAQBMAlgAAAEOAC0AAABmAGYAZgCkALAAvADIANQA4ADsAVwBwgHOAioCNgKeAvQDAAMMA4oDlgOiA+4ETgRaBGIEogSuBLoExgTSBN4E6gT2BQIFfAW0BhwGKAY0BkAGTAaGBuIG7gcQBxwHKAc0B0AHTAdYB2QHcAfCB84IGggmCDIIZghyCJwIqAjgCOwJOAl0CbIJ6An0CgAKDAp8CogK4ArsCvgLBAsQCxwLKAs0C7YLwgvODJwM7A1ADaAN8A38DggOFA54DoQOkA8cDygPNA++D/AQMhA+EMAQzBEKERYRIhEuEToRRhFSEV4RvhHQEdwSDBJMElgSZBJwEnwSuBLuEvoTBhMSEx4TWBNkE3ATfBQKFIwUmBSkFLAUvBTIFNQVXBVoFXQWnhaqFywXbhd6F4YYJBgwGDwYthkcGaAaLhqCGo4amhqmGrIavhrKGtYa4htOG6IcKhw2HEgc9B0AHUgdpB22HfYeGB4kHjAePB5IHlQeYB5sHnge3h7qH0Yfgh+OH5of0B/cH+QgBiAYIEYgUiBkIJghCCFgIWwheCGEIZAiGCIkImYiciJ+IooiliKiIq4iuiMeIyojNiQAJHok4CVkJbolxiXSJd4mWiZmJnInKCc0J0AnzigeKFYonijoKYwpmCnwKfwqCCoUKiAqLCo4KkQqkCqcKqgq1isUKyArLCs4K0QrfiuwK7wryCvUK+AsGiwmLDIsPixGLNYs4izuLPotBi0SLR4tlC2gLawujC6YLzYvQi9OMBYwIjB+MIowljCiMK4xADGoMbQxwDKWMqIyrjL4MxQzIDMsM2AzcjO6M8Yz2DQeNEg0VDRgNGw0qDT0NVQ1uDXENfI1/jYKNhY2IjYuNjo2RjaUNqA2rDb6NwY3EjceNyo3Mjc+N0o3VjdiN243ejfwN/w4CDgQOBw4JDgwODw5BDkQORg5JDkwOTw5SDoSOog6+jtsO+w8TDzgPSo9Mj2YPaA92j3mPjY+sj66PsY+0j8kP6Y/5D/wP/xABEAQQF5AZkBuQHZAsEC4QMBAyEEiQS5BokGqQfxCRkKKQtxDPEOeRAhEFESSRTpFQkWwRiZGLkY6RkJGvkdiR8hITEhUSLhI9kmMSf5KQkqOSwJLCksSSxpLIksqSzJLOkui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AFMAZQByAGkAZgAgAEYAbwBuAHQAaAB0AHQAcAA6AC8ALwBmAG8AbgB0AGYAYQBiAHIAaQBjAC4AYwBvAG0ALwBoAHQAdABwADoALwAvAGYAbwBuAHQAZgBhAGIAcgBpAGMALgBjAG8AbQAvAEUAbgBkACAAdQBzAGUAcgAgAGwAaQBjAGUAbgBzAGUAIABhAGcAcgBlAGUAbQBlAG4AdAAgAGEAdgBhAGkAbABhAGIAbABlACAAYQB0ACAAaAB0AHQAcAA6AC8ALwB3AHcAdwAuAGYAbwBuAHQAZgBhAGIAcgBpAGMALgBjAG8AbQBoAHQAdABwADoALwAvAHcAdwB3AC4AZgBvAG4AdABmAGEAYgByAGkAYwAuAGMAbwBtAE4AZQB4AGEASABlAGEAdgB5AAAAAgAAAAAAAP+1ADIAAAAAAAAAAAAAAAAAAAAAAAAAAAMxAAAAAgADACQAyQECAMcAYgCtAQMBBABjAK4AkAEFACUAJgD9AP8AZAEGAQcAJwDpAQgBCQAoAGUBCgELAMgAygEMAMsBDQEOACkAKgD4AQ8BEAERACsBEgETACwBFADMARUAzQDOAPoAzwEWARcBGAAtARkBGgAuARsALwEcAR0BHgEfAOIAMAAxASABIQEiASMAZgAyANABJADRAGcA0wElASYAkQEnAK8AsAAzAO0ANAA1ASgBKQEqADYBKwDkAPsBLAEtAS4ANwEvATABMQEyADgA1AEzANUAaADWATQBNQE2ATcBOAA5ADoBOQE6ATsBPAA7ADwA6wE9ALsBPgA9AT8A5gFAAUEARABpAUIAawBsAGoBQwFEAG4AbQCgAUUARQBGAP4BAABvAUYBRwBHAOoBSAEBAEgAcAFJAUoAcgBzAUsAcQFMAU0ASQBKAPkBTgFPAVAASwFRAVIATADXAHQBUwB2AHcBVAB1AVUBVgFXAVgATQFZAVoBWwBOAVwBXQBPAV4BXwFgAWEA4wBQAFEBYgFjAWQBZQFmAHgAUgB5AWcAewB8AHoBaAFpAKEBagB9ALEAUwDuAFQAVQFrAWwBbQBWAW4A5QD8AW8BcACJAXEAVwFyAXMBdAF1AFgAfgF2AIAAgQB/AXcBeAF5AXoBewBZAFoBfAF9AX4BfwBbAFwA7AGAALoBgQBdAYIA5wGDAYQBhQGGAYcBiAGJAYoBiwGMAY0BjgGPAZABkQGSAZMBlAGVAZYBlwGYAZkBmgGbAZwBnQGeAZ8BoAGhAaIBowGkAaUBpgGnAagBqQGqAasBrAGtAa4BrwGwAbEBsgGzAbQBtQG2AbcBuAG5AboBuwG8Ab0BvgG/AcABwQHCAcMBxAHFAcYBxwHIAckBygHLAcwBzQHOAc8B0AHRAdIB0wHUAdUB1gHXAdgB2QHaAdsAwADBAdwB3QHeAJ0AngHfAeAB4QHiAeMB5AHlAeYB5wHoAekB6gHrAewB7QHuAe8B8AHxAfIB8wH0AfUB9gH3AfgB+QH6AfsB/AH9Af4B/wIAAgECAgIDAgQCBQIGAgcCCAIJAgoCCwIMAg0CDgIPAhACEQISAhMCFAIVAhYCFwIYAhkCGgIbAhwCHQIeAh8CIAIhAiICIwIkAiUCJgInAigCKQIqAisCLAItAi4CLwIwAjECMgIzAjQCNQI2AjcCOAI5AjoCOwI8Aj0CPgI/AkACQQJCAkMCRAJFAkYCRwJIAkkCSgJLAkwCTQJOAk8CUAJRAlICUwJUAlUCVgJXAlgCWQJaAlsCXAJdAl4CXwJgAmECYgJjAmQCZQJmAmcCaAJpAmoCawJsAm0CbgJvAnACcQJyAnMCdAJ1AnYCdwJ4AnkCegJ7AnwCfQJ+An8CgAKBAoICgwKEAoUChgKHAogCiQKKAosCjAKNAo4CjwKQApECkgKTApQClQKWApcCmAKZAJsAEwAUABUAFgAXABgAGQAaABsAHAKaApsCnAKdAp4CnwKgAqECogKjAqQCpQKmAqcCqAKpAqoCqwKsAq0CrgKvArACsQKyArMCtAK1ArYCtwK4ArkCugK7ArwCvQK+Ar8CwALBAsICwwLEAsUCxgLHAsgCyQLKAssAvAD0AswCzQD1APYCzgLPAtAC0QLSAtMC1ALVAtYC1wLYAtkAEQAPAB0AHgCrAAQAowAiAKIAwwCHAA0C2gAGABIAPwLbAtwACwAMAF4AYAA+AEAC3QLeAt8C4ALhAuIAEALjALIAswBCAuQC5QLmAMQAxQC0ALUAtgC3AKkAqgC+AL8ABQAKAucC6ALpAuoC6wLsAu0AhAC9AAcC7gCmAu8C8ALxAIUAlgLyAvMC9AL1AvYC9wL4AvkADgDvAPAAuAAgAI8AIQAfAJUAlACTAKcAYQCkAEEAkgL6AJwC+wL8AJoAmQClAJgC/QAIAMYC/gL/AwADAQMCAwMDBAMFALkDBgAjAAkAiACGAIsAigMHAIwAgwMIAwkAXwDoAIIDCgDCAwsDDAMNAw4DDwMQAxEDEgMTAxQDFQMWAxcDGAMZAxoDGwMcAx0AjQDbAOEA3gDYAI4A3ABDAN8A2gDgAN0A2QMeAx8DIAMhAyIDIwMkAyUDJgMnAygDKQMqAysDLAMtAy4DLwMwAzEDMgMzAzQDNQM2AzcDOAM5AzoGQWJyZXZlB0FtYWNyb24HQW9nb25lawdBRWFjdXRlC0NjaXJjdW1mbGV4CkNkb3RhY2NlbnQGRGNhcm9uBkRjcm9hdAZFYnJldmUGRWNhcm9uCkVkb3RhY2NlbnQHRW1hY3JvbgdFb2dvbmVrC0djaXJjdW1mbGV4B3VuaTAxMjIKR2RvdGFjY2VudARIYmFyC0hjaXJjdW1mbGV4AklKBklicmV2ZQdJbWFjcm9uB0lvZ29uZWsGSXRpbGRlC3VuaTAwQTQwMzAxC0pjaXJjdW1mbGV4B3VuaTAxMzYGTGFjdXRlBkxjYXJvbgd1bmkwMTNCBExkb3QGTmFjdXRlBk5jYXJvbgd1bmkwMTQ1A0VuZwZPYnJldmUNT2h1bmdhcnVtbGF1dAdPbWFjcm9uC09zbGFzaGFjdXRlBlJhY3V0ZQZSY2Fyb24HdW5pMDE1NgZTYWN1dGULU2NpcmN1bWZsZXgHdW5pMDIxOAd1bmkxRTlFBFRiYXIGVGNhcm9uB3VuaTAxNjIHdW5pMDIxQQZVYnJldmUNVWh1bmdhcnVtbGF1dAdVbWFjcm9uB1VvZ29uZWsFVXJpbmcGVXRpbGRlBldhY3V0ZQtXY2lyY3VtZmxleAlXZGllcmVzaXMGV2dyYXZlC1ljaXJjdW1mbGV4BllncmF2ZQZaYWN1dGUKWmRvdGFjY2VudAZRLnNzMDIGYWJyZXZlB2FtYWNyb24HYW9nb25lawdhZWFjdXRlC2NjaXJjdW1mbGV4CmNkb3RhY2NlbnQGZGNhcm9uBmVicmV2ZQZlY2Fyb24KZWRvdGFjY2VudAdlbWFjcm9uB2VvZ29uZWsLZ2NpcmN1bWZsZXgHdW5pMDEyMwpnZG90YWNjZW50BGhiYXILaGNpcmN1bWZsZXgGaWJyZXZlCWkubG9jbFRSSwJpagdpbWFjcm9uB2lvZ29uZWsGaXRpbGRlB3VuaTAyMzcLdW5pMDA2QTAzMDELamNpcmN1bWZsZXgHdW5pMDEzNwxrZ3JlZW5sYW5kaWMGbGFjdXRlBmxjYXJvbgd1bmkwMTNDBGxkb3QGbmFjdXRlC25hcG9zdHJvcGhlBm5jYXJvbgd1bmkwMTQ2A2VuZwZvYnJldmUNb2h1bmdhcnVtbGF1dAdvbWFjcm9uC29zbGFzaGFjdXRlBnJhY3V0ZQZyY2Fyb24HdW5pMDE1NwZzYWN1dGULc2NpcmN1bWZsZXgHdW5pMDIxOQVsb25ncwR0YmFyBnRjYXJvbgd1bmkwMTYzB3VuaTAyMUIGdWJyZXZlDXVodW5nYXJ1bWxhdXQHdW1hY3Jvbgd1b2dvbmVrBXVyaW5nBnV0aWxkZQZ3YWN1dGULd2NpcmN1bWZsZXgJd2RpZXJlc2lzBndncmF2ZQt5Y2lyY3VtZmxleAZ5Z3JhdmUGemFjdXRlCnpkb3RhY2NlbnQPZ2VybWFuZGJscy5jYWx0BmEuc3MwMQthYWN1dGUuc3MwMQthYnJldmUuc3MwMRBhY2lyY3VtZmxleC5zczAxDmFkaWVyZXNpcy5zczAxC2FncmF2ZS5zczAxDGFtYWNyb24uc3MwMQxhb2dvbmVrLnNzMDEKYXJpbmcuc3MwMQthdGlsZGUuc3MwMQdhZS5zczAxDGFlYWN1dGUuc3MwMQZnLnNzMDELZ2JyZXZlLnNzMDEQZ2NpcmN1bWZsZXguc3MwMQx1bmkwMTIzLnNzMDEPZ2RvdGFjY2VudC5zczAxBnkuc3MwMQt5YWN1dGUuc3MwMRB5Y2lyY3VtZmxleC5zczAxDnlkaWVyZXNpcy5zczAxC3lncmF2ZS5zczAxBmYuc3MwMgZnLnNzMDILZ2JyZXZlLnNzMDIQZ2NpcmN1bWZsZXguc3MwMgx1bmkwMTIzLnNzMDIPZ2RvdGFjY2VudC5zczAyB2lqLnNzMDIGai5zczAyDHVuaTAyMzcuc3MwMhB1bmkwMDZBMDMwMS5zczAyEGpjaXJjdW1mbGV4LnNzMDIGbC5zczAyC2xhY3V0ZS5zczAyC2xjYXJvbi5zczAyDHVuaTAxM0Muc3MwMglsZG90LnNzMDILbHNsYXNoLnNzMDIGci5zczAyC3JhY3V0ZS5zczAyC3JjYXJvbi5zczAyDHVuaTAxNTcuc3MwMgZ0LnNzMDIJdGJhci5zczAyC3RjYXJvbi5zczAyDHVuaTAxNjMuc3MwMgx1bmkwMjFCLnNzMDIGdS5zczAyC3VhY3V0ZS5zczAyC3VicmV2ZS5zczAyEHVjaXJjdW1mbGV4LnNzMDIOdWRpZXJlc2lzLnNzMDILdWdyYXZlLnNzMDISdWh1bmdhcnVtbGF1dC5zczAyDHVtYWNyb24uc3MwMgx1b2dvbmVrLnNzMDIKdXJpbmcuc3MwMgt1dGlsZGUuc3MwMgZ5LnNzMDILeWFjdXRlLnNzMDIQeWNpcmN1bWZsZXguc3MwMg55ZGllcmVzaXMuc3MwMgt5Z3JhdmUuc3MwMgZhLnNzMDQLYWFjdXRlLnNzMDQLYWJyZXZlLnNzMDQQYWNpcmN1bWZsZXguc3MwNA5hZGllcmVzaXMuc3MwNAthZ3JhdmUuc3MwNAxhbWFjcm9uLnNzMDQMYW9nb25lay5zczA0CmFyaW5nLnNzMDQLYXRpbGRlLnNzMDQHYWUuc3MwNAxhZWFjdXRlLnNzMDQGZy5zczA0C2dicmV2ZS5zczA0EGdjaXJjdW1mbGV4LnNzMDQMdW5pMDEyMy5zczA0D2dkb3RhY2NlbnQuc3MwNAZ5LnNzMDQLeWFjdXRlLnNzMDQQeWNpcmN1bWZsZXguc3MwNA55ZGllcmVzaXMuc3MwNAt5Z3JhdmUuc3MwNANmX2YIZl9mLnNzMDIHZmkuc3MwMgdmbC5zczAyB3VuaTA0MTAHdW5pMDQxMQd1bmkwNDEyB3VuaTA0MTMHdW5pMDQwMwd1bmkwNDkwB3VuaTA0MTQHdW5pMDQxNQd1bmkwNDAwB3VuaTA0MDEHdW5pMDQxNgd1bmkwNDE3B3VuaTA0MTgHdW5pMDQxOQd1bmkwNDBEB3VuaTA0MUEHdW5pMDQwQwd1bmkwNDFCB3VuaTA0MUMHdW5pMDQxRAd1bmkwNDFFB3VuaTA0MUYHdW5pMDQyMAd1bmkwNDIxB3VuaTA0MjIHdW5pMDQyMwd1bmkwNDBFB3VuaTA0MjQHdW5pMDQyNQd1bmkwNDI3B3VuaTA0MjYHdW5pMDQyOAd1bmkwNDI5B3VuaTA0MEYHdW5pMDQyQwd1bmkwNDJBB3VuaTA0MkIHdW5pMDQwOQd1bmkwNDBBB3VuaTA0MDUHdW5pMDQwNAd1bmkwNDJEB3VuaTA0MDYHdW5pMDQwNwd1bmkwNDA4B3VuaTA0MEIHdW5pMDQyRQd1bmkwNDJGB3VuaTA0MDIHdW5pMDRENA91bmkwNDE0LmxvY2xCR1IPdW5pMDQxQi5sb2NsQkdSD3VuaTA0MjQubG9jbEJHUgx1bmkwNDE0LnNzMDIMdW5pMDQxQi5zczAyDHVuaTA0Mjcuc3MwMgx1bmkwNDA5LnNzMDIMdW5pMDQxNC5zczAzDHVuaTA0MUIuc3MwMwx1bmkwNDI0LnNzMDMMdW5pMDQxNC5zczA0DHVuaTA0MUIuc3MwNAx1bmkwNDI0LnNzMDQHdW5pMDQzMAd1bmkwNDMxB3VuaTA0MzIHdW5pMDQzMwd1bmkwNDUzB3VuaTA0OTEHdW5pMDQzNAd1bmkwNDM1B3VuaTA0NTAHdW5pMDQ1MQd1bmkwNDM2B3VuaTA0MzcHdW5pMDQzOAd1bmkwNDM5B3VuaTA0NUQHdW5pMDQzQQd1bmkwNDVDB3VuaTA0M0IHdW5pMDQzQwd1bmkwNDNEB3VuaTA0M0UHdW5pMDQzRgd1bmkwNDQwB3VuaTA0NDEHdW5pMDQ0Mgd1bmkwNDQzB3VuaTA0NUUHdW5pMDQ0NAd1bmkwNDQ1B3VuaTA0NDcHdW5pMDQ0Ngd1bmkwNDQ4B3VuaTA0NDkHdW5pMDQ1Rgd1bmkwNDRDB3VuaTA0NEEHdW5pMDQ0Qgd1bmkwNDU5B3VuaTA0NUEHdW5pMDQ1NQd1bmkwNDU0B3VuaTA0NEQHdW5pMDQ1Ngd1bmkwNDU3B3VuaTA0NTgHdW5pMDQ1Qgd1bmkwNDRFB3VuaTA0NEYHdW5pMDQ1Mgd1bmkwNEQ1D3VuaTA0MzIubG9jbEJHUg91bmkwNDMzLmxvY2xCR1IPdW5pMDQzNC5sb2NsQkdSD3VuaTA0MzYubG9jbEJHUg91bmkwNDM3LmxvY2xCR1IPdW5pMDQzOC5sb2NsQkdSD3VuaTA0MzkubG9jbEJHUg91bmkwNDVELmxvY2xCR1IPdW5pMDQzQS5sb2NsQkdSD3VuaTA0M0IubG9jbEJHUg91bmkwNDNGLmxvY2xCR1IPdW5pMDQ0Mi5sb2NsQkdSD3VuaTA0NDYubG9jbEJHUg91bmkwNDQ4LmxvY2xCR1IPdW5pMDQ0OS5sb2NsQkdSD3VuaTA0NEMubG9jbEJHUg91bmkwNDRBLmxvY2xCR1IPdW5pMDQ0RS5sb2NsQkdSDHVuaTA0MzAuc3MwMQx1bmkwNDQzLnNzMDEMdW5pMDQ1RS5zczAxDHVuaTA0RDUuc3MwMQx1bmkwNDMxLnNzMDIMdW5pMDQzNC5zczAyDHVuaTA0M0Iuc3MwMgx1bmkwNDQzLnNzMDIMdW5pMDQ1RS5zczAyDHVuaTA0NDcuc3MwMgx1bmkwNDU5LnNzMDIUdW5pMDQzNC5sb2NsQkdSLnNzMDIUdW5pMDQzNy5sb2NsQkdSLnNzMDIUdW5pMDQzRi5sb2NsQkdSLnNzMDIUdW5pMDQ0Mi5sb2NsQkdSLnNzMDIMdW5pMDQzMi5zczAzDHVuaTA0MzMuc3MwMwx1bmkwNDM0LnNzMDMMdW5pMDQzNi5zczAzDHVuaTA0Mzcuc3MwMwx1bmkwNDM4LnNzMDMMdW5pMDQzOS5zczAzDHVuaTA0NUQuc3MwMwx1bmkwNDNBLnNzMDMMdW5pMDQzQi5zczAzDHVuaTA0M0Yuc3MwMwx1bmkwNDQyLnNzMDMMdW5pMDQ0Ni5zczAzDHVuaTA0NDguc3MwMwx1bmkwNDQ5LnNzMDMMdW5pMDQ0Qy5zczAzDHVuaTA0NEEuc3MwMwx1bmkwNDRFLnNzMDMMdW5pMDQzMC5zczA0DHVuaTA0MzIuc3MwNAx1bmkwNDMzLnNzMDQMdW5pMDQzNC5zczA0DHVuaTA0MzYuc3MwNAx1bmkwNDM3LnNzMDQMdW5pMDQzOC5zczA0DHVuaTA0Mzkuc3MwNAx1bmkwNDVELnNzMDQMdW5pMDQzQS5zczA0DHVuaTA0M0Iuc3MwNAx1bmkwNDNGLnNzMDQMdW5pMDQ0Mi5zczA0DHVuaTA0NDMuc3MwNAx1bmkwNDVFLnNzMDQMdW5pMDQ0Ni5zczA0DHVuaTA0NDguc3MwNAx1bmkwNDQ5LnNzMDQMdW5pMDQ0Qy5zczA0DHVuaTA0NEEuc3MwNAx1bmkwNDRFLnNzMDQMdW5pMDRENS5zczA0B3VuaTAzQkMHemVyby50ZgZvbmUudGYGdHdvLnRmCHRocmVlLnRmB2ZvdXIudGYHZml2ZS50ZgZzaXgudGYIc2V2ZW4udGYIZWlnaHQudGYHbmluZS50Zgd1bmkyMDgwB3VuaTIwODEHdW5pMjA4Mgd1bmkyMDgzB3VuaTIwODQHdW5pMjA4NQd1bmkyMDg2B3VuaTIwODcHdW5pMjA4OAd1bmkyMDg5CXplcm8uZG5vbQhvbmUuZG5vbQh0d28uZG5vbQp0aHJlZS5kbm9tCWZvdXIuZG5vbQlmaXZlLmRub20Ic2l4LmRub20Kc2V2ZW4uZG5vbQplaWdodC5kbm9tCW5pbmUuZG5vbQl6ZXJvLm51bXIIb25lLm51bXIIdHdvLm51bXIKdGhyZWUubnVtcglmb3VyLm51bXIJZml2ZS5udW1yCHNpeC5udW1yCnNldmVuLm51bXIKZWlnaHQubnVtcgluaW5lLm51bXIHdW5pMjA3MAd1bmkwMEI5B3VuaTAwQjIHdW5pMDBCMwd1bmkyMDc0B3VuaTIwNzUHdW5pMjA3Ngd1bmkyMDc3B3VuaTIwNzgHdW5pMjA3OQd1bmkyMTUzB3VuaTIxNTQHdW5pMjE1NQd1bmkyMTU2B3VuaTIxNTcHdW5pMjE1OAd1bmkyMTU5B3VuaTIxNUEHdW5pMjE1MAlvbmVlaWdodGgMdGhyZWVlaWdodGhzC2ZpdmVlaWdodGhzDHNldmVuZWlnaHRocwd1bmkyMTUxB3VuaTIwM0QTcGVyaW9kY2VudGVyZWQuY2FzZQtidWxsZXQuY2FzZQ5wYXJlbmxlZnQuY2FzZQ9wYXJlbnJpZ2h0LmNhc2UOYnJhY2VsZWZ0LmNhc2UPYnJhY2VyaWdodC5jYXNlEGJyYWNrZXRsZWZ0LmNhc2URYnJhY2tldHJpZ2h0LmNhc2UHdW5pMDBBRAtoeXBoZW4uY2FzZQtlbmRhc2guY2FzZQtlbWRhc2guY2FzZRJndWlsbGVtb3RsZWZ0LmNhc2UTZ3VpbGxlbW90cmlnaHQuY2FzZRJndWlsc2luZ2xsZWZ0LmNhc2UTZ3VpbHNpbmdscmlnaHQuY2FzZQd1bmkwMEEwB3VuaTIwMDkHdW5pMjAwQgRFdXJvB3VuaTIwQjQHdW5pMjBCQQd1bmkyMEJEB2NlbnQudGYJZG9sbGFyLnRmB0V1cm8udGYJZmxvcmluLnRmC3N0ZXJsaW5nLnRmBnllbi50Zgd1bmkyMjE5B3VuaTIyMTUIZW1wdHlzZXQHdW5pMjEyNgd1bmkyMjA2B3VuaTAwQjUHYXJyb3d1cAd1bmkyMTk3CmFycm93cmlnaHQHdW5pMjE5OAlhcnJvd2Rvd24HdW5pMjE5OQlhcnJvd2xlZnQHdW5pMjE5Ngd1bmlGOEZGB3VuaTIxMTcGbWludXRlBnNlY29uZAd1bmkyMTEzCWVzdGltYXRlZAd1bmkyMTE2CGJhci5jYXNlDmFtcGVyc2FuZC5zczAxB3VuaTAzMDgHdW5pMDMwNwlncmF2ZWNvbWIJYWN1dGVjb21iB3VuaTAzMEIHdW5pMDMwMgd1bmkwMzBDB3VuaTAzMDYHdW5pMDMwQQl0aWxkZWNvbWIHdW5pMDMwNAd1bmkwMzEyB3VuaTAzMjYHdW5pMDMyNwd1bmkwMzI4DHVuaTAzMDguY2FzZQx1bmkwMzA3LmNhc2UOZ3JhdmVjb21iLmNhc2UOYWN1dGVjb21iLmNhc2UMdW5pMDMwQi5jYXNlDHVuaTAzMDIuY2FzZQx1bmkwMzBDLmNhc2UMdW5pMDMwNi5jYXNlDnRpbGRlY29tYi5jYXNlDHVuaTAzMDQuY2FzZQx1bmkwMzI3LmNhc2UMdW5pMDMyOC5jYXNlDnVuaTAzMDgubmFycm93EGdyYXZlY29tYi5uYXJyb3cQYWN1dGVjb21iLm5hcnJvdw51bmkwMzAyLm5hcnJvdw51bmkwMzA2Lm5hcnJvdxB0aWxkZWNvbWIubmFycm93DnVuaTAzMDQubmFycm93DnVuaTAzMjgubmFycm93E3VuaTAzMDIuY2FzZS5uYXJyb3cTdW5pMDMwNC5jYXNlLm5hcnJvdwticmV2ZWNvbWJjeRBicmV2ZWNvbWJjeS5jYXNlB3VuaTAwMDAHaWphY3V0ZQdJSmFjdXRlB2JyZXZlY3kQY29tbWF0dXJuZWRhYm92ZQAAAAABAAH//wAPAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAnACcAIUAhQK8AAAB7gAA/yoCzf/wAfn/9f8qABgAGAAYABgB7v/0/yoB7v/0/yoAnACcAIUAhQK8AAACvAHuAAD/KgLK//ACygH5//X/EwBgAGAAWwBbASH/sAEo/6kAYABgAFsAWwMvAb4DNgG3sAAsILAAVVhFWSAgS7gADlFLsAZTWliwNBuwKFlgZiCKVViwAiVhuQgACABjYyNiGyEhsABZsABDI0SyAAEAQ2BCLbABLLAgYGYtsAIsIyEjIS2w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"
    base_image = base64.b64decode(image_string)
    base_font_01 = base64.b64decode(font_string_01)
    base_font_02 = base64.b64decode(font_string_02)
    try:
        image01 = Image.open(image)
        image02 = Image.open(logo)
        image03 = Image.open(BytesIO(base_image))
        image04 = changeImageSize(1280, 720, image01)
        image05 = ImageEnhance.Brightness(image04)
        image06 = image05.enhance(1.3)
        image07 = ImageEnhance.Contrast(image06)
        image08 = image07.enhance(1.3)
        image09 = circle_image(image08, 365)
        image10 = circle_image(image02, 90)
        image11 = image08.filter(ImageFilter.GaussianBlur(15))
        image12 = ImageEnhance.Brightness(image11)
        image13 = image12.enhance(0.5)
        image13.paste(image09, (140, 180), mask=image09)
        image13.paste(image10, (410, 450), mask=image10)
        image13.paste(image03, (0, 0), mask=image03)

        font01 = ImageFont.truetype(BytesIO(base_font_01), 45)
        font02 = ImageFont.truetype(BytesIO(base_font_02), 30)
        draw = ImageDraw.Draw(image13)
        para = textwrap.wrap(title, width=28)
        para_size = len(para)
        if para_size == 1:
            title_height = 230
        else:
            title_height = 180
        j = 0
        for line in para:
            if j == 1:
                j += 1
                draw.text((565, 230), f"{line}", fill="white", font=font01)
            if j == 0:
                j += 1
                draw.text((565, title_height), f"{line}", fill="white", font=font01)
        draw.text(
            (565, 320), f"{channel}  |  {views[:23]}", (255, 255, 255), font=font02
        )

        line_length = 580
        line_color = random_color_generator()

        if duration != "Live":
            color_line_percentage = random.uniform(0.15, 0.85)
            color_line_length = int(line_length * color_line_percentage)
            white_line_length = line_length - color_line_length
            start_point_color = (565, 380)
            end_point_color = (565 + color_line_length, 380)
            draw.line([start_point_color, end_point_color], fill=line_color, width=9)
            start_point_white = (565 + color_line_length, 380)
            end_point_white = (565 + line_length, 380)
            draw.line([start_point_white, end_point_white], fill="white", width=8)
            circle_radius = 10
            circle_position = (end_point_color[0], end_point_color[1])
            draw.ellipse(
                [
                    circle_position[0] - circle_radius,
                    circle_position[1] - circle_radius,
                    circle_position[0] + circle_radius,
                    circle_position[1] + circle_radius,
                ],
                fill=line_color,
            )
        else:
            line_color = (255, 0, 0)
            start_point_color = (565, 380)
            end_point_color = (565 + line_length, 380)
            draw.line([start_point_color, end_point_color], fill=line_color, width=9)

            circle_radius = 10
            circle_position = (end_point_color[0], end_point_color[1])
            draw.ellipse(
                [
                    circle_position[0] - circle_radius,
                    circle_position[1] - circle_radius,
                    circle_position[0] + circle_radius,
                    circle_position[1] + circle_radius,
                ],
                fill=line_color,
            )

        draw.text((565, 400), "00:00", (255, 255, 255), font=font02)
        if len(duration) == 4:
            draw.text((1090, 400), duration, (255, 255, 255), font=font02)
        elif len(duration) == 5:
            draw.text((1055, 400), duration, (255, 255, 255), font=font02)
        elif len(duration) == 8:
            draw.text((1015, 400), duration, (255, 255, 255), font=font02)

        image14 = ImageOps.expand(image13, border=10, fill=random_color_generator())
        image15 = changeImageSize(1280, 720, image14)
        image15.save(f"cache/{vidid}_{user_id}.png")
        return f"cache/{vidid}_{user_id}.png"
    except Exception as e:
        LOGGER.info(f"Thumbnail Error: {e}")
        return START_IMAGE_URL


# Some Functions For VC Player


async def add_active_media_chat(
    chat_id, stream_type
):
    if stream_type == "Audio":
        if chat_id in ACTIVE_VIDEO_CHATS:
            ACTIVE_VIDEO_CHATS.remove(chat_id)
        if chat_id not in ACTIVE_AUDIO_CHATS:
            ACTIVE_AUDIO_CHATS.append(chat_id)
    elif stream_type == "Video":
        if chat_id in ACTIVE_AUDIO_CHATS:
            ACTIVE_AUDIO_CHATS.remove(chat_id)
        if chat_id not in ACTIVE_VIDEO_CHATS:
            ACTIVE_VIDEO_CHATS.append(chat_id)
    if chat_id not in ACTIVE_MEDIA_CHATS:
        ACTIVE_MEDIA_CHATS.append(chat_id)


async def remove_active_media_chat(chat_id):
    if chat_id in ACTIVE_AUDIO_CHATS:
        ACTIVE_AUDIO_CHATS.remove(chat_id)
    if chat_id in ACTIVE_VIDEO_CHATS:
        ACTIVE_VIDEO_CHATS.remove(chat_id)
    if chat_id in ACTIVE_MEDIA_CHATS:
        ACTIVE_MEDIA_CHATS.remove(chat_id)


# VC Player Queue


async def add_to_queue(
    chat_id,
    user,
    title,
    duration,
    stream_file,
    stream_type,
    thumbnail,
):
    put = {
        "chat_id": chat_id,
        "user": user,
        "title": title,
        "duration": duration,
        "stream_file": stream_file,
        "stream_type": stream_type,
        "thumbnail": thumbnail,
    }
    check = QUEUE.get(chat_id)
    if check:
        QUEUE[chat_id].append(put)
    else:
        QUEUE[chat_id] = []
        QUEUE[chat_id].append(put)

    return len(QUEUE[chat_id]) - 1


async def clear_queue(chat_id):
    check = QUEUE.get(chat_id)
    if check:
        QUEUE.pop(chat_id)


# Log All Streams
async def start_call(chat_id):
    """راه‌اندازی تماس گروهی"""
    if chat_id not in calls:
        try:
            group_call = GroupCallConfig()
            calls[chat_id] = group_call
        except Exception as e:
            print(f"خطای راه‌اندازی تماس: {str(e)}")
            raise

async def stop_call(chat_id):
    """پایان تماس گروهی"""
    if chat_id in calls:
        try:
            await calls[chat_id].stop()
            del calls[chat_id]
        except Exception as e:
            print(f"خطای توقف تماس: {str(e)}")

async def is_call_active(chat_id: int) -> bool:
    """بررسی فعال بودن تماس"""
    return chat_id in calls and calls[chat_id].is_connected

async def play_audio(chat_id: int, audio_path: str):
    """پخش فایل صوتی"""
    try:
        await start_call(chat_id)
        group_call = calls[chat_id]
        
        if not group_call.is_connected:
            await group_call.join(chat_id)
        
        await group_call.start_audio(AudioPiped(audio_path))
        return True
    except Exception as e:
        print(f"خطای پخش صوت: {str(e)}")
        return False

async def play_video(chat_id: int, video_path: str):
    """پخش فایل ویدیویی"""
    try:
        await start_call(chat_id)
        group_call = calls[chat_id]
        
        if not group_call.is_connected:
            await group_call.join(chat_id)
        
        await group_call.start_video(AudioVideoPiped(video_path))
        return True
    except Exception as e:
        print(f"خطای پخش ویدیو: {str(e)}")
        return False

async def stream_logger(
    chat_id, user, title, duration, stream_type, thumbnail, position=None
):
    if LOG_GROUP_ID != 0:
        if chat_id != LOG_GROUP_ID:
            chat = await bot.get_chat(chat_id)
            chat_name = chat.title
            if chat.username:
                chat_link = f"@{chat.username}"
            else:
                chat_link = "Private Chat"
            try:
                if user.username:
                    requested_by = f"@{user.username}"
                else:
                    requested_by = user.mention
            except Exception:
                requested_by = user.title
            if position:
                caption = f"""**✅ Aᴅᴅᴇᴅ Tᴏ Qᴜᴇᴜᴇ Aᴛ :** #{position}

**❒ عنوان:** {title}
**❒ مدت زمان:** {duration}
**❒ نوع پخش:** {stream_type}
**❒ نام گروه:** {chat_name}
**❒ لینک گروه:** {chat_link}
**❒ درخواست شده توسط:** {requested_by}"""
            else:
                caption = f"""**✅ Sᴛᴀʀᴛɪɴɢ Sᴛʀᴇᴀᴍɪɴɢ Oɴ VC.**

**❒ عنوان:** {title}
**❒ مدت زمان:** {duration}
**❒ نوع پخش:** {stream_type}
**❒ نام گروه:** {chat_name}
**❒ لینک گروه:** {chat_link}
**❒ درخواست شده توسط:** {requested_by}"""
            try:
                await bot.send_photo(LOG_GROUP_ID, photo=thumbnail, caption=caption)
            except Exception:
                pass


# Change stream & Close Stream


async def change_stream(chat_id):
    queued = QUEUE.get(chat_id)
    if queued:
        queued.pop(0)
    if not queued:
        await bot.send_message(chat_id, "**✼ ҉ ҉ ✼ Nᴏ ᴍᴏʀᴇ sᴏɴɢ, Sᴏ Lᴇғᴛ\nFʀᴏᴍ Vᴏɪᴄᴇ Cʜᴀᴛ❗...**")
        return await close_stream(chat_id)

    title = queued[0].get("title")
    duration = queued[0].get("duration")
    stream_file = queued[0].get("stream_file")
    stream_type = queued[0].get("stream_type")
    thumbnail = queued[0].get("thumbnail")
    try:
        requested_by = queued[0].get("user").mention
    except Exception:
        if queued[0].get("user").username:
            requested_by = (
                "["
                + queued[0].get("user").title
                + "](https://t.me/"
                + queued[0].get("user").username
                + ")"
            )
        else:
            requested_by = queued[0].get("user").title

    if stream_type == "Audio":
        stream_media = MediaStream(
            media_path=stream_file,
            video_flags=MediaStream.Flags.IGNORE,
            audio_parameters=AudioQuality.STUDIO,
            ytdlp_parameters="--cookies cookies.txt",
        )
    elif stream_type == "Video":
        stream_media = MediaStream(
            media_path=stream_file,
            audio_parameters=AudioQuality.STUDIO,
            video_parameters=VideoQuality.HD_720p,
            ytdlp_parameters="--cookies cookies.txt",
        )

    await call.play(chat_id, stream_media, config=call_config)
    await add_active_media_chat(chat_id, stream_type)
    caption = f"""```\n🔊<b>【◖ 𝙀𝘼𝙂𝙇𝙀_𝙋𝙇𝘼𝙔𝙀𝙍◗ 】🚩•```\n<b>␥ آهنگ •</b> {title}\n<b>␥ زمان •</b> {duration} دقیقه\n<b>␥ درخواست کننده  •</b> {requested_by}```\nᴘᴏᴡᴇʀᴇᴅ ʙʏ➛ ˹ 𝙍𝘼𝙉𝙂𝙀𝙍 ™˼```"""
    buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⌾ توقف ⌾", callback_data="pause_running_stream_on_vc"
            ),
            InlineKeyboardButton(
                text="⌾ پخش ⌾", callback_data="resume_paused_stream_on_vc"
            )
        ],
        [
            InlineKeyboardButton(
                text="⌾ بعدی ⌾", callback_data="skip_and_change_stream"
            ),
            InlineKeyboardButton(
                text="⌾ پایان ⌾", callback_data="stop_stream_and_leave_vc"
            )
        ],
        [
            InlineKeyboardButton(
                text="˹ بروزرسانی ˼", url="https://t.me/ATRINMUSIC_TM"
            ),
            InlineKeyboardButton(
                text="˹ پشتیبانی ˼", url="https://t.me/ATRINMUSIC_TM1"
            )
        ],
        [
            InlineKeyboardButton(
                text="⌾ 𝙀𝘼𝙂𝙇𝙀 𝙏𝙀𝘼𝙈 ⌾", callback_data="force_close"
            )
        ]
    ]
)
    return await bot.send_photo(chat_id, thumbnail, caption, reply_markup=buttons)


async def close_stream(chat_id):
    try:
        await call.leave_call(chat_id)
    except Exception:
        pass
    await clear_queue(chat_id)
    await remove_active_media_chat(chat_id)


# Get Call Status


async def get_call_status(chat_id):
    calls = await call.calls
    chat_call = calls.get(chat_id)
    if chat_call:
        status = chat_call.capture
        if status == Call.Status.IDLE:
            call_status = "IDLE"
        elif status == Call.Status.ACTIVE:
            call_status = "PLAYING"

        elif status == Call.Status.PAUSED:
            call_status = "PAUSED"
    else:
        call_status = "NOTHING"

    return call_status



@bot.on_message(cdz(["play", "پخش","vplay"]) & ~pyrofl.private)
async def stream_audio_or_video(client, message):
    try:
        await message.delete()
    except Exception:
        pass
    
    chat_id = message.chat.id
    user_id = message.from_user.id if message.from_user else None
    
    # بررسی دسترسی کاربر
    try:
        # بررسی اگر کاربر مالک ربات است
        if user_id == OWNER_ID:  # OWNER_ID را در تنظیمات ربات تعریف کنید
            is_authorized = True
        else:
            # بررسی وضعیت ادمین بودن کاربر
            member = await bot.get_chat_member(chat_id, user_id)
            is_authorized = member.status in ["administrator", "creator"]
        
        if not is_authorized:
            await message.reply("❌ فقط ادمین‌های گروه و مالک ربات می‌توانند از دستور پخش استفاده کنند!")
            return
            
    except Exception as e:
        print(f"خطا در بررسی دسترسی: {str(e)}")
        await message.reply("❌ خطا در بررسی دسترسی!")
        return

    await add_served_chat(chat_id)
    user = message.from_user if message.from_user else message.sender_chat
    replied = message.reply_to_message
    audio = (replied.audio or replied.voice) if replied else None
    video = (replied.video or replied.document) if replied else None
    
    stickers = [
        "🌹", "🌺", "🎉", "🎃", "💥", "🦋", "🕊️",
        "❤️", "💖", "💝", "💗", "💓", "💘", "💞",
    ]
    
    aux = await message.reply_text(random.choice(stickers))
    
    if audio:
        title = "Unsupported Title"
        duration = "Unknown"
        try:
            stream_file = await replied.download()
        except Exception:
            await aux.edit("❌ خطا در دانلود فایل صوتی!")
            return
        result_x = None
        stream_type = "Audio"

    elif video:
        title = "Unsupported Title"
        duration = "Unknown"
        try:
            stream_file = await replied.download()
        except Exception:
            await aux.edit("❌ خطا در دانلود فایل ویدیویی!")
            return
        result_x = None
        stream_type = "Video"
    
    else:
        if len(message.command) < 2:
            buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="⌾ توقف ⌾", callback_data="pause_running_stream_on_vc"
                        ),
                        InlineKeyboardButton(
                            text="⌾ پخش ⌾", callback_data="resume_paused_stream_on_vc"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="🔊 +10", callback_data="volume_up_10"
                        ),
                        InlineKeyboardButton(
                            text="🔈 -10", callback_data="volume_down_10"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⌾ بعدی ⌾", callback_data="skip_and_change_stream"
                        ),
                        InlineKeyboardButton(
                            text="⌾ پایان ⌾", callback_data="stop_stream_and_leave_vc"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="˹ بروزرسانی ˼", url="https://t.me/ATRINMUSIC_TM"
                        ),
                        InlineKeyboardButton(
                            text="˹ پشتیبانی ˼", url="https://t.me/ATRINMUSIC_TM1"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="⌾ 𝙀𝘼𝙂𝙇𝙀 𝙏𝙀𝘼𝙈 ⌾", callback_data="force_close"
                        )
                    ]
                ]
            )

            return await aux.edit_text(
                "**⎋ Gɪᴠᴇ ᴍᴇ ᴀɴʏ ǫᴜɪʀʏ ᴛᴏ ᴘʟᴀʏ\n\n Exᴀᴍᴘʟᴇ:\n➥ Aᴜɪᴅɪᴏ: `/play Zihal`\n➥ Vɪᴅᴇᴏ: `/vplay Zihal`**",
            )
        query = message.text.split(None, 1)[1]
        if "https://" in query:
            base = r"(?:https?:)?(?:\/\/)?(?:www\.)?(?:youtu\.be\/|youtube(?:\-nocookie)?\.(?:[A-Za-z]{2,4}|[A-Za-z]{2,3}\.[A-Za-z]{2})\/)?(?:shorts\/|live\/)?(?:watch|embed\/|vi?\/)*(?:\?[\w=&]*vi?=)?([^#&\?\/]{11}).*$"
            resu = re.findall(base, query)
            vidid = resu[0] if resu[0] else None
        else:
            vidid = None
        url = f"https://www.youtube.com/watch?v={vidid}" if vidid else None
        search_query = url if url else query
        results = VideosSearch(search_query, limit=1)
        for result in (await results.next())["result"]:
            vid_id = vidid if vidid else result["id"]
            vid_url = url if url else result["link"]
            try:
                title = "[" + (result["title"][:18]) + "]" + f"({vid_url})"
                title_x = result["title"]
            except Exception:
                title = "Unsupported Title"
                title_x = title
            try:
                durationx = result.get("duration")
                if not durationx:
                    duration = "Live Stream"
                    duration_x = "Live"
                elif len(durationx) == 4 or len(durationx) == 7:
                    duration = f"0{durationx} Mins"
                    duration_x = f"0{durationx}"
                else:
                    duration = f"{durationx} Mins"
                    duration_x = f"{duration}"
            except Exception:
                duration = "Unknown"
                duration_x = "Unknown Mins"
            try:
                views = result["viewCount"]["short"]
            except Exception:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except Exception:
                channel = "Unknown Channel"
        stream_file = url if url else result["link"]
        result_x = {
            "title": title_x,
            "id": vid_id,
            "link": vid_url,
            "duration": duration_x,
            "views": views,
            "channel": channel,
        }
        stream_type = "Audio" if str(message.command[0][0]) != "v" else "Video"

    try:
        requested_by = user.mention
    except Exception:
        if user.username:
            requested_by = "[" + user.title + "](https://t.me/" + user.username + ")"
        else:
            requested_by = user.title
    buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⌾ توقف ⌾", callback_data="pause_running_stream_on_vc"
            ),
            InlineKeyboardButton(
                text="⌾ پخش ⌾", callback_data="resume_paused_stream_on_vc"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔊 +10", callback_data="volume_up_10"
            ),
            InlineKeyboardButton(
                text="🔈 -10", callback_data="volume_down_10"
            )
        ],
        [
            InlineKeyboardButton(
                text="⌾ بعدی ⌾", callback_data="skip_and_change_stream"
            ),
            InlineKeyboardButton(
                text="⌾ پایان ⌾", callback_data="stop_stream_and_leave_vc"
            )
        ],
        [
            InlineKeyboardButton(
                text="˹ بروزرسانی ˼", url="https://t.me/ATRINMUSIC_TM"
            ),
            InlineKeyboardButton(
                text="˹ پشتیبانی ˼", url="https://t.me/ATRINMUSIC_TM1"
            )
        ],
        [
            InlineKeyboardButton(
                text="⌾ 𝙀𝘼𝙂𝙇𝙀 𝙏𝙀𝘼𝙈 ⌾", callback_data="force_close"
            )
        ]
    ]
)

    if stream_type == "Audio":
        stream_media = MediaStream(
            media_path=stream_file,
            video_flags=MediaStream.Flags.IGNORE,
            audio_parameters=AudioQuality.STUDIO,
            ytdlp_parameters="--cookies cookies.txt",
        )
    elif stream_type == "Video":
        stream_media = MediaStream(
            media_path=stream_file,
            audio_parameters=AudioQuality.STUDIO,
            video_parameters=VideoQuality.HD_720p,
            ytdlp_parameters="--cookies cookies.txt",
        )
    call_status = await get_call_status(chat_id)
    try:
        if call_status == "PLAYING" or call_status == "PAUSED":
            try:
                thumbnail = await create_thumbnail(result_x, user.id)
                position = await add_to_queue(
                    chat_id, user, title, duration, stream_file, stream_type, thumbnail
                )
                caption = f"""```\n🔊 Aᴅᴅᴇᴅ {position} ǫᴜᴇᴜᴇ```\n␥ ʜᴇʏ {requested_by}\n␥ ʏᴏᴜʀ sᴏɴɢ {title}\n␥ ᴘʟᴀʏ ᴀғᴛᴇʀ {position} sᴏɴɢ.```\n⏤͟͟͞͞★ ?𝙀𝘼𝙂𝙇𝙀 𝙋𝙇𝘼𝙔𝙀𝙍  🚩```"""
                await bot.send_photo(chat_id, thumbnail, caption, reply_markup=buttons)
                await stream_logger(
                    chat_id, user, title, duration, stream_type, thumbnail, position
                )
            except Exception as e:
                try:
                    return await aux.edit(f"**Queue Error:** `{e}`")
                except Exception:
                    LOGGER.info(f"Queue Error: {e}")
                    return
        elif call_status == "IDLE" or call_status == "NOTHING":
            try:
                await call.play(chat_id, stream_media, config=call_config)
            except NoActiveGroupCall:
                try:
                    assistant = await bot.get_chat_member(chat_id, app.me.id)
                    if (
                        assistant.status == ChatMemberStatus.BANNED
                        or assistant.status == ChatMemberStatus.RESTRICTED
                    ):
                        try:
                            return await aux.edit_text(
                                f"**🤖 At First, Unban [Assistant ID](https://t.me/{app.me.username}) To Start Stream❗**"
                            )
                        except Exception:
                            LOGGER.info(
                                f"🤖 At First, Unban Assistant ID To Start Stream❗**"
                            )
                            return
                except ChatAdminRequired:
                    try:
                        return await aux.edit_text(
                            "**🤖 At First, Promote Me as An Admin❗**"
                        )
                    except Exception:
                        LOGGER.info("**🤖 At First, Promote Me as An Admin❗**")
                        return
                except UserNotParticipant:
                    if message.chat.username:
                        invitelink = message.chat.username
                        try:
                            await app.resolve_peer(invitelink)
                        except Exception:
                            pass
                    else:
                        try:
                            invitelink = await bot.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            return await aux.edit_text(
                                "**🤖 Hey, I need invite user permission to add Assistant ID❗**"
                            )
                        except Exception as e:
                            try:
                                return await aux.edit_text(
                                    f"**🚫 Assistant Error:** `{e}`"
                                )
                            except Exception:
                                pass
                            LOGGER.info(f"🚫 Assistant Error: {e}")
                            return
                    try:
                        await asyncio.sleep(1)
                        await app.join_chat(invitelink)
                    except InviteRequestSent:
                        try:
                            await bot.approve_chat_join_request(chat_id, adi.me.id)
                        except Exception as e:
                            try:
                                return await aux.edit_text(
                                    f"**🚫 Approve Error:** `{e}`"
                                )
                            except Exception:
                                pass
                            LOGGER.info(f"🚫 Approve Error: {e}")
                            return
                    except UserAlreadyParticipant:
                        pass
                    except Exception as e:
                        try:
                            return await aux.edit_text(
                                f"**🚫 Assistant Join Error:** `{e}`"
                            )
                        except Exception:
                            pass
                        LOGGER.info(f"🚫 Assistant Join Error: {e}")
                        return
                try:
                    await call.play(chat_id, stream_media, config=call_config)
                except NoActiveGroupCall:
                    try:
                        return await aux.edit_text(f"**⚠️ No Active VC❗...**")
                    except Exception:
                        LOGGER.info(f"⚠️ No Active VC ({chat_id})❗... ")
                        return
            except TelegramServerError:
                return await aux.edit_text("**⚠️ Telegram Server Issue❗...**")
            try:
                thumbnail = await create_thumbnail(result_x, user.id)
                position = await add_to_queue(
                    chat_id, user, title, duration, stream_file, stream_type, thumbnail
                )
                caption = f"""```\n🔊<b>【◖ 𝙀𝘼𝙂𝙇𝙀_𝙋𝙇𝘼𝙔𝙀𝙍 ◗ 】🚩•```\n<b>␥ آهنگ •</b> {title}\n<b>␥ زمان •</b> {duration} دقیقه\n<b>␥ درخواست کننده  •</b> {requested_by}```\nᴘᴏᴡᴇʀᴇᴅ ʙʏ➛ ˹ ?𝙍𝘼𝙉𝙂𝙀𝙍™˼```"""
                await bot.send_photo(chat_id, thumbnail, caption, reply_markup=buttons)
                await stream_logger(
                    chat_id, user, title, duration, stream_type, thumbnail
                )
            except Exception as e:
                try:
                    return await aux.edit(f"**Send Error:** `{e}`")
                except Exception:
                    LOGGER.info(f"Send Error: {e}")
                    return
        else:
            return
        try:
            await aux.delete()
        except Exception:
            pass
        await add_active_media_chat(chat_id, stream_type)
        return
    except Exception as e:
        try:
            return await aux.edit_text(f"**Stream Error:** `{e}`")
        except Exception:
            LOGGER.info(f"🚫 Stream Error: {e}")
            return
@bot.on_callback_query(filters.regex("pause_running_stream_on_vc"))
async def pause_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "IDLE" or call_status == "NOTHING":
            return await callback_query.answer("هیچ پخش جاری وجود ندارد", show_alert=True)
        elif call_status == "PAUSED":
            return await callback_query.answer("پخش قبلاً در حالت مکث قرار دارد", show_alert=True)
        elif call_status == "PLAYING":
            await call.pause_stream(chat_id)
            await callback_query.answer("پخش در حالت مکث قرار گرفت", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"خطا: {str(e)}", show_alert=True)

@bot.on_callback_query(filters.regex("resume_paused_stream_on_vc"))
async def resume_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "IDLE" or call_status == "NOTHING":
            return await callback_query.answer("هیچ پخش جاری وجود ندارد", show_alert=True)
        elif call_status == "PLAYING":
            return await callback_query.answer("پخش در حال اجرا است", show_alert=True)
        elif call_status == "PAUSED":
            await call.resume_stream(chat_id)
            await callback_query.answer("پخش از سر گرفته شد", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"خطا: {str(e)}", show_alert=True)

@bot.on_callback_query(filters.regex("skip_and_change_stream"))
async def skip_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "IDLE" or call_status == "NOTHING":
            return await callback_query.answer("هیچ پخش جاری وجود ندارد", show_alert=True)
        elif call_status == "PLAYING" or call_status == "PAUSED":
            await change_stream(chat_id)
            await callback_query.answer("آهنگ بعدی در حال پخش است", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"خطا: {str(e)}", show_alert=True)

@bot.on_callback_query(filters.regex("stop_stream_and_leave_vc"))
async def stop_callback(client, callback_query):
    chat_id = callback_query.message.chat.id
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "NOTHING":
            return await callback_query.answer("هیچ پخش جاری وجود ندارد", show_alert=True)
        elif call_status == "IDLE":
            return await callback_query.answer("با موفقیت از چت صوتی خارج شد", show_alert=True)
        elif call_status == "PLAYING" or call_status == "PAUSED":
            await close_stream(chat_id)
            await callback_query.answer("پخش متوقف شد و از چت صوتی خارج شد", show_alert=True)
    except Exception as e:
        await callback_query.answer(f"خطا: {str(e)}", show_alert=True)

# هندلر برای دکمه بستن (force_close)
@bot.on_callback_query(filters.regex("force_close"))
async def force_close_callback(client, callback_query):
    await callback_query.message.delete()

@bot.on_message(cdx(["pause", "مکث" ,"vpause"]) & ~pyrofl.private)
async def pause_running_stream_on_vc(client, message):
    chat_id = message.chat.id
    try:
        await message.delete()
    except Exception:
        pass
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "IDLE" or call_status == "NOTHING":
            return await message.reply_text("**➥ هیچ پخش جاری وجود ندارد**")

        elif call_status == "PAUSED":
            return await message.reply_text("**➥ پخش قبلاً در حالت مکث قرار دارد**")
        elif call_status == "PLAYING":
            await call.pause_stream(chat_id)
            return await message.reply_text("**➥ پخش در حالت مکث قرار گرفت**")
        else:
            return
    except Exception as e:
        try:
            await bot.send_message(chat_id, f"**🚫 خطا در مکث پخش:** `{e}`")
        except Exception:
            LOGGER.info(f"🚫 خطای مکث پخش: {e}")
            return

@bot.on_message(cdx(["resume", "ادامه","vresume"]) & ~pyrofl.private)
async def resume_paused_stream_on_vc(client, message):
    chat_id = message.chat.id
    try:
        await message.delete()
    except Exception:
        pass
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "IDLE" or call_status == "NOTHING":
            return await message.reply_text("**➥ هیچ پخش جاری وجود ندارد**")

        elif call_status == "PLAYING":
            return await message.reply_text("**➥ پخش در حال اجرا است**")
        elif call_status == "PAUSED":
            await call.resume_stream(chat_id)
            return await message.reply_text("**➥ پخش از سر گرفته شد**")
        else:
            return
    except Exception as e:
        try:
            await bot.send_message(chat_id, f"**🚫 خطا در ادامه پخش:** `{e}`")
        except Exception:
            LOGGER.info(f"🚫 خطای ادامه پخش: {e}")
            return
@bot.on_message(filters.command("install","نصب") & filters.group)
async def install_handler(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    try:
        chat_member = await bot.get_chat_member(chat_id, user_id)
        if chat_member.status != ChatMemberStatus.OWNER:
            await message.reply("❌ فقط مالک گروه می‌تواند ربات را نصب کند!")
            return
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return

    # بررسی وضعیت فعلی اشتراک
    current_sub = await get_subscription(chat_id)
    if current_sub and current_sub.get("is_installed"):
        expiry = current_sub["expiry_date"]
        await message.reply(
            f"⚠️ این گروه قبلاً نصب شده است!\n"
            f"📅 تاریخ انقضا: {expiry.strftime('%Y-%m-%d')}\n"
            f"برای تمدید با پشتیبانی در تماس باشید."
        )
        return

    buttons = [
        [
            InlineKeyboardButton("1 ماهه - 50,000 تومان", callback_data=f"sub_1_{chat_id}"),
            InlineKeyboardButton("3 ماهه - 140,000 تومان", callback_data=f"sub_3_{chat_id}")
        ],
        [
            InlineKeyboardButton("6 ماهه - 260,000 تومان", callback_data=f"sub_6_{chat_id}"),
            InlineKeyboardButton("12 ماهه - 500,000 تومان", callback_data=f"sub_12_{chat_id}")
        ],
        [
            InlineKeyboardButton("🔰 پشتیبانی", url="https://t.me/ATRINMUSIC_TM1")
        ]
    ]
    
    await message.reply(
        "🎯 به پنل نصب ربات خوش آمدید\n\n"
        "📌 لطفا یکی از پلن‌های زیر را انتخاب کنید:\n"
        "⚠️ پس از انتخاب پلن، درگاه پرداخت برای شما ارسال خواهد شد.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# هندلر کالبک‌ها
@bot.on_callback_query(filters.regex(r"^sub_(\d+)_(\d+)"))
async def subscription_callback(client, callback_query):
    months = int(callback_query.matches[0].group(1))
    chat_id = int(callback_query.matches[0].group(2))
    
    try:
        # ذخیره اشتراک
        await save_subscription(chat_id, months)
        
        expiry_date = datetime.now() + timedelta(days=30*months)
        await callback_query.edit_message_text(
            f"✅ ربات با موفقیت نصب شد!\n\n"
            f"📌 اطلاعات اشتراک:\n"
            f"└ مدت زمان: {months} ماه\n"
            f"└ تاریخ نصب: {datetime.now().strftime('%Y-%m-%d')}\n"
            f"└ تاریخ انقضا: {expiry_date.strftime('%Y-%m-%d')}\n\n"
            f"🔰 از اعتماد شما متشکریم!"
        )
        
        # ارسال به کانال لاگ
        if LOG_GROUP_ID:
            log_text = f"#نصب_جدید\nگروه: {chat_id}\nمدت: {months} ماه"
            await bot.send_message(LOG_GROUP_ID, log_text)
        
    except Exception as e:
        print(f"Error in subscription: {e}")
        await callback_query.answer("❌ خطا در ثبت اشتراک. لطفا مجدد تلاش کنید.", show_alert=True)


@bot.on_message(cdx(["skip", "بعدی","vskip"]) & ~pyrofl.private)
async def skip_and_change_stream(client, message):
    chat_id = message.chat.id
    try:
        await message.delete()
    except Exception:
        pass
    try:
        call_status = await get_call_status(chat_id)
        if call_status == "IDLE" or call_status == "NOTHING":
            return await bot.send_message(chat_id, "**➥ هیچ پخش جاری وجود ندارد...**")
        elif call_status == "PLAYING" or call_status == "PAUSED":
            stickers = [
                "🌹",
                "🌺",
                "🎉",
                "🎃",
                "💥",
                "🦋",
                "🕊️",
                "❤️",
                "💖",
                "💝",
                "💗",
                "💓",
                "💘",
                "💞",
            ]
            aux = await message.reply_text(random.choice(stickers))
            await change_stream(chat_id)
            try:
                await aux.delete()
            except Exception:
                pass
    except Exception as e:
        try:
            await bot.send_message(chat_id, f"**🚫 خطا در رد کردن آهنگ:** `{e}`")
        except Exception:
            LOGGER.info(f"🚫 خطای رد کردن آهنگ: {e}")
            return
@bot.on_message(cdx(["help", "راهنما"]) & ~filters.private)
async def show_help(client, message):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 پخش موزیک", callback_data="help_music"),
            InlineKeyboardButton("📥 دانلود", callback_data="help_youtube")
        ],
        [
            InlineKeyboardButton("👮‍♂️ مدیریت", callback_data="help_admin"),
            InlineKeyboardButton("📋 پلی‌لیست", callback_data="help_playlist")
        ],
        [
            InlineKeyboardButton("🔄 صفحه اصلی", callback_data="help_main"),
            InlineKeyboardButton("❌ بستن", callback_data="close_help")
        ]
    ])

    await message.reply_text(
        """
╔════════════════════╗
║   🎵 𝙈𝙐𝙎𝙄𝘾 𝙃𝙀𝙇𝙋 🎵   ║
╚════════════════════╝

👋 به راهنمای ربات خوش آمدید
لطفا بخش مورد نظر خود را انتخاب کنید:

╔════════════════════╗
║  @ATRINMUSIC_TM  ║
╚════════════════════╝
""",
        reply_markup=keyboard
    )

@bot.on_callback_query(filters.regex("^help_"))
async def help_callback(client, callback_query):
    command = callback_query.data.split("_")[1]
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎵 پخش موزیک", callback_data="help_music"),
            InlineKeyboardButton("📥 دانلود", callback_data="help_youtube")
        ],
        [
            InlineKeyboardButton("👮‍♂️ مدیریت", callback_data="help_admin"),
            InlineKeyboardButton("📋 پلی‌لیست", callback_data="help_playlist")
        ],
        [
            InlineKeyboardButton("🔄 صفحه اصلی", callback_data="help_main"),
            InlineKeyboardButton("❌ بستن", callback_data="close_help")
        ]
    ])

    if command == "main":
        text = """
╔════════════════════╗
║   🎵 𝙈𝙐𝙎𝙄𝘾 𝙃𝙀𝙇𝙋 🎵   ║
╚════════════════════╝

👋 به راهنمای ربات خوش آمدید
لطفا بخش مورد نظر خود را انتخاب کنید:

╔════════════════════╗
║  @ATRINMUSIC_TM  ║
╚════════════════════╝
"""
    elif command == "music":
        text = MUSIC_HELP
    elif command == "youtube":
        text = YOUTUBE_HELP
    elif command == "admin":
        text = ADMIN_HELP
    elif command == "playlist":
        text = PLAYLIST_HELP
    else:
        return

    try:
        await callback_query.message.edit_text(
            text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(e)

@bot.on_callback_query(filters.regex("^close_help"))
async def close_help(client, callback_query):
    await callback_query.message.delete()
@bot.on_message(cdz(["vol", "صدا"]) & ~pyrofl.private)
async def change_volume(client, message):
    try:
        chat_id = message.chat.id
        
        # بررسی دسترسی ادمین
        user_id = message.from_user.id
        member = await bot.get_chat_member(chat_id, user_id)
        if not member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await message.reply("❌ فقط ادمین‌های گروه می‌توانند صدا را تنظیم کنند!")

        # بررسی دستور و مقدار صدا
        if len(message.command) < 2:
            return await message.reply("❌ لطفا مقدار صدا را به صورت عدد وارد کنید (0-200)")
        
        try:
            volume = int(message.command[1])
        except ValueError:
            return await message.reply("❌ لطفا یک عدد معتبر وارد کنید")

        if not 0 <= volume <= 200:
            return await message.reply("❌ مقدار صدا باید بین 0 تا 200 باشد")

        # بررسی فعال بودن پخش
        if not await is_call_active(chat_id):
            return await message.reply("❌ در حال حاضر چیزی پخش نمی‌شود!")

        # تغییر صدا
        await set_call_volume(chat_id, volume)
        await message.reply(f"🔊 میزان صدا به {volume}% تغییر کرد")

    except Exception as e:
        print(f"خطای تغییر صدا: {str(e)}")
        await message.reply("❌ خطا در تغییر صدا")
@bot.on_message(cdx(["reload", "ریلود"]) & filters.group)
async def reload_vc(client, message):
    try:
        if not await is_admin(message.chat.id, message.from_user.id):
            return await message.reply("❌ فقط ادمین‌ها می‌توانند ریلود کنند!")
            
        chat_id = message.chat.id
        
        if await pytgcalls.get_call(chat_id):
            try:
                await pytgcalls.leave_group_call(chat_id)
            except:
                pass
                
        await asyncio.sleep(1)
        
        await pytgcalls.join_group_call(
            chat_id,
            InputAudioStream(
                'input.raw',
                HighQualityAudio(),
            ),
        )
        
        await message.reply("✅ تنظیمات صدا با موفقیت بازنشانی شد")
        
    except Exception as e:
        await message.reply(f"❌ خطا در بازنشانی: {str(e)}")

# تنظیم اولیه PyTgCalls


@bot.on_message(cdx(["yt", "یوتیوب"]) & ~filters.private)
async def youtube_search(client, message):
    try:
        if len(message.command) < 2:
            return await message.reply_text(
                "**استفاده:** `/yt [نام موزیک]`\n**مثال:** `/yt shape of you`"
            )

        query = " ".join(message.command[1:])
        m = await message.reply_text("🔎 در حال جستجو...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                search_query = f"ytsearch5:{query}"
                results = ydl.extract_info(search_query, download=False)['entries']

                if not results:
                    return await m.edit("❌ موردی یافت نشد!")

                text = "🎵 **نتایج جستجو در یوتیوب:**\n\n"
                for i, item in enumerate(results, 1):
                    title = item.get('title', 'No Title')
                    duration = item.get('duration_string', 'N/A')
                    views = item.get('view_count', 'N/A')
                    url = item.get('webpage_url', '')
                    
                    text += f"**{i}.** `{title}`\n"
                    text += f"⏱ مدت: {duration} | 👁 بازدید: {views:,}\n"
                    text += f"🔗 {url}\n\n"

                await m.edit(
                    text,
                    disable_web_page_preview=True,
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "دانلود",
                                callback_data=f"download_{results[0]['id']}"
                            ),
                            InlineKeyboardButton(
                                "بستن",
                                callback_data="close"
                            )
                        ]
                    ])
                )

            except Exception as e:
                await m.edit(f"❌ خطا در جستجو: {str(e)}")

    except Exception as e:
        await message.reply_text(f"❌ خطا: {str(e)}")

@bot.on_callback_query(filters.regex(r"^download_(.+)"))
async def download_callback(client, callback_query):
    video_id = callback_query.matches[0].group(1)
    message = callback_query.message

    await callback_query.message.edit_text("⏳ در حال دانلود...")

    try:
        info = await get_youtube_info(f"https://www.youtube.com/watch?v={video_id}")
        if not info:
            return await message.edit("❌ خطا در دریافت اطلاعات ویدیو")

        title = info['title']
        duration = info.get('duration_string', 'نامشخص')
        thumbnail = info.get('thumbnail', None)
        
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])

        audio_file = None
        for file in os.listdir():
            if file.startswith(title) and file.endswith('.mp3'):
                audio_file = file
                break

        if not audio_file:
            return await message.edit("❌ خطا در دانلود فایل")

        caption = f"""
🎵 **عنوان:** {title}
⏱ **مدت زمان:** {duration}
👤 **درخواست کننده:** {callback_query.from_user.mention}

🤖 @ATRINMUSIC_TM
"""
        
        await client.send_audio(
            message.chat.id,
            audio_file,
            caption=caption,
            duration=info.get('duration'),
            performer=info.get('uploader', 'YouTube Music'),
            title=title,
            thumb=thumbnail
        )

        try:
            os.remove(audio_file)
        except:
            pass

        await message.delete()

    except Exception as e:
        await message.edit(f"❌ خطا در دانلود: {str(e)}")
@bot.on_message(cdz(["mylink", "لینک_من"]))
async def get_referral_link(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    try:
        # ساخت لینک دعوت
        invite_link = await bot.create_chat_invite_link(
            chat_id,
            name=f"Referral_{user_id}",
            creates_join_request=False
        )
        
        await message.reply(
            f"🔗 لینک دعوت شما:\n{invite_link.invite_link}\n\n"
            "✨ به ازای هر عضو جدید 10 امتیاز دریافت می‌کنید!"
        )
    except Exception as e:
        await message.reply("❌ خطا در ساخت لینک دعوت!")

@bot.on_chat_join_request()
async def handle_join_request(client, join_request):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id
    invite_link = join_request.invite_link

    if invite_link and "Referral_" in invite_link.name:
        referrer_id = int(invite_link.name.split("_")[1])
        await add_referral(user_id, referrer_id)        
@bot.on_message(cdz(["dlvideo", "دانلود_فیلم"]) & ~pyrofl.private)
async def download_youtube_video(client, message):
    try:
        # چک کردن وجود فایل کوکی
        if not os.path.exists(COOKIES_FILE):
            await message.reply("❌ فایل کوکی یافت نشد! لطفا فایل cookies.txt را در سرور آپلود کنید.")
            return

        # چک کردن ادمین بودن
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await message.reply("❌ فقط ادمین‌های گروه می‌توانند از دستور دانلود استفاده کنند!")
                return
        except Exception as e:
            print(f"Error checking admin status: {e}")
            await message.reply("❌ خطا در بررسی وضعیت ادمین!")
            return

        # بررسی لینک یا کوئری جستجو
        if len(message.command) < 2:
            await message.reply(
                "❌ لطفا لینک یا نام ویدیو را وارد کنید!\n\n"
                "مثال:\n"
                "`دانلود_فیلم https://youtube.com/...`\n"
                "یا\n"
                "`دانلود_فیلم نام ویدیو`"
            )
            return

        search_query = message.text.split(None, 1)[1]
        status_msg = await message.reply("🔍 در حال جستجو...")

        # تنظیمات دانلود ویدیو با کوکی
        video_opts = {
            'format': 'best[height<=720]',  # محدود به کیفیت 720p
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': False,
            'nocheckcertificate': True,
            'logtostderr': False,
            'source_address': '0.0.0.0',
            'cookiefile': COOKIES_FILE,  # استفاده از فایل کوکی
            'extract_flat': True,
            'youtube_include_dash_manifest': False,
        }

        try:
            # جستجو و دریافت اطلاعات ویدیو
            if "youtube.com" in search_query or "youtu.be" in search_query:
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    video_info = ydl.extract_info(search_query, download=False)
            else:
                # جستجو در یوتیوب
                vs = VideosSearch(search_query, limit=1)
                results = await vs.next()
                if not results or not results.get("result"):
                    await status_msg.edit("❌ ویدیویی یافت نشد!")
                    return
                    
                video_url = results["result"][0]["link"]
                with yt_dlp.YoutubeDL(video_opts) as ydl:
                    video_info = ydl.extract_info(video_url, download=False)

            if not video_info:
                await status_msg.edit("❌ خطا در دریافت اطلاعات ویدیو!")
                return

            title = video_info.get('title', 'Unknown Title')
            duration = video_info.get('duration', 0)

            # نمایش اطلاعات دانلود
            await status_msg.edit(
                f"⏳ در حال دانلود:\n\n"
                f"🎥 {title}\n"
                f"⏱ مدت زمان: {duration//60}:{duration%60:02d}"
            )

            # دانلود ویدیو
            video_path = f"downloads/{title}.mp4"
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                ydl.download([video_info['webpage_url']])

            # آپلود به تلگرام
            if os.path.exists(video_path):
                await status_msg.edit("📤 در حال آپلود به تلگرام...")
                
                try:
                    await message.reply_video(
                        video_path,
                        caption=(
                            f"🎥 **عنوان:** {title}\n"
                            f"⏱ **مدت زمان:** {duration//60}:{duration%60:02d}\n\n"
                            f"🤖 @{bot.me.username}"
                        ),
                        duration=duration,
                        supports_streaming=True
                    )
                    await status_msg.delete()
                except Exception as e:
                    await status_msg.edit(f"❌ خطا در آپلود: {str(e)}")
                finally:
                    # پاک کردن فایل
                    try:
                        os.remove(video_path)
                    except:
                        pass
            else:
                await status_msg.edit("❌ خطا در دانلود ویدیو!")

        except Exception as e:
            await status_msg.edit(f"❌ خطا در دانلود: {str(e)}")

    except Exception as e:
        print(f"Main error: {str(e)}")
        await message.reply("❌ خطایی رخ داد. لطفا مجدد تلاش کنید.")
# هندلر بستن پیام
@bot.on_callback_query(filters.regex("^close"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()

@call.on_update(pytgfl.chat_update(ChatUpdate.Status.CLOSED_VOICE_CHAT))
@call.on_update(pytgfl.chat_update(ChatUpdate.Status.KICKED))
@call.on_update(pytgfl.chat_update(ChatUpdate.Status.LEFT_GROUP))
async def stream_services_handler(_, update: Update):
    chat_id = update.chat_id
    return await close_stream(chat_id)


@call.on_update(pytgfl.stream_end())
async def stream_end_handler(_, update: Update):
    chat_id = update.chat_id
    return await change_stream(chat_id)


@bot.on_message(cdx("ping") & ~pyrofl.bot)
async def check_sping(client, message):
    start = datetime.now()
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    m = await message.reply_text("**⥂ Pɪɴɢ ᴘᴏɴɢ...!!**")
    await m.edit(f"**➠ Pɪɴɢᴇᴅ...!!\nLᴀᴛᴇɴᴄʏ:** `{ms}` ᴍs")


@bot.on_message(cdx(["repo", "repository"]) & ~pyrofl.bot)
async def git_repo_link(client, message):
    if message.sender_chat:
        mention = message.sender_chat.title
    else:
        mention = message.from_user.mention
    if message.chat.type == ChatType.PRIVATE:
        caption = f"""```
        {mention}```
        ```• ᴜsᴇ ᴛʜɪs ʀᴇᴘᴏ •
➠ Aɴʏ ᴇʀʀᴏʀ sᴇɴᴅ ss ᴏᴜʀ sᴜᴘᴘᴏʀᴛ```"""
    else:
        caption = f"** Hᴇʟʟᴏ, {mention}.**"
    buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="˹ پشتیبانی ˼",
                url="https://t.me/EAGLE_SUPPORT" 
            ),
            InlineKeyboardButton(
                text="˹ مالک ˼",
                url="https://t.me/EAGLE_SOURCE"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⌾ 𝙀𝘼𝙂𝙇𝙀 𝙏𝙀𝘼𝙈 ⌾",
                callback_data="force_close"
            ),
        ]
    ]
)
    try:
        await message.reply_photo(
            photo=REPO_IMAGE_URL, caption=caption, reply_markup=buttons
        )
    except Exception as e:
        LOGGER.info(f"🚫 Error: {e}")
        return

@bot.on_message(filters.command(["start_wheel", "شروع_قرعه‌کشی"]) & ~filters.private)
async def start_wheel_cmd(client, message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        
        # چک کردن ادمین بودن
        if not await is_admin(chat_id, user_id):
            await message.reply("❌ فقط ادمین‌ها می‌توانند قرعه‌کشی را شروع کنند!")
            return

        # گرفتن جایزه از متن پیام
        command = message.text.split()
        if len(command) < 2:
            await message.reply("❌ لطفا جایزه را مشخص کنید!\nمثال: /start_wheel یک عدد نیترو")
            return
            
        prize = " ".join(command[1:])
        
        # شروع قرعه‌کشی جدید
        wheel.is_active = True
        wheel.participants = []
        wheel.prize = prize
        
        await message.reply(
            f"🎲 قرعه‌کشی جدید شروع شد!\n\n"
            f"🎁 جایزه: {prize}\n"
            f"👥 برای شرکت در قرعه‌کشی، روی دکمه زیر کلیک کنید.",
            reply_markup=get_wheel_buttons()
        )

    except Exception as e:
        print(f"Error in start_wheel: {e}")
        await message.reply("❌ خطایی رخ داد. لطفا مجدد تلاش کنید.")

@bot.on_callback_query(filters.regex("^join_wheel$"))
async def join_wheel_callback(client, callback_query: CallbackQuery):
    try:
        if not wheel.is_active:
            await callback_query.answer("❌ در حال حاضر قرعه‌کشی فعالی وجود ندارد!", show_alert=True)
            return
            
        user_id = callback_query.from_user.id
        if user_id in wheel.participants:
            await callback_query.answer("⚠️ شما قبلاً در این قرعه‌کشی شرکت کرده‌اید!", show_alert=True)
            return
            
        wheel.participants.append(user_id)
        await callback_query.answer("✅ شما با موفقیت در قرعه‌کشی ثبت‌نام شدید!", show_alert=True)
        
        # بروزرسانی پیام اصلی
        await callback_query.message.edit_text(
            f"🎲 قرعه‌کشی در حال انجام\n\n"
            f"🎁 جایزه: {wheel.prize}\n"
            f"👥 تعداد شرکت‌کنندگان: {len(wheel.participants)}",
            reply_markup=get_wheel_buttons()
        )

    except Exception as e:
        print(f"Error in join_wheel_callback: {e}")
        await callback_query.answer("❌ خطایی رخ داد. لطفا مجدد تلاش کنید.", show_alert=True)

@bot.on_callback_query(filters.regex("^participants_list$"))
async def participants_list_callback(client, callback_query: CallbackQuery):
    try:
        if not wheel.is_active:
            await callback_query.answer("❌ قرعه‌کشی فعالی وجود ندارد!", show_alert=True)
            return
            
        if not wheel.participants:
            await callback_query.answer("❌ هنوز کسی در قرعه‌کشی شرکت نکرده است!", show_alert=True)
            return
            
        participants_text = "👥 لیست شرکت‌کنندگان:\n\n"
        for i, user_id in enumerate(wheel.participants, 1):
            user = await client.get_users(user_id)
            participants_text += f"{i}. {user.mention}\n"
            
        await callback_query.message.reply(participants_text)
        await callback_query.answer()

    except Exception as e:
        print(f"Error in participants_list_callback: {e}")
        await callback_query.answer("❌ خطایی رخ داد. لطفا مجدد تلاش کنید.", show_alert=True)

@bot.on_callback_query(filters.regex("^spin_wheel$"))
async def spin_wheel_callback(client, callback_query: CallbackQuery):
    try:
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id
        
        # چک کردن ادمین بودن
        if not await is_admin(chat_id, user_id):
            await callback_query.answer("❌ فقط ادمین‌ها می‌توانند گردونه را بچرخانند!", show_alert=True)
            return

        if not wheel.is_active:
            await callback_query.answer("❌ قرعه‌کشی فعالی وجود ندارد!", show_alert=True)
            return

        if len(wheel.participants) == 0:
            await callback_query.answer("❌ هیچ شرکت‌کننده‌ای در قرعه‌کشی وجود ندارد!", show_alert=True)
            return

        # انیمیشن چرخش
        msg = await callback_query.message.edit_text("🎰 در حال چرخش گردونه...")
        for i in range(3):
            await asyncio.sleep(1)
            await msg.edit_text(f"🎰 در حال چرخش گردونه{'.'*(i+1)}")

        # انتخاب برنده
        winner_id = random.choice(wheel.participants)
        winner = await client.get_users(winner_id)
        
        await msg.edit_text(
            f"🎉 تبریک! برنده قرعه‌کشی:\n\n"
            f"👤 {winner.mention}\n"
            f"🎁 جایزه: {wheel.prize}\n\n"
            f"تعداد شرکت‌کنندگان: {len(wheel.participants)}"
        )

        # پایان قرعه‌کشی
        wheel.is_active = False
        wheel.participants = []
        wheel.prize = ""

    except Exception as e:
        print(f"Error in spin_wheel_callback: {e}")
        await callback_query.answer("❌ خطایی رخ داد. لطفا مجدد تلاش کنید.", show_alert=True)

# تابع کمکی برای چک کردن ادمین بودن
async def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

@bot.on_message(cdx("update") & bot_owner_only)
async def update_repo_latest(client, message):
    response = await message.reply_text("Checking for available updates...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git Command Error")
    except InvalidGitRepositoryError:
        return await response.edit("Invalid Git Repsitory")
    to_exc = f"git fetch origin aditya &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/aditya"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up-to-date!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[(format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4],
    )
    for info in repo.iter_commits(f"HEAD..origin/aditya"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n"
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        link = await paste_queue(updates)
        url = link + "/index.txt"
        nrs = await response.edit(
            f"<b>A new update is available for the Bot!</b>\n\n➣ Pushing Updates Now</code>\n\n**<u>Updates:</u>**\n\n[Click Here to checkout Updates]({url})"
        )
    else:
        nrs = await response.edit(_final_updates_, disable_web_page_preview=True)
    os.system("git stash &> /dev/null && git pull")
    await response.edit(
        f"{nrs.text}\n\nBot was updated successfully! Now, wait for 1 - 2 mins until the bot reboots!"
    )
    os.system("pip3 install -r requirements.txt --force-reinstall")
    os.system(f"kill -9 {os.getpid()} && python3 -m AdityaHalder")
    sys.exit()
    return

@bot.on_message(filters.command(["ai", "جمینی", "هی"]) & ~filters.private)
async def ai_handler(client: Client, message: Message):
    try:
        # بررسی وجود متن سوال
        if len(message.command) < 2:
            await message.reply(
                "❌ لطفا سوال خود را همراه با دستور وارد کنید!\n"
                "مثال: /ai سلام خوبی؟"
            )
            return

        # نمایش وضعیت در حال تایپ
        await client.send_chat_action(message.chat.id, "typing")
            
        # گرفتن متن سوال
        question = " ".join(message.command[1:])
        
        # ارسال پیام در حال پردازش
        processing_msg = await message.reply("🤖 در حال پردازش سوال شما...")
        
        # دریافت پاسخ از AI
        response = await generate_ai_response(question)
        
        # ساخت متن پاسخ
        user_mention = message.from_user.mention if message.from_user else "کاربر ناشناس"
        reply_text = (
            f"🤖 پاسخ هوش مصنوعی:\n\n"
            f"{response}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔍 سوال: {question}\n"
            f"👤 کاربر: {user_mention}\n"
            f"🤖 موتور: GPT-3.5"
        )
        
        # ویرایش پیام با پاسخ نهایی
        await processing_msg.edit(reply_text)
        
    except Exception as e:
        print(f"AI Error: {str(e)}")
        await message.reply("❌ متاسفانه خطایی رخ داد. لطفا مجددا تلاش کنید.")

@bot.on_message(filters.command(["aihelp", "راهنمای_هوش_مصنوعی"]) & ~filters.private)
async def ai_help_handler(client: Client, message: Message):
    help_text = """
🤖 **راهنمای استفاده از هوش مصنوعی**

📝 **دستورات:**
• `/ai` یا `/جمینی` یا `/هی` + متن سوال
• مثال: `/ai سلام، حالت چطوره؟`

🔰 **قابلیت‌ها:**
• پاسخگویی به سوالات
• نوشتن متن و مقاله
• حل مسائل ریاضی
• برنامه‌نویسی
• ترجمه متون
• و موارد دیگر...

⚠️ **نکات:**
• سوالات خود را واضح و دقیق بپرسید
• از ارسال محتوای نامناسب خودداری کنید
• این سرویس کاملاً رایگان است
"""
    await message.reply(help_text)
@bot.on_message(cdx(["stats", "stat"]) & ~pyrofl.bot)
async def git_repo_link(client, message):
    if message.sender_chat:
        mention = message.sender_chat.title
    else:
        mention = message.from_user.mention
    if message.chat.type == ChatType.PRIVATE:
        caption = f"""```
◖ Sαηαтαηι ◗ Sᴛᴀᴛs```
➠ Sᴛᴀᴛs ᴏғ sᴀɴᴀᴛᴀɴɪ ᴠɪʙᴇs"""
    else:
        caption = f"** Hᴇʟʟᴏ, {mention}.**"
    buttons = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                text="˹ نمایش آمار ˼",
                callback_data="check_stats"
            ),
        ],
        [
            InlineKeyboardButton(
                text="⌾ 𝙀𝘼𝙂𝙇𝙀 𝙏𝙀𝘼𝙈 ⌾",
                callback_data="force_close"
            ),
        ]
    ]
)

    try:
        await message.reply_photo(
            photo=STATS_IMAGE_URL, caption=caption, reply_markup=buttons
        )
    except Exception as e:
        LOGGER.info(f"🚫 Error: {e}")
        return

@bot.on_callback_query(rgx("check_stats"))
async def check_total_stats(client, query):
    try:
        user_id = query.from_user.id
        runtime = __start_time__
        boot_time = int(time.time() - runtime)
        uptime = get_readable_time((boot_time))
        served_chats = len(await get_served_chats())
        served_users = len(await get_served_users())
        activ_chats = len(ACTIVE_MEDIA_CHATS)
        audio_chats = len(ACTIVE_AUDIO_CHATS)
        video_chats = len(ACTIVE_VIDEO_CHATS)
        
        return await query.answer(
            f"""🏹 Bᴏᴛ Rᴜɴ Tɪᴍᴇ [◖ Sαηαтαηι ◗]
⎋ {uptime}

➥ Sᴇʀᴠᴇᴅ Cʜᴀᴛs: {served_chats}
➥ Sᴇʀᴠᴇᴅ Usᴇʀ: {served_users}

➠ Tᴏᴛᴀʟ Aᴄᴛɪᴠᴇ Cʜᴀᴛs [{activ_chats}]
⎋ Aᴜɪᴅᴏ Sᴛʀᴇᴀᴍ: {audio_chats}
⎋ Vɪᴅᴇᴏ Sᴛʀᴇᴀᴍ: {video_chats}""",
            show_alert=True
        )
    except Exception as e:
        LOGGER.info(f"🚫 Stats Error: {e}")
        pass


@bot.on_message(cdx(["broadcast", "gcast"]) & bot_owner_only)
async def broadcast_message(client, message):
    try:
        await message.delete()
    except:
        pass
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("**⎋ Usᴇs**:\n/broadcast [Mᴇssᴀɢᴇ] Oʀ [Rᴇᴘʟʏ Tᴏ ᴀ Mᴇssᴀɢᴇ]")
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply_text("**⎋ Pʟᴇᴀsᴇ ɢɪᴠᴇ ᴍᴇ sᴏᴍᴇ Tᴇxᴛ To Bʀᴏᴀᴅᴄᴀsᴛ...**")
    
    # Bot broadcast inside chats
    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = (
                    await bot.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await bot.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except Exception:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except Exception:
                        continue
                sent += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
        try:
            await message.reply_text("**✅ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ Iɴ {0}  Cʜᴀᴛs Wɪᴛʜ {1} Pɪɴs Fʀᴏᴍ Bᴏᴛ.**".format(sent, pin))
        except:
            pass

    # Bot broadcasting to users
    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await bot.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await bot.send_message(i, text=query)
                )
                susr += 1
            except FloodWait as e:
                flood_time = int(e.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                pass
        try:
            await message.reply_text("**✅ Bʀᴏᴀᴅᴄᴀsᴛ Mᴇssᴀɢᴇ Tᴏ {0} Usᴇʀs.**".format(susr))
        except:
            pass





if __name__ == "__main__":
    loop.run_until_complete(main())
    
    
    
    
    
   


