import os
import asyncio
import time

from yt_dlp import YoutubeDL
from pyrogram import enums
from pyrogram.types import Message
from pyrogram import Client, filters

from config import Config
from plugins.functions.help_ytdl import get_file_extension_from_url, get_resolution
from plugins.functions.display_progress import progress_for_pyrogram

YTDL_REGEX = r"^((?:https?:)?\/\/)"


@Client.on_callback_query(filters.regex("^ytdl_audio$"))
async def callback_query_ytdl_audio(_, callback_query):
    try:
        url = callback_query.message.reply_to_message.text
        message = callback_query.message
        start_time = time.time()

        def download_progress_hook(d):
            if d['status'] == 'downloading':
                current = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
                asyncio.create_task(progress_for_pyrogram(current, total, "Downloading...", message, start_time))
            elif d['status'] == 'finished':
                asyncio.create_task(message.edit_text("**Download finished. Uploading...**"))

        ydl_opts = {
            "format": "bestaudio",
            "outtmpl": "%(title)s - %(extractor)s-%(id)s.%(ext)s",
            "writethumbnail": True,
            "progress_hooks": [download_progress_hook],
            "cookiefile": "cookies.txt", # Add this line
        }
        with YoutubeDL(ydl_opts) as ydl:
            await message.reply_chat_action(enums.ChatAction.TYPING)
            info_dict = ydl.extract_info(url, download=True) # Changed to download=True
            audio_file = ydl.prepare_filename(info_dict)

            basename = audio_file.rsplit(".", 1)[-2]
            if info_dict["ext"] == "webm":
                audio_file_weba = f"{basename}.weba"
                os.rename(audio_file, audio_file_weba)
                audio_file = audio_file_weba
            thumbnail_url = info_dict["thumbnail"]
            thumbnail_file = f"{basename}.{get_file_extension_from_url(thumbnail_url)}"
            download_location = f"{Config.DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"
            thumb = download_location if os.path.isfile(download_location) else None
            webpage_url = info_dict["webpage_url"]
            title = info_dict["title"] or ""
            caption = f'<b><a href="{webpage_url}">{title}</a></b>'
            duration = int(float(info_dict["duration"]))
            performer = info_dict["uploader"] or ""

            start_time = time.time() # Reset start time for upload
            await message.reply_audio(
                audio_file,
                caption=caption,
                duration=duration,
                performer=performer,
                title=title,
                parse_mode=enums.ParseMode.HTML,
                thumb=thumb,
                progress=progress_for_pyrogram,
                progress_args=("Uploading...", message, start_time)
            )

            os.remove(audio_file)
            os.remove(thumbnail_file)

    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        await callback_query.message.reply_to_message.delete()
        await callback_query.message.delete()


@Client.on_callback_query(filters.regex("^ytdl_video$"))
async def callback_query_ytdl_video(_, callback_query):
    try:
        url = callback_query.message.reply_to_message.text
        message = callback_query.message
        start_time = time.time()

        def download_progress_hook(d):
            if d['status'] == 'downloading':
                current = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', d.get('total_bytes_estimate', 0))
                asyncio.create_task(progress_for_pyrogram(current, total, "Downloading...", message, start_time))
            elif d['status'] == 'finished':
                asyncio.create_task(message.edit_text("**Download finished. Uploading...**"))

        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": "%(title)s - %(extractor)s-%(id)s.%(ext)s",
            "writethumbnail": True,
            "progress_hooks": [download_progress_hook],
            "cookiefile": "cookies.txt", # Add this line
        }
        with YoutubeDL(ydl_opts) as ydl:
            await message.reply_chat_action(enums.ChatAction.TYPING)
            info_dict = ydl.extract_info(url, download=True) # Changed to download=True
            video_file = ydl.prepare_filename(info_dict)

            basename = video_file.rsplit(".", 1)[-2]
            thumbnail_url = info_dict["thumbnail"]
            thumbnail_file = f"{basename}.{get_file_extension_from_url(thumbnail_url)}"
            download_location = f"{Config.DOWNLOAD_LOCATION}/{message.from_user.id}.jpg"
            thumb = download_location if os.path.isfile(download_location) else None
            webpage_url = info_dict["webpage_url"]
            title = info_dict["title"] or ""
            caption = f'<b><a href="{webpage_url}">{title}</a></b>'
            duration = int(float(info_dict["duration"]))
            width, height = get_resolution(info_dict)

            start_time = time.time() # Reset start time for upload
            await message.reply_video(
                video_file,
                caption=caption,
                duration=duration,
                width=width,
                height=height,
                parse_mode=enums.ParseMode.HTML,
                thumb=thumb,
                progress=progress_for_pyrogram,
                progress_args=("Uploading...", message, start_time)
            )

            os.remove(video_file)
            os.remove(thumbnail_file)

    except Exception as e:
        await message.reply_text(f"Error: {e}")
    finally:
        await callback_query.message.reply_to_message.delete()
        await callback_query.message.delete()
