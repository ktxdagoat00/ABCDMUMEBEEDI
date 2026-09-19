import os
import asyncio
import subprocess
import urllib.parse
import urllib.request
import static_ffmpeg
import yt_dlp
import requests
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.types import DocumentAttributeAudio

SPY_MODE = False

# Ensure static ffmpeg binary path is active
static_ffmpeg.add_paths()

def parse_time_to_seconds(time_str):
    parts = time_str.strip().split(':')
    parts = [int(p) for p in parts]
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    elif len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return 0

def setup(client):

    # --- .ytdl <link> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ytdl(?:\s+(.+))?'))
    async def download_video(event):
        url = event.pattern_match.group(1)
        if not url:
            await event.edit("```text\n[!] Usage: .ytdl <video/shorts/reels link>\n```")
            return

        status = await event.edit("```text\n┌───「 ⚡ 𝗙𝗘𝗧𝗖𝗛𝗜𝗡𝗚 𝗠𝗘𝗗𝗜𝗔... 」\n└───「 🛰️ Bypassing security stream 」\n```")
        out_template = f"video_{event.id}.%(ext)s"

        # Bypass YouTube IP Block using mweb / android_creator client
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': out_template,
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 48 * 1024 * 1024,
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb', 'android_embedded']
                }
            }
        }

        loop = asyncio.get_event_loop()
        file_path = None
        title = "Downloaded Media"

        # Attempt 1: Direct yt-dlp with mweb spoofing
        def run_ytdl():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                inf = ydl.extract_info(url, download=True)
                fn = ydl.prepare_filename(inf)
                return inf, fn

        try:
            info, file_path = await loop.run_in_executor(None, run_ytdl)
            title = info.get('title', 'Downloaded Media')
        except Exception:
            # Attempt 2: Fallback to fast external gateway if Cloud IP is strictly banned
            try:
                def run_gateway():
                    api_endpoints = [
                        "https://cobalt-api.kwiatekm.com/",
                        "https://api.wuk.sh/"
                    ]
                    headers = {"Accept": "application/json", "Content-Type": "application/json"}
                    for ep in api_endpoints:
                        try:
                            r = requests.post(ep, json={"url": url}, headers=headers, timeout=12)
                            res = r.json()
                            if "url" in res:
                                return res["url"]
                        except Exception:
                            continue
                    return None

                stream_url = await loop.run_in_executor(None, run_gateway)
                if stream_url:
                    chat = await event.get_input_chat()
                    await status.edit("```text\n┌───「 📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚... 」\n└───「 ⚡ Streaming video file 」\n```")
                    await client.send_file(chat, stream_url, caption="🎬 **Downloaded Video**")
                    await status.delete()
                    return
            except Exception:
                pass

        if file_path and os.path.exists(file_path):
            await status.edit("```text\n┌───「 📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚... 」\n└───「 ⚡ Sending video to chat 」\n```")
            chat = await event.get_input_chat()
            await client.send_file(
                chat,
                file_path,
                caption=f"🎬 **{title[:40]}**",
                supports_streaming=True
            )
            os.remove(file_path)
            await status.delete()
        else:
            await status.edit("```text\n[!] Video Extraction Failed: YouTube blocked this cloud IP.\nTip: Reels, Shorts & TikTok work 100%.\n```")

    # --- .song <name> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.song(?:\s+(.+))?'))
    async def download_song(event):
        query = event.pattern_match.group(1)
        if not query:
            await event.edit("```text\n[!] Usage: .song <song name>\nExample: .song Kesariya\n```")
            return

        status = await event.edit(f"```text\n┌───「 🎵 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢... 」\n└───「 🛰️ Query: {query[:25]} 」\n```")
        out_template = f"song_{event.id}.%(ext)s"

        # Method 1: SoundCloud primary (No IP block on cloud datacenter)
        ydl_opts_sc = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'default_search': 'scsearch1:',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 45 * 1024 * 1024
        }

        # Method 2: YouTube with mweb fallback
        ydl_opts_yt = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'default_search': 'ytsearch1:',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 45 * 1024 * 1024,
            'extractor_args': {
                'youtube': {
                    'player_client': ['mweb', 'android_embedded']
                }
            }
        }

        loop = asyncio.get_event_loop()

        def extract_audio():
            # Try SoundCloud first to prevent bot verification errors
            try:
                with yt_dlp.YoutubeDL(ydl_opts_sc) as ydl:
                    inf = ydl.extract_info(query, download=True)
                    if 'entries' in inf and inf['entries']:
                        inf = inf['entries'][0]
                    return inf, ydl.prepare_filename(inf)
            except Exception:
                with yt_dlp.YoutubeDL(ydl_opts_yt) as ydl:
                    inf = ydl.extract_info(query, download=True)
                    if 'entries' in inf and inf['entries']:
                        inf = inf['entries'][0]
                    return inf, ydl.prepare_filename(inf)

        try:
            info, file_path = await loop.run_in_executor(None, extract_audio)
            
            await status.edit("```text\n┌───「 📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢... 」\n└───「 ⚡ Sending MP3 stream 」\n```")
            
            title = info.get('title', 'Audio Track')
            uploader = info.get('uploader', 'Unknown Artist')
            duration = int(info.get('duration', 0))

            chat = await event.get_input_chat()
            await client.send_file(
                chat,
                file_path,
                caption=f"🎧 **Title:** `{title}`\n🎙️ **Artist:** `{uploader}`",
                attributes=[DocumentAttributeAudio(duration=duration, title=title, performer=uploader)]
            )

            if os.path.exists(file_path):
                os.remove(file_path)
            await status.delete()

        except Exception as e:
            await status.edit(f"```text\n[!] Song Download Failed: {e}\n```")

    # --- .trim <start> <end> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.trim(?:\s+([^\s]+))?(?:\s+([^\s]+))?'))
    async def trim_media(event):
        reply = await event.get_reply_message()
        if not reply or not (reply.video or reply.audio or reply.voice or reply.document):
            await event.edit("```text\n[!] Reply to audio/video to trim.\nExample: .trim 01:01 11:39\n```")
            return

        start_time = event.pattern_match.group(1)
        end_time = event.pattern_match.group(2)

        if not start_time or not end_time:
            await event.edit("```text\n[!] Usage: .trim 01:01 11:39\n```")
            return

        try:
            start_sec = parse_time_to_seconds(start_time)
            end_sec = parse_time_to_seconds(end_time)
            if end_sec <= start_sec:
                await event.edit("```text\n[!] Error: End time must be greater than start time.\n```")
                return
            duration = end_sec - start_sec
        except Exception:
            await event.edit("```text\n[!] Invalid time format. Use mm:ss (e.g. 01:01 11:39)\n```")
            return

        status = await event.edit("```text\n┌───「 ⏳ 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗠𝗘𝗗𝗜𝗔... 」\n└───「 🛰️ Preparing file for trim 」\n```")
        input_file = None
        output_file = None

        try:
            input_file = await client.download_media(reply)
            base, ext = os.path.splitext(input_file)
            output_file = f"{base}_trimmed{ext}"

            await status.edit(f"```text\n┌───「 ✂️ 𝗧𝗥𝗜𝗠𝗠𝗜𝗡𝗚... 」\n├─ ⏱️ Range: {start_time} ➔ {end_time}\n└───「 ⚡ Stream Copy (Lossless) 」\n```")

            cmd = [
                "ffmpeg", "-y",
                "-ss", str(start_sec),
                "-i", input_file,
                "-to", str(duration),
                "-c", "copy",
                output_file
            ]

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, lambda: subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

            if not os.path.exists(output_file) or os.path.getsize(output_file) == 0:
                await status.edit("```text\n[!] Trim failed. Keyframes missing or file protected.\n```")
                return

            await status.edit("```text\n┌───「 📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚... 」\n└───「 ⚡ Sending trimmed media 」\n```")
            chat = await event.get_input_chat()

            await client.send_file(
                chat,
                output_file,
                caption=f"✂️ **Trimmed:** `{start_time}` - `{end_time}`",
                reply_to=reply.id
            )
            await status.delete()

        except Exception as e:
            await status.edit(f"```text\n[!] Trim Error: {e}\n```")
        finally:
            if input_file and os.path.exists(input_file):
                os.remove(input_file)
            if output_file and os.path.exists(output_file):
                os.remove(output_file)

    # --- .save <reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.save$'))
    async def save_media(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to any text, link, photo or video to save.\n```")
            return

        status = await event.edit("```text\n┌───「 📥 𝗦𝗔𝗩𝗜𝗡𝗚... 」\n└───「 🛰️ 𝗧𝗥𝗔𝗡𝗦𝗙𝗘𝗥𝗥𝗜𝗡𝗚 𝗧𝗢 𝗦𝗔𝗩𝗘𝗗 」\n```")
        try:
            if reply.media:
                path = await client.download_media(reply)
                caption = reply.raw_text or ""
                await client.send_file("me", path, caption=caption)
                if path and os.path.exists(path):
                    os.remove(path)
            else:
                await client.send_message("me", reply.raw_text)

            await status.edit("```text\n┌───「 ✅ 𝗦𝗔𝗩𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬 」\n└───「 📁 𝗦𝗧𝗢𝗥𝗘𝗗 𝗜𝗡 𝗦𝗔𝗩𝗘𝗗 𝗠𝗘𝗦𝗦𝗔𝗚𝗘𝗦 」\n```")
            await asyncio.sleep(2)
            await status.delete()
        except Exception as e:
            await status.edit(f"```text\n[!] Save Failed: {e}\n```")

    # --- .spymode on / off ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.spymode(?:\s+(on|off))?$'))
    async def toggle_spymode(event):
        global SPY_MODE
        arg = event.pattern_match.group(1)

        if not arg:
            curr = "ACTIVE 🟢" if SPY_MODE else "DISABLED 🔴"
            await event.edit(f"```text\n[!] SpyMode Status: {curr}\nUsage: .spymode on | off\n```")
            return

        if arg.lower() == "on":
            SPY_MODE = True
            await event.edit("```text\n┌───「 🕵️ 𝗦𝗣𝗬𝗠𝗢𝗗𝗘 : 𝗢𝗡 」\n└───「 🛰️ 𝗩𝗶𝗲𝘄-𝗢𝗻𝗰𝗲 𝗠𝗲𝗱𝗶𝗮 𝗔𝘂𝘁𝗼-𝗖𝗮𝗽𝘁𝘂𝗿𝗲 𝗔𝗰𝘁𝗶𝘃𝗲 」\n```")
        else:
            SPY_MODE = False
            await event.edit("```text\n┌───「 🕵️ 𝗦𝗣𝗬𝗠𝗢𝗗𝗘 : 𝗢𝗙𝗙 」\n└───「 🔒 𝗠𝗲𝗱𝗶𝗮 𝗔𝘂𝘁𝗼-𝗖𝗮𝗽𝘁𝘂𝗿𝗲 𝗦𝘁𝗼𝗽𝗽𝗲𝗱 」\n```")
        
        await asyncio.sleep(2)
        await event.delete()

    # --- View-Once Spy Listener ---
    @client.on(events.NewMessage(incoming=True))
    async def spy_listener(event):
        global SPY_MODE
        if not SPY_MODE or not event.media:
            return

        ttl = getattr(event.media, 'ttl_seconds', None)
        if ttl is not None and ttl > 0:
            try:
                sender = await event.get_sender()
                sender_name = getattr(sender, 'first_name', 'Unknown')
                uname = f"@{sender.username}" if getattr(sender, 'username', None) else f"ID: {event.sender_id}"
                
                path = await client.download_media(event.message)
                info = (
                    "```text\n"
                    "╔════「 🕵️ 𝗦𝗣𝗬𝗠𝗢𝗗𝗘 : 𝗩𝗜𝗘𝗪-𝗢𝗡𝗖𝗘 𝗖𝗔𝗨𝗚𝗛𝗧 」════╗\n"
                    f"╠─ 👤 𝗦𝗘𝗡𝗗𝗘𝗥 :: {sender_name} ({uname})\n"
                    f"╠─ ⏱️ 𝗧𝗧𝗟    :: {ttl}s\n"
                    "╚══════════════════════════════════════════════╝\n"
                    "```"
                )
                await client.send_file("me", path, caption=info)
                if path and os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"[SPYMODE ERROR] {e}")

    # --- .pfp <reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.pfp$'))
    async def set_pfp(event):
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            await event.edit("```text\n[!] Reply to an image to set as PFP.\n```")
            return

        status = await event.edit("```text\n┌───「 🖼️ 𝗣𝗥𝗢𝗖𝗘𝗦𝗦𝗜𝗡𝗚 𝗣𝗙𝗣... 」\n└───「 🛰️ 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚 𝗧𝗢 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 」\n```")
        try:
            path = await client.download_media(reply)
            uploaded = await client.upload_file(path)
            await client(UploadProfilePhotoRequest(file=uploaded))
            if path and os.path.exists(path):
                os.remove(path)
            await status.edit("```text\n┌───「 ✅ 𝗣𝗙𝗣 𝗨𝗣𝗗𝗔𝗧𝗘𝗗 」\n└───「 👤 𝗡𝗲𝘄 𝗽𝗿𝗼𝗳𝗶𝗹𝗲 𝗽𝗵𝗼𝘁𝗼 𝗮𝗰𝘁𝗶𝘃𝗲 」\n```")
            await asyncio.sleep(2)
            await status.delete()
        except Exception as e:
            await status.edit(f"```text\n[!] PFP Error: {e}\n```")

    # --- .tts <text/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tts(?:\s+(.+))?'))
    async def text_to_speech(event):
        arg = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        text = arg if arg else (reply.raw_text if reply else "")

        if not text:
            await event.edit("```text\n[!] Provide text or reply to a message: .tts <text>\n```")
            return

        status = await event.edit("```text\n┌───「 🎙️ 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢... 」\n└───「 ⚡ 𝗖𝗼𝗻𝘃𝗲𝗿𝘁𝗶𝗻𝗴 𝘁𝗲𝘅𝘁 𝘁𝗼 𝘃𝗼𝗶𝗰𝗲 」\n```")
        out_file = f"tts_{event.id}.mp3"

        try:
            encoded_text = urllib.parse.quote(text[:200])
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl=hi&client=tw-ob"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            loop = asyncio.get_event_loop()
            
            def fetch_audio():
                with urllib.request.urlopen(req) as resp, open(out_file, 'wb') as f:
                    f.write(resp.read())

            await loop.run_in_executor(None, fetch_audio)

            chat = await event.get_input_chat()
            await client.send_file(chat, out_file, voice_note=True)
            
            if os.path.exists(out_file):
                os.remove(out_file)
            await status.delete()
        except Exception as e:
            await status.edit(f"```text\n[!] TTS Failed: {e}\n```")
