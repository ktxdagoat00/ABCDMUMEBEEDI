import os
import json
import asyncio
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoto

BACKUP_FILE = "state/original_identity.json"
SAVED_PFP = "state/original_pfp.jpg"

# Visual spoofing mapping for usernames
SPOOF_MAP = {
    'l': 'I',
    'I': 'l',
    'o': '0',
    '0': 'o',
    'O': '0',
    's': '5',
    '5': 's',
    'z': '2',
    '2': 'z'
}

def generate_stealth_usernames(target_user):
    target = target_user.lower()
    variations = []

    # 1. Single character homoglyph replacement (Minimum visible change)
    for i, ch in enumerate(target):
        if ch in SPOOF_MAP:
            cand = target[:i] + SPOOF_MAP[ch] + target[i+1:]
            if cand != target and len(cand) >= 5:
                variations.append(cand)

    # 2. Subtle trailing modifications
    if len(target) < 32:
        variations.append(f"{target}_")
        variations.append(f"_{target}")
        variations.append(f"{target}x")
        variations.append(f"{target}o")

    # 3. Double character trick
    if len(target) < 32:
        for i in range(len(target)):
            cand = target[:i] + target[i] + target[i:]
            variations.append(cand)

    return list(dict.fromkeys(variations))

async def save_original_identity(client):
    me = await client.get_me()
    full_me = await client(GetFullUserRequest(me.id))
    
    # Download original profile photo if exists
    pfp_exists = False
    if me.photo:
        await client.download_profile_photo("me", file=SAVED_PFP)
        pfp_exists = True

    data = {
        "first_name": me.first_name or "",
        "last_name": me.last_name or "",
        "about": full_me.full_user.about or "",
        "username": me.username or "",
        "had_pfp": pfp_exists
    }

    with open(BACKUP_FILE, "w") as f:
        json.dump(data, f, indent=4)

async def resolve_target(client, event):
    reply = await event.get_reply_message()
    if reply:
        return reply.sender_id
    
    parts = event.raw_text.split(maxsplit=1)
    if len(parts) > 1:
        target = parts[1].strip()
        if target.isdigit() or (target.startswith("-") and target[1:].isdigit()):
            return int(target)
        try:
            entity = await client.get_entity(target)
            return entity.id
        except Exception:
            return None
    return None

