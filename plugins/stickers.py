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
            await event.edit("```text\n[!] Reply to any message to quote it.\n```")
            return

        arg = (event.pattern_match.group(1) or "").strip().lower()
        status = await event.edit("```text\n┌───「 💬 𝗤𝗨𝗢𝗧𝗜𝗡𝗚 𝗠𝗘𝗦𝗦𝗔𝗚𝗘... 」\n└───「 ⚡ Processing sticker frame 」\n```")
        chat = await event.get_input_chat()

        try:
            quotly_peer = await client.get_input_entity("@QuotLyBot")
            
            # Message(s) to forward
            msgs_to_fwd = []
            if "r" in arg:
                # If .q r is used, check if the replied message itself is replying to another message
                parent_reply = await reply.get_reply_message()
                if parent_reply:
                    msgs_to_fwd = [parent_reply, reply]
                else:
                    msgs_to_fwd = [reply]
            else:
                msgs_to_fwd = [reply]

            last_sent = await client.forward_messages(quotly_peer, msgs_to_fwd)
            threshold_id = last_sent[-1].id if isinstance(last_sent, list) else last_sent.id

            sticker_msg = None
            for _ in range(35):
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
        uname = me.username or f"user_{user_id}"
        pack_shortname = f"keshav_{user_id}_pack"
        pack_title = f"K E S H A V Pack (@{uname})"

        formatted_path = f"kang_{event.id}.png"
        downloaded_file = None

        try:
            downloaded_file = await client.download_media(reply, file=f"temp_kang_{event.id}")
            if not downloaded_file or not os.path.exists(downloaded_file):
                await status.edit("```text\n[!] Media download failed.\n```")
                return

            resize_for_sticker(downloaded_file, formatted_path)

            async with client.conversation("@Stickers", timeout=30) as conv:
                # Reset previous unfinished dialog
                await conv.send_message("/cancel")
                await conv.get_response()

                # Step 1: Try adding to existing pack
                await conv.send_message("/addsticker")
                resp1 = await conv.get_response()

                # If Stickers bot asks to choose a pack
                if "Choose a sticker set" in resp1.text or "Choose a sticker pack" in resp1.text or "pack" in resp1.text.lower():
                    await conv.send_message(pack_shortname)
                    resp2 = await conv.get_response()
                else:
                    resp2 = resp1

                # If pack does not exist yet -> create newpack
                if "Invalid pack" in resp2.text or "not found" in resp2.text.lower() or "don't have" in resp2.text.lower():
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

                # Pack exists, just upload the sticker
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
