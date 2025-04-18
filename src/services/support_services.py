from pathlib import Path


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
