from utils.exceptions import ParserError


class TokenStream:
    """A class to manage a stream of tokens produced by the lexer.

    Provides methods for peeking, consuming, and matching tokens
    safely while maintaining internal state.
    """

    def __init__(self, tokens):
        # Encapsulated attributes
        self._tokens = tokens
        self._position = 0
        self._length = len(tokens)

    def current(self):
        """Return the current token in the stream."""
        if self._position < self._length:
            return self._tokens[self._position]
        else:
            # Always return EOF if out of bounds
            return self._tokens[-1]

    def advance(self):
        """Move to the next token in the stream."""
        if self._position < self._length:
            self._position += 1

    def peek(self, k=1):
        """Return the token k positions ahead without advancing."""
        if self._position + k < self._length:
            return self._tokens[self._position + k]
        else:
            # Always return EOF if peek goes past end
            return self._tokens[-1]

    def at_end(self):
        """Check if the stream has reached the end (EOF)."""
        return self.current().type == "EOF"

    def expect(self, token_type):
        """Assert that the current token matches the expected type, otherwise raise an error."""
        token = self.current()
        if token.type != token_type:
            raise ParserError(
                f"Expected token type {token_type}, but found {token.type}",
                position=token.position,
            )
        self.advance()
        return token

    def match(self, token_type):
        """Check if the current token matches the given type (returns True/False)."""
        if self.current().type == token_type:
            self.advance()
            return True
        return False

    def consume(self):
        """Return the current token and advance the stream by one."""
        token = self.current()
        self.advance()
        return token

    def reset(self):
        """Reset the stream to the start (useful for backtracking)."""
        self._position = 0

    def __repr__(self):
        """Debug-friendly representation showing current position."""
        return f"<TokenStream position={self._position} current={self.current()}>"
