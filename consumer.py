import pika
import pyttsx3

# RabbitMQ server details
rabbitmq_host = '192.168.1.5'  # Replace with your RabbitMQ server IP or hostname
credentials = pika.PlainCredentials('workertwo', '1298')
queue_name = 'test_queue'

def text_to_speech(text):
    """
    Convert text to speech using pyttsx3.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def callback(ch, method, properties, body):
    """
    Callback function to process received messages.
    """
    message = body.decode('utf-8')  # Decode the message
    print(f"Received: {message}")
    text_to_speech(message)  # Convert the message to speech

def start_consumer():
    """
    Start the RabbitMQ consumer to receive and process messages.
    """
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_host, credentials=credentials))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue=queue_name)

    print(" [*] Waiting for messages. To exit press CTRL+C")

    # Set up consumer with a callback
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    # Start consuming messages
    channel.start_consuming()

if __name__ == "__main__":
    try:
        start_consumer()
    except KeyboardInterrupt:
        print("Consumer stopped. Exiting...")