import discord
from discord.ext import commands
import datetime
import pytz

# Set up bot intents
intents = discord.Intents.default()
intents.members = True  # Needed to detect new members
intents.messages = True  # Needed for commands
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Default log channel and contact person (can be updated)
log_channel_id = 1330217746885120000  # Replace with your log channel ID
contact_person = "abanded"  # Default contact person

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    for guild in bot.guilds:
        owner = guild.owner
        if owner:
            try:
                await owner.send(
                    f"👋 Hello! Thanks for adding {bot.user.name} to {guild.name}!\n\n"
                    f"To set the log channel, use: `!setlog <channel_id>`\n"
                    f"To set the contact person, use: `!setcontact <name>`"
                )
            except discord.Forbidden:
                print(f"❌ Couldn't message {owner} (DMs closed).")

@bot.event
async def on_member_join(member):
    """Detects new accounts and bans them if under 24 hours old."""
    global log_channel_id, contact_person

    now = datetime.datetime.now(pytz.utc)  # Get current time in UTC
    account_age = now - member.created_at.replace(tzinfo=pytz.utc)  # Ensure timezones match

    # If account is created within the last 24 hours, ban the user
    if account_age.days < 1:
        try:
            # Send DM before banning
            await member.send(
                f"⚠️ You have been **banned** from the server because your account is very new.\n"
                f"If you believe this was a mistake, please contact **{contact_person}** on Discord."
            )
        except discord.Forbidden:
            print(f"❌ Couldn't message {member} (DMs closed).")

        # Ban the user
        await member.guild.ban(member, reason="Auto-ban: Account too new")

        # Log the ban in the specified channel
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(
                f"🚨 **Auto-Banned User** 🚨\n"
                f"User: {member.mention} ({member.name}#{member.discriminator})\n"
                f"Account Created: <t:{int(member.created_at.timestamp())}:R>\n"
                f"Reason: Account too new (less than 24 hours old)."
            )

@bot.command()
async def setlog(ctx, channel_id: int):
    """Command to update the log channel."""
    global log_channel_id
    log_channel_id = channel_id
    await ctx.send(f"✅ Log channel updated! Logs will now be sent to <#{log_channel_id}>.")

@bot.command()
async def setcontact(ctx, *, name: str):
    """Command to update the contact person."""
    global contact_person
    contact_person = name
    await ctx.send(f"✅ Contact person updated! Users should now contact **{contact_person}** if banned.")

# Run bot
bot.run("Secret :3")
