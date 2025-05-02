from pathlib import Path
from tqdm import tqdm
from src.services.support_services import get_doc, split_strip
from src.services.params import ParserParams
from typing import TextIO


class Parser:
    @staticmethod
    def open_token(res: str, doc: TextIO, indx: int, symbol: str, prm: ParserParams) -> None:
        """
        Parameters:
            res: str - self.get_doc() функция, возвращающая файл xml в виде одной строки без пробелов между токенами
            doc: TextIO - документ/файл, в который пишем результат
            indx: int - текущий индекс в итерации по enumerate(res). Перебирает все индексы, символы из res
            symbol: str - текущий символ в итерации
            prm: ParserParams - все параметры для функционирования:
            (
                stack, end_stack, stack_for_array, end_stack_for_array, empty_file,
                tab, encapsulation_token, only_values, next_token
            )
        """
        now_close_key = res.find(">", indx)  # >

        # Нынешний токен <book> or <book id="1">
        token = res[indx: now_close_key + 1]
        # Следующий токен <title> или </title>
        # >
        next_close_key: int | None = (
            res.find(">", now_close_key + 1) if res[now_close_key + 1] == "<" else None
        )
        prm.stack.append(token)
        # Если после открывающего токена еще один, то будем записывать токен
        if next_close_key:
            prm.next_token = res[now_close_key + 1: next_close_key + 1]

        # Вложенность токена (следующий закрытый токен) </book>
        nesting_of_token = res.find(f"</{split_strip(token)}>", indx)
        # Если пробелы внутри токена, будем закидывать в список параметры токена до знака ">"
        if " " in token:
            token_with_spaces = token[:-1].split()[1:]
            prm.encapsulation_token.append(token_with_spaces)

        if split_strip(token) in prm.same_tokens and split_strip(token) in prm.only_values:
            doc.write(f"{(len(prm.stack) + 1) * prm.tab}")
            return
        elif split_strip(token) in prm.same_tokens:
            doc.write(f'{len(prm.stack) * prm.tab}"{split_strip(token)}": [\n')
            doc.write(f"{(len(prm.stack) + 1) * prm.tab}")
            prm.only_values.append(split_strip(token))
            return

        # Если следующий токен встречается несколько раз
        if (
                next_close_key
                and res.count(f"<{split_strip(prm.next_token)}", indx, nesting_of_token) > 1
        ):
            if all(
                    split_strip(prm.next_token) in x for x in res[indx:nesting_of_token].split("</")
            ):
                prm.same_tokens.append(split_strip(prm.next_token))
            else:
                prm.stack_for_array.append(split_strip(prm.next_token))

        if split_strip(token) in prm.stack_for_array and split_strip(token) not in prm.only_values:
            doc.write(f'{len(prm.stack) * prm.tab}"{split_strip(token)}": [\n')
            doc.write(f"{(len(prm.stack) + 1) * prm.tab}{{\n")
            prm.only_values.append(split_strip(token))
        # Если следующий токен отличается и он открывающий - открываем абзац
        elif (
                next_close_key
                and split_strip(token) != split_strip(prm.next_token)
                and "/" not in prm.next_token
        ):

            if split_strip(token) not in prm.stack_for_array:
                doc.write(f'{len(prm.stack) * prm.tab}"{split_strip(token)}": {{\n')
                # print(prm.end_stack, prm.end_stack_for_array, 1)
                # print(token, "token")
            else:
                doc.write(f"{(len(prm.stack) + 1) * prm.tab}{{\n")
                # print(prm.end_stack, prm.end_stack_for_array, 2)
        # Если следующий символ в res не "<>/" (не токен, а значение,
        # без открытия абзацев - в одну строку), то записываем токен
        elif res[now_close_key + 1] not in "<>/":
            doc.write(f'{len(prm.stack) * prm.tab}"{split_strip(token)}": ')

        prm.next_token = ""

    @staticmethod
    def close_token(res: str, doc: TextIO, indx: int, symbol: str, prm: ParserParams) -> None:
        """
        Parameters:
            res: str - self.get_doc() функция, возвращающая файл xml в виде одной строки без пробелов между токенами
            doc: TextIO - документ/файл, в который пишем результат
            indx: int - текущий индекс в итерации по enumerate(res). Перебирает все индексы, символы из res
            symbol: str - текущий символ в итерации
            prm: ParserParams - все параметры для функционирования:
            (
                stack, end_stack, stack_for_array, end_stack_for_array, empty_file,
                tab, encapsulation_token, only_values, next_token
            )
        """
        left_key = indx - 1
        right_key = indx  # <
        # Ищем и записываем значение между токенами
        if res[indx - 1] not in "<>/":
            while res[left_key] != ">":
                left_key -= 1
            doc.write(f'"{res[left_key + 1: right_key].replace("\"", "\'")}"')

        # Нынешний токен
        if prm.stack:
            prm.end_stack = prm.stack.pop()

        # Далее выполнится проверка следующего токена, если есть (проверка будет на то, является ли следующий
        # символ закрывающем токен /)
        next_open_key = res.find("<", indx + 1)  # <
        # Граница следующего токена
        next_close_key = res.find(">", next_open_key + 1)  # >
        # Следующий токен: <Item> или </Item>
        next_token = res[next_open_key: next_close_key + 1]

        if "/" in next_token:
            if split_strip(next_token) != split_strip(prm.end_stack):
                if (
                        split_strip(prm.end_stack) in prm.same_tokens
                        and split_strip(prm.end_stack) in prm.only_values
                ):
                    doc.write(f"\n{(len(prm.stack) + 2) * prm.tab}]")
                    doc.write(f"\n{(len(prm.stack) + 1) * prm.tab}}}\n")
                    prm.only_values.remove(split_strip(prm.end_stack))
                    prm.same_tokens.remove(split_strip(prm.end_stack))

                elif (
                        split_strip(prm.end_stack) in prm.only_values
                        and split_strip(prm.end_stack) in prm.stack_for_array
                ):
                    doc.write(f"\n{(len(prm.stack) + 2) * prm.tab}}}")
                    # doc.write(f"\n{(len(prm.stack) + 1) * prm.tab}}}")
                    doc.write(f"\n{(len(prm.stack) + 1) * prm.tab}]")
                    # print(prm.end_stack)
                    # print(prm.stack_for_array)
                    prm.stack_for_array.remove(split_strip(prm.end_stack))
                    prm.only_values.remove(split_strip(prm.end_stack))

                # if split_strip(prm.end_stack) in prm.only_values:
                #     doc.write(f'\n{(len(prm.stack) + 1) * prm.tab}}}--')

            # # Если нужно добавить токены с id, PartNumber и тд.
            # if prm.encapsulation_token:
            #     doc.write(f",\n")
            #     print(prm.encapsulation_token)
            #     end_of_list_params = prm.encapsulation_token.pop()
            #     list_params = [i.split("=") for i in end_of_list_params]
            #     for i, el in enumerate(list_params):
            #         param, val = el
            #         if i == len(list_params) - 1:
            #             doc.write(f'{(len(prm.stack) + 1) * prm.tab}"__{param}": {val}\n')
            #             # doc.write(f"{len(prm.stack) * prm.tab}}}")
            #         else:
            #             doc.write(f'{len(prm.stack) * prm.tab}"__{param}": {val},\n')
            # # Если нет параметров внутри токена (id, ...)
            # else:
            #     doc.write(f"\n{len(prm.stack) * prm.tab}}}")
        elif not next_token:
            doc.write(f"\n{prm.tab}}}\n")

        elif "/" not in next_token:
            if split_strip(prm.end_stack) in prm.stack_for_array:
                if split_strip(prm.end_stack) != split_strip(next_token):
                    doc.write(f"\n{(len(prm.stack) + 2) * prm.tab}}}\n")
                    doc.write(f"{(len(prm.stack) + 1) * prm.tab}],\n")
                elif (
                    split_strip(prm.end_stack) == split_strip(next_token) and
                    split_strip(prm.end_stack) in prm.stack_for_array
                ):
                    doc.write(f'\n{(len(prm.stack) + 2) * prm.tab}}},--\n')
                # else:
                #     doc.write(f"\n{(len(prm.stack) + 2) * prm.tab}}},\n")
            else:
                doc.write(",\n")

    def convert_join(self, doc_path: str | Path, res_doc_name: str | Path) -> None:
        res: str = get_doc(doc_path)
        prm = ParserParams()
        with open(doc_path, "r") as doc:
            if not doc.read().strip():
                prm.empty_file = True

        with open(res_doc_name, "w") as doc:
            if not prm.empty_file:
                doc.write("{\n")
                for indx, symbol in tqdm(enumerate(res)):
                    # закрывающий токен </
                    if symbol == "<" and res[indx + 1] == "/":
                        self.close_token(res, doc, indx, symbol, prm)

                    # открывающий токен <
                    elif symbol == "<":
                        self.open_token(res, doc, indx, symbol, prm)
                doc.write("}")


DOCS_DIR = Path(__file__).parent.parent / "docs"
book = str(DOCS_DIR / "xml" / "book.xml")
order = str(DOCS_DIR / "xml" / "order.xml")
big_data = DOCS_DIR / "xml" / "big_data.xml"
company = DOCS_DIR / "xml" / "company.xml"

p = Parser()
p.convert_join(order, DOCS_DIR / "json" / "order_converted.json")
p.convert_join(company, DOCS_DIR / "json" / "company_converted.json")
p.convert_join(book, DOCS_DIR / "json" / "book_converted.json")
p.convert_join(DOCS_DIR / "xml" / "lib.xml", DOCS_DIR / "json" / "lib_converted.json")
p.convert_join(DOCS_DIR / "xml" / "level.xml", DOCS_DIR / "json" / "level_converted.json")
# p.convert_join(big_data, DOCS_DIR / "json" / "big_data_converted.json")
