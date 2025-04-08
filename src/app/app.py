from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import FileResponse, RedirectResponse
import uvicorn
from src.services.services import Parser
from pydantic import BaseModel, Field
from lxml import etree
import uuid

app = FastAPI()
parser = Parser()


@app.post("/files")
def body_convert(body_xml: str = Body(media_type="text/plain")) -> RedirectResponse:
    filename = str(uuid.uuid4())[:16] + ".xml"
    with open(f"src/docs/xml/{filename}", "w") as file:
        file.write(body_xml)
    return RedirectResponse(url=f"/files/doc/{filename}", status_code=303)


@app.post("/files/doc")
def convert(upload_file: UploadFile) -> RedirectResponse:
    filename = upload_file.filename
    file = upload_file.file
    with open(f"src/docs/xml/{filename}", "wb") as f:
        f.write(file.read())
    return RedirectResponse(url=f"/files/doc/{filename}", status_code=303)


@app.get("/files/doc/{filename}")
def get_file(filename: str) -> FileResponse:
    filename_json = filename.split(".xml")[0]
    parser.convert_join(f"src/docs/xml/{filename}", f"src/docs/json/{filename_json}.json")
    return FileResponse(f"src/docs/json/{filename_json}.json")


def main() -> None:
    uvicorn.run(app=app, reload=True)
