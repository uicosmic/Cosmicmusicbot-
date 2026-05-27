import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import yt_dlp
import config

bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)

# Modified Bypass Song Download Function
def download_song(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'keepvideo': False,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        # YouTube block bypass karne ke liye search sequence badla hai
        'default_search': 'ytsearch',
        'noplaylist': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        # Yeh headers YouTube ko chakma dene ke liye hain
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
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
        # Background download thread
        filename, title = await asyncio.to_thread(download_song, query)
        
        await m.edit_text("📤 **Uploading song to Telegram...**")
        
        # Audio file send karna
        await message.reply_audio(
            audio=filename,
            title=title,
            caption=f"🎵 **Uploaded successfully!**\n🎧 **Requested By:** {message.from_user.mention if message.from_user else 'User'}"
        )
        await m.delete()
        
        # Delete file after upload to save space
        if os.path.exists(filename):
            os.remove(filename)
            
    except Exception as e:
        # Agar fir bhi block ho, toh query link format error clear karega
        await m.edit_text(f"❌ **Error:** YouTube temporary blocked this request. Please try another song name or retry in a group!")

async def start_server():
    await bot.start()
    print("🚀 Cosmic Downloader Bot is fully live and active!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    asyncio.get_event_loop().run_until_complete(start_server())
    
