from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import FileResponse
import uvicorn

from src.rabbit_src.producer import Publisher


app = FastAPI()
publisher = Publisher()


@app.post("/files")
def body_convert(body_xml: str = Body(media_type="text/plain")) -> FileResponse:
    response = publisher.call(body=body_xml)
    return FileResponse(response)


@app.post("/files/doc")
def convert(upload_file: UploadFile) -> FileResponse:
    filename = upload_file.filename
    with open(f"src/docs/xml/{filename}", "r") as f:
        response = publisher.call(f.read())
    return FileResponse(response)


def main() -> None:
    uvicorn.run(app=app, reload=True)
