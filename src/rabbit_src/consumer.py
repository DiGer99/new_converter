import os
from typing import TYPE_CHECKING
import logging
import uuid
from src.rabbit_src.rabbit_base import SimpleRabbit
from src.services.old import Parser as OldParser
from pika.spec import Basic, BasicProperties
from src.config.config import logging_config

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

log = logging.getLogger(__name__)
parser = OldParser()

def message_callback_body(
    ch: "BlockingChannel", method: "Basic.Deliver", properties: "BasicProperties", body: bytes
):
    response = body.decode()
    filename = str(uuid.uuid4())[:16]
    with open(f"src/docs/xml/{filename}.xml", "w") as f:
        f.write(response)

    parser.convert_join(
        doc_path=f"src/docs/xml/{filename}.xml", res_doc_name=f"src/docs/json/{filename}.json"
    )
    result = f"src/docs/json/{filename}.json"
    ch.basic_publish(exchange=os.getenv("MQ_EXCHANGE"),
                     routing_key=properties.reply_to,
                     properties=BasicProperties(
                         correlation_id=properties.correlation_id
                     ),
                     body=result)
    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.info(f"Message was convert: {properties.correlation_id}")


def main():
    with SimpleRabbit() as rabbit:
        rabbit.consume_message(
            queue_routing_key=os.getenv("MQ_ROUTING_KEY"),
            message_callback=message_callback_body,
            prefetch_count=1
        )


if __name__ == "__main__":
    logging_config()
    main()