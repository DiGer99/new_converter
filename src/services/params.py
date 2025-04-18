class ParserParams:
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.end_stack: str = ""
        self.stack_for_array: list[str] = []
        self.end_stack_for_array: str = ""
        self.empty_file = False
        self.tab = " " * 4
        self.encapsulation_token: list[list[str]] = []
        self.only_values: list[str] = []
        self.next_token = ""
        self.entry_array_only_values: list[str] = []

    def reset(self) -> "ParserParams":
        return self.__init__()
