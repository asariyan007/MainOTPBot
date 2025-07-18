import time
import requests
import json
import hashlib
import re
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
import asyncio
import os

# ========== BASIC CONFIG ==========
BOT_TOKEN = '7943158999:AAG5t9je40J4Sb1p6CaCLLEfRKtckp3JWtc'
ADMIN_ID = 5359578794
CACHE_FILE = "otp_cache.json"
STATUS_FILE = "bot_status.json"

DEFAULT_CHANNEL = "https://t.me/+aYrPdVod0_Y2NzY1"
DEFAULT_FILE = "https://t.me/+Tu3UHeItqb5lOTFl"
DEFAULT_CREDIT = "𝙏𝙀𝘼𝙈 𝙀𝙇𝙄𝙏𝙀 𝙓"
DEFAULT_APIS = ["https://techflare.nagad.my.id/mainapi.php"]

def get_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE) as f:
            return json.load(f)
    return {
        "on": True,
        "admins": [ADMIN_ID],
        "groups": [-1002690654446],
        "link": DEFAULT_FILE,
        "apis": DEFAULT_APIS,
        "credits": {},
        "group_links": {},
        "group_files": {}
    }

def save_status(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, indent=4)

status = get_status()

def extract_code(text):
    match = re.search(r'\b(\d{4,8}|\d{3}-\d{3})\b', text)
    return match.group(1).replace('-', '') if match else ""

def detect_country(number):
    number = number.replace(' ', '').replace('-', '')
    for code in sorted(country_codes.keys(), key=lambda x: -len(x)):
        if number.startswith(code) or number.startswith("+" + code):
            return country_codes[code]
    return ("Unknown", "🌍")

