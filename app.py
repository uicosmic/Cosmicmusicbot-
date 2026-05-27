import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from pytgcalls.types.groups import GroupCallConfig
import yt_dlp
import config

bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
assistant = Client("Assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_NAME)

call_py = PyTgCalls(assistant)
music_queue = {}

def get_live_stream(query):
    ydl_opts = {"format": "bestaudio/best", "quiet": True, "default_search": "ytsearch", "nocheckcertificate": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title']

@bot.on_message(filters.command("play") & filters.group)
async def play_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/play [song name]`")
    
    query = message.text.split(None, 1)[1]
    chat_id = message.chat.id
    m = await message.reply_text("🔎 Searching...")

    try:
        link, title = await asyncio.to_thread(get_live_stream, query)
        
        if chat_id not in music_queue:
            music_queue[chat_id] = []
        music_queue[chat_id].append(query)

        if len(music_queue[chat_id]) > 1:
            return await m.edit_text(f"📝 **Queued:** `{title}`")

        await call_py.join_group_call(chat_id, MediaStream(link), config=GroupCallConfig(ask_join_as=True))
        await m.edit_text(f"🎵 **Playing:** `{title}`")
    except Exception as e:
        await m.edit_text(f"❌ **Error:** {e}")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, message: Message):
    try:
        await call_py.leave_call(message.chat.id)
        music_queue[message.chat.id] = []
        await message.reply_text("⏹️ **Stopped streaming.**")
    except:
        await message.reply_text("❌ Assistant Voice Chat me nahi hai.")

async def start_server():
    await bot.start()
    await assistant.start()
    await call_py.start()
    print("🚀 Bot and Assistant are running perfectly!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
  
