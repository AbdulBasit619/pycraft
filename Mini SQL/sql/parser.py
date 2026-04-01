# Grammar (Phase 2 - WHERE clause)
#
# SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE WHERE CONDITION SEMICOLON
#
# COLUMN_LIST → * | IDENTIFIER (COMMA IDENTIFIER)*
#
# TABLE → IDENTIFIER
#
# CONDITION → IDENTIFIER OPERATOR VALUE
#
# VALUE → NUMBER | STRING

from sql.ast_nodes import SelectNode, AllColumnsNode, ConditionNode
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

        # If first token is SELECT, consume it and move forward.
        self.tokens.consume()

        ###
        # Recursively Descent to parsing column.
        columns = self.parse_columns()

        ###
        # Next token must be FROM, otherwise raise syntax error.
        self.tokens.expect("FROM")

        # If next token is FROM, consume it and move forward.
        self.tokens.consume()

        ###
        # Recursively Descent to parsing table
        table = self.parse_table()

        ###
        # Optionally parse WHERE clause
        if self.tokens.match("WHERE"):
            where_clause = self.parse_where()
        else:
            where_clause = None

        ###
        # Optionally parse SEMICOLON
        if self.tokens.match("SEMICOLON"):
            self.tokens.consume()

        return SelectNode(columns, table, where_clause)

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

        # If token is an identifier, consume it and move forward.
        self.tokens.consume()

        return table_name

    def parse_where(self):
        """
        Parse the WHERE statement.

        CFG:\n
        WHERE → CONDITION
        """

        print("[Parser] Parsing conditions")

        # Token must be WHERE, otherwise raise syntax error.
        self.tokens.expect("WHERE")

        # If next token is WHERE, consume it and move forward.
        self.tokens.consume()

        return self.parse_condition()

    def parse_condition(self):
        """
        Parse the conditions after WHERE statement.

        CFG:\n
        CONDITION → IDENTIFIER OPERATOR VALUE
        """
        print("[Parser] Parsing WHERE condition")

        ###
        # Token must be an identifier, otherwise raise syntax error.
        token = self.tokens.expect("IDENTIFIER")
        column_name = token.value

        # If token is an identifier, consume it and move forward.
        self.tokens.consume()

        ###
        # Next token must be OPERATOR, otherwise raise syntax error.
        token = self.tokens.expect("OPERATOR")
        operator = token.value

        # If token is an OPERATOR, consume it and move forward.
        self.tokens.consume()

        ###
        # Next token must be VALUE, otherwise raise syntax error.
        value = self.parse_value()

        return ConditionNode(column_name, operator, value)

    def parse_value(self):
        """
        Parse the condition VALUES.

        CFG:\n
        VALUE → NUMBER | STRING
        """

        ###
        # Parse either a number or a string as value.

        # Check for NUMBER
        if self.tokens.match("NUMBER"):

            # If token is a number, consume it and move forward.
            token = self.tokens.consume()

            # Convert to int or float
            if "." in token.value:
                return float(token.value)
            return int(token.value)

        # Check for STRING
        elif self.tokens.match("STRING"):

            # If token is a string, consume it and move forward.
            token = self.tokens.consume()

            # Remove surrounding quotes
            return token.value[1:-1]

        else:

            current = self.tokens.current()
            raise ParserError(
                f"Expected NUMBER or STRING, but found {current.type}",
                position=current.position,
            )
