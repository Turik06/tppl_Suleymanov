import runpy
import sys
from pathlib import Path
import pytest

from main import Lexer, LexicalException
import main

MAIN_PY = Path(__file__).resolve().parent.parent / "main.py"


class TestLexer:
    @pytest.mark.parametrize(
        "text, expected",
        [
            (
                "x = y * 2 + z * 3",
                [
                    ("IDENT", "x", 1, 1),
                    ("OP", "=", 1, 3),
                    ("IDENT", "y", 1, 5),
                    ("OP", "*", 1, 7),
                    ("INT", "2", 1, 9),
                    ("OP", "+", 1, 11),
                    ("IDENT", "z", 1, 13),
                    ("OP", "*", 1, 15),
                    ("INT", "3", 1, 17),
                ],
            ),
            (
                "def f(a, b) {\n  return a >= b; # cmp\n}",
                [
                    ("KEYWORD", "def", 1, 1),
                    ("IDENT", "f", 1, 5),
                    ("SEP", "(", 1, 6),
                    ("IDENT", "a", 1, 7),
                    ("SEP", ",", 1, 8),
                    ("IDENT", "b", 1, 10),
                    ("SEP", ")", 1, 11),
                    ("SEP", "{", 1, 13),
                    ("KEYWORD", "return", 2, 3),
                    ("IDENT", "a", 2, 10),
                    ("OP", ">=", 2, 12),
                    ("IDENT", "b", 2, 15),
                    ("SEP", ";", 2, 16),
                    ("SEP", "}", 3, 1),
                ],
            ),
        ],
    )
    def test_basic_tokenization(self, text, expected):
        assert Lexer(text).tokenize() == expected

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("42", [("INT", "42", 1, 1)]),
            ("0", [("INT", "0", 1, 1)]),
            ("3.14", [("FLOAT", "3.14", 1, 1)]),
            ("1.", [("FLOAT", "1.", 1, 1)]),
            ("0.5", [("FLOAT", "0.5", 1, 1)]),
        ],
    )
    def test_numbers(self, text, expected):
        assert Lexer(text).tokenize() == expected

    @pytest.mark.parametrize(
        "keyword",
        ["if", "else", "while", "return", "for", "def"],
    )
    def test_keywords(self, keyword):
        assert Lexer(keyword).tokenize() == [("KEYWORD", keyword, 1, 1)]

    @pytest.mark.parametrize(
        "text",
        ["iff", "definition", "If", "_if", "x1", "_a_1", "returns"],
    )
    def test_identifiers(self, text):
        assert Lexer(text).tokenize() == [("IDENT", text, 1, 1)]

    @pytest.mark.parametrize(
        "text, expected",
        [
            ('""', [("STRING", '""', 1, 1)]),
            ('"hello"', [("STRING", '"hello"', 1, 1)]),
            ('"a # b ( 1"', [("STRING", '"a # b ( 1"', 1, 1)]),
            (
                'val = "test"',
                [
                    ("IDENT", "val", 1, 1),
                    ("OP", "=", 1, 5),
                    ("STRING", '"test"', 1, 7),
                ],
            ),
        ],
    )
    def test_strings(self, text, expected):
        assert Lexer(text).tokenize() == expected

    @pytest.mark.parametrize(
        "text, line, col",
        [
            ('"unclosed', 1, 1),
            ('x = "abc', 1, 5),
            ('a\n  "broken\nnext', 2, 3),
        ],
    )
    def test_unclosed_string_error(self, text, line, col):
        with pytest.raises(LexicalException) as exc_info:
            Lexer(text).tokenize()
        assert exc_info.value.line == line
        assert exc_info.value.col == col
        assert "unterminated string literal" in exc_info.value.text

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("+", [("OP", "+", 1, 1)]),
            ("-", [("OP", "-", 1, 1)]),
            ("*", [("OP", "*", 1, 1)]),
            ("/", [("OP", "/", 1, 1)]),
            ("=", [("OP", "=", 1, 1)]),
            ("<", [("OP", "<", 1, 1)]),
            (">", [("OP", ">", 1, 1)]),
            ("==", [("OP", "==", 1, 1)]),
            ("<=", [("OP", "<=", 1, 1)]),
            (">=", [("OP", ">=", 1, 1)]),
            ("= =", [("OP", "=", 1, 1), ("OP", "=", 1, 3)]),
            (
                "a<=b",
                [
                    ("IDENT", "a", 1, 1),
                    ("OP", "<=", 1, 2),
                    ("IDENT", "b", 1, 4),
                ],
            ),
        ],
    )
    def test_operators(self, text, expected):
        assert Lexer(text).tokenize() == expected

    def test_separators(self):
        assert Lexer("(){},;").tokenize() == [
            ("SEP", "(", 1, 1),
            ("SEP", ")", 1, 2),
            ("SEP", "{", 1, 3),
            ("SEP", "}", 1, 4),
            ("SEP", ",", 1, 5),
            ("SEP", ";", 1, 6),
        ]

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("# only comment", []),
            ("x # comment", [("IDENT", "x", 1, 1)]),
            ("x # comment\ny", [("IDENT", "x", 1, 1), ("IDENT", "y", 2, 1)]),
            ("# line 1\n# line 2\nz", [("IDENT", "z", 3, 1)]),
        ],
    )
    def test_comments(self, text, expected):
        assert Lexer(text).tokenize() == expected

    @pytest.mark.parametrize(
        "text, expected",
        [
            ("", []),
            ("   \t \r \n  ", []),
            ("  \t var_name", [("IDENT", "var_name", 1, 5)]),
            (
                "x\n\n  y",
                [
                    ("IDENT", "x", 1, 1),
                    ("IDENT", "y", 3, 3),
                ],
            ),
        ],
    )
    def test_whitespaces_and_newlines(self, text, expected):
        assert Lexer(text).tokenize() == expected

    @pytest.mark.parametrize(
        "text, line, col, bad_char",
        [
            ("a @ b", 1, 3, "@"),
            ("~x", 1, 1, "~"),
            ("foo $ bar", 1, 5, "$"),
        ],
    )
    def test_unexpected_character(self, text, line, col, bad_char):
        with pytest.raises(LexicalException) as exc_info:
            Lexer(text).tokenize()
        assert exc_info.value.line == line
        assert exc_info.value.col == col
        assert f"unexpected character '{bad_char}'" in exc_info.value.text


