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
review_chat_id = '+919989161534'  # Replace with the human review chat ID or username
captcha_bot_username = '+916364539426'

os.makedirs(output_folder, exist_ok=True)

# Create the Telegram client
client = TelegramClient('captcha_bot', API_ID, API_HASH)

# Create an asyncio queue to handle images sequentially
image_queue = Queue()
approval_dict = {}  # Store approvals using message ID as a key

@client.on(events.NewMessage(chats=captcha_bot_username))
async def new_message_handler(event):
    """Handles new incoming messages from mycaptchabot."""
    if event.photo:  # Check if the message contains a photo
        await image_queue.put(event)  # Add the event to the queue
        print(f"Image added to queue. Queue size: {image_queue.qsize()}")

async def process_images():
    """Processes images from the queue sequentially and waits for human approval."""
    while True:
        event = await image_queue.get()  # Get the next event from the queue
        file_path = await event.download_media(file=output_folder)  # Download the photo
        
        # Extract text from the image
        extracted_text = extract_text_from_image(file_path)
        
        # Send the image and extracted text to the review chat
        review_message = await client.send_message(
            review_chat_id,
            f"Review this extracted text:\n\n{extracted_text}",
            file=file_path
        )
        print(f"Sent for review: {file_path} with text: {extracted_text}")

        # Store the event and extracted text for later approval
        approval_dict[review_message.id] = {
            "event": event,
            "extracted_text": extracted_text
        }

        image_queue.task_done()  # Mark the task as done

@client.on(events.NewMessage(chats=review_chat_id))
async def review_handler(event):
    """Handles human approval from the review chat."""
    if not event.reply_to:
        print("Approval command must be a reply to the bot's review message.")
        return

    if event.raw_text.lower() == "approve":
        # Get the original message being replied to
        original_message_id = event.reply_to.reply_to_msg_id

        if original_message_id in approval_dict:
            # Retrieve the original event and extracted text
            original_event = approval_dict[original_message_id]["event"]
            extracted_text = approval_dict[original_message_id]["extracted_text"]

            # Send the approved text back to the original chat
            await client.send_message(original_event.chat_id, extracted_text, parse_mode=None)
            print(f"Approved and sent: {extracted_text}")

            # Clean up the approval dictionary
            del approval_dict[original_message_id]
        else:
            print("No matching approval request found.")
    

    elif event.reply_to and event.raw_text.lower() == "reject":
        # Handle rejection if necessary
        original_message_id = event.reply_to.msg_id
        if original_message_id in approval_dict:
            print(f"Rejected: {approval_dict[original_message_id]['extracted_text']}")
            del approval_dict[original_message_id]
            
    else:
        print("Command not recognized. Use 'approve'.")

async def main():
    """Main function to start listening for new messages and processing the queue."""
    print("Listening for new messages...")
    # Start the image processing task
    asyncio.create_task(process_images())
    await client.run_until_disconnected()  # Keep the client running to listen for incoming messages

with client:
    client.loop.run_until_complete(main())
