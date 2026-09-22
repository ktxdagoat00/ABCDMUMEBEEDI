import base64
from telethon import events

SECRET_VAULT = {}

def setup(client):

    # Command 1: .secret <password> | <secret message>
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.secret\s+([^|]+)\|(.+)'))
    async def secret_drop(event):
        password = event.pattern_match.group(1).strip()
        secret_msg = event.pattern_match.group(2).strip()

        # Obfuscate payload
        b64_cipher = base64.b64encode(secret_msg.encode()).decode()
        SECRET_VAULT[event.id] = {"pwd": password, "msg": secret_msg}

        card = (
            "```text\n"
            "╔════「 🔒 𝗞 𝗘 𝗦 𝗛 𝗔 𝗩  𝗖 𝗜 𝗣 𝗛 𝗘 𝗥 」════╗\n"
            "║\n"
            "╠─ 🛡️ STATUS :: ENCRYPTED DROP\n"
            f"╠─ 📦 CIPHER :: {b64_cipher[:16]}...==\n"
            "║\n"
            "╠─ 🔑 UNLOCK :: Reply .unlock <password>\n"
            "╚══════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(card)

    # Command 2: .unlock <password> (Reply to secret drop)
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.unlock(?:\s+(.+))?'))
    async def secret_unlock(event):
        reply = await event.get_reply_message()
        if not reply or reply.id not in SECRET_VAULT:
            await event.edit("```text\n[!] Reply to an active .secret encrypted drop!\n```")
            return

        pass_input = (event.pattern_match.group(1) or "").strip()
        vault_entry = SECRET_VAULT[reply.id]

        if pass_input != vault_entry["pwd"]:
            await event.edit("```text\n[!] ACCESS DENIED: Incorrect password.\n```")
            return

        revealed_card = (
            "```text\n"
            "╔════「 🔓 𝗖 𝗜 𝗣 𝗛 𝗘 𝗥  𝗨 𝗡 𝗟 𝗢 𝗖 𝗞 𝗘 𝗗 」════╗\n"
            "║\n"
            f"╠─ 📩 MESSAGE :: {vault_entry['msg']}\n"
            "║\n"
            "╚══════════════════════════════════════╝\n"
            "```"
        )
        await event.edit(revealed_card)
