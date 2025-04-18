import os
import logging
from typing import Callable, TYPE_CHECKING
from rabit_exc import RabbitException
from config import connection_params

import pika

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


log = logging.getLogger(__name__)


class RabbitBase:
    def __init__(self, connection_params: pika.ConnectionParameters = connection_params) -> None:
        self.connection_params: pika.ConnectionParameters = connection_params
        self._connection: pika.BlockingConnection | None = None
        self._channel: BlockingChannel | None = None

    def get_connection(self) -> pika.BlockingConnection:
        return pika.BlockingConnection(parameters=self.connection_params)

    @property
    def channel(self) -> BlockingChannel:
        if self._channel is None:
            raise RabbitException("Please use context manager for Rabbit helper.")
        return self._channel

    def __enter__(self):
        self._connection = self.get_connection()
        self._channel = self._connection.channel()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._channel.is_open:
            self._channel.close()
        if self._connection.is_open:
            self._connection.close()


class RabbitMixin:
    channel: "BlockingChannel"

    def declare_queue(self, queue_routing_key) -> None:
        queue = self.channel.queue_declare(queue=queue_routing_key)
        log.info(f"Declared queue {queue.method.queue}")

    def consume_message(
        self,
        queue_routing_key: str,
        message_callback: Callable[
            ["BlockingChannel", "Basic.Deliver", "BasicProperties", bytes], None
        ],
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        self.declare_queue(queue_routing_key=queue_routing_key)
        self.channel.basic_consume(
            queue=queue_routing_key,
            on_message_callback=message_callback
        )
        log.warning("Waiting for message...")
        self.channel.start_consuming()


class SimpleRabbit(RabbitMixin, RabbitBase):
    pass
