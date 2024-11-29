import asyncio
from datetime import datetime, timedelta
from pymongo import MongoClient
from pyrogram import filters
from pytz import timezone
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait
from YTMUSIC import app
from config import OWNER_ID
from YTMUSIC.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from YTMUSIC.utils.decorators.language import language
from YTMUSIC.utils.formatters import alpha_to_int
from config import adminlist

# MongoDB सेटअप
client = MongoClient("mongodb+srv://Yash_607:Yash_607@cluster0.r3s9sbo.mongodb.net/?retryWrites=true&w=majority")
db = client["subscriberDB"]
subscribers = db["subscribers"]

IS_BROADCASTING = False


# Subscriber को जोड़ने का फंक्शन
async def add_subscriber(user_id, days):
    expiry_date = datetime.now() + timedelta(days=days)
    added_on = datetime.now()
    subscribers.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
                "added_on": added_on.strftime("%Y-%m-%d %H:%M:%S"),
                "subscription_days": days,
                "usage_count": 0
            }
        },
        upsert=True,
    )
    return True


# Subscriber को हटाने का फंक्शन
async def remove_subscriber(user_id):
    subscribers.delete_one({"user_id": user_id})
    return True


# Expired subscribers को हटाने का बैकग्राउंड टास्क
async def clean_expired_subscribers():
    while True:
        now = datetime.now()
        subscribers.delete_many({"expiry_date": {"$lt": now}})
        await asyncio.sleep(3600)  # हर घंटे चेक करें


@app.on_message(filters.command("sublist"))
async def list_subscribers(client, message):
    if message.from_user.id != OWNER_ID:
        return 

    all_subscribers = list(subscribers.find())
    if not all_subscribers:
        return await message.reply("Nᴏ sᴜʙsᴄʀɪʙᴇʀ ᴜsᴇʀ !")

    # India timezone setup
    india_tz = timezone("Asia/Kolkata")

    text = "### Subscriber List ###\n\n"
    for sub in all_subscribers:
        try:
            user_id = sub["user_id"]

            # Expiry date को सही प्रकार से हैंडल करें
            if isinstance(sub["expiry_date"], datetime):
                expiry_date = sub["expiry_date"]
            else:
                expiry_date = datetime.strptime(sub["expiry_date"], "%Y-%m-%d %H:%M:%S")

            # Added On को सही प्रकार से हैंडल करें
            if isinstance(sub["added_on"], datetime):
                added_on = sub["added_on"]
            else:
                added_on = datetime.strptime(sub["added_on"], "%Y-%m-%d %H:%M:%S")

            subscription_days = sub["subscription_days"]

            # Remaining time calculation
            remaining_time = expiry_date - datetime.now()
            days = remaining_time.days
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, _ = divmod(remainder, 60)

            # Get user's name
            try:
                user = await app.get_users(user_id)
                user_name = user.mention if user.first_name else "Unknown"
            except:
                user_name = "Unknown"

            # Convert times to IST
            added_on_ist = added_on.astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')
            expiry_date_ist = expiry_date.astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')

            text += (
                f"**Name**: {user_name}\n"
                f"**UserID**: `{user_id}`\n"
                f"**Added On (IST)**: `{added_on_ist}`\n"
                f"**Subscription Days**: `{subscription_days}` days\n"
                f"**Remaining Time**: `{days}` days, `{hours}` hours, `{minutes}` minutes\n\n"
            )
        except Exception as e:
            text += f"Error while processing subscriber {sub.get('user_id', 'Unknown')}: {e}\n\n"

    await message.reply(text, disable_web_page_preview=True)


