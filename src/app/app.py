import logging
import os
import uuid

from fastapi.params import Depends
from src.services.support_services import publish_response_get_from_s3

from src.s3_storage.s3_service import s3_bucket_service_factory

from src.config.config import logging_config
from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import Response
import uvicorn

from src.auth.auth import router as auth_router
from src.auth.validation import (
    get_current_auth_user,
)
from src.rabbit_src.producer import Publisher
from src.users.schemas import UserSchema

log = logging.getLogger(__name__)
logging_config()

app = FastAPI()
app.include_router(auth_router)


@app.post("/files")
def body_convert(body_xml: str = Body(media_type="text/plain")):
    res_file = publish_response_get_from_s3(body=body_xml)
    return Response(content=res_file)


@app.post("/files/doc")
def convert(
        upload_file: UploadFile,
        user: UserSchema = Depends(get_current_auth_user)
) -> Response:
    file = upload_file.file
    res_file = publish_response_get_from_s3(body=file.read())
    return Response(content=res_file)


def main() -> None:
    uvicorn.run(app=app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
