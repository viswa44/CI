import pika

rabbitmq_host = 'localhost'

connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
channel = connection.channel()

queue_name = 'test_queue'

channel.queue_declare(queue=queue_name)

def callback(ch,method,properties,body):
    print(f"received:{body.decode()}")
    
channel.basic_consume(queue=queue_name,on_message_callback=callback,auto_ack=True)
print("Waiting for messages. TO exit, press ctrl + c")
channel.start_consuming()