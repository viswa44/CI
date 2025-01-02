# C:\Program Files\Tesseract-OCR
import cv2
import numpy as np
import pytesseract
from mss import mss

# Path to Tesseract-OCR (ensure it's installed on your system)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize screen capture using `mss`
screen_capture = mss()

def capture_screen():
    """Captures the entire screen in real-time."""
    monitor = screen_capture.monitors[1]  # Monitor 1 (Change index for multiple monitors)
    screen = screen_capture.grab(monitor)
    frame = np.array(screen)  # Convert to numpy array
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

def detect_captcha(image, template_path):
    """Detects CAPTCHA region using template matching."""
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(gray_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val > 0.8:  # Threshold for matching
        return True, max_loc
    return False, None

def extract_text(image, region):
    """Extracts text from a specific region."""
    x, y, w, h = region
    cropped = image[y:y+h, x:x+w]
    text = pytesseract.image_to_string(cropped, config='--psm 6')
    return text.strip()

def main(template_path, region_size=(200, 100)):
    """Main function to monitor screen and solve CAPTCHA."""
    while True:
        screen = capture_screen()  # Continuous capture of the screen
        detected, location = detect_captcha(screen, template_path)
        if detected:
            print("CAPTCHA detected!")
            x, y = location
            region = (x, y, region_size[0], region_size[1])
            captcha_text = extract_text(screen, region)
            print("CAPTCHA Solved:", captcha_text)
            # Optionally, input the text automatically
            # pyautogui.write(captcha_text)
            # pyautogui.press('enter')

        # Display the live screen for debugging (optional)
        #cv2.imshow("Live Screen", screen)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Path to a sample CAPTCHA template image
    captcha_template = r"C:\Users\Admin\Downloads\2356g.png"
    main(captcha_template)

