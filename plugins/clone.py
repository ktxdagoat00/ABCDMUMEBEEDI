import os
import json
import asyncio
from telethon import events
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from telethon.tl.functions.users import GetFullUserRequest

# Safe dynamic imports
try:
    from telethon.tl.functions.account import UpdateBirthdayRequest
    from telethon.tl.types import Birthday
    HAS_BIRTHDAY = True
except Exception:
    HAS_BIRTHDAY = False

try:
    from telethon.tl.functions.account import UpdateEmojiStatusRequest
    from telethon.tl.types import EmojiStatus, EmojiStatusEmpty
    HAS_EMOJI_STATUS = True
except Exception:
    HAS_EMOJI_STATUS = False

BACKUP_FILE = "state/original_identity.json"
SAVED_PFP = "state/original_pfp.jpg"

HOMOGLYPHS = [
    ('l', 'I'),
    ('I', 'l'),
    ('o', '0'),
    ('O', '0'),
    ('0', 'O'),
    ('0', 'o'),
    ('s', '5'),
    ('S', '5'),
    ('z', '2'),
    ('Z', '2')
]

def generate_stealth_usernames(target):
    variations = []

    # 1. Homoglyphs with case preservation
    for i, ch in enumerate(target):
        for orig, sub in HOMOGLYPHS:
            if ch == orig:
                cand = target[:i] + sub + target[i+1:]
                if cand != target and len(cand) >= 5:
                    variations.append(cand)

    # 2. Minimum modifications (_1, _0 fallback)
    if len(target) <= 30:
        variations.append(f"{target}_1")
        variations.append(f"{target}_0")
        variations.append(f"{target}1")
        variations.append(f"{target}_")

    return list(dict.fromkeys(variations))

async def save_original_identity(client):
    me = await client.get_me()
    full_me = await client(GetFullUserRequest(me.id))
    
    pfp_exists = False
    if me.photo:
        await client.download_profile_photo("me", file=SAVED_PFP)
        pfp_exists = True

    status_doc_id = None
    if getattr(me, 'emoji_status', None):
        if hasattr(me.emoji_status, 'document_id'):
            status_doc_id = me.emoji_status.document_id

    b_day, b_month, b_year = None, None, None
    if getattr(full_me.full_user, 'birthday', None):
        b = full_me.full_user.birthday
        b_day = getattr(b, 'day', None)
        b_month = getattr(b, 'month', None)
        b_year = getattr(b, 'year', None)

    # Completely dynamic: takes whatever username the logged-in user actually has
    current_uname = me.username if me.username else ""

    data = {
        "first_name": me.first_name or "",
        "last_name": me.last_name or "",
        "about": full_me.full_user.about or "",
        "username": current_uname,
        "status_doc_id": status_doc_id,
        "b_day": b_day,
        "b_month": b_month,
        "b_year": b_year,
        "had_pfp": pfp_exists,
        "had_username": bool(me.username)
    }

    os.makedirs("state", exist_ok=True)
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

    # --- .clone <user/reply> ---
    @client.on(events.NewMessage(outgoing=True, pattern=r'^\.clone(?:\s+(.*))?'))
    async def clone_identity(event):
        target_id = await resolve_target(client, event)
        if not target_id:
            await event.edit("```text\n[!] Reply to a user or provide username/ID\n```")
            return

        msg = await event.edit("```text\n┌───「 🧬 𝗜𝗡𝗜𝗧𝗜𝗔𝗧𝗜𝗡𝗚 𝗖𝗟𝗢𝗡𝗜𝗡𝗚 」\n└───「 🛰️ 𝗙𝗥𝗘𝗘𝗭𝗜𝗡𝗚 𝗢𝗥𝗜𝗚𝗜𝗡𝗔𝗟 𝗜𝗗 」\n```")

        try:
            me = await client.get_me()
            # Backup only if not already cloned
            if not os.path.exists(BACKUP_FILE):
                await save_original_identity(client)

            target_user = await client.get_entity(target_id)
            target_full = await client(GetFullUserRequest(target_id))

            t_first = target_user.first_name or ""
            t_last = target_user.last_name or ""
            t_about = target_full.full_user.about or ""
            t_username = target_user.username or ""

            await msg.edit("```text\n┌───「 🧬 𝗦𝗬𝗡𝗖𝗜𝗡𝗚 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 」\n└───「 👤 𝗡𝗔𝗠𝗘 + 𝗕𝗜𝗢 + 𝗕𝗜𝗥𝗧𝗛𝗗𝗔𝗬 + 𝗦𝗧𝗔𝗧𝗨𝗦 + 𝗣𝗙𝗣 」\n```")

            # 1. Update Name & Bio
            await client(UpdateProfileRequest(
                first_name=t_first,
                last_name=t_last,
                about=t_about
            ))

            # 2. Sync Birthday
            bday_status = "None"
            if HAS_BIRTHDAY and getattr(target_full.full_user, 'birthday', None):
                tb = target_full.full_user.birthday
                try:
                    await client(UpdateBirthdayRequest(
                        birthday=Birthday(
                            day=tb.day,
                            month=tb.month,
                            year=getattr(tb, 'year', None)
                        )
                    ))
                    bday_status = f"{tb.day}/{tb.month}" + (f"/{tb.year}" if getattr(tb, 'year', None) else "")
                except Exception:
                    bday_status = "Privacy Blocked"

            # 3. Sync Music / Emoji Status
            music_status_applied = "None"
            if HAS_EMOJI_STATUS and getattr(target_user, 'emoji_status', None):
                if hasattr(target_user.emoji_status, 'document_id'):
                    doc_id = target_user.emoji_status.document_id
                    if getattr(me, 'premium', False):
                        try:
                            await client(UpdateEmojiStatusRequest(
                                emoji_status=EmojiStatus(document_id=doc_id)
                            ))
                            music_status_applied = "Copied 🎵"
                        except Exception:
                            music_status_applied = "Failed"
                    else:
                        music_status_applied = "Skipped (Premium Required)"

            # 4. Download and upload high-res PFP
            temp_pfp = "state/temp_clone_pfp.jpg"
            if target_user.photo:
                await client.download_profile_photo(target_user, file=temp_pfp)
                uploaded_photo = await client.upload_file(temp_pfp)
                await client(UploadProfilePhotoRequest(file=uploaded_photo))
                if os.path.exists(temp_pfp):
                    os.remove(temp_pfp)

            # 5. Case-preserving Username Cloak
            spoofed_username = "Unchanged"
            if t_username:
                await msg.edit("```text\n┌───「 🧬 𝗖𝗟𝗢𝗔𝗞𝗜𝗡𝗚 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 」\n└───「 🛰️ 𝗛𝗢𝗠𝗢𝗚𝗟𝗬𝗣𝗛 + 𝗙𝗔𝗟𝗟𝗕𝗔𝗖𝗞 」\n```")
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
                f"╠─ 👤 𝗡𝗔𝗠𝗘      :: {t_first} {t_last}\n"
                f"╠─ 📝 𝗔𝗕𝗢𝗨𝗧     :: {t_about[:35]}...\n"
                f"╠─ 🎂 𝗕𝗜𝗥𝗧𝗛𝗗𝗔𝗬  :: {bday_status}\n"
                f"╠─ 🎯 𝗧𝗔𝗥𝗚𝗘𝗧    :: @{t_username if t_username else 'None'}\n"
                f"╠─ 🎭 𝗦𝗣𝗢𝗢𝗙 𝗨𝗦𝗘𝗥 :: {spoofed_username}\n"
                f"╠─ 🎵 𝗠𝗨𝗦𝗜𝗖/𝗦𝗧𝗔𝗧 :: {music_status_applied}\n"
                f"╠─ 🖼️ 𝗣𝗙𝗣 𝗦𝗬𝗡𝗖   :: Complete\n"
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

            # 2. Restore Original Dynamic Username
            had_username = backup.get("had_username", False)
            orig_username = backup.get("username", "")

            try:
                if had_username and orig_username:
                    await client(UpdateUsernameRequest(orig_username))
                else:
                    await client(UpdateUsernameRequest(""))
            except Exception as ue:
                print(f"Username restore log: {ue}")

            # 3. Restore Birthday
            if HAS_BIRTHDAY:
                try:
                    b_day = backup.get("b_day")
                    b_month = backup.get("b_month")
                    b_year = backup.get("b_year")
                    if b_day and b_month:
                        await client(UpdateBirthdayRequest(
                            birthday=Birthday(day=b_day, month=b_month, year=b_year)
                        ))
                    else:
                        await client(UpdateBirthdayRequest(birthday=None))
                except Exception:
                    pass

            # 4. Restore Emoji / Music Status
            if HAS_EMOJI_STATUS:
                status_id = backup.get("status_doc_id")
                try:
                    if status_id:
                        await client(UpdateEmojiStatusRequest(emoji_status=EmojiStatus(document_id=status_id)))
                    else:
                        await client(UpdateEmojiStatusRequest(emoji_status=EmojiStatusEmpty()))
                except Exception:
                    pass

            # 5. Restore PFP
            if backup.get("had_pfp") and os.path.exists(SAVED_PFP):
                uploaded_photo = await client.upload_file(SAVED_PFP)
                await client(UploadProfilePhotoRequest(file=uploaded_photo))
                try:
                    os.remove(SAVED_PFP)
                except Exception:
                    pass

            if os.path.exists(BACKUP_FILE):
                os.remove(BACKUP_FILE)

            display_user = f"@{orig_username}" if (had_username and orig_username) else "None"
            card = (
                "```text\n"
                "╔════「 🕊️ 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 𝗥𝗘𝗦𝗧𝗢𝗥𝗘𝗗 ⚡ 」════╗\n"
                "║\n"
                f"╠─ 👤 𝗡𝗔𝗠𝗘     :: {backup.get('first_name')} {backup.get('last_name')}\n"
                f"╠─ 🏷️ 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 :: {display_user}\n"
                "├─ 🛡️ 𝗦𝗧𝗔𝗧𝗨𝗦   :: 100% Original Identity Restored\n"
                "║\n"
                "╚════════「 🔥 𝗨𝗦𝗘𝗥𝗕𝗢𝗧 𝗖𝗢𝗥𝗘 」════════╝\n"
                "```"
            )
            await msg.edit(card)

        except Exception as e:
            await msg.edit(f"```text\n[!] Revert Failed: {e}\n```")
