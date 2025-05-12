import os
from typing import TYPE_CHECKING
import logging
import uuid
from src.rabbit_src.rabbit_base import SimpleRabbit
from src.services.old import Parser as OldParser
from src.services.services import Parser
from pika.spec import Basic, BasicProperties
from src.config.config import logging_config
from src.s3_storage.s3_service import s3_bucket_service_factory

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel

log = logging.getLogger(__name__)
# parser = OldParser()
parser = Parser()

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

    with open(f"src/docs/json/{filename}.json") as fl:
        res_file = fl.read()

    file_path_in_s3 = f"src/docs/json/{filename}.json"

    client = s3_bucket_service_factory()
    client.upload_file_object(prefix="", source_file_name=file_path_in_s3, content=res_file)

    ch.basic_publish(exchange=os.getenv("MQ_EXCHANGE"),
                     routing_key=properties.reply_to,
                     properties=BasicProperties(
                         correlation_id=properties.correlation_id
                     ),
                     body=file_path_in_s3)

    ch.basic_ack(delivery_tag=method.delivery_tag)
    log.info(f"Message was convert: {properties.correlation_id}")
    os.remove(f"src/docs/xml/{filename}.xml")



def main():
    logging_config()
    with SimpleRabbit() as rabbit:
        rabbit.consume_message(
            queue_routing_key=os.getenv("MQ_ROUTING_KEY"),
            message_callback=message_callback_body,
            prefetch_count=1
        )


if __name__ == "__main__":
    main()