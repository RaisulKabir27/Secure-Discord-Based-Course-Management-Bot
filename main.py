# ---------- main.py ----------
import os, re
import pandas as pd
import discord
from discord.ext import commands
from dotenv import load_dotenv
import keep_alive  # tiny Flask server to keep Replit awake

# ================== CONFIG ==================
EXCEL_PATH = "reg-2-26.xlsx"  # your file (you uploaded one named like this)
SHEET_NAME = "Worksheet"  # your workbook's sheet name
SKIP_ROWS = 6  # header starts on row 7 -> skip first 6 rows
ROLE_PREFIX = "Section"  # change to "SEC" if you want SEC-01, etc.
LEADING_ZERO = True  # True -> Section 01, False -> Section 1
# ============================================

# ---------- secrets ----------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCORD_TOKEN in Secrets")


# ---------- helpers ----------
def norm_id(s: str) -> str:
    """Keep digits only; handles '221-35-1234', '221351234', '221351234.0', etc."""
    if s is None:
        return ""
    return re.sub(r"\D", "", str(s))


def make_section_role(v) -> str:
    """Build role name from the numeric Section column."""
    raw = str(v).strip()
    try:
        n = int(float(raw))
        return f"{ROLE_PREFIX} {n:02d}" if LEADING_ZERO else f"{ROLE_PREFIX} {n}"
    except:
        # If already a text like 'Section 01', return as-is or prefix if missing
        return raw if raw.lower().startswith(
            ROLE_PREFIX.lower()) else f"{ROLE_PREFIX} {raw}"


# ---------- load Excel & build map ----------
try:
    df = pd.read_excel(EXCEL_PATH,
                       sheet_name=SHEET_NAME,
                       skiprows=SKIP_ROWS,
                       engine="openpyxl")
except Exception as e:
    print(f"❌ Failed to load Excel file: {e}")
    raise SystemExit(1)

# normalize header names so we handle 'Student Id' vs 'Student ID'
df.columns = [str(c).strip() for c in df.columns]
lower_map = {c.lower(): c for c in df.columns}


def col(name_options):
    """Return the actual column name from a list of case/spacing variants."""
    for opt in name_options:
        if opt.lower() in lower_map:
            return lower_map[opt.lower()]
    raise RuntimeError(
        f"Required column not found. Looked for one of: {name_options}. Found: {df.columns}"
    )


COL_STUDENT = col(["Student Id", "Student ID", "StudentID", "ID"])
COL_SECTION = col(["Section"])

df = df.dropna(subset=[COL_STUDENT, COL_SECTION])

id_to_section = {}
for _, row in df.iterrows():
    sid = norm_id(row[COL_STUDENT])
    if not sid:
        continue
    id_to_section[sid] = make_section_role(row[COL_SECTION])

print(
    f"📘 Loaded {len(id_to_section)} students into map from sheet='{SHEET_NAME}' skiprows={SKIP_ROWS}"
)
print("📘 Sample entries:", list(id_to_section.items())[:5])

# ---------- discord client ----------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    app = await bot.application_info()
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Activity(
                                  type=discord.ActivityType.watching,
                                  name="student verifications"))
    print("=== RUNNING BOT IDENTIFIERS ===")
    print(f"bot.user: {bot.user}  id={bot.user.id}")
    print(f"application: {app.name}  app_id={app.id}")
    perms = 268504064  # Manage Roles + View/Send + Read History
    invite = f"https://discord.com/oauth2/authorize?client_id={app.id}&permissions={perms}&scope=bot%20applications.commands"
    print(f"Invite this exact bot with:\n{invite}")
    print("================================")


# ---------- quick test commands ----------
@bot.command()
@commands.is_owner()
async def test_map(ctx, *, typed_id: str):
    """Check how an ID string maps to a Section role label."""
    sid = norm_id(typed_id)
    section = id_to_section.get(sid)
    await ctx.send(f"ID '{sid}' → {section or 'NOT FOUND'}")


@bot.command()
@commands.is_owner()
async def test_role(ctx, *, section_label: str):
    """Check if a role exists by exact name (run inside the server)."""
    guild = ctx.guild
    if guild is None:
        await ctx.send("Run this inside the server to check roles.")
        return
    role = discord.utils.get(guild.roles, name=section_label)
    await ctx.send(
        f"Role '{section_label}' → {(role and role.id) or 'NOT FOUND'}")


