from telethon import TelegramClient, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
import os
import asyncio

# Replace these with your own API ID and hash
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']

# Replace 'your_username' with the username you want to get messages from
target_usernames = ['@vpnstorefast', '@FreakConfig']

# Use a session file to store the client's authorization
session_file = 'Session/@ssarvari1378.session'

def filter_links(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Process the lines
    filtered_lines = []
    for line in lines:
        if 'vless://' in line or 'vmess://' in line or 'ss://' in line:
            # Remove backticks at the beginning and end of the line
            line = line.strip('`')
            # Add the line to the list only if it is not empty
            if line:
                filtered_lines.append(line)

    # Limit the number of lines to 100
    filtered_lines = filtered_lines[:50]

    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write the processed lines back to the file
    with open(output_file, 'w') as f:
        for line in filtered_lines:
            f.write(line)

async def get_messages():
    # Create a Telegram client
    async with TelegramClient(session_file, api_id, api_hash) as client:
        for target_username in target_usernames:
            # Get the target channel's entity
            target_channel = await client.get_entity(target_username)

            # Get the last 100 messages from the target channel
            messages = await client.get_messages(target_channel, limit=100)

            # Create the directory if it doesn't exist
            os.makedirs("Subs", exist_ok=True)

            # Save the messages to a file
            with open(f"Subs/{target_username}.txt", "w", encoding="utf-8") as f:
                for message in messages:
                    f.write(f"{message.sender.username}: {message.text}\n")

            # Call the filter_links function for the current target_username
            filter_links(f"Subs/{target_username}.txt", f"Subs/{target_username}.txt")

            print(f"Messages from {target_username} saved to Subs/{target_username}.txt")

async def main():
    await get_messages()

if __name__ == "__main__":
    asyncio.run(main())
