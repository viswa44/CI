#human feedback
#pros - only allows human to approve
#cons - it does not allow -- how to deal with videos, other stuff
# - it does not know how if user is away


from telethon import TelegramClient, events
import os
import asyncio
from asyncio import Queue
import sys

# Add your custom module to the path if required
sys.path.append(r'C:\Users\Admin\Desktop\reciever-rabbitmq')
from text_extraction.text_extraction1 import extract_text_from_image

# User's Telegram API credentials # 6364539426
USER_API_ID = '29704689'
USER_API_HASH = '1366eac3f7bf9e72446c5215dcb4a5d3'

# Telegram chat IDs
BOT_CHAT_ID = '+447746285387'  # Bot chat ID for receiving images
REVIEW_CHAT_ID = '+919989161534'  # Reviewer chat ID
output_folder = 'downloaded_pictures'

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

# Queue for processing images
image_queue = Queue()

# Dictionary to manage approvals
approval_dict = {}

# Create the Telegram client for the user
user_client = TelegramClient('user_account', USER_API_ID, USER_API_HASH)


@user_client.on(events.NewMessage(chats=BOT_CHAT_ID))  # Listen for messages from the bot
async def image_handler(event):
    """Handles incoming images from the bot and adds them to the queue for review."""
    if event.photo:  # Check if the message contains a photo
        try:
            # Add the image event to the processing queue
            await image_queue.put(event)
            print("Image added to the processing queue.")
        except Exception as e:
            print(f"Error adding image to the queue: {e}")
    else:
        print("No photo detected in the message.")


async def process_images():
    """Processes images from the queue and sends them to the reviewer."""
    while True:
        event = await image_queue.get()  # Get the next image event from the queue

        try:
            # Download the image
            file_path = await event.download_media(file=output_folder)
            print(f"Image downloaded to: {file_path}")

            # Extract text from the image
            extracted_text = extract_text_from_image(file_path)
            print(f"Extracted text: {extracted_text}")

            # Send the extracted text to the reviewer for approval
            review_message = await user_client.send_message(
                REVIEW_CHAT_ID,
                f"Review this extracted text:\n\n{extracted_text}",
                file=file_path
            )
            print(f"Sent extracted text for review: {review_message.id}")

            # Store the review message in the approval dictionary
            approval_dict[review_message.id] = {
                "event": event,
                "extracted_text": extracted_text
            }

        except Exception as e:
            print(f"Error processing image: {e}")

        finally:
            image_queue.task_done()  # Mark the queue task as done


@user_client.on(events.NewMessage(chats=REVIEW_CHAT_ID))  # Listen for reviewer's response
async def review_handler(event):
    """Handles approval or rejection of the extracted text."""
    if not event.is_reply:
        print("Approval or rejection must be a reply to the review message.")
        return

    original_message_id = event.reply_to_msg_id

    if original_message_id not in approval_dict:
        print("No matching approval request found.")
        return

    # Get the original event and extracted text
    original_event = approval_dict[original_message_id]["event"]
    extracted_text = approval_dict[original_message_id]["extracted_text"]

    if event.raw_text.lower() == "approve":
        # Send the extracted text back to the bot
        await user_client.send_message(
            original_event.chat_id,
            extracted_text
        )
        print(f"Approved and sent text: {extracted_text}")

        # Remove from the approval dictionary
        del approval_dict[original_message_id]

    elif event.raw_text.lower() == "reject":
        print(f"Rejected text: {extracted_text}")

        # Remove from the approval dictionary
        del approval_dict[original_message_id]
    else:
        print("Command not recognized. Use 'approve' or 'reject'.")


async def main():
    """Run the user client."""
    print("User is running and listening for incoming images and review commands...")
    asyncio.create_task(process_images())  # Start the image processing task
    await user_client.run_until_disconnected()


# Start the user client
with user_client:
    user_client.loop.run_until_complete(main())
