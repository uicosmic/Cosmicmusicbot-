import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioImagePiped
import yt_dlp
import config

# Clients Initialization
bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
assistant = Client("Assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_NAME)
call_py = PyTgCalls(assistant)

# YouTube Se Audio Link Nikalne Ka Function
def get_stream_link(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "quiet": True,
        "default_search": "ytsearch",
        "nocheckcertificate": True,
        "noplaylist": True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info and len(info['entries']) > 0:
            info = info['entries'][0]
        return info['url'], info['title']

# Play Command
@bot.on_message(filters.command("play") & filters.group)
async def play_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/play [song name]`")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 **Searching song... Please wait**")
    
    try:
        # Background thread mein song search karna taaki bot lag na kare
        link, title = await asyncio.to_thread(get_stream_link, query)
        
        # Voice chat join karke audio stream chalana
        await call_py.join_group_call(
            message.chat.id,
            AudioImagePiped(link)
        )
        await m.edit_text(f"🎵 **Now Playing:** `{title}`\n\n🎧 **Requested By:** {message.from_user.mention}")
    except Exception as e:
        await m.edit_text(f"❌ **Error:** {e}")

# Stop Command
@bot.on_message(filters.command("stop") & filters.group)
async def stop_handler(_, message: Message):
    try:
        await call_py.leave_group_call(message.chat.id)
        await message.reply_text("⏹️ **Stream Stopped successfully!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** {e}")

# Server Start Function
async def start_server():
    await bot.start()
    await assistant.start()
    await call_py.start()
    print("🚀 Cosmic Music Bot with Playback is Online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    
