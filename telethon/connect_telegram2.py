from telethon import TelegramClient, events
from telethon.tl.types import InputMessagesFilterPhotos
import os
import asyncio

# Replace with your API ID and API Hash
API_ID = '29704689'
API_HASH = '1366eac3f7bf9e72446c5215dcb4a5d3'
output_folder = 'downloaded_pictures'
chat_username_or_id = '+919989161534'  # Replace with the correct username or ID
PHONE_NUMBER = '+447746285387'

os.makedirs(output_folder, exist_ok=True)

# Create the Telegram client
client = TelegramClient('default_response_bot', API_ID, API_HASH)

# async def download_pictures():
#     print("Starting the download process...")
#     async for message in client.iter_messages(chat_username_or_id, limit=None, filter=InputMessagesFilterPhotos):
#         if message.photo:
#             file_path = await message.download_media(file=output_folder)
#             print(f"Image downloaded: {file_path}")
#             print("Waiting for 20 seconds before downloading the next image...")
#             await asyncio.sleep(20)  # Delay before processing the next image

@client.on(events.NewMessage(chats=chat_username_or_id))
async def new_message_handler(event):
    if event.photo:
        file_path = await event.download_media(file=output_folder)
        print(f"New image downloaded from incoming message: {file_path}")
        print("Waiting for 20 seconds before handling the next incoming image...")
        await asyncio.sleep(20)  # Delay after handling the incoming image

# Start the client
async def main():
    print("Initializing...")
    # await download_pictures()  # Process existing images
    await new_message_handler(events=events)
    print("Switching to listening for new messages...")
    # Listening for new messages will happen via the `new_message_handler`

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
