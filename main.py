# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
# Additional Credit: CR Choudhary

import os
import sys
import asyncio
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from vars import API_ID, API_HASH, BOT_TOKEN
from pyromod.listen import Listen  # Ensure this is installed

# Bot Initialization
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
        "I Am A Bot Created By <a href='https://t.me/KingVJ01'>VJ</a> "
        f"and <a href='https://t.me/CR_Choudhary'>CR Choudhary</a>.\n\n"
        "I Help You Download Links From Your **.TXT** File And Upload Them To Telegram.\n"
        "To Get Started, Send Me /upload And Follow The Steps.\n\n"
        "Use /stop to cancel any ongoing task.</b>"
    )


@bot.on_message(filters.command("stop"))
async def stop_handler(_, m: Message):
    await m.reply_text("**Stopped** 🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)


@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text("Send your **.txt** file containing download links 🔗")
    input_file: Message = await bot.listen(editable.chat.id)  # Wait for user to send a file
    downloaded_path = await input_file.download()
    await input_file.delete()  # Clean up the user message after processing

    try:
        with open(downloaded_path, "r") as file:
            links = file.read().strip().split("\n")
        os.remove(downloaded_path)
    except Exception as e:
        await m.reply_text(f"**Error:** {e}")
        return

    await editable.edit(
        f"**Total Links Found:** {len(links)}\n\n"
        "Send the **starting index** for downloading (default is 1)."
    )
    start_msg: Message = await bot.listen(editable.chat.id)
    start_index = int(start_msg.text.strip()) if start_msg.text.isdigit() else 1
    await start_msg.delete()

    await editable.edit("Send a **batch name** for the uploads:")
    batch_msg: Message = await bot.listen(editable.chat.id)
    batch_name = batch_msg.text.strip()
    await batch_msg.delete()

    await editable.edit("Send the **resolution** for videos (e.g., 144, 240, 360, 480, 720, 1080):")
    resolution_msg: Message = await bot.listen(editable.chat.id)
    resolution = resolution_msg.text.strip()
    await resolution_msg.delete()

    await editable.edit("Send a **caption** for your uploaded files (optional):")
    caption_msg: Message = await bot.listen(editable.chat.id)
    caption = caption_msg.text.strip() or "No Caption Provided"
    await caption_msg.delete()

    await editable.edit("Send a **thumbnail URL** or type 'no' if not required:")
    thumbnail_msg: Message = await bot.listen(editable.chat.id)
    thumbnail = thumbnail_msg.text.strip()
    await thumbnail_msg.delete()
    thumbnail = thumbnail if thumbnail.lower() != "no" else None

    await editable.edit("Processing your request... Please wait!")

    # Downloading and uploading process
    async with aiohttp.ClientSession() as session:
        for i, link in enumerate(links[start_index - 1:], start=start_index):
            file_name = f"{batch_name}_{i}"  # Dynamic file name
            try:
                if ".pdf" in link.lower():  # Check if link is a PDF
                    await download_file(session, link, f"{file_name}.pdf")
                    await bot.send_document(
                        m.chat.id,
                        f"{file_name}.pdf",
                        caption=caption
                    )
                    os.remove(f"{file_name}.pdf")  # Clean up local file
                elif ".mp4" in link.lower() or "video" in link.lower():  # Check if link is a video
                    await download_file(session, link, f"{file_name}.mp4")
                    await bot.send_video(
                        m.chat.id,
                        f"{file_name}.mp4",
                        caption=caption,
                        thumb=thumbnail
                    )
                    os.remove(f"{file_name}.mp4")  # Clean up local file
                else:
                    await m.reply_text(f"**Skipping unknown file type:** {link}")
            except Exception as e:
                await m.reply_text(f"**Error processing {link}:** {e}")

    await m.reply_text("**Task Completed!** 😎\n\n**Credits:** CR Choudhary & VJ")


async def download_file(session, url, file_name):
    """Helper function to download files."""
    async with session.get(url) as response:
        if response.status == 200:
            with open(file_name, "wb") as f:
                f.write(await response.read())
        else:
            raise Exception(f"Failed to download {url} - HTTP {response.status}")


bot.run()
