import pytest
from src.services.services import Parser
import pathlib


# CORRECT_DOCS_DIR = pathlib.Path(__file__).parent / "correct_converted_docs"
# correct_book_doc = CORRECT_DOCS_DIR / "test_book.json"
# correct_order_doc = CORRECT_DOCS_DIR / "test_order.json"

# ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
# DOCS_DIR = ROOT_DIR / "src" / "docs"
# order = DOCS_DIR / "xml" / "order.xml"
# book = DOCS_DIR / "xml" / "book.xml"


class RootDir:
    """Получаем корневую директорию converter"""

    @classmethod
    def root_dir(cls):
        ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
        return ROOT_DIR


class CorrectTestDocJSON(RootDir):
    @classmethod
    def correct_docs_dir(cls):
        """converter/tests/correct_converted_docs"""
        CORRECT_DOCS_DIR = pathlib.Path(__file__).parent / "correct_converted_docs"
        return CORRECT_DOCS_DIR

    @classmethod
    def get_test_doc(cls, test_name: str):
        """Имя и путь ТЕСТОВОГО файла в JSON из директории tests/correct_converted_docs"""
        CORRECT_DOCS_DIR = cls.correct_docs_dir()
        return CORRECT_DOCS_DIR / f"test_{test_name}.json"


class DocsSrcXML(RootDir):
    @classmethod
    def src_docs_dir(cls):
        """converter/src/docs"""
        ROOT_DIR = cls.root_dir()
        return ROOT_DIR / "src" / "docs"

    @classmethod
    def get_doc(cls, doc_xml_name: str):
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
    ],
)
def test_convert_join(enter_doc_path, res_doc_path, correct_doc):
    p = Parser()
    path = RootDir.root_dir() / "src" / "docs" / "json" / res_doc_path
    p.convert_join(doc_path=enter_doc_path, res_doc_name=path)

    with open(path) as res_doc, open(correct_doc) as test_doc:
        result_doc = res_doc.read()
        test_doc = test_doc.read()
    assert result_doc == test_doc
