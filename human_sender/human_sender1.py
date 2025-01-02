from telethon import TelegramClient, events

API_ID = 'your_api_id'
API_HASH = 'your_api_hash'

client = TelegramClient('bot', API_ID, API_HASH)

@client.on(events.NewMessage)
async def handle_image(event):
    """Handle incoming images, extract text, and re-send it as a typed message."""
    if event.photo:  # Check if the message contains an image
        # Step 1: Download and extract text
        file_path = await event.download_media()
        extracted_text = extract_text_from_image(file_path)  # Your text extraction function

        # Step 2: Re-send the extracted text as a new message
        await client.send_message(event.chat_id, extracted_text)
        print("Extracted text sent as a new message, no metadata attached.")

def extract_text_from_image(file_path):
    """Mock function to simulate text extraction."""
    return "Extracted text from image"

client.start()
client.run_until_disconnected()