country_codes = {
    '1': ('United States', '🇺🇸'),
    '7': ('Russia', '🇷🇺'),
    '20': ('Egypt', '🇪🇬'),
    '27': ('South Africa', '🇿🇦'),
    '30': ('Greece', '🇬🇷'),
    '31': ('Netherlands', '🇳🇱'),
    '32': ('Belgium', '🇧🇪'),
    '33': ('France', '🇫🇷'),
    '34': ('Spain', '🇪🇸'),
    '36': ('Hungary', '🇭🇺'),
    '39': ('Italy', '🇮🇹'),
    '40': ('Romania', '🇷🇴'),
    '41': ('Switzerland', '🇨🇭'),
    '43': ('Austria', '🇦🇹'),
    '44': ('United Kingdom', '🇬🇧'),
    '45': ('Denmark', '🇩🇰'),
    '46': ('Sweden', '🇸🇪'),
    '47': ('Norway', '🇳🇴'),
    '48': ('Poland', '🇵🇱'),
    '49': ('Germany', '🇩🇪'),
    '51': ('Peru', '🇵🇪'),
    '52': ('Mexico', '🇲🇽'),
    '53': ('Cuba', '🇨🇺'),
    '54': ('Argentina', '🇦🇷'),
    '55': ('Brazil', '🇧🇷'),
    '56': ('Chile', '🇨🇱'),
    '57': ('Colombia', '🇨🇴'),
    '58': ('Venezuela', '🇻🇪'),
    '60': ('Malaysia', '🇲🇾'),
    '61': ('Australia', '🇦🇺'),
    '62': ('Indonesia', '🇮🇩'),
    '63': ('Philippines', '🇵🇭'),
    '64': ('New Zealand', '🇳🇿'),
    '65': ('Singapore', '🇸🇬'),
    '66': ('Thailand', '🇹🇭'),
    '81': ('Japan', '🇯🇵'),
    '82': ('South Korea', '🇰🇷'),
    '84': ('Vietnam', '🇻🇳'),
    '86': ('China', '🇨🇳'),
    '90': ('Turkey', '🇹🇷'),
    '91': ('India', '🇮🇳'),
    '92': ('Pakistan', '🇵🇰'),
    '93': ('Afghanistan', '🇦🇫'),
    '94': ('Sri Lanka', '🇱🇰'),
    '95': ('Myanmar', '🇲🇲'),
    '98': ('Iran', '🇮🇷'),
    '211': ('South Sudan', '🇸🇸'),
    '212': ('Morocco', '🇲🇦'),
    '213': ('Algeria', '🇩🇿'),
    '216': ('Tunisia', '🇹🇳'),
    '218': ('Libya', '🇱🇾'),
    '220': ('Gambia', '🇬🇲'),
    '221': ('Senegal', '🇸🇳'),
    '222': ('Mauritania', '🇲🇷'),
    '223': ('Mali', '🇲🇱'),
    '224': ('Guinea', '🇬🇳'),
    '225': ('Ivory Coast', '🇨🇮'),
    '226': ('Burkina Faso', '🇧🇫'),
    '227': ('Niger', '🇳🇪'),
    '228': ('Togo', '🇹🇬'),
    '229': ('Benin', '🇧🇯'),
    '230': ('Mauritius', '🇲🇺'),
    '231': ('Liberia', '🇱🇷'),
    '232': ('Sierra Leone', '🇸🇱'),
    '233': ('Ghana', '🇬🇭'),
    '234': ('Nigeria', '🇳🇬'),
    '235': ('Chad', '🇹🇩'),
    '236': ('Central African Republic', '🇨🇫'),
    '237': ('Cameroon', '🇨🇲'),
    '238': ('Cape Verde', '🇨🇻'),
    '239': ('Sao Tome and Principe', '🇸🇹'),
    '240': ('Equatorial Guinea', '🇬🇶'),
    '241': ('Gabon', '🇬🇦'),
    '242': ('Republic of the Congo', '🇨🇬'),
    '243': ('DR Congo', '🇨🇩'),
    '244': ('Angola', '🇦🇴'),
    '245': ('Guinea-Bissau', '🇬🇼'),
    '246': ('British Indian Ocean Territory', '🇮🇴'),
    '248': ('Seychelles', '🇸🇨'),
    '249': ('Sudan', '🇸🇩'),
    '250': ('Rwanda', '🇷🇼'),
    '251': ('Ethiopia', '🇪🇹'),
    '252': ('Somalia', '🇸🇴'),
    '253': ('Djibouti', '🇩🇯'),
    '254': ('Kenya', '🇰🇪'),
    '255': ('Tanzania', '🇹🇿'),
    '256': ('Uganda', '🇺🇬'),
    '257': ('Burundi', '🇧🇮'),
    '258': ('Mozambique', '🇲🇿'),
    '260': ('Zambia', '🇿🇲'),
    '261': ('Madagascar', '🇲🇬'),
    '263': ('Zimbabwe', '🇿🇼'),
    '264': ('Namibia', '🇳🇦'),
    '265': ('Malawi', '🇲🇼'),
    '266': ('Lesotho', '🇱🇸'),
    '267': ('Botswana', '🇧🇼'),
    '268': ('Eswatini', '🇸🇿'),
    '269': ('Comoros', '🇰🇲'),
    '290': ('Saint Helena', '🇸🇭'),
    '291': ('Eritrea', '🇪🇷'),
    '297': ('Aruba', '🇦🇼'),
    '298': ('Faroe Islands', '🇫🇴'),
    '299': ('Greenland', '🇬🇱'),
    '351': ('Portugal', '🇵🇹'),
    '352': ('Luxembourg', '🇱🇺'),
    '353': ('Ireland', '🇮🇪'),
    '354': ('Iceland', '🇮🇸'),
    '355': ('Albania', '🇦🇱'),
    '356': ('Malta', '🇲🇹'),
    '357': ('Cyprus', '🇨🇾'),
    '358': ('Finland', '🇫🇮'),
    '359': ('Bulgaria', '🇧🇬'),
    '370': ('Lithuania', '🇱🇹'),
    '371': ('Latvia', '🇱🇻'),
    '372': ('Estonia', '🇪🇪'),
    '373': ('Moldova', '🇲🇩'),
    '374': ('Armenia', '🇦🇲'),
    '375': ('Belarus', '🇧🇾'),
    '376': ('Andorra', '🇦🇩'),
    '377': ('Monaco', '🇲🇨'),
    '378': ('San Marino', '🇸🇲'),
    '380': ('Ukraine', '🇺🇦'),
    '381': ('Serbia', '🇷🇸'),
    '382': ('Montenegro', '🇲🇪'),
    '385': ('Croatia', '🇭🇷'),
    '386': ('Slovenia', '🇸🇮'),
    '387': ('Bosnia and Herzegovina', '🇧🇦'),
    '389': ('North Macedonia', '🇲🇰'),
    '420': ('Czech Republic', '🇨🇿'),
    '421': ('Slovakia', '🇸🇰'),
    '423': ('Liechtenstein', '🇱🇮'),
    '852': ('Hong Kong', '🇭🇰'),
    '853': ('Macau', '🇲🇴'),
    '855': ('Cambodia', '🇰🇭'),
    '856': ('Laos', '🇱🇦'),
    '880': ('Bangladesh', '🇧🇩'),
    '886': ('Taiwan', '🇹🇼'),
    '960': ('Maldives', '🇲🇻'),
    '961': ('Lebanon', '🇱🇧'),
    '962': ('Jordan', '🇯🇴'),
    '963': ('Syria', '🇸🇾'),
    '964': ('Iraq', '🇮🇶'),
    '965': ('Kuwait', '🇰🇼'),
    '966': ('Saudi Arabia', '🇸🇦'),
    '967': ('Yemen', '🇾🇪'),
    '968': ('Oman', '🇴🇲'),
    '970': ('Palestine', '🇵🇸'),
    '971': ('UAE', '🇦🇪'),
    '972': ('Israel', '🇮🇱'),
    '973': ('Bahrain', '🇧🇭'),
    '974': ('Qatar', '🇶🇦'),
    '975': ('Bhutan', '🇧🇹'),
    '976': ('Mongolia', '🇲🇳'),
    '977': ('Nepal', '🇳🇵'),
    '992': ('Tajikistan', '🇹🇯'),
    '993': ('Turkmenistan', '🇹🇲'),
    '994': ('Azerbaijan', '🇦🇿'),
    '995': ('Georgia', '🇬🇪'),
    '996': ('Kyrgyzstan', '🇰🇬'),
    '998': ('Uzbekistan', '🇺🇿'),
}

