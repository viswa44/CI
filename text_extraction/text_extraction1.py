import cv2
import pytesseract
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Tesseract executable path from environment variable
tesseract_path = os.getenv('TESSERACT_CMD')

# Ensure the Tesseract path is loaded properly
if not tesseract_path:
    raise ValueError("Tesseract path not found in the environment. Check your .env file.")

# Set Tesseract command path
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Debugging: Print the loaded Tesseract path
print(f"Tesseract Path Loaded: {tesseract_path}")

def extract_text_from_image(image_path):
    # Load the image
    img = cv2.imread(image_path)
    
    if img is None:
        # Return "no image found" if the image couldn't be loaded
        print(f"Error: Could not load the image at {image_path}. Check the file path.")
        return "no image found"
    
    # Convert image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Extract text
    try:
        text = pytesseract.image_to_string(gray)
    except Exception as e:
        print(f"Error during text extraction: {e}")
        return "need help"
    
    if not text.strip():  # Check if the text is empty or contains only whitespace
        # Return "need help" if no text could be extracted
        return "need help"
    
    print("Extracted Text:")
    print(text)
    return text

# Example usage
# image_path = r'C:\Users\Admin\Desktop\reciever-rabbitmq\text_extraction\captcha.png'
# extracted_text = extract_text_from_image(image_path)
# print("Final Result:", extracted_text)
