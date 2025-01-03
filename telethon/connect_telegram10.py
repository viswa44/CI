from telethon import TelegramClient, events
import os
import asyncio
from asyncio import Queue
import sys
import time

# Add your custom module to the path if required
sys.path.append(r'C:\Users\Admin\Desktop\reciever-rabbitmq')
from text_extraction.text_extraction1 import extract_text_from_image

# User's Telegram API credentials
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

# Dictionary to manage approvals with timestamps
approval_dict = {}

# Flag to indicate if the user extracted text
user_extracted_text = False

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
    """Processes images from the queue and sends them to the reviewer if needed."""
    while True:
        event = await image_queue.get()  # Get the next image event from the queue

        try:
            # Download the image
            file_path = await event.download_media(file=output_folder)
            print(f"Image downloaded to: {file_path}")

            # Extract text from the image
            extracted_text = extract_text_from_image(file_path)
            print(f"Extracted text: {extracted_text}")

            if user_extracted_text:
                # Directly send the extracted text to the bot without review
                await user_client.send_message(
                    event.chat_id,
                    extracted_text
                )
                print(f"User-extracted text sent without review: {extracted_text}")
            else:
                # Send for review if the user didn't extract the text
                review_message = await user_client.send_message(
                    REVIEW_CHAT_ID,
                    f"Review this extracted text. Edit if necessary and reply with the corrected text:\n\n{extracted_text}",
                    file=file_path
                )
                print(f"Sent extracted text for review: {review_message.id}")

                # Store the review message in the approval dictionary with a timestamp
                approval_dict[review_message.id] = {
                    "event": event,
                    "extracted_text": extracted_text,
                    "timestamp": time.time()
                }

        except Exception as e:
            print(f"Error processing image: {e}")

        finally:
            image_queue.task_done()  # Mark the queue task as done


async def monitor_inactivity():
    """Automatically approve messages if the reviewer doesn't respond in 30 minutes."""
    while True:
        current_time = time.time()
        to_approve = []

        for message_id, data in approval_dict.items():
            if current_time - data["timestamp"] > 150:  # 30 minutes in seconds
                to_approve.append(message_id)

        for message_id in to_approve:
            original_event = approval_dict[message_id]["event"]
            extracted_text = approval_dict[message_id]["extracted_text"]

            # Automatically approve
            await user_client.send_message(
                original_event.chat_id,
                extracted_text
            )
            print(f"Automatically approved after 30 minutes: {extracted_text}")
            del approval_dict[message_id]

        await asyncio.sleep(60)  # Check every minute


@user_client.on(events.NewMessage(chats=REVIEW_CHAT_ID))
async def review_handler(event):
    """Handles approval, rejection, or editing of extracted text."""
    if not event.is_reply:
        print("Approval, rejection, or editing must be a reply to the review message.")
        return

    original_message_id = event.reply_to_msg_id

    if original_message_id not in approval_dict:
        print("No matching approval request found.")
        return

    # Get the original event and extracted text
    original_event = approval_dict[original_message_id]["event"]
    extracted_text = approval_dict[original_message_id]["extracted_text"]

    # Check if the reviewer is sending approval or rejection
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
        # Treat the reply as an edited/corrected text
        corrected_text = event.raw_text.strip()
        if corrected_text:
            print(f"Edited text received: {corrected_text}")

            # Send the corrected text back to the bot
            await user_client.send_message(
                original_event.chat_id,
                corrected_text
            )
            print(f"Sent edited text: {corrected_text}")

            # Update the extracted text in the approval dictionary
            approval_dict[original_message_id]["extracted_text"] = corrected_text

            # Remove from the approval dictionary after handling
            del approval_dict[original_message_id]
        else:
            print("No corrected text provided.")


# Main function to run the Telegram client
async def main():
    try:
        # Start processing images and monitoring inactivity
        await asyncio.gather(
            process_images(),
            monitor_inactivity()
        )
    except Exception as e:
        print(f"Error in the main function: {e}")


if __name__ == "__main__":
    # Start the Telegram client
    with user_client:
        user_client.loop.run_until_complete(main())
