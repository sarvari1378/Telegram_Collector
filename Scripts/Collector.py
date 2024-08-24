from telethon import TelegramClient
import os
import asyncio
import json
import re
import base64
from datetime import datetime
import pytz
import jdatetime

# Replace these with your own API ID and hash
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
session_file = 'Session/@ssarvari1378.session'

# Load target usernames and limits from JSON file
with open('Jsons/target_usernames.json', 'r') as f:
    target_channels = json.load(f)['channels']

def rename_link(link, message_time):
    if link.startswith('ss://') or link.startswith('vless://'):
        # Remove characters after last '#'
        if '#' in link:
            link = link.rsplit('#', 1)[0]
        link = f"{link}#{message_time}"
    elif link.startswith('vmess://'):
        # Base64 decode, modify, and encode back
        try:
            decoded = base64.urlsafe_b64decode(link[8:]).decode('utf-8')
            if '#' in decoded:
                decoded = decoded.rsplit('#', 1)[0]
            modified = f"{decoded}#{message_time}"
            link = f"vmess://{base64.urlsafe_b64encode(modified.encode('utf-8')).decode('utf-8')}"
        except Exception as e:
            print(f"Error decoding vmess link: {e}")
    return link

def extract_links(text, message_time):
    """Extract specific links from the text and apply renaming logic."""
    links = []
    for line in text.split('\n'):
        # Remove the 'Config(s): ```' prefix if it exists
        line = line.replace('Config(s): ```', '').strip('`')
        
        if 'vless://' in line or 'vmess://' in line or 'ss://' in line:
            if line:
                renamed_link = rename_link(line, message_time)
                links.append(renamed_link)
    return links

def convert_to_iran_time(utc_time):
    tehran_tz = pytz.timezone('Asia/Tehran')
    iran_time = utc_time.astimezone(tehran_tz)
    # Convert to Jalali date
    iran_time_jalali = jdatetime.datetime.fromgregorian(datetime=iran_time)
    return iran_time_jalali.strftime('%Y|%m|%d_%H:%M:%S')

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
                            message_time_iran = convert_to_iran_time(message.date)
                            links = extract_links(message.text, message_time_iran)
                            all_links.extend(links)
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
