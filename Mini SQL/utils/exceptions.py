class LexerError(Exception):
    """Base class for lexer-related errors."""

    def __init__(self, message, position=None, line=None, column=None):

        location = ""
        if line is not None and column is not None:
            location = f"at line {line}, column {column}"
        elif position is not None:
            location = f"at position {position}"
        super().__init__(f"LexerError {location}: {message}")
        self.position = position
        self.line = line
        self.column = column


class UnexpectedCharacterError(LexerError):
    pass


class ParserError(LexerError):
    pass
