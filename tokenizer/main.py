import sys

USAGE_MESSAGE = "usage: python main.py <file>"
HELP_MESSAGE = f"""{USAGE_MESSAGE}

Tokenize source code from <file> and print one token per line:
  (<type>, <value>, <line>:<col>)
where <type> is IDENT, KEYWORD, INT, FLOAT, STRING, OP or SEP.

On an invalid character prints
  <file>:<line>:<col>: lexical: <message>
and exits with code 1."""


class LexicalException(Exception):
    def __init__(self, line, col, text):
        super().__init__(f"{line}:{col}: lexical: {text}")
        self.line = line
        self.col = col
        self.text = text


class Lexer:
    keywords = {"if", "else", "while", "return", "for", "def"}
    operators = {"+", "-", "*", "/", "=", "<", ">"}
    separators = {"(", ")", "{", "}", ",", ";"}

    def __init__(self, text):
        self.text = text
        self.length = len(text)
        self.pos = 0
        self.line = 1
        self.col = 1

    # символ на текущей позиции
    def peek(self):
        return self.text[self.pos] if self.pos < self.length else ""

    # сдвиг указателя с пересчетом координат
    def advance(self):
        c = self.text[self.pos]
        if c == "\n":
            self.line += 1
            self.col = 0
        self.col += 1
        self.pos += 1
        return c

    # чтение серии символов 
    def read_while(self, predicate):
        start = self.pos
        while self.peek() and predicate(self.peek()):
            self.advance()
        return self.text[start:self.pos]

    # идентификатор 
    def read_word(self):
        start_line, start_col = self.line, self.col
        word = self.read_while(lambda c: c.isalnum() or c == "_")
        token_type = "KEYWORD" if word in self.keywords else "IDENT"
        return (token_type, word, start_line, start_col)

    # числовой литерал
    def read_number(self):
        start_line, start_col = self.line, self.col
        num = self.read_while(lambda c: c.isdigit())
        if self.peek() == ".":
            num += self.advance()
            num += self.read_while(lambda c: c.isdigit())
            return ("FLOAT", num, start_line, start_col)
        return ("INT", num, start_line, start_col)

    # строковый литерал 
    def read_string(self):
        start_line, start_col = self.line, self.col
        result = self.advance()
        result += self.read_while(lambda c: c != '"' and c != "\n")
        if self.peek() != '"':
            raise LexicalException(start_line, start_col, "unterminated string literal")
        result += self.advance()
        return ("STRING", result, start_line, start_col)

    # операция ==, <=, >=
    def read_op(self):
        start_line, start_col = self.line, self.col
        op = self.advance()
        if op in {"=", "<", ">"} and self.peek() == "=":
            op += self.advance()
        return ("OP", op, start_line, start_col)

    # разделители
    def read_sep(self):
        start_line, start_col = self.line, self.col
        return ("SEP", self.advance(), start_line, start_col)

    # пропуск комментария
    def skip_comment(self):
        self.read_while(lambda c: c != "\n")

    # генератор токенов
    def tokens(self):
        while self.peek():
            c = self.peek()

            if c.isspace():
                self.advance()
            elif c.isdigit():
                yield self.read_number()
            elif c.isalpha() or c == "_":
                yield self.read_word()
            elif c == '"':
                yield self.read_string()
            elif c in self.operators:
                yield self.read_op()
            elif c in self.separators:
                yield self.read_sep()
            elif c == "#":
                self.skip_comment()
            else:
                raise LexicalException(self.line, self.col, f"unexpected character '{c}'")

    # итоговый список токенов
    def tokenize(self):
        return list(self.tokens())


def main():
    if len(sys.argv) < 2:
        print(HELP_MESSAGE, file=sys.stderr)
        sys.exit(2)
    if len(sys.argv) > 2:
        print(USAGE_MESSAGE, file=sys.stderr)
        sys.exit(2)

    filename = sys.argv[1]
    try:
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()

        lexer = Lexer(text)
        for token_type, val, line, col in lexer.tokenize():
            print(f"({token_type}, {val}, {line}:{col})")

    except LexicalException as e:
        print(f"{filename}:{e}", file=sys.stderr)
        sys.exit(1)
    except (OSError, UnicodeDecodeError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
