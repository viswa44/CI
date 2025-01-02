import pika
import screen_brightness_control as sbc  # type: ignore
import os
import subprocess
import psutil
import speedtest 
from speedtest import Speedtest
# RabbitMQ Configuration
RABBITMQ_HOST = '192.168.1.5'
RABBITMQ_VHOST = '/'
RABBITMQ_USER = 'workertwo'
RABBITMQ_PASSWORD = '1298'
QUEUE_NAME = 'test_queue'

# Function Definitions
def reduce_brightness():
    """
    Reduce system brightness by 10%.
    """
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = max(current_brightness - 10, 0)
        sbc.set_brightness(new_brightness)
        print(f"Brightness reduced to {new_brightness}%")
    except Exception as e:
        print(f"Failed to reduce brightness: {e}")

def increase_brightness():
    """
    Increase system brightness by 10%.
    """
    try:
        current_brightness = sbc.get_brightness()[0]
        new_brightness = min(current_brightness + 10, 100)
        sbc.set_brightness(new_brightness)
        print(f"Brightness increased to {new_brightness}%")
    except Exception as e:
        print(f"Failed to increase brightness: {e}")

def shutdown_system():
    """
    Shutdown the system.
    """
    try:
        subprocess.run(["shutdown", "/s", "/t", "0"], check=True)
        print("System shutting down...")
    except Exception as e:
        print(f"Failed to shut down the system: {e}")

def mute_sound():
    """
    Mute the system sound.
    """
    try:
        os.system(r'"C:\Users\Admin\nircmd-x64 (1)\nircmd.exe" mutesysvolume 1')
        print("System sound muted.")
    except Exception as e:
        print(f"Failed to mute sound: {e}")

def unmute_sound():
    """
    Unmute the system sound.
    """
    try:
        # Set the system volume to maximum as a fallback for unmuting
        # os.system(r'"C:\Users\Admin\nircmd-x64 (1)\nircmd.exe" setsysvolume 65535')
        # Ensure mute is turned off
        os.system(r'"C:\Users\Admin\nircmd-x64 (1)\nircmd.exe" mutesysvolume 0')
        print("System in sound.")
    except Exception as e:
        print(f"Failed to unmute sound: {e}")

def open_application(app_name):
    """
    Open a specified application.
    """
    try:
        subprocess.Popen(app_name, shell=True)
        print(f"Application {app_name} opened.")
    except Exception as e:
        print(f"Failed to open application {app_name}: {e}")

def close_application(app_name):
    """
    Close a specified application by name.
    """
    try:
        os.system(f"taskkill /f /im {app_name}.exe")
        print(f"Application {app_name} closed.")
    except Exception as e:
        print(f"Failed to close application {app_name}: {e}")
def fetch_wifi_speed():
    """
    Fetch current Wi-Fi speed or return "No internet" if not connected.
    """
    try:
        st = Speedtest()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        print(f"Download speed: {download_speed:.2f} Mbps, Upload speed: {upload_speed:.2f} Mbps")
    except Exception as e:
        print(f"No internet or failed to fetch Wi-Fi speed: {e}")



def fetch_battery_level():
    """
    Fetch current battery level.
    """
    try:
        battery = psutil.sensors_battery()
        if battery:
            print(f"Battery level: {battery.percent}%, Charging: {battery.power_plugged}")
        else:
            print("Battery information not available.")
    except Exception as e:
        print(f"Failed to fetch battery level: {e}")
        
def fetch_system_temperature():
    """
    Fetch current system temperature.
    """
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temperatures = psutil.sensors_temperatures()
            if "coretemp" in temperatures:
                for entry in temperatures["coretemp"]:
                    print(f"{entry.label or 'CPU'}: {entry.current}°C")
            else:
                print("Temperature sensors not available.")
        else:
            print("Temperature monitoring not supported on this system.")
    except Exception as e:
        print(f"Failed to fetch system temperature: {e}")
        

def execute_command(command):
    """
    Execute the received command.
    """
    try:
        if command == "reduce brightness":
            reduce_brightness()
        elif command == "increase brightness":
            increase_brightness()
        elif command == "shutdown":
            shutdown_system()
        elif command == "mute" or command == "mute sound":
            mute_sound()
        elif command == "sound" or command == "unmute sound":
            unmute_sound()
        elif command.startswith("open application:"):
            app_name = command.split(":", 1)[1].strip()
            open_application(app_name)
        elif command.startswith("close application:"):
            app_name = command.split(":", 1)[1].strip()
            close_application(app_name)
        elif command == "wifi speed" or command == "wifi status" or command == "wifi":
            fetch_wifi_speed()
        elif command == "battery level" or command == "battery" or command == "system battery":
            fetch_battery_level()
        elif command == "fetch system temperature" or command == "system temperature":
            fetch_system_temperature()
        elif command == "fetch cpu usage":
            fetch_cpu_usage()
        else:
            print(f"Unknown command received: {command}")
        
    except Exception as e:
        print(f"Error executing command '{command}': {e}")

def on_message_received(ch, method, properties, body):
    """
    RabbitMQ callback function to handle received messages.
    """
    try:
        command = body.decode('utf-8')
        print(f"Received command: {command}")
        execute_command(command)
    except Exception as e:
        print(f"Failed to process message: {e}")

def fetch_cpu_usage():
    """
    Fetch current CPU usage percentage.
    """
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        print(f"Current CPU usage: {cpu_usage}%")
    except Exception as e:
        print(f"Failed to fetch CPU usage: {e}")
        
        
def start_receiver():
    """
    Start RabbitMQ receiver to listen for commands.
    """
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, virtual_host=RABBITMQ_VHOST, credentials=credentials)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME)
        print("Listening for commands...")

        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message_received, auto_ack=True)
        channel.start_consuming()
    except pika.exceptions.AMQPError as error:
        print(f"Failed to connect to RabbitMQ: {error}")
    except Exception as e:
        print(f"Error in RabbitMQ receiver: {e}")

# Entry Point
if __name__ == "__main__":
    start_receiver()
