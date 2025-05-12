class ParserParams:
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.end_stack: str = ""
        self.stack_for_array: set[str] = set()
        self.end_stack_for_array: str = ""
        self.tab = " " * 4
        self.encapsulation_token: list[list[str]] = []
        self.only_values: set[str] = set()
        self.next_token = ""
        self.same_tokens: set[str] = set()

    def reset(self) -> "ParserParams":
        return self.__init__()
