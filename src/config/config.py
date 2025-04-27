from dotenv import load_dotenv
from os import getenv
import logging

def logging_config(level = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(filename)-8s %(name)s - %(funcName)s %(lineno)d %(message)s"
    )



load_dotenv()

MQ_EXCHANGE = getenv("MQ_EXCHANGE")
MQ_ROUTING_KEY = getenv("MQ_ROUTING_KEY")

MQ_HOST = getenv("MQ_HOST")
MQ_PORT = getenv("MQ_PORT")


