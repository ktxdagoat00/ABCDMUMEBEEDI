import sys
import io
import traceback
import asyncio
from telethon import events

async def fetch_sangmata_history(client, user_id):
    bots = ["@SangMata_BOT", "@SangMata_beta_bot", "@SangmataInfo_bot"]
    
    for bot in bots:
        try:
            async with client.conversation(bot, timeout=10) as conv:
                # Sangmata accepts direct ID or /search_id
                sent_msg = await conv.send_message(f"/search_id {user_id}")
                
                collected_lines = []
                # Sangmata sends acknowledgment first, then history in 1-2 responses
                for _ in range(3):
                    try:
                        resp = await conv.get_response(timeout=4)
                        if resp and resp.text:
                            text = resp.text.strip()
                            # Ignore basic query placeholders
                            if "searching" in text.lower() or "please wait" in text.lower():
                                continue
                            collected_lines.append(text)
                    except asyncio.TimeoutError:
                        break
                
                # Traces saaf karo
                try:
                    await client.delete_dialog(bot)
                except Exception:
                    pass

                if collected_lines:
                    full_res = "\n".join(collected_lines).strip()
                    # Filter generic headers
                    lines = [l for l in full_res.splitlines() if not l.startswith("Search result for")]
                    cleaned = "\n".join(lines).strip()
                    if cleaned:
                        return cleaned
        except Exception:
            continue

    return "No past username/name records found in DB."

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
