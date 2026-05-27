import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
import yt_dlp
import config

bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
assistant = Client("Assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_NAME)
call_py = PyTgCalls(assistant)

def get_stream_link(query):
    ydl_opts = {"format": "bestaudio/best", "quiet": True, "default_search": "ytsearch", "nocheckcertificate": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]
        return info['url'], info['title']

@bot.on_message(filters.command("play") & filters.group)
async def play_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/play [song name]`")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 **Searching...**")
    try:
        link, title = await asyncio.to_thread(get_stream_link, query)
        await call_py.join_group_call(message.chat.id, MediaStream(link))
        await m.edit_text(f"🎵 **Now Playing:** `{title}`")
    except Exception as e:
        await m.edit_text(f"❌ **Error:** {e}")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, message: Message):
    try:
        await call_py.leave_call(message.chat.id)
        await message.reply_text("⏹️ **Stream Stopped!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {e}")

async def start_server():
    await bot.start()
    await assistant.start()
    await call_py.start()
    print("🚀 Bot is live and light on resources!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    
