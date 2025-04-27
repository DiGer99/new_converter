import uuid

import pika
from src.rabbit_src.config_rabbit import connection_params
import logging
import os
from src.config.config import logging_config

log = logging.getLogger(__name__)
logging_config()



class Publisher:
    """
        RPC Client (Publisher)
    """
    def __init__(self):
        self.connection = pika.BlockingConnection(
            connection_params
        )
        self.channel = self.connection.channel()
        result = self.channel.queue_declare(
            queue="",
            exclusive=True
        )
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response
        )

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, body):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange=os.getenv("MQ_EXCHANGE"),
            routing_key=os.getenv("MQ_ROUTING_KEY"),
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=body
        )
        log.info(f"Message was send: {self.corr_id}")
        while self.response is None:
            self.connection.process_data_events(time_limit=5)
        return self.response