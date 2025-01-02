from telethon import TelegramClient, events
import os
import asyncio
from asyncio import Queue
import sys
sys.path.append(r'C:\Users\Admin\Desktop\reciever-rabbitmq')
from text_extraction.text_extraction1 import extract_text_from_image

# API credentials for the main bot +916364539426
API_ID = '29704689'
API_HASH = '1366eac3f7bf9e72446c5215dcb4a5d3' 

# API credentials for +447746285387
SENDER_API_ID = '26344089'
SENDER_API_HASH = 'd4950e25fd03d72b461e44665342f98e'

output_folder = 'downloaded_pictures'
review_chat_id = '+919989161534'
captcha_bot_username = '+916364539426'

os.makedirs(output_folder, exist_ok=True)

# Create the Telegram clients
client = TelegramClient('captcha_bot', API_ID, API_HASH)
sender_client = TelegramClient('sender_client', SENDER_API_ID, SENDER_API_HASH)

image_queue = Queue()
approval_dict = {}

@client.on(events.NewMessage(chats=captcha_bot_username))
async def new_message_handler(event):
    if event.photo:
        await image_queue.put(event)
        print(f"Image added to queue. Queue size: {image_queue.qsize()}")

async def process_images():
    while True:
        event = await image_queue.get()
        file_path = await event.download_media(file=output_folder)
        extracted_text = extract_text_from_image(file_path)
        
        review_message = await client.send_message(
            review_chat_id,
            f"Review this extracted text:\n\n{extracted_text}",
            file=file_path
        )
        approval_dict[review_message.id] = {
            "event": event,
            "extracted_text": extracted_text
        }
        image_queue.task_done()

@client.on(events.NewMessage(chats=review_chat_id))
async def review_handler(event):
    if not event.reply_to:
        print("Approval command must be a reply to the bot's review message.")
        return

    if event.raw_text.lower() == "approve":
        original_message_id = event.reply_to.reply_to_msg_id
        if original_message_id in approval_dict:
            original_event = approval_dict[original_message_id]["event"]
            extracted_text = approval_dict[original_message_id]["extracted_text"]

            # Send the message using the sender_client
            async with sender_client:
                await sender_client.send_message(
                    original_event.chat_id,
                    extracted_text,
                    parse_mode=None
                )
            print(f"Approved and sent from +447746285387: {extracted_text}")

            del approval_dict[original_message_id]
        else:
            print("No matching approval request found.")

    elif event.raw_text.lower() == "reject":
        original_message_id = event.reply_to.msg_id
        if original_message_id in approval_dict:
            print(f"Rejected: {approval_dict[original_message_id]['extracted_text']}")
            del approval_dict[original_message_id]
    else:
        print("Command not recognized. Use 'approve' or 'reject'.")

async def main():
    print("Listening for new messages...")
    asyncio.create_task(process_images())
    await client.run_until_disconnected()

with client, sender_client:
    client.loop.run_until_complete(main())
