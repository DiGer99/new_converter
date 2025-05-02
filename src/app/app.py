import logging
import os

from starlette.responses import Response

from src.s3_storage.s3_service import s3_bucket_service_factory

from src.config.config import logging_config
from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import FileResponse, Response
import uvicorn

from src.rabbit_src.producer import Publisher

log = logging.getLogger(__name__)
logging_config()
app = FastAPI()
publisher = Publisher()


@app.post("/files")
def body_convert(body_xml: str = Body(media_type="text/plain")):
    response = publisher.call(body=body_xml)
    # client = s3_bucket_service_factory()
    # client.download_file_object(res)
    file = FileResponse(response)
    return file


@app.post("/files/doc")
def convert(upload_file: UploadFile) -> Response:
    filename = upload_file.filename
    with open(f"src/docs/xml/{filename}", "r") as f:
        response = publisher.call(f.read())

    response_from_publisher = response.decode("utf-8")

    client = s3_bucket_service_factory()
    client.download_file_object(response_from_publisher, "res_file.json")
    res_file = open("res_file.json").read()

    os.remove(response_from_publisher)

    return Response(content=res_file)


def main() -> None:
    uvicorn.run(app=app, reload=True)
