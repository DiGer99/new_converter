from pyexpat.errors import messages
from typing import TYPE_CHECKING
import pika
from src.app.app import parser
import uuid
if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties


def message_callback_body(
        ch: "BlockingChannel",
        method: "Basic.Deliver",
        properties: "BasicProperties",
        body: bytes
):
    res = body.decode()
    filename = str(uuid.uuid4())[:16]
    with open(f"src/docs/xml{filename}.xml", "w") as f:
        f.write(res)

    parser.convert_join(
        doc_path=f"src/docs/xml{filename}.xml",
        res_doc_name=f"src/docs/json/{filename}.json"
    )
    ... # redirect ?
    ch.basic_ack(delivery_tag=method.delivery_tag)