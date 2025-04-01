import logging 
import logging.config
import os
import asyncio
from aiohttp import web
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import *
from utils import temp
from plugins import web_server
from lazybot import LazyPrincessBot
from util.keepalive import ping_server
from lazybot.clients import initialize_clients

# ✅ Logging Configuration
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

# ✅ Use Koyeb-assigned port (Default: 8080)
PORT = int(os.environ.get("PORT", 8080))  

async def Lazy_start():
    print('\nInitializing Telegram Bot...')
    
    # ✅ Ensure download directory exists
    if not os.path.isdir(DOWNLOAD_LOCATION):
        os.makedirs(DOWNLOAD_LOCATION)

    # ✅ Start the bot properly inside the event loop
    await LazyPrincessBot.start()
    
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username

    await initialize_clients()

    if ON_HEROKU:  # ✅ Not needed for Koyeb, but safe to keep
        asyncio.create_task(ping_server())

    b_users, b_chats, lz_verified = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    temp.LAZY_VERIFIED_CHATS = lz_verified

    await Media.ensure_indexes()

    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username

    # ✅ Web Server for Koyeb Health Checks
    app = web.Application()
    app.add_routes([web.get("/", lambda request: web.Response(text="Bot is running on Koyeb! 🚀"))])  

    # ✅ Use your actual web server setup
    runner = web.AppRunner(await web_server())  
    await runner.setup()

    # ✅ Bind to 0.0.0.0 (required for Koyeb)
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    logging.info(f"{me.first_name} running Pyrogram v{__version__} (Layer {layer}) started as {me.username}.")
    logging.info(LOG_STR)

    await idle()

if __name__ == '__main__':
    try:
        asyncio.run(Lazy_start())  # ✅ Fixes event loop issues
        logging.info('-----------------------🧐 Service running in Lazy Mode 😴-----------------------')
    except KeyboardInterrupt:
        logging.info('-----------------------😜 Service Stopped Sweetheart 😝-----------------------')
        
