import pytest
from src.services.services import Parser
import pathlib


CORRECT_DOCS_DIR = pathlib.Path(__file__).parent / "correct_converted_docs" 
correct_book_doc = CORRECT_DOCS_DIR / "test_book.json"
correct_order_doc = CORRECT_DOCS_DIR / "test_order.json"

ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT_DIR / "src" / "docs" 
order = DOCS_DIR / "xml" / "order.xml"
book = DOCS_DIR / "xml" / "book.xml"


@pytest.mark.parametrize(
        "enter_doc_path, res_doc_path, correct_doc",
        [
            (order, "order_converted.json", correct_order_doc),
            (book, "book_converted.json", correct_book_doc),
        ]
)
def test_convert_join(enter_doc_path, res_doc_path, correct_doc):
    p = Parser()
    p.convert_join(doc_path=enter_doc_path, res_doc_name=DOCS_DIR / "json" / res_doc_path)
    res_path = DOCS_DIR / "json" / res_doc_path
    with open(res_path) as res_doc, open(correct_doc) as test_doc:
        result_doc = res_doc.read()
        test_doc = test_doc.read()
        assert result_doc == test_doc