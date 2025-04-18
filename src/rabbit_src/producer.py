from rabbit_base import SimpleRabbit
import logging
import os

log = logging.getLogger(__name__)


class Publisher(SimpleRabbit):
    def produce_message(self, queue_routing_key: str, body: str) -> None:
        self.channel.basic_publish(
            exchange=os.getenv("MQ_EXCHANGE"), routing_key=queue_routing_key, body=body
        )
        log.info("Send message.")
