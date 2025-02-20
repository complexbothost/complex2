import discord
import json
import base64
import os

# Define the bot client
intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

# Function to encode user ID in base64
def encode_user_id(user_id):
    return base64.b64encode(user_id.encode()).decode()

# Function to gather data from the server
async def gather_data(guild):
    data = {
        "members": [],
        "channels": [],
        "invite_links": [],
        "roles": [],
        "emojis": [],
        "stickers": [],
        "action_logs": [],
        "messages": []
    }

    # Gather members
    for member in guild.members:
        data["members"].append({
            "user_id": encode_user_id(str(member.id)),
            "name": member.name
        })

    # Gather channels
    for channel in guild.channels:
        data["channels"].append({
            "channel_id": str(channel.id),
            "name": channel.name
        })

    # Gather roles
    for role in guild.roles:
        data["roles"].append({
            "role_id": str(role.id),
            "name": role.name
        })

    # Gather emojis
    for emoji in guild.emojis:
        data["emojis"].append({
            "emoji_id": str(emoji.id),
            "name": emoji.name
        })

    # Gather stickers (if applicable)
    if hasattr(guild, 'stickers'):
        for sticker in guild.stickers:
            data["stickers"].append({
                "sticker_id": str(sticker.id),
                "name": sticker.name
            })

    # Gather messages and action logs
    for channel in guild.text_channels:
        try:
            async for message in channel.history(limit=100):
                data["messages"].append({
                    "message_id": str(message.id),
                    "content": message.content,
                    "channel_id": str(channel.id)
                })
        except Exception as e:
            print(f"Error fetching messages from {channel.name}: {e}")

    return data

# Function to save data to a JSON file
def save_to_file(data):
    try:
        with open('discord_data.txt', 'w') as f:
            json.dump(data, f, indent=4)
        print("Data saved to discord_data.txt")
    except Exception as e:
        print(f"Error saving data to file: {e}")

# Event when the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    for guild in client.guilds:
        data = await gather_data(guild)
        save_to_file(data)

        # Find the first channel the bot can send messages to
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                try:
                    with open('discord_data.txt', 'r') as f:
                        await channel.send(file=discord.File(f, 'discord_data.txt'))
                    print(f"Data sent to {channel.name}")
                    break
                except Exception as e:
                    print(f"Error sending message to {channel.name}: {e}")
                break

# Run the bot with your token
TOKEN = input('input bot token: ')
client.run(TOKEN)
