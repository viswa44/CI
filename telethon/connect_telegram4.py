
########### without human feedback

from telethon import TelegramClient, events
import os
import asyncio
from asyncio import Queue
import random

import sys
sys.path.append(r'C:\Users\Admin\Desktop\reciever-rabbitmq')  # Add this line
from text_extraction.text_extraction1 import extract_text_from_image




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
        ###############
        extracted_text = extract_text_from_image(file_path)
        ###############
        wait_time = random.randint(5, 20)

        print(f"Image downloaded: {file_path}")
        print("Waiting for 20 seconds before processing the next image...")
        await asyncio.sleep(wait_time)  # Wait before processing the next image
        await client.send_message(event.chat_id, f"Extracted text: {extracted_text}")
        image_queue.task_done()  # Mark the task as done

async def main():
    """Main function to start listening for new messages and processing the queue."""
    print("Listening for new messages...")
    # Start the image processing task
    asyncio.create_task(process_images())
    await client.run_until_disconnected()  # Keep the client running to listen for incoming messages

with client:
    client.loop.run_until_complete(main())