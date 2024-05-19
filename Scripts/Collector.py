from telethon import TelegramClient
import os
import asyncio
import json

# Replace these with your own API ID and hash
api_id = '26963557'
api_hash = '70aed19a29d2321933d9c4f652534c0f'
session_file = 'Session/@ssarvari1378.session'

# Load target usernames and limits from JSON file
with open('Jsons/target_usernames.json', 'r') as f:
    target_channels = json.load(f)['channels']

def extract_links(text):
    """Extract specific links from the text."""
    links = []
    for line in text.split('\n'):
        if 'vless://' in line or 'vmess://' in line or 'ss://' in line:
            line = line.strip('`')
            if line:
                links.append(line)
    return links

async def get_messages():
    async with TelegramClient(session_file, api_id, api_hash) as client:
        for channel_data in target_channels:
            target_identifier = channel_data['identifier']
            limit = channel_data['limit']
            output_name = channel_data.get('name', target_identifier)
            all_links = []

            if target_identifier.isdigit() or (target_identifier.startswith('-') and target_identifier[1:].isdigit()):
                target_identifier = int(target_identifier)

            try:
                target_channel = await client.get_entity(target_identifier)
            except ValueError as e:
                print(f"ValueError: {e}. Skipping entity with identifier {target_identifier}.")
                continue
            except Exception as e:
                print(f"Error: {e}. Skipping entity with identifier {target_identifier}.")
                continue

            offset_id = 0
            while len(all_links) < limit:
                try:
                    messages = await client.get_messages(target_channel, limit=100, offset_id=offset_id)
                    if not messages:
                        break
                    for message in messages:
                        if message.text:
                            all_links.extend(extract_links(message.text))
                    offset_id = messages[-1].id
                except Exception as e:
                    print(f"Error while fetching messages: {e}")
                    break

            all_links = all_links[:limit]

            os.makedirs("Subs", exist_ok=True)
            with open(f"Subs/{output_name}.txt", "w", encoding="utf-8") as f:
                for link in all_links:
                    f.write(f"{link}\n")

            print(f"Links from {target_identifier} saved to Subs/{output_name}.txt")

async def main():
    await get_messages()

if __name__ == "__main__":
    asyncio.run(main())