def format_message(entry, gid):
    time_now = datetime.now().strftime('%H:%M:%S')
    date_now = datetime.now().strftime('%d %B %Y')
    country, emoji = detect_country(entry["Number"])
    otp = extract_code(entry["OTP"])
    full = entry["OTP"]

    credit = status["credits"].get(str(gid), DEFAULT_CREDIT)
    main_link = status["group_links"].get(str(gid), DEFAULT_CHANNEL)
    num_file = status["group_files"].get(str(gid), status.get("link", DEFAULT_FILE))

    return (
        f"✨ <b>𝙉𝙀𝙒 𝘾𝙊𝘿𝙀 𝙍𝙀𝘾𝙀𝙄𝙑𝙀𝘿</b> ✨\n"
        f"<b>⏰ Time:</b> {time_now}\n"
        f"<b>🗓️ Date:</b> {date_now}\n"
        f"<b>🌍 Country:</b> {country} {emoji}\n"
        f"<b>⚙️ Service:</b> {entry['Platform']}\n"
        f"<b>☎️ Number:</b> <code>{entry['Number']}</code>\n"
        f"<b>🔑 OTP:</b> <code>{otp}</code>\n"
        f"✉️ <b>Full Message:</b>\n<pre>{full}</pre>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 Note: ~ Wait 1 minute for new code ~\n"
        f"Pᴏᴡᴇʀᴇᴅ ʙʏ {credit}\n"
        f"Dᴇᴠᴇʟᴏᴘᴇᴅ Bʏ <a href='https://t.me/WareWolfOwner'>Ariyan</a>"
    ), InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀Main Channel", url=main_link)],
        [InlineKeyboardButton("📁Numbers File", url=num_file)]
    ])

async def fetch_otps(app):
    if not status["on"]: return
    apis = status.get("apis", DEFAULT_APIS)
    for url in apis:
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if not isinstance(data, list) or not data:
                continue
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE) as f:
                    cache = json.load(f)
            else:
                cache = []
            for entry in data:
                uid = hashlib.md5((entry["Number"] + entry["Platform"] + entry["OTP"]).encode()).hexdigest()
                if uid in [c["id"] for c in cache]: continue
                cache.append({"id": uid})
                for gid in status["groups"]:
                    text, buttons = format_message(entry, gid)
                    await app.bot.send_message(chat_id=gid, text=text, parse_mode="HTML", reply_markup=buttons)
            with open(CACHE_FILE, "w") as f:
                json.dump(cache, f, indent=2)
            break
        except Exception as e:
            await app.bot.send_message(chat_id=ADMIN_ID, text=f"⚠️ API Error:\n<pre>{e}</pre>", parse_mode="HTML")

