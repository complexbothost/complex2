import discord
import json
import base64
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define intents
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.guild_messages = True
intents.guild_voice_states = True

# Create bot instance
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    for guild in bot.guilds:
        logging.info(f'Connected to guild: {guild.name} (ID: {guild.id})')

@bot.event
async def on_message(message):
    # Prevent the bot from responding to its own messages
    if message.author == bot.user:
        return

    # Check if the message content is "setup"
    if message.content.lower() == "setup":
        await send_server_info(message.channel)

async def send_server_info(channel):
    # Gather server information
    server_info = {
        "audit_logs": await fetch_audit_logs(channel.guild),
        "roles": await fetch_roles(channel.guild),
        "members": await fetch_members(channel.guild),
        "channels": await fetch_channels(channel.guild)
    }

    # Create a .txt file with the server information
    file_path = "server_info.txt"
    with open(file_path, "w") as file:
        file.write(json.dumps(server_info, indent=4))

    # Send the .txt file to the channel
    await channel.send(file=discord.File(file_path))

    # Clean up the file after sending
    os.remove(file_path)

async def fetch_audit_logs(guild):
    try:
        audit_logs = await guild.audit_logs(limit=10).flatten()
        return [{"action": log.action, "user": str(log.user), "target": str(log.target)} for log in audit_logs]
    except Exception as e:
        logging.error(f'Error fetching audit logs: {e}')
        return []

async def fetch_roles(guild):
    try:
        return [{"name": role.name, "id": role.id} for role in guild.roles]
    except Exception as e:
        logging.error(f'Error fetching roles: {e}')
        return []

async def fetch_members(guild):
    try:
        return [{"name": member.name, "id": base64.b64encode(str(member.id).encode()).decode()} for member in guild.members]
    except Exception as e:
        logging.error(f'Error fetching members: {e}')
        return []

async def fetch_channels(guild):
    try:
        channels = [{"name": channel.name, "id": channel.id, "type": str(channel.type)} for channel in guild.channels]
        voice_channels = [{"name": vc.name, "id": vc.id} for vc in guild.voice_channels]
        return {"channels": channels, "voice_channels": voice_channels}
    except Exception as e:
        logging.error(f'Error fetching channels: {e}')
        return {}

# Run the bot with your token
TOKEN = 'MTM0MjIyNjgzMTE1OTMyODg3MA.Go7eN_.cNXN4SrAYRvLzUgzr7jfPrTYdGVmYWxntGMabU'
bot.run(TOKEN)
