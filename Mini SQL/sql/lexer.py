import re


from dataclasses import dataclass
from utils.exceptions import LexerError, UnexpectedCharacterError


@dataclass
class Token:
    type: str
    value: str
    position: int

    def __repr__(self):
        return f"{self.type}('{self.value}' => {self.position})"


class Lexer:
    # SQL Keywords
    KEYWORDS = {
        "SELECT",
        "FROM",
        "WHERE",
        "INSERT",
        "CREATE",
        "TABLE",
        "DATABASE",
        "INTO",
        "VALUES",
        "UPDATE",
        "SET",
        "DELETE",
        "AND",
        "OR",
        "NOT",
        "ORDER",
        "BY",
        "ASC",
        "DESC",
        "SCHEMA",
        "PRIMARY",
        "KEY",
        "ALTER",
        "ADD",
        "DROP",
        "COLUMN",
        "JOIN",
        "INNER",
        "LEFT",
        "RIGHT",
        "ON",
        "COUNT",
        "SUM",
        "AVG",
        "MIN",
        "MAX",
    }

    TOKEN_SPEC = [
        ("NUMBER", r"\d+(\.\d+)?"),
        ("STRING", r"'([^']|'')*'"),
        #
        # Identifiers
        ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),
        #
        # Operators
        ("OPERATOR", r">=|<=|!=|<>|=|>|<"),
        #
        # Symbols
        ("STAR", r"\*"),
        ("DOT", r"\."),
        ("COMMA", r","),
        ("LPAREN", r"\("),
        ("RPAREN", r"\)"),
        ("SEMICOLON", r";"),
        #
        # Ignore whitespace
        ("SKIP", r"[ \t\n]+"),
    ]

    def __init__(self):
        self.master_pattern = re.compile(
            "|".join(f"(?P<{name}>{pattern})" for name, pattern in self.TOKEN_SPEC),
            re.IGNORECASE,
        )

    def tokenize(self, sql):
        """Convert SQL strings into a list of tokens."""

        tokens = []
        pos = 0  # Track current scanning position

        for match in self.master_pattern.finditer(sql):
            start, end = match.span()
            kind = match.lastgroup
            value = match.group()

            # Detect unexpected characters between tokens
            if start > pos:
                error_text = sql[pos:start]
                raise UnexpectedCharacterError(
                    f"Invalid or unexpected token near '{error_text}'",
                    position=pos,
                )

            if kind is None:
                raise UnexpectedCharacterError(
                    f"Invalid or unexpected token near '{value}'",
                    position=pos,
                )

            if kind == "SKIP":
                pos = end
                continue

            if kind == "IDENTIFIER":
                upper_val = value.upper()
                if upper_val in self.KEYWORDS:
                    kind = upper_val
                    value = upper_val

            tokens.append(Token(kind, value, start))
            pos = end

        # Check for any trailing unexpected errors.
        if pos < len(sql):
            error_text = sql[pos:]
            raise UnexpectedCharacterError(
                f"Unexpected characters: '{error_text}'", position=pos
            )
        tokens.append(Token("EOF", "", len(sql)))

        # print(tokens)
        return tokens

    def determine_query_type(self, tokens):
        """Determine the type of SQL Query: SELECT, INSERT, UPDATE, DELETE, CREATE, etc."""
        if tokens:
            return tokens[0].type

        return "UNKNOWN"