# ---------- main command: scan a channel and assign roles ----------
@bot.command()
@commands.is_owner()
async def count_msgs(ctx, guild_id: int, channel_id: int, limit: int = 10000):
    """Count total messages in a channel (up to the given limit)."""
    guild = bot.get_guild(guild_id)
    channel = guild.get_channel(channel_id)
    if channel is None:
        await ctx.send("❌ Channel not found.")
        return

    count = 0
    async for _ in channel.history(limit=limit):
        count += 1
    await ctx.send(
        f"🧮 Counted **{count}** messages in #{channel.name} (limit={limit}).")


@bot.command()
@commands.is_owner()
async def diag_id(ctx,
                  guild_id: int,
                  channel_id: int,
                  student_id: str,
                  limit: int = 200):
    """Show who posted a given student ID and attempt assignment once."""
    from discord.utils import get
    guild = bot.get_guild(guild_id)
    if not guild:
        await ctx.send("Guild not found.")
        return
    channel = guild.get_channel(channel_id)
    if not channel:
        await ctx.send("Channel not found.")
        return

    target_sid = norm_id(student_id)
    hits = []
    async for m in channel.history(limit=limit):
        sid = norm_id(m.content)
        if sid == target_sid:
            hits.append(m)

    if not hits:
        await ctx.send(f"No messages with ID {target_sid} in the last {limit}."
                       )
        return

    # take the most recent hit
    m = hits[0]
    section = id_to_section.get(target_sid)
    await ctx.send(
        f"Found {m.author.display_name} posted ID {target_sid}. Excel maps to: {section or 'NOT FOUND'}"
    )

    if not section:
        return

    role = get(guild.roles, name=section)
    if not role:
        await ctx.send(f"Role '{section}' not found.")
        return
    if role >= guild.me.top_role:
        await ctx.send(f"My highest role must be above '{role.name}'.")
        return

    member = guild.get_member(m.author.id) or await guild.fetch_member(
        m.author.id)
    if role in member.roles:
        await ctx.send(f"{member.display_name} already has '{role.name}'.")
        return

    try:
        await member.add_roles(role, reason="diag_id assignment")
        await ctx.send(f"✅ Gave '{role.name}' to {member.display_name}.")
    except discord.Forbidden:
        await ctx.send("❌ Missing permission to add that role.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


@bot.command()
@commands.is_owner()
async def assign_roles(ctx, guild_id: int, channel_id: int, limit: int = 100):
    # Use in DM for safety
    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("⚠️ Use this command in a **DM** with the bot.")
        return

    guild = bot.get_guild(guild_id)
    if guild is None:
        await ctx.send("❌ Invalid guild ID or I’m not in that server.")
        return

    channel = guild.get_channel(channel_id)
    if channel is None:
        await ctx.send("❌ Invalid channel ID in that guild.")
        return

    me = guild.me
    if not me.guild_permissions.manage_roles:
        await ctx.send("❌ I need **Manage Roles** in that server.")
        return
    if not channel.permissions_for(me).read_message_history:
        await ctx.send("❌ I need **Read Message History** in that channel.")
        return

    await ctx.send(
        f"🔍 Scanning last {limit} messages in **#{channel.name}** on **{guild.name}**..."
    )

    count = 0
    i = 0
    async for message in channel.history(limit=limit):
        raw = message.content
        sid = norm_id(raw)
        section_role_name = id_to_section.get(sid)

        print(f"[{i}] Msg by {message.author}: raw={raw!r} → sid='{sid}'")
        i += 1

        if not sid:
            print(" - No digits in message; skip")
            continue
        if not section_role_name:
            print(f" - No section for sid='{sid}'")
            continue

        role = discord.utils.get(guild.roles, name=section_role_name)
        if role is None:
            print(f" - Role '{section_role_name}' not found")
            continue  # or auto-create it here if you prefer

        if role >= guild.me.top_role:
            await ctx.send(
                f"⚠️ Move my highest role **above** `{role.name}` so I can assign it."
            )
            continue

        member = guild.get_member(message.author.id)
        if member is None:
            print(f" - Member {message.author} not found in guild")
            continue

        if role in member.roles:
            print(f" - {member} already has {role.name}")
            continue

        try:
            await member.add_roles(
                role, reason="Student verification (channel scan)")
            print(f"✅ Assigned {role.name} to {member}")
            count += 1
        except discord.Forbidden:
            await ctx.send(
                f"❌ Missing permission to assign `{role.name}` to {member}.")
        except Exception as e:
            await ctx.send(f"❌ Error assigning role to {member}: {e}")

    await ctx.send(f"🏁 Done. Assigned roles to **{count}** users.")


# ---------- run ----------
keep_alive.keep_alive()
bot.run(TOKEN)
