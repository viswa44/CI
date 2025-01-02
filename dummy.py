from pynput.keyboard import Listener

# Function that will be called when a key is pressed
def on_press(key):
    try:
        print(f"Key {key.char} pressed")
        if key.char == 'q':  # If 'q' is pressed, stop the listener
            print("Exiting...")
            return False
    except AttributeError:
        print(f"Special key {key} pressed")

# Start the listener to monitor keyboard events
with Listener(on_press=on_press) as listener:
    listener.join()








# # import os

# # # Test the unmute command
# # os.system(r'"C:\Users\Admin\nircmd-x64 (1)\nircmd.exe" setsysvolume 32768')

# # import speedtest

# # from speedtest import Speedtest
# # st = Speedtest()
# # print(f"Download: {st.download() / 1_000_000:.2f} Mbps")
# # print(f"Upload: {st.upload() / 1_000_000:.2f} Mbps")

# import psutil

# def fetch_system_temperature():
#     """
#     Fetch current system temperature.
#     """
#     try:
#         if hasattr(psutil, "sensors_temperatures"):
#             temperatures = psutil.sensors_temperatures()
#             if temperatures:
#                 for name, entries in temperatures.items():
#                     print(f"Sensor: {name}")
#                     for entry in entries:
#                         print(f"  {entry.label or 'Unknown'}: {entry.current}°C")
#             else:
#                 print("No temperature data available.")
#         else:
#             print("Temperature monitoring not supported on this system.")
#     except Exception as e:
#         print(f"Failed to fetch system temperature: {e}")

# fetch_system_temperature()
# from telethon.tl.types import InputMessagesFilterPhotos
# print(InputMessagesFilterPhotos)
# import sys
# sys.path.append(r'C:\Users\Admin\Desktop\reciever-rabbitmq\text_extraction')  # Add this line
# from text_extraction.text_extraction1 import extract_text_from_image

