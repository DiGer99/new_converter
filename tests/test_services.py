import itertools
from itertools import zip_longest

import pytest

# from src.services.services import Parser
from src.services.old import Parser
from pathlib import Path


class RootDir:
    """Получаем корневую директорию converter"""

    @classmethod
    def root_dir(cls) -> Path:
        ROOT_DIR = Path(__file__).resolve().parent.parent
        return ROOT_DIR


class CorrectTestDocJSON(RootDir):
    @classmethod
    def correct_docs_dir(cls) -> Path:
        """converter/tests/correct_converted_docs"""
        CORRECT_DOCS_DIR = Path(__file__).parent / "correct_converted_docs"
        return CORRECT_DOCS_DIR

    @classmethod
    def get_test_doc(cls, test_name: str) -> Path:
        """Имя и путь ТЕСТОВОГО файла в JSON из директории tests/correct_converted_docs"""
        CORRECT_DOCS_DIR = cls.correct_docs_dir()
        return CORRECT_DOCS_DIR / f"test_{test_name}.json"


class DocsSrcXML(RootDir):
    @classmethod
    def src_docs_dir(cls) -> Path:
        """converter/src/docs"""
        ROOT_DIR = cls.root_dir()
        return ROOT_DIR / "src" / "docs"

    @classmethod
    def get_doc(cls, doc_xml_name: str) -> Path:
        """Получаем имя начального документа xml из директории src/docs/xml, которое нужно конвертировать в json"""
        DOCS_DIR = cls.src_docs_dir()
        return DOCS_DIR / "xml" / f"{doc_xml_name}.xml"


@pytest.mark.parametrize(
    "enter_doc_path, res_doc_path, correct_doc",
    [
        (
            DocsSrcXML.get_doc("order"),
            "order_converted.json",
            CorrectTestDocJSON.get_test_doc("order"),
        ),
        (
            DocsSrcXML.get_doc("book"),
            "book_converted.json",
            CorrectTestDocJSON.get_test_doc("book"),
        ),
        (
            DocsSrcXML.get_doc("big_data_file"),
            "big_data_converted.json",
            CorrectTestDocJSON.get_test_doc("big_data"),
        ),
        (
            DocsSrcXML.get_doc("company"),
            "company_converted.json",
            CorrectTestDocJSON.get_test_doc("company"),
        ),
        (
            DocsSrcXML.get_doc("lib"),
            "lib_converted.json",
            CorrectTestDocJSON.get_test_doc("lib"),
        ),
        # (
        #     DocsSrcXML.get_doc("level"),
        #     "level_converted.json",
        #     CorrectTestDocJSON.get_test_doc("level"),
        # ),
    ],
)
def test_convert_join(enter_doc_path: Path, res_doc_path: str, correct_doc: Path) -> None:
    p = Parser()
    path = RootDir.root_dir() / "src" / "docs" / "json" / res_doc_path
    p.convert_join(doc_path=enter_doc_path, res_doc_name=path)

    with open(path) as res_doc, open(correct_doc) as correct_test_doc:
        result_doc = res_doc.readlines()
        correct_test_doc = correct_test_doc.readlines()
        for res, test in itertools.zip_longest(result_doc, correct_test_doc):
            assert res.strip() == test.strip()
