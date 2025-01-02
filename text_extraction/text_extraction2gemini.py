import cv2
import pytesseract
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the Tesseract command path from .env
pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD')

# Validate if the path is loaded correctly
if not pytesseract.pytesseract.tesseract_cmd:
    raise ValueError("Tesseract path not found. Check your .env file.")

# Path to your image
image_path = r'C:\Users\Admin\Desktop\reciever-rabbitmq\text_extraction\captcha.png'



def extract_text(image_path):
    # Load and process the image
    img = cv2.imread(image_path)

    if img is None:
        print(f"Error: Could not load the image at {image_path}. Check the file path.")
    else:
        # Convert image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Extract text
        text = pytesseract.image_to_string(gray)
        print("Extracted Text:")
        #print(text)
    return text

v = extract_text(image_path=image_path)
print(v)