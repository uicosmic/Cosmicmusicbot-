import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
import config

bot = Client("MusicBot", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.BOT_TOKEN)
assistant = Client("Assistant", api_id=config.API_ID, api_hash=config.API_HASH, session_string=config.SESSION_NAME)

@bot.on_message(filters.command("start") & filters.private)
async def start_handler(_, message: Message):
    await message.reply_text("✨ **Cosmic Music Bot is successfully online on Railway!**")

async def start_server():
    await bot.start()
    await assistant.start()
    print("🚀 Bot is online!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(start_server())
    
