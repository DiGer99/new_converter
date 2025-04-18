from pika.connection import ConnectionParameters
import os


connection_params = ConnectionParameters(
    host=os.getenv("MQ_HOST"),
    port=os.getenv("MQ_PORT")
)
