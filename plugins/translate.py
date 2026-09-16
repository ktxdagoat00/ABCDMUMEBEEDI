import urllib.parse
import urllib.request
import json
import asyncio
from telethon import events

def fetch_translation(text, target_lang='hi'):
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={urllib.parse.quote(text)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        # Concatenate all translated parts
        return "".join([part[0] for part in data[0] if part[0]])

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tr(?:\s+([\s\S]+))?'))
    async def translate_to_hindi(event):
        text_to_translate = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        if not text_to_translate and reply:
            text_to_translate = reply.raw_text

        if not text_to_translate:
            await event.edit("```text\n[!] Koi text likho ya message reply karke .tr bhejo!\n```")
            return

        msg = await event.edit("```text\n┌───「 🌐 𝗧𝗥𝗔𝗡𝗦𝗟𝗔𝗧𝗜𝗡𝗚... 」\n└───「 🛰️ 𝗛𝗜𝗡𝗗𝗜 𝗖𝗢𝗡𝗩𝗘𝗥𝗦𝗜𝗢𝗡 」\n```")

        try:
            translated = await asyncio.to_thread(fetch_translation, text_to_translate, 'hi')

            card = (
                "```text\n"
                "┌───「 🌐 𝗧𝗥𝗔𝗡𝗦𝗟𝗔𝗧𝗜𝗢𝗡 𝗖𝗢𝗥𝗘 ⚡ 」\n"
                "│\n"
                f"├─ 📥 𝗜𝗡𝗣𝗨𝗧  :: {text_to_translate[:45]}{'...' if len(text_to_translate) > 45 else ''}\n"
                "├─ 🗣️ 𝗧𝗔𝗥𝗚𝗘𝗧 :: Hindi (हिन्दी)\n"
                "│\n"
                "└───「 📝 𝗢𝗨𝗧𝗣𝗨𝗧 」\n"
                "```\n"
                f"👉 **{translated}**"
            )
            await msg.edit(card)
        except Exception as e:
            await msg.edit(f"```text\n[!] Translation Error: {e}\n```")
