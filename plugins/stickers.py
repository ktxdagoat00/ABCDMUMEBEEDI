import os
import asyncio
from PIL import Image
from telethon import events
from telethon.errors import YouBlockedUserError

def resize_for_sticker(image_path, output_path):
    im = Image.open(image_path)
    im = im.convert("RGBA")
    maxsize = (512, 512)
    im.thumbnail(maxsize, Image.Resampling.LANCZOS)
    im.save(output_path, "PNG")

def setup(client):

    # --- 1. .q / .q r (Quoted message to Sticker via Quotly) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.q(?:\s+(.+))?'))
    async def quotly_cmd(event):
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("```text\n[!] Reply to any text message to quote it.\n```")
            return

        arg = (event.pattern_match.group(1) or "").strip().lower()
        status = await event.edit("```text\n┌───「 💬 𝗤𝗨𝗢𝗧𝗜𝗡𝗚 𝗠𝗘𝗦𝗦𝗔𝗚𝗘... 」\n└───「 ⚡ Processing sticker frame 」\n```")
        chat = await event.get_input_chat()

        try:
            quotly_peer = await client.get_input_entity("@QuotLyBot")

            fwd_msg = await client.forward_messages(quotly_peer, reply)

            if "r" in arg:
                await asyncio.sleep(0.3)
                cmd_msg = await client.send_message(quotly_peer, "/q r", reply_to=fwd_msg.id)
                threshold_id = cmd_msg.id
            else:
                threshold_id = fwd_msg.id

            sticker_msg = None
            for _ in range(30):
                await asyncio.sleep(0.5)
                async for msg in client.iter_messages(quotly_peer, limit=5):
                    if msg.id > threshold_id and msg.media:
                        sticker_msg = msg
                        break
                if sticker_msg:
                    break

            if sticker_msg and sticker_msg.media:
                await client.send_file(chat, sticker_msg.media, reply_to=reply.id)
                await status.delete()
                await client.send_read_acknowledge(quotly_peer)
            else:
                await status.edit("```text\n[!] Quotly bot timed out. Try again!\n```")

        except YouBlockedUserError:
            await status.edit("```text\n[!] Unblock @QuotLyBot first!\n```")
        except Exception as e:
            await status.edit(f"```text\n[!] Quote Error: {e}\n```")

    # --- 2. .kang <emoji> (Sticker / Image to K E S H A V Pack) ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.kang(?:\s+(.+))?'))
    async def kang_cmd(event):
        reply = await event.get_reply_message()
        if not reply or not (reply.photo or reply.sticker or (reply.document and "image" in reply.document.mime_type)):
            await event.edit("```text\n[!] Reply to an image or sticker to kang it!\n```")
            return

        target_emoji = event.pattern_match.group(1) or "⚡"
        status = await event.edit("```text\n┌───「 📥 𝗞𝗔𝗡𝗚𝗜𝗡𝗚 𝗦𝗧𝗜𝗖𝗞𝗘𝗥... 」\n└───「 🛰️ Processing media stream 」\n```")

        me = await client.get_me()
        user_id = me.id
        uname = me.username or f"user_{user_id}"
        pack_shortname = f"keshav_{user_id}_pack"
        pack_title = f"K E S H A V Pack (@{uname})"

        formatted_path = f"kang_{event.id}.png"
        downloaded_file = None

        try:
            # Telethon returns the actual saved filepath
            downloaded_file = await client.download_media(reply, file=f"temp_kang_{event.id}")
            if not downloaded_file or not os.path.exists(downloaded_file):
                await status.edit("```text\n[!] Media download failed.\n```")
                return

            resize_for_sticker(downloaded_file, formatted_path)

            async with client.conversation("@Stickers", timeout=25) as conv:
                await conv.send_message("/cancel")
                await conv.get_response()

                await conv.send_message("/addsticker")
                resp = await conv.get_response()

                if "Choose a sticker pack" in resp.text or "pack" in resp.text.lower():
                    await conv.send_message(pack_shortname)
                    resp = await conv.get_response()

                if "Invalid pack" in resp.text or "not found" in resp.text.lower() or "Choose a sticker set" in resp.text:
                    await conv.send_message("/cancel")
                    await conv.get_response()
                    await conv.send_message("/newpack")
                    await conv.get_response()
                    await conv.send_message(pack_title)
                    await conv.get_response()
                    await conv.send_file(formatted_path, force_document=True)
                    await conv.get_response()
                    await conv.send_message(target_emoji)
                    await conv.get_response()
                    await conv.send_message("/publish")
                    await conv.get_response()
                    await conv.send_message("/skip")
                    await conv.get_response()
                    await conv.send_message(pack_shortname)
                    await conv.get_response()
                else:
                    await conv.send_file(formatted_path, force_document=True)
                    await conv.get_response()
                    await conv.send_message(target_emoji)
                    await conv.get_response()
                    await conv.send_message("/done")
                    await conv.get_response()

                await conv.mark_read()

            card = (
                "```text\n"
                "╔════「 ⚡ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗞𝗔𝗡𝗚𝗘𝗗 ⚡ 」════╗\n"
                "║\n"
                "╠─ 👤 MASTER :: K E S H A V\n"
                f"╠─ 🎭 EMOJI  :: {target_emoji}\n"
                f"╠─ 📦 PACK   :: t.me/addstickers/{pack_shortname}\n"
                "║\n"
                "╚══════════════════════════════════╝\n"
                "```"
            )
            await status.edit(card)

        except YouBlockedUserError:
            await status.edit("```text\n[!] Unblock @Stickers bot first!\n```")
        except Exception as e:
            await status.edit(f"```text\n[!] Kang Failed: {e}\n```")
        finally:
            if downloaded_file and os.path.exists(downloaded_file):
                os.remove(downloaded_file)
            if os.path.exists(formatted_path):
                os.remove(formatted_path)
