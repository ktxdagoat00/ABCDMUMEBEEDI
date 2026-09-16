import asyncio
from telethon import events
from deep_translator import GoogleTranslator

def setup(client):

    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.tr(?:\s+([\s\S]+))?'))
    async def translate_to_hindi(event):
        text_to_translate = event.pattern_match.group(1)
        reply = await event.get_reply_message()

        # Reply message se text lena agar direct text na diya ho
        if not text_to_translate and reply:
            text_to_translate = reply.raw_text

        if not text_to_translate:
            await event.edit("```text\n[!] Koi text likho ya message reply karke .tr bhejo!\n```")
            return

        msg = await event.edit("```text\n┌───「 🌐 𝗧𝗥𝗔𝗡𝗦𝗟𝗔𝗧𝗜𝗡𝗚... 」\n└───「 🛰️ 𝗛𝗜𝗡𝗗𝗜 𝗖𝗢𝗡𝗩𝗘𝗥𝗦𝗜𝗢𝗡 」\n```")

        try:
            # Run in thread so async event loop freeze na ho
            translated = await asyncio.to_thread(
                GoogleTranslator(source='auto', target='hi').translate,
                text_to_translate
            )

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
