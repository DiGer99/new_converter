import pathlib


DOCS_DIR = pathlib.Path(__file__).parent.parent / "docs"
book = str(DOCS_DIR / "xml" / "book.xml")
order = str(DOCS_DIR / "xml" / "order.xml")
big_data_file = DOCS_DIR / "xml" / "big_data_file.xml"
company = DOCS_DIR / "xml" / "company.xml"


class Parser:
    def get_doc(self, doc_path: str) -> str:
        """
        Возвращает файл xml в одну строку
        """
        with open(doc_path) as doc:
            res = doc.readlines()[1:]  # убираем версию xml

        for i, el in enumerate(res):
            res[i] = el.strip()
        res = "".join(res)
        return res

    @staticmethod
    def _split_strip(token: str, split_: bool = True, chars: str = "<>/") -> str:
        if split_ and token:
            return token.split()[0].strip(chars)
        return token.strip(chars)

    def _check_array(self, token: str) -> bool:
        """
        Проверка содержания списка types в токенах
        """
        types = ["type", "partnumber", "id"]
        res = any(x in token.lower() for x in types)
        return res

    def convert_join(self, doc_path: str, res_doc_name: str) -> None:
        stack: list[str] = []
        res: str = self.get_doc(doc_path)
        end_stack: str = ""
        # Токены, которые открывают массив
        stack_for_array: list[str] = []
        end_stack_for_array: str = ""
        empty_file = False
        tab = " " * 4
        with open(doc_path, "r") as doc:
            if not doc.read().strip():
                empty_file = True

        with open(res_doc_name, "w") as doc:
            if not empty_file:
                doc.write("{\n")
                for indx, symbol in enumerate(res):
                    # закрывающий токен </
                    if symbol == "<" and res[indx + 1] == "/":
                        left_key = indx - 1
                        right_key = indx  # <
                        # ищем и записываем значение между токенами
                        if res[indx - 1] not in ("<>/"):
                            while res[left_key] != ">":
                                left_key -= 1
                            doc.write(f'"{res[left_key + 1: right_key].replace("\"", "\'")}"')

                        # Нынешний токен
                        end_stack = token = stack.pop()

                        # далее выполнится проверка следующего токена, если есть (проверка будет на то, что является ли следующий символ закрывающем токен /)
                        next_open_key = res.find("<", indx + 1)  # <
                        # граница следующего токена
                        next_close_key = res.find(">", next_open_key + 1)  # >
                        # Следующий токен: <Item> или </Item>
                        next_token = res[next_open_key : next_close_key + 1]

                        # закрывать массив после того как перчисления закончились
                        if (
                            stack_for_array
                            and self._split_strip(end_stack) == stack_for_array[-1]
                            and self._split_strip(next_token) != self._split_strip(end_stack)
                        ):
                            doc.write(f"\n{len(stack) * tab}]")
                            end_stack_for_array = stack_for_array.pop()

                        # если следующий токен тоже закрывающий,то закрываем абзац
                        if "/" in next_token:
                            doc.write(f"\n{len(stack) * tab}}}")
                        elif "/" not in next_token and stack:

                            doc.write(",\n")

                    # открывающий токен <
                    elif symbol == "<":
                        now_close_key = res.find(">", indx)  # >

                        # Нынешний токен <book> or <book id="1">
                        token = res[indx : now_close_key + 1]
                        line = (
                            f'{len(stack) * tab}"{self._split_strip(token)}": '  # записываем токен
                        )
                        # Следующий токен <title> или </title>
                        # >
                        next_close_key = (
                            res.find(">", now_close_key + 1)
                            if res[now_close_key + 1] == "<"
                            else None
                        )

                        # Если после открывающего токена еще один, то будем записывать токен
                        if next_close_key:
                            next_token = res[now_close_key + 1 : next_close_key + 1]

                        # Вложенность токена (следующий закрытый токен) </book>
                        nesting_of_token = res.find(f"</{self._split_strip(token)}>", indx)
                        # Если токен равен тому, который перечисляется сейчас
                        if stack_for_array and self._split_strip(token) == stack_for_array[-1]:
                            stack.append(token)
                            # Если только такие токены встречаются во вложенности и больше никакие другие - то будем просто их перечислять в списке без открытия словаря {
                            if all(next_token in x for x in res[indx:nesting_of_token].split("</")):
                                doc.write(f"{len(stack) * tab}")
                                continue
                            else:
                                doc.write(f"{len(stack) * tab}{{\n")
                                continue

                        # Если следующий токен отличается и он открывающий - открываем абзац
                        if (
                            next_close_key
                            and self._split_strip(token) != self._split_strip(next_token)
                            and "/" not in next_token
                        ):
                            doc.write(f'{len(stack) * tab}"{self._split_strip(token)}": {{\n')

                        # Если следующий токен встречается несколько раз - открываем массив
                        if next_close_key and (
                            res.count(f"<{self._split_strip(next_token)}", indx, nesting_of_token)
                            > 1
                        ):
                            stack_for_array.append(self._split_strip(next_token))
                            doc.write(
                                f'{(len(stack) + 1) * tab}"{self._split_strip(next_token)}": [\n'
                            )
                        # Если следующий символ в res не "<>/" (не токен, а значение,
                        # без открытия абзацев - в одну строку), то записываем токен
                        elif res[now_close_key + 1] not in ("<>/"):
                            doc.write(line)

                        stack.append(token)
            doc.write("\n}")


p = Parser()
# p.convert_join(book, DOCS_DIR / "json" / "book_converted.json")
# p.convert_join(order, DOCS_DIR / "json" / "order_converted.json")
# p.convert_join(big_data_file, DOCS_DIR / "json" / "big_data_converted.json")
# p.convert_join(company, DOCS_DIR / "json" / "company_converted.json")
# p.convert_join(DOCS_DIR / "xml" / "lib.xml", DOCS_DIR / "json" / "lib_converted.json")
p.convert_join(DOCS_DIR / "xml" / "level.xml", DOCS_DIR / "json" / "level_converted.json")
