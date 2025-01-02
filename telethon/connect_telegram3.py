from telethon import TelegramClient, events
import os
import asyncio
from asyncio import Queue

# Replace with your API ID and API Hash
API_ID = '29704689'
API_HASH = '1366eac3f7bf9e72446c5215dcb4a5d3'
output_folder = 'downloaded_pictures'
chat_username_or_id = '+919989161534'  # Replace with the correct username or ID
PHONE_NUMBER = '+447746285387'

os.makedirs(output_folder, exist_ok=True)

# Create the Telegram client
client = TelegramClient('default_response_bot', API_ID, API_HASH)

# Create an asyncio queue to handle images sequentially
image_queue = Queue()

@client.on(events.NewMessage(chats=chat_username_or_id))
async def new_message_handler(event):
    """Handles new incoming messages by adding them to the queue."""
    if event.photo:  # Check if the new message contains a photo
        await image_queue.put(event)  # Add the event to the queue
        print(f"Image added to queue. Queue size: {image_queue.qsize()}")

async def process_images():
    """Processes images from the queue sequentially."""
    while True:
        event = await image_queue.get()  # Get the next event from the queue
        file_path = await event.download_media(file=output_folder)  # Download the photo
        print(f"Image downloaded: {file_path}")
        print("Waiting for 20 seconds before processing the next image...")
        await asyncio.sleep(20)  # Wait before processing the next image
        image_queue.task_done()  # Mark the task as done

async def main():
    """Main function to start listening for new messages and processing the queue."""
    print("Listening for new messages...")
    # Start the image processing task
    asyncio.create_task(process_images())
    await client.run_until_disconnected()  # Keep the client running to listen for incoming messages

with client:
    client.loop.run_until_complete(main())

# from telethon import TelegramClient, events
# import os
# import asyncio

# # Replace with your API ID and API Hash
# API_ID = '29704689'
# API_HASH = '1366eac3f7bf9e72446c5215dcb4a5d3'
# output_folder = 'downloaded_pictures'
# chat_username_or_id = '+919989161534'  # Replace with the correct username or ID
# PHONE_NUMBER = '+447746285387'

# os.makedirs(output_folder, exist_ok=True)

# # Create the Telegram client
# client = TelegramClient('default_response_bot', API_ID, API_HASH)

# @client.on(events.NewMessage(chats=chat_username_or_id))
# async def new_message_handler(event):
#     """Handles new incoming messages and downloads photos."""
#     if event.photo:  # Check if the new message contains a photo
#         file_path = await event.download_media(file=output_folder)  # Download the photo
#         print(f"New image downloaded from incoming message: {file_path}")
#         print("Waiting for 20 seconds before processing the next message...")
#         await asyncio.sleep(20)  # Wait for 20 seconds before handling the next photo

# async def main():
#     """Main function to start listening for new messages."""
#     print("Listening for new messages...")
#     await client.run_until_disconnected()  # Keep the client running to listen for incoming messages

# with client:
#     client.loop.run_until_complete(main())
