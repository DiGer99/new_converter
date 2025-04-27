from pika.connection import ConnectionParameters
from src.config.config import MQ_HOST, MQ_PORT

connection_params = ConnectionParameters(
    host=MQ_HOST,
    port=MQ_PORT
)
