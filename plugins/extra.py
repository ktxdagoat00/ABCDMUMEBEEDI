import sys
import io
import traceback
import asyncio
from telethon import events

async def fetch_sangmata_history(client, user_id):
    bots = ["@SangMata_beta_bot", "@SangMataInfo_bot"]
    history_text = ""

    for bot in bots:
        try:
            async with client.conversation(bot, timeout=12) as conv:
                await conv.send_message(f"/search_id {user_id}")
                # Wait for reply message from bot
                response = await conv.get_response()
                if response and response.raw_text:
                    history_text = response.raw_text.strip()
                    # SangMata generic initial header filter
                    lines = [line for line in history_text.splitlines() if not line.startswith("Search result for")]
                    history_text = "\n".join(lines).strip()
                
                # Cleanup conversation trace in dialogs
                await client.delete_dialog(bot)
                if history_text:
                    return history_text
        except Exception:
            continue

    return "No recorded name history found or bot busy."

def setup(client):

    # --- .info COMMAND WITH ENHANCED SANGMATA HISTORY ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.info(?:\s+(.*))?'))
    async def user_info(event):
        arg = event.pattern_match.group(1)
        reply = await event.get_reply_message()
        target = None

        if reply:
            target = reply.sender_id
        elif arg:
            target = int(arg) if arg.isdigit() else arg
        else:
            target = "me"

        msg = await event.edit("```text\n┌───「 🔍 𝗙𝗘𝗧𝗖𝗛𝗜𝗡𝗚 𝗜𝗡𝗙𝗢... 」\n└───「 🛰️ 𝗤𝗨𝗘𝗥𝗬𝗜𝗡𝗚 𝗦𝗔𝗡𝗚𝗠𝗔𝗧𝗔 𝗗𝗕 」\n```")

        try:
            user = await client.get_entity(target)
            first_name = user.first_name or "None"
            last_name = user.last_name or ""
            full_name = f"{first_name} {last_name}".strip()
            username = f"@{user.username}" if user.username else "None"
            user_id = user.id
            dc_id = user.photo.dc_id if user.photo else "Unknown"
            is_bot = "Yes" if user.bot else "No"
            is_verified = "Yes" if user.verified else "No"

            history = await fetch_sangmata_history(client, user_id)

            card = (
                "```text\n"
                "╔════「 🛰️ 𝗨𝗦𝗘𝗥 𝗜𝗡𝗧𝗘𝗟 𝗖𝗢𝗥𝗘 」════╗\n"
                "║\n"
                f"╠─ 👤 𝗡𝗔𝗠𝗘     :: {full_name}\n"
                f"╠─ 🆔 𝗨𝗦𝗘𝗥_𝗜𝗗  :: {user_id}\n"
                f"╠─ 🏷️ 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :: {username}\n"
                f"╠─ 🌐 𝗗𝗖_𝗜𝗗    :: {dc_id}\n"
                f"╠─ 🤖 𝗜𝗦_𝗕𝗢𝗧   :: {is_bot}\n"
                f"╠─ 🛡️ 𝗩𝗘𝗥𝗜𝗙𝗜𝗘𝗗 :: {is_verified}\n"
                "║\n"
                "╠════「 📜 𝗡𝗔𝗠𝗘/𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 𝗛𝗜𝗦𝗧𝗢𝗥𝗬 」\n"
                f"{history}\n"
                "║\n"
                "╚════════「 ⚡ 𝗞𝗘𝗦𝗛𝗔𝗩-𝗦𝗬𝗦 ⚡ 」════════╝\n"
                "```"
            )
            await msg.edit(card)
        except Exception as e:
            await msg.edit(f"```text\n[!] Info Query Failed: {e}\n```")

    # --- .type COMMAND ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.type(?:\s+(.*))?'))
    async def typewriter(event):
        text = event.pattern_match.group(1)
        if not text:
            await event.edit("```text\n[!] Usage: .type <message>\n```")
            return

        typing_symbol = "█"
        current_text = ""
        for char in text:
            current_text += char
            try:
                await event.edit(current_text + typing_symbol)
                await asyncio.sleep(0.08)
            except Exception:
                pass
        await event.edit(current_text)

    # --- .eval COMMAND ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.eval(?:\s+([\s\S]+))?'))
    async def evaluate_code(event):
        code = event.pattern_match.group(1)
        if not code:
            await event.edit("```text\n[!] Provide python code to evaluate.\n```")
            return

        await event.edit("```text\n[⚙️] Executing...\n```")
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()
        result = None

        try:
            try:
                result = eval(code)
            except SyntaxError:
                exec_code = f"async def __ex():\n" + "\n".join(f"    {line}" for line in code.splitlines())
                exec(exec_code)
                result = await locals()["__ex"]()

            sys.stdout = old_stdout
            stdout_val = redirected_output.getvalue()
            final_output = stdout_val if stdout_val else str(result)

            card = (
                "```text\n"
                "┌───「 🐍 𝗘𝗩𝗔𝗟 𝗘𝗫𝗘𝗖𝗨𝗧𝗜𝗢𝗡 」\n"
                "│\n"
                f"├─ 📥 𝗜𝗡𝗣𝗨𝗧  ::\n{code}\n"
                "│\n"
                f"└─ 📤 𝗢𝗨𝗧𝗣𝗨𝗧 ::\n{final_output}\n"
                "```"
            )
            await event.edit(card)
        except Exception:
            sys.stdout = old_stdout
            err = traceback.format_exc()
            await event.edit(f"```text\n[!] Eval Error:\n{err[:400]}\n```")
