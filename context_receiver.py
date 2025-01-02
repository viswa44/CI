import pika
import screen_brightness_control as sbc  # type: ignore
import os
import subprocess

# Function Definitions
def reduce_brightness():
    """
    Reduce system brightness by 10%.
    """
    current_brightness = sbc.get_brightness()[0]
    new_brightness = max(current_brightness - 10, 0)
    sbc.set_brightness(new_brightness)
    print(f"Brightness reduced to {new_brightness}%")

def increase_brightness():
    """
    Increase system brightness by 10%.
    """
    current_brightness = sbc.get_brightness()[0]
    new_brightness = min(current_brightness + 10, 100)
    sbc.set_brightness(new_brightness)
    print(f"Brightness increased to {new_brightness}%")

def shutdown_system():
    """
    Shutdown the system.
    """
    subprocess.run(["shutdown", "/s", "/t", "0"])
    print("System shutting down...")

def mute_sound():
    """
    Mute the system sound.
    """
    os.system("nircmd.exe mutesysvolume 1")
    print("System sound muted.")

def unmute_sound():
    """
    Unmute the system sound.
    """
    os.system("nircmd.exe mutesysvolume 0")
    print("System sound unmuted.")

def open_application(app_name):
    """
    Open a specified application.
    """
    try:
        subprocess.Popen(app_name)
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

def execute_command(command):
    """
    Execute the received command.
    """
    if command == "reduce brightness":
        reduce_brightness()
    elif command == "increase brightness":
        increase_brightness()
    elif command == "shutdown":
        shutdown_system()
    elif command == "mute sound":
        mute_sound()
    elif command == "unmute sound":
        unmute_sound()
    elif command.startswith("open application:"):
        app_name = command.split(":", 1)[1].strip()
        open_application(app_name)
    elif command.startswith("close application:"):
        app_name = command.split(":", 1)[1].strip()
        close_application(app_name)
    else:
        print(f"Unknown command received: {command}")

def on_message_received(ch, method, properties, body):
    """
    RabbitMQ callback function to handle received messages.
    """
    command = body.decode('utf-8')
    print(f"Received command: {command}")
    execute_command(command)

def start_receiver():
    # """
    # Start RabbitMQ receiver to listen for commands.
    # """
    # try:
    #     credentials = pika.PlainCredentials('workerone', '1298')
    #     connection = pika.BlockingConnection(
    #         pika.ConnectionParameters(host='192.168.1.6', virtual_host='/', credentials=credentials)
    #     )
    #     channel = connection.channel()
    #     channel.queue_declare(queue='test_queue')
    #     print("Listening for commands...")
    #     channel.basic_consume(queue='test_queue', on_message_callback=on_message_received, auto_ack=True)
    #     channel.start_consuming()
    # except pika.exceptions.AMQPError as error:
    #     print(f"Failed to connect to RabbitMQ: {error}")
    
    try:
        credentials = pika.PlainCredentials('workertwo', '1298')
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='192.168.1.5',
                virtual_host='/',
                credentials=credentials
            )
        )
        print("Connection successful!")
        # connection.close()
    except Exception as e:
        print(f"Connection failed: {e}")

# Entry Point
if __name__ == "__main__":
    start_receiver()
