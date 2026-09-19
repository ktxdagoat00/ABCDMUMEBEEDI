import os
import asyncio
import urllib.parse
import urllib.request
import yt_dlp
from telethon import events
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.types import DocumentAttributeAudio

SPY_MODE = False

def setup(client):

    # --- .song <name> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.song(?:\s+(.+))?'))
    async def download_song(event):
        query = event.pattern_match.group(1)
        if not query:
            await event.edit("```text\n[!] Usage: .song <song name or link>\nExample: .song Kesariya\n```")
            return

        status = await event.edit(f"```text\n┌───「 🎵 𝗦𝗘𝗔𝗥𝗖𝗛𝗜𝗡𝗚 𝗔𝗨𝗗𝗜𝗢... 」\n└───「 🛰️ Query: {query[:25]} 」\n```")
        
        out_template = f"song_{event.id}.%(ext)s"
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_template,
            'default_search': 'ytsearch1:',
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'max_filesize': 45 * 1024 * 1024
        }

        loop = asyncio.get_event_loop()
        try:
            def extract():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(query, download=True)
                    if 'entries' in info:
                        info = info['entries'][0]
                    file_path = ydl.prepare_filename(info)
                    return info, file_path

            info, file_path = await loop.run_in_executor(None, extract)
            
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

    # --- .ytdl <link> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.ytdl(?:\s+(.+))?'))
    async def download_video(event):
        url = event.pattern_match.group(1)
        if not url:
            await event.edit("```text\n[!] Usage: .ytdl <video/shorts/reels link>\n```")
            return

        status = await event.edit("```text\n┌───「 ⚡ 𝗙𝗘𝗧𝗖𝗛𝗜𝗡𝗚 𝗠𝗘𝗗𝗜𝗔... 」\n└───「 🛰️ 𝗥𝗲𝗾𝘂𝗲𝘀𝘁𝗶𝗻𝗴 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝘀𝘁𝗿𝗲𝗮𝗺 」\n```")
        try:
            import requests
            api_url = "https://api.cobalt.tools/api/json"
            headers = {"Accept": "application/json", "Content-Type": "application/json"}
            payload = {"url": url}
            
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: requests.post(api_url, json=payload, headers=headers, timeout=15))
            data = res.json()

            stream_url = data.get("url")
            if not stream_url:
                await status.edit("```text\n[!] Stream URL not extracted. Site may be protected.\n```")
                return

            await status.edit("```text\n┌───「 📤 𝗨𝗣𝗟𝗢𝗔𝗗𝗜𝗡𝗚... 」\n└───「 ⚡ 𝗦𝗲𝗻𝗱𝗶𝗻𝗴 𝗺𝗲𝗱𝗶𝗮 𝗳𝗶𝗹𝗲 」\n```")
            chat = await event.get_input_chat()
            await client.send_file(chat, stream_url, caption="🎬 **Downloaded Media**")
            await status.delete()
        except Exception as e:
            await status.edit(f"```text\n[!] YTDL Error: {e}\n```")
