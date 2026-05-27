import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp
import config

bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
assistant = Client("Assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_NAME)
call_py = PyTgCalls(assistant)

# Live VC Streaming Link Generator
def get_live_link(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "noplaylist": True,
        "geo_bypass": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]
        return info['url'], info['title']

@bot.on_message(filters.command("play") & filters.group)
async def play_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/play [song name]`")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 **Searching and connecting to Voice Chat...**")
    
    try:
        # YouTube se stream link nikalna
        link, title = await asyncio.to_thread(get_live_link, query)
        
        # Assistant ko VC ke andar join karwa kar live stream chalana
        await call_py.join_group_call(
            message.chat.id,
            AudioPiped(link)
        )
        await m.edit_text(f"🎵 **Started Streaming on VC:** `{title}`\n\n🎧 **Requested By:** {message.from_user.mention}")
    except Exception as e:
        await m.edit_text(f"❌ **VC Error:** {e}\n\n*Make sure group Voice Chat is started and Assistant is in the group!*")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, message: Message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("⏹️ **Voice Chat streaming stopped!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {e}")

async def start_server():
    await bot.start()
    await assistant.start()
    await call_py.start()
    print("🚀 VC Music Bot is Live!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    