def setup(client):

    # --- .clone <target/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.clone(?:\s+(.*))?'))
    async def clone_identity(event):
        target_id = await resolve_target(client, event)
        if not target_id:
            await event.edit("```text\n[!] Reply to user or provide username/ID\n```")
            return

        msg = await event.edit("```text\n┌───「 🧬 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗜𝗡𝗚 𝗖𝗟𝗢𝗡𝗜𝗡𝗚 」\n└───「 🛰️ 𝗕𝗔𝗖𝗞𝗜𝗡𝗚 𝗨𝗣 𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟 𝗜𝗗 」\n```")

        try:
            # Step 1: Backup current identity if not already backed up
            if not os.path.exists(BACKUP_FILE):
                await save_original_identity(client)

            # Step 2: Extract Target Info
            target_user = await client.get_entity(target_id)
            target_full = await client(GetFullUserRequest(target_id))

            t_first = target_user.first_name or ""
            t_last = target_user.last_name or ""
            t_about = target_full.full_user.about or ""
            t_username = target_user.username or ""

            await msg.edit("```text\n┌───「 🧬 𝗦𝗬𝗡𝗖𝗜𝗡𝗚 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 𝗗𝗔𝗧𝗔 」\n└───「 👤 𝗡𝗔𝗠𝗘 + 𝗕𝗜𝗢 + 𝗣𝗙𝗣 」\n```")

            # Step 3: Update Name and Bio
            await client(UpdateProfileRequest(
                first_name=t_first,
                last_name=t_last,
                about=t_about
            ))

            # Step 4: Download and set Target PFP
            temp_pfp = "state/temp_clone_pfp.jpg"
            if target_user.photo:
                await client.download_profile_photo(target_user, file=temp_pfp)
                uploaded_photo = await client.upload_file(temp_pfp)
                await client(UploadProfilePhotoRequest(file=uploaded_photo))
                if os.path.exists(temp_pfp):
                    os.remove(temp_pfp)

            # Step 5: Stealth Lookalike Username Cloak
            spoofed_username = None
            if t_username:
                await msg.edit("```text\n┌───「 🧬 𝗖𝗟𝗢𝗔𝗞𝗜𝗡𝗚 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 」\n└───「 🛰️ 𝗛𝗢𝗠𝗢𝗚𝗟𝗬𝗣𝗛 𝗦𝗣𝗢𝗢𝗙𝗜𝗡𝗚 」\n```")
                candidates = generate_stealth_usernames(t_username)
                for cand in candidates:
                    try:
                        await client(UpdateUsernameRequest(cand))
                        spoofed_username = f"@{cand}"
                        break
                    except Exception:
                        continue

            card = (
                "```text\n"
                "╔════「 🧬 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 𝗖𝗟𝗢𝗡𝗘𝗗 ⚡ 」════╗\n"
                "║\n"
                f"╠─ 👤 𝗡𝗔𝗠𝗘     :: {t_first} {t_last}\n"
                f"╠─ 📝 𝗔𝗕𝗢𝗨𝗧    :: {t_about[:40]}...\n"
                f"╠─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧   :: @{t_username if t_username else 'None'}\n"
                f"╠─ 🎭 𝗦𝗣𝗢𝗢𝗙     :: {spoofed_username if spoofed_username else 'Unchanged'}\n"
                f"╠─ 🖼️ 𝗣𝗙𝗣 𝗦𝗬𝗡𝗖  :: Complete\n"
                "║\n"
                "╚════════「 ⚡ 𝗦𝗧𝗘𝗔𝗟𝗧𝗛 𝗔𝗖𝗧𝗜𝗩𝗘 ⚡ 」════════╝\n"
                "```"
            )
            await msg.edit(card)

        except Exception as e:
            await msg.edit(f"```text\n[!] Cloning Failed: {e}\n```")

    # --- .revert ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.revert$'))
    async def revert_identity(event):
        if not os.path.exists(BACKUP_FILE):
            await event.edit("```text\n[!] No original identity backup found.\n```")
            return

        msg = await event.edit("```text\n┌───「 🔄 𝗥𝗘𝗦𝗧𝗢𝗥𝗜𝗡𝗚 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 」\n└───「 🛰️ 𝗥𝗘𝗩𝗘𝗥𝗧𝗜𝗡𝗚 𝗔𝗟𝗟 𝗣𝗥𝗢𝗙𝗜𝗟𝗘 𝗗𝗔𝗧𝗔 」\n```")

        try:
            with open(BACKUP_FILE, "r") as f:
                backup = json.load(f)

            # 1. Restore Name & Bio
            await client(UpdateProfileRequest(
                first_name=backup.get("first_name", ""),
                last_name=backup.get("last_name", ""),
                about=backup.get("about", "")
            ))

            # 2. Restore Original PFP
            if backup.get("had_pfp") and os.path.exists(SAVED_PFP):
                uploaded_photo = await client.upload_file(SAVED_PFP)
                await client(UploadProfilePhotoRequest(file=uploaded_photo))
                try:
                    os.remove(SAVED_PFP)
                except Exception:
                    pass

            # 3. Restore Original Username
            orig_username = backup.get("username")
            if orig_username:
                try:
                    await client(UpdateUsernameRequest(orig_username))
                except Exception:
                    pass

            # Remove backup to reset state
            if os.path.exists(BACKUP_FILE):
                os.remove(BACKUP_FILE)

            card = (
                "```text\n"
                "╔════「 🕊️ 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 𝗥𝗘𝗦𝗧𝗢𝗥𝗘𝗗 ⚡ 」════╗\n"
                "║\n"
                f"╠─ 👤 𝗡𝗔𝗠𝗘     :: {backup.get('first_name')} {backup.get('last_name')}\n"
                f"╠─ 🏷️ 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :: @{orig_username}\n"
                "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦   :: Back to Original Master\n"
                "║\n"
                "╚════════「 🔥 𝗞𝗘𝗦𝗛𝗔𝗩-𝗨𝗦𝗘𝗥𝗕𝗢𝗧 」════════╝\n"
                "```"
            )
            await msg.edit(card)

        except Exception as e:
            await msg.edit(f"```text\n[!] Revert Failed: {e}\n```")
