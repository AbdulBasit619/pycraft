# Grammar (Phase 1 - Minimal)
#
# SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE SEMICOLON
#
# COLUMN_LIST → IDENTIFIER (COMMA IDENTIFIER)*
#
# TABLE → IDENTIFIER

from sql.ast_nodes import SelectNode
from sql.ast_nodes import AllColumnsNode
from utils.exceptions import ParserError


class Parser:
    """Recursive Descent Parser for mini MySQL clone."""

    def __init__(self, token_stream):
        self.tokens = token_stream

    def parse(self):
        """Parse the token stream and return an AST"""
        if self.tokens.match("SELECT"):
            return self.parse_select()

    def parse_select(self):
        """
        Parse the SELECT statement.

        CFG:\n
        SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE SEMICOLON
        """
        print("[Parser] Parsing SELECT statement")

        ###
        # First token must be SELECT, otherwise raise syntax error.
        self.tokens.expect("SELECT")

        # If first token is SELECT, move forward.
        self.tokens.consume()

        ###
        # Recursively Descent to parsing column.
        columns = self.parse_columns()

        ###
        # Next token must be FROM, otherwise raise syntax error.
        self.tokens.expect("FROM")

        # If next token is FROM, move forward.
        self.tokens.consume()

        ###
        # Recursively Descent to parsing table
        table = self.parse_table()

        ###
        # Optionally parse SEMICOLON
        if self.tokens.match("SEMICOLON"):
            self.tokens.consume()

        return SelectNode(columns, table)

    def parse_columns(self):
        """
        Parse the table column.

        CFG:
        COLUMN_LIST → * | IDENTIFIER (COMMA IDENTIFIER)*
        """
        print("[Parser] Parsing columns")

        columns = []

        if self.tokens.match("STAR"):
            token = AllColumnsNode()
            self.tokens.consume()
            return token
        else:
            # Token must be an identifier, otherwise raise syntax error.
            column_name = self.tokens.expect("IDENTIFIER").value

            # First column is mandatory
            columns.append(column_name)

            # Consume the current identifier and
            # advance to the next token.
            self.tokens.consume()

            while self.tokens.match("COMMA"):
                # While the current token is COMMA,
                # consume it and advance to the next IDENTIFIER
                # consume the identifier and advance
                # until there is no COMMA
                self.tokens.consume()
                column_name = self.tokens.expect("IDENTIFIER").value
                self.tokens.consume()
                columns.append(column_name)

        return columns

    def parse_table(self):
        """
        Parse the table.

        CFG:\n
        TABLE → IDENTIFIER
        """
        print("[Parser] Parsing table")
        # Token must be an identifier, otherwise raise syntax error.
        token = self.tokens.expect("IDENTIFIER")
        table_name = token.value

        # If token is an identifier, move forward.
        self.tokens.consume()

        return table_name
