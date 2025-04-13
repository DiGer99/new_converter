class ParserParams:
    def __init__(self):
        self.stack: list[str] = []
        self.end_stack: str = ""
        self.stack_for_array: list[str] = []
        self.end_stack_for_array: str = ""
        self.empty_file = False
        self.tab = " " * 4
        self.encapsulation_token: list[list[str]] = []
        self.only_values: bool = False
        self.next_token = ""

    def reset(self):
        return self.__init__()
