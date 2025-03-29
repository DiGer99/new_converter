from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
import uvicorn
from src.services.services import Parser

app = FastAPI()
parser = Parser()


@app.post("/files")
def convert(upload_file: UploadFile):
    filename = upload_file.filename
    file = upload_file.file
    with open(f"src/docs/xml/{filename}", "wb") as f:
        f.write(file.read())
    return RedirectResponse(url=f"/files/{filename}", status_code=303)


@app.get("/files/{filename}")
def get_file(filename: str):
    filename_json = filename.split(".xml")[0]
    parser.convert_join(f"src/docs/xml/{filename}", f"src/docs/json/{filename_json}.json")
    return FileResponse(f"src/docs/json/{filename_json}.json")


def main():
    uvicorn.run(app=app, reload=True)
