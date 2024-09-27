import time
import pika
from app.config.whisper_logging import write_log_error
from app.services.transcribe_audio import process_audio_file
from app.config.configuration import config


def start_consumer():
    isConnected = True
    while isConnected:
        try:
            credentials = pika.PlainCredentials(
                username=str(config.get("RABBITMQ_USER")),
                password=str(config.get("RABBITMQ_PASSWORD")),
            )
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=str(config.get("RABBITMQ_HOST")), credentials=credentials
                )
            )
            channel = connection.channel()
            queue_name = str(config.get("RABBITMQ_QUEUE_1"))
            channel.queue_declare(queue=queue_name)

            def callback(ch, method, properties, body):
                print(f" [x] Received {body}")
                audio_file_id = body.decode()
                process_audio_file(audio_file_id)

            channel.basic_consume(
                queue=queue_name, 
                on_message_callback=callback, 
                auto_ack=True
            )
            print(" [*] Waiting for messages. To exit press CTRL+C")
            channel.start_consuming()
            isConnected = False
        except Exception as ex:
            write_log_error(ex)
            time.sleep(5)
            isConnected = True

if __name__ == "__main__":
    start_consumer()
