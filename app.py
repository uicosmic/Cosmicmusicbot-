import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp
import config

bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

def download_song(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'default_search': 'ytsearch',
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        },
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)
        if 'entries' in info:
            info = info['entries'][0]
        filename = ydl.prepare_filename(info).replace(info['ext'], 'mp3')
        return filename, info['title']

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply_text("✨ **Cosmic Music Downloader Bot is Online!**\n\nGroup me `/play [song name]` likhein download karne ke liye.")

@bot.on_message(filters.command("play"))
async def play_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/play [song name]`")
    
    query = message.text.split(None, 1)[1]
    m = await message.reply_text("🔎 **Searching and Downloading your song... Please wait**")
    
    try:
        filename, title = await asyncio.to_thread(download_song, query)
        await m.edit_text("📤 **Uploading song to Telegram...**")
        
        await message.reply_audio(
            audio=filename,
            title=title,
            caption=f"🎵 **Uploaded successfully!**\n🎧 **Requested By:** {message.from_user.mention if message.from_user else 'User'}"
        )
        await m.delete()
        
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        await m.edit_text(f"❌ **Error:** {e}")

async def start_server():
    await bot.start()
    print("🚀 Cosmic Downloader Bot is live!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    asyncio.get_event_loop().run_until_complete(start_server())
    