@app.on_message(filters.command("mystats"))
async def my_stats(client, message):
    user_id = message.from_user.id

    # MongoDB में यूज़र को खोजें
    user_data = subscribers.find_one({"user_id": user_id})
    if not user_data:
        # InlineKeyboardMarkup और Button जोड़ें
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("ɪɴғᴏ", url="https://t.me/BABY09_WORLD/250")]]
        )

        # संदेश के साथ बटन भेजें
        return await message.reply(
            "Yᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ sᴜʙsᴄʀɪʙᴇʀ ᴜsᴇʀ !\n\n"
            "Fɪʀsᴛ ɢᴏ ɪɴғᴏ ᴀɴᴅ sᴜʙsᴄʀɪʙᴇ. 🙂",
            reply_markup=keyboard,
        )
    # India timezone setup
    india_tz = timezone("Asia/Kolkata")

    # डेटा प्राप्त करें
    expiry_date = datetime.strptime(user_data["expiry_date"], "%Y-%m-%d %H:%M:%S")
    added_on = datetime.strptime(user_data["added_on"], "%Y-%m-%d %H:%M:%S")
    subscription_days = user_data["subscription_days"]

    # Remaining time calculation
    remaining_time = expiry_date - datetime.now()
    days = remaining_time.days
    hours, remainder = divmod(remaining_time.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    # Get the user's name
    try:
        user = await app.get_users(user_id)
        user_name = user.mention if user.first_name else "Unknown"
    except Exception:
        user_name = "Unknown"

    # Convert times to IST
    added_on_ist = added_on.astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')
    expiry_date_ist = expiry_date.astimezone(india_tz).strftime('%Y-%m-%d %H:%M:%S')

    # Prepare stats message
    text = (
        f"```\nYᴏᴜʀ Sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴛᴀᴛᴜs 🕐```\n\n"
        f"Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Aᴅᴅᴇᴅ Oɴ: ̗̀➛ `{added_on_ist}`\n"
        f"Sᴜʙsᴄʀɪᴘᴛɪᴏɴ Exᴘɪʀʏ Oɴ: ̗̀➛ `{expiry_date_ist}`\n"
        f"Mᴇᴍʙᴇʀsʜɪᴘ ғᴏʀ: ̗̀➛ `{subscription_days}` Dᴀʏs\n"
        f"Rᴇᴍᴀɪɴɪɴɢ Tɪᴍᴇ: ̗̀➛ `{days}` Dᴀʏs, `{hours}` Hᴏᴜʀs, `{minutes}` Mɪɴᴜᴛᴇs\n\n"
        f"Tʜᴀɴᴋs {user_name} ☺️"
    )

    # Inline button to check subscription status
    switch_button = InlineKeyboardButton(
    text="Iɴᴠɪᴛᴇ ᴏᴛʜᴇʀs & sᴜᴘᴘᴏʀᴛ",
    switch_inline_query=(
        """Hᴇʏ ɪ ᴀᴍ sᴜʙsᴄʀɪʙᴇᴅ ᴛᴏ ʙᴀʙʏᴍᴜsɪᴄ
Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ғʀᴇᴇ ᴘʀᴏᴍᴏ
Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴜsᴇ ғʀᴇᴇ ᴀᴅᴠᴀɴᴄᴇ ᴀɪ ᴛᴏᴏʟ
Aʟʟ ɪs ᴘᴏssɪʙʟᴇ 😊 ɢᴏ ᴛᴏ @YOUTUBE_RROBOT Sᴛᴀʀᴛ ᴀɴᴅ Dᴍ ᴏᴡɴᴇʀ ᴛᴏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ"""
    )
)

    # Create InlineKeyboardMarkup with the switch button
    reply_markup = InlineKeyboardMarkup([[switch_button]])

    # Send the message with the button
    await message.reply(text, reply_markup=reply_markup, disable_web_page_preview=True)

@app.on_message(filters.command("add"))
async def add_command(client, message):
    if message.from_user.id != OWNER_ID:
        return 

    try:
        args = message.text.split()
        user_id = int(args[1])
        days = int(args[2])
        await add_subscriber(user_id, days)
        await message.reply(f"Usᴇʀ {user_id} ᴛᴏ ᴀᴅᴅᴇᴅ sᴜʙsᴄʀɪʙᴇʀʟɪsᴛ ғᴏʀ {days} ᴅᴀʏs !")
    except:
        await message.reply("Pʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴄᴏʀʀᴇᴄᴛ: `/add user_id days`")


# Remove Subscriber Command
@app.on_message(filters.command("rm"))
async def remove_command(client, message):
    if message.from_user.id != OWNER_ID:
        return 

    try:
        args = message.text.split()
        user_id = int(args[1])
        await remove_subscriber(user_id)
        await message.reply(f"Usᴇʀ {user_id} ᴛᴏ ʀᴇᴍᴏᴠᴇ sᴜʙsᴄʀɪʙᴇʀʟɪsᴛ !")
    except:
        await message.reply("Pʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴄᴏʀʀᴇᴄᴛ: `/rm user_id`")



# Broadcast Command
@app.on_message(filters.command("broadcast"))
@language
async def broadcast_message(client, message, _):
    global IS_BROADCASTING
    user_id = message.from_user.id

    # Owner चेक
    if user_id != OWNER_ID:
        user = subscribers.find_one({"user_id": user_id})
        if not user:
            return await message.reply("Oɴʟʏ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴜsᴇʀ ᴜsᴇ !")

        # Usage limit चेक करें
        if user["usage_count"] >= 3:
            return await message.reply("Yᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ᴜsᴇs ᴛᴏᴅᴀʏ ǫᴜɪᴛᴀ ʀᴇᴛʀʏ ᴀғᴛᴇʀ 24ʜʀ")

        # Usage count बढ़ाएं
        subscribers.update_one({"user_id": user_id}, {"$inc": {"usage_count": 1}})

    # Broadcast Logic
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])
        query = message.text.split(None, 1)[1]
        query = query.replace("-pin", "").replace("-nobot", "").replace("-pinloud", "").replace("-assistant", "").replace("-user", "")
        if query == "":
            return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

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
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except:
            pass

    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await app.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await app.send_message(i, text=query)
                )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except:
            pass

    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from YTMUSIC.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    await client.forward_messages(
                        dialog.chat.id, y, x
                    ) if message.reply_to_message else await client.send_message(
                        dialog.chat.id, text=query
                    )
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass
    IS_BROADCASTING = False


# Auto-clean Task
async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS):
                        if user.privileges.can_manage_video_chats:
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


# Background Tasks
asyncio.create_task(auto_clean())
asyncio.create_task(clean_expired_subscribers())
        
