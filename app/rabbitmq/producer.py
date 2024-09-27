import pika
from app.config.whisper_logging import write_log_error, write_log_info
from app.config.configuration import config


def send_message(message: str):
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

        channel.basic_publish(exchange="", routing_key=queue_name, body=message)
        write_log_info(f" [x] Sent {message} from Producer of RabbitMQ")
        # connection.close()
    except Exception as e:
        write_log_error(str(e))
