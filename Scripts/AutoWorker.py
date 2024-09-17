# libraries
import asyncio
from telethon.sync import TelegramClient
import re
import requests
from collections import namedtuple
import os
import base64

# Telegram API credentials
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
Session = 'Session/@AliMostafai.session'
bot_username = "@Qv2raybot"

# Initialize the client
client = TelegramClient(Session, api_id, api_hash)

# Function to extract the HTTPS link from a message
def extract_https_link(message_text):
    # Use regex to find an HTTPS link
    https_link = re.search(r'https://[^\s]+', message_text)
    return https_link.group(0) if https_link else None

# Function to request content from the HTTPS link
def get_link_content(link):
    try:
        response = requests.get(link)
        return response.text
    except Exception as e:
        print(f"Failed to retrieve content from {link}. Error: {e}")
        return None

# Function to check if the content is Base64 encoded
def is_base64_encoded(content):
    # Base64 strings are typically only composed of certain characters
    base64_regex = r'^[A-Za-z0-9+/=]+\Z'
    if re.match(base64_regex, content):
        try:
            # Try decoding to check if it’s valid Base64
            base64.b64decode(content).decode('utf-8')
            return True
        except Exception:
            return False
    return False

# Function to decode the content if it's Base64 encoded
def decode_content_if_needed(content):
    if is_base64_encoded(content):
        try:
            # Decode the Base64 content
            decoded_content = base64.b64decode(content).decode('utf-8')
            print("Content was Base64 encoded, decoded successfully.")
            return decoded_content
        except Exception as e:
            print(f"Failed to decode Base64 content. Error: {e}")
            return content  # Return original content if decoding fails
    else:
        # Content is not encoded
        print("Content is not Base64 encoded.")
        return content

# Function to save content to a file
def save_content_to_file(content, filename='Subs/AutoWorker.txt'):
    with open(filename, 'wb') as file:
        file.write(content.encode('utf-8'))
    print(f"Saved content to {filename}.")

async def main():
    # Connect to the bot
    await client.start()
    bot_entity = await client.get_entity(bot_username)

    while True:
        # Check for the last message
        async for message in client.iter_messages(bot_entity, limit=1):
            if message.message:
                link = extract_https_link(message.message)
                if link:
                    content = get_link_content(link)
                    if content:
                        # Check if content is Base64 encoded and decode if necessary
                        decoded_content = decode_content_if_needed(content)
                        
                        # Check if the decoded content starts with the specific phrase
                        if decoded_content.startswith("trojan://pooya@Qv2raychannel:80?"):
                            print("The link is old.")
                            await client.send_message(bot_entity, 'Xray')
                            print("Sent 'Xray' to the bot.")
                        else:
                            # Save content (decoded or original) if it doesn't match the phrase
                            save_content_to_file(decoded_content)
                            return  # Exit after saving the content
                else:
                    # If no link is found, send "Xray" to the bot
                    await client.send_message(bot_entity, 'Xray')
                    print("No HTTPS link found. Sent 'Xray' to the bot.")
        
        # Wait for a few seconds before checking again to avoid flooding
        await asyncio.sleep(5)

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
