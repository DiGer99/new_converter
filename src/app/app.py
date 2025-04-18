from fastapi import FastAPI, UploadFile, Body
from fastapi.responses import FileResponse, RedirectResponse
import uvicorn
from src.services.services import Parser
from src.services.old import Parser as OldParser
from src.rabbit_src.producer import Publisher
import uuid
import os


app = FastAPI()
# parser = Parser()
parser = OldParser()


@app.post("/files")
def body_convert(body_xml: str = Body(media_type="text/plain")):
    with Publisher() as publisher:
        publisher.produce_message(
            queue_routing_key=os.getenv("MQ_ROUTING_KEY"),
            body=body_xml
        )
    return {"message": "Send message in rabbit."}
    # filename = str(uuid.uuid4())[:16] + ".xml"
    # with open(f"src/docs/xml/{filename}", "w") as file:
    #     file.write(body_xml)
    # return RedirectResponse(url=f"/files/doc/{filename}", status_code=303)


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
    os.remove(f"src/docs/xml/{filename}")  # удаляет файл xml
    ...  # логика отправки файла в s3, rabbit, redis (для кэша)
    ...  # удаление файла json после отправки по consumers
    return FileResponse(f"src/docs/json/{filename_json}.json")


def main() -> None:
    uvicorn.run(app=app, reload=True)