# ==== COMMAND SYSTEM ====

async def restricted(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ You are not allowed to use this command.")

def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = str(update.effective_user.id)
        if user not in map(str, status["admins"]): return await restricted(update, context)
        return await func(update, context)
    return wrapper

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Commands:\n"
        "/on /off /status\n"
        "/addgroup <id> /rmvgroup <id>\n"
        "/addadmin <id> /rmvadmin <id>\n"
        "/cnglink <link>\n"
        "/cngcredit <group_id> <name>\n"
        "/cngcnllink <group_id> <link>\n"
        "/cngnumlink <group_id> <link>\n"
        "/addapi <url> /rmvapi <url>\n"
        "/listapis /admins"
    )

@admin_only
async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status["on"] = True
    save_status(status)
    await update.message.reply_text("✅ Bot is ON.")

@admin_only
async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status["on"] = False
    save_status(status)
    await update.message.reply_text("⛔ Bot is OFF.")

@admin_only
async def addgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gid = int(context.args[0])
    if gid not in status["groups"]:
        status["groups"].append(gid)
        save_status(status)
        await update.message.reply_text("✅ Group added.")

@admin_only
async def rmvgroup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gid = int(context.args[0])
    if gid in status["groups"]:
        status["groups"].remove(gid)
        save_status(status)
        await update.message.reply_text("✅ Group removed.")

@admin_only
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = int(context.args[0])
    if uid not in status["admins"]:
        status["admins"].append(uid)
        save_status(status)
        await update.message.reply_text("✅ Admin added.")

@admin_only
async def rmvadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = int(context.args[0])
    if uid in status["admins"]:
        status["admins"].remove(uid)
        save_status(status)
        await update.message.reply_text("✅ Admin removed.")

@admin_only
async def cnglink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status["link"] = context.args[0]
    save_status(status)
    await update.message.reply_text("✅ Default numbers file link updated.")

@admin_only
async def cngcredit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gid, name = context.args[0], " ".join(context.args[1:])
    status["credits"][gid] = name
    save_status(status)
    await update.message.reply_text(f"✅ Credit for group {gid} updated.")

@admin_only
async def cngcnllink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gid, link = context.args[0], context.args[1]
    status["group_links"][gid] = link
    save_status(status)
    await update.message.reply_text(f"✅ Main Channel link for group {gid} updated.")

@admin_only
async def cngnumlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gid, link = context.args[0], context.args[1]
    status["group_files"][gid] = link
    save_status(status)
    await update.message.reply_text(f"✅ Numbers File link for group {gid} updated.")

@admin_only
async def addapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0]
    if url not in status["apis"]:
        status["apis"].append(url)
        save_status(status)
        await update.message.reply_text("✅ API added.")

@admin_only
async def rmvapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = context.args[0]
    if url in status["apis"]:
        status["apis"].remove(url)
        save_status(status)
        await update.message.reply_text("✅ API removed.")

@admin_only
async def listapis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 APIs:\n" + "\n".join(status.get("apis", [])))

@admin_only
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👮 Admins:\n" + "\n".join(map(str, status["admins"])))

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    handlers = [
        ("start", start), ("on", on), ("off", off), ("addgroup", addgroup),
        ("rmvgroup", rmvgroup), ("addadmin", addadmin), ("rmvadmin", rmvadmin),
        ("cnglink", cnglink), ("cngcredit", cngcredit), ("cngcnllink", cngcnllink),
        ("cngnumlink", cngnumlink), ("addapi", addapi), ("rmvapi", rmvapi),
        ("listapis", listapis), ("admins", admins)
    ]
    for cmd, func in handlers:
        app.add_handler(CommandHandler(cmd, func))

    async def runner():
        while True:
            await fetch_otps(app)
            await asyncio.sleep(10)

    asyncio.create_task(runner())
    print("✅ Bot Running...")
    await app.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
