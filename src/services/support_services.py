from pathlib import Path
import os
import uuid
from src.s3_storage.s3_service import s3_bucket_service_factory
from fastapi.responses import Response
from typing_extensions import TextIO
from src.services.params import ParserParams
from src.rabbit_src.producer import Publisher



def publish_response_get_from_s3(body: str) -> str:
    publisher = Publisher()
    response = publisher.call(body=body)
    response_from_publisher = response.decode("utf-8")

    client = s3_bucket_service_factory()
    client.download_file_object(response_from_publisher, uuid_file := str(uuid.uuid4()))
    with open(uuid_file) as res_file:
        res_file = res_file.read()

    os.remove(response_from_publisher)
    os.remove(uuid_file)

    return res_file




def split_strip(token: str, split_: bool = True, chars: str = "<>/") -> str:
    if split_ and token:
        return token.split()[0].strip(chars)
    return token.strip(chars)


def get_doc(doc_path: str | Path) -> str:
    """
    Возвращает файл xml в одну строку
    """
    with open(doc_path) as doc:
        res = doc.readlines()[1:]  # убираем версию xml
    for i, el in enumerate(res):
        res[i] = el.strip()
    return "".join(res)


def encapsulation(prm: ParserParams, doc: TextIO):
    if prm.encapsulation_token and prm.encapsulation_token[-1][0] == split_strip(prm.end_stack):
        doc.write(f",\n")
        end_of_list_params = prm.encapsulation_token.pop()[1:]
        list_params = [i.split("=") for i in end_of_list_params]
        for i, el in enumerate(list_params):
            param, val = el
            if split_strip(prm.end_stack) in prm.only_values:
                if split_strip(prm.end_stack) in prm.stack_for_array:
                    doc.write(f'{(len(prm.stack) + 2) * prm.tab}"__{param}": {val}')
                # elif split_strip(prm.end_stack) in prm.same_tokens:
                #     doc.write(f'{(len(prm.stack) + 2) * prm.tab}"__{param}": {val},\n{(len(prm.stack) + 2) * prm.tab}')
            elif i == len(list_params) - 1:
                doc.write(f'{(len(prm.stack) + 1) * prm.tab}"__{param}": {val}')
            else:
                doc.write(f'{len(prm.stack) * prm.tab}"__{param}": {val},\n')

