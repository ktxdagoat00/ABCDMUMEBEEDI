import os
import asyncio
from PIL import Image
from telethon import events
from telethon.errors import YouBlockedUserError

def resize_for_sticker(image_path, output_path):
    im = Image.open(image_path)
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

        mode_arg = (event.pattern_match.group(1) or "").strip().lower()
        status = await event.edit("```text\n┌───「 💬 𝗤𝗨𝗢𝗧𝗜𝗡𝗚 𝗠𝗘𝗦𝗦𝗔𝗚𝗘... 」\n└───「 ⚡ Converting via Quotly 」\n```")
        chat = await event.get_input_chat()

        try:
            # Send/forward directly without conversation lock
            fwd_msg = await client.forward_messages("@QuotLyBot", reply)

            if mode_arg == "r":
                await client.send_message("@QuotLyBot", "/q r")

            # Wait for Quotly bot to reply (max 12 seconds)
            sticker_msg = None
            for _ in range(24):
                await asyncio.sleep(0.5)
                async for msg in client.iter_messages("@QuotLyBot", limit=3):
                    if msg.id > fwd_msg.id and msg.media:
                        sticker_msg = msg
                        break
                if sticker_msg:
                    break

            if sticker_msg and sticker_msg.media:
                await client.send_file(chat, sticker_msg.media, reply_to=reply.id)
                await status.delete()
                # Mark as read in bot DM
                await client.send_read_acknowledge("@QuotLyBot")
            else:
                await status.edit("```text\n[!] Quotly bot did not respond in time.\n```")

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
        uname = me.username or f"user{user_id}"
        pack_shortname = f"keshav_{user_id}_pack"
        pack_title = f"K E S H A V Pack (@{uname})"

        dl_path = f"temp_kang_{event.id}"
        formatted_path = f"kang_{event.id}.png"

        try:
            await client.download_media(reply, file=dl_path)
            resize_for_sticker(dl_path, formatted_path)

            async with client.conversation("@Stickers", timeout=20) as conv:
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
            if os.path.exists(dl_path):
                os.remove(dl_path)
            if os.path.exists(formatted_path):
                os.remove(formatted_path)