class TestMain:
    @staticmethod
    def run_cli(monkeypatch, *args):
        monkeypatch.setattr(sys, "argv", ["main.py", *args])
        main.main()

    def test_successful_run(self, monkeypatch, capsys, tmp_path):
        src = tmp_path / "code.txt"
        src.write_text("x = 42\n", encoding="utf-8")

        self.run_cli(monkeypatch, str(src))

        captured = capsys.readouterr()
        assert captured.out == "(IDENT, x, 1:1)\n(OP, =, 1:3)\n(INT, 42, 1:5)\n"
        assert captured.err == ""

    def test_lexical_error_output(self, monkeypatch, capsys, tmp_path):
        src = tmp_path / "bad.txt"
        src.write_text("a @ b", encoding="utf-8")

        with pytest.raises(SystemExit) as exit_info:
            self.run_cli(monkeypatch, str(src))

        assert exit_info.value.code == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == f"{src}:1:3: lexical: unexpected character '@'\n"

    def test_missing_cli_argument(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as exit_info:
            self.run_cli(monkeypatch)

        assert exit_info.value.code == 2
        assert main.HELP_MESSAGE in capsys.readouterr().err

    def test_extra_cli_arguments(self, monkeypatch, capsys):
        with pytest.raises(SystemExit) as exit_info:
            self.run_cli(monkeypatch, "file1.txt", "file2.txt")

        assert exit_info.value.code == 2
        assert capsys.readouterr().err == main.USAGE_MESSAGE + "\n"

    def test_file_not_found(self, monkeypatch, capsys, tmp_path):
        missing = tmp_path / "missing.txt"
        with pytest.raises(SystemExit) as exit_info:
            self.run_cli(monkeypatch, str(missing))

        assert exit_info.value.code == 1
        assert str(missing) in capsys.readouterr().err or "No such file" in capsys.readouterr().err

    def test_decode_error(self, monkeypatch, capsys, tmp_path):
        bad_file = tmp_path / "bad.bin"
        bad_file.write_bytes(b"\xff\xfe\x00")

        with pytest.raises(SystemExit) as exit_info:
            self.run_cli(monkeypatch, str(bad_file))

        assert exit_info.value.code == 1
        assert capsys.readouterr().err != ""

    def test_direct_script_execution(self, monkeypatch, capsys, tmp_path):
        src = tmp_path / "input.txt"
        src.write_text("return", encoding="utf-8")
        monkeypatch.setattr(sys, "argv", ["main.py", str(src)])

        runpy.run_path(str(MAIN_PY), run_name="__main__")

        assert capsys.readouterr().out == "(KEYWORD, return, 1:1)\n"
