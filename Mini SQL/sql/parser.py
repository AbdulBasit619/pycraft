# Grammar (Phase 2 - WHERE clause)
#
# SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE WHERE EXPRESSION ORDER BY ORDER_LIST SEMICOLON
#
# COLUMN_LIST → * | IDENTIFIER ( COMMA IDENTIFIER )*
#
# TABLE → IDENTIFIER
#
# EXPRESSION → TERM ( (OR) TERM )*
#
# TERM → FACTOR ( (AND) FACTOR )*
#
# FACTOR → NOT FACTOR
#        | CONDITION
#        | LPAREN EXPRESSION RPAREN
#
# CONDITION → IDENTIFIER OPERATOR VALUE
#
# VALUE → NUMBER | STRING
#
# ORDER_LIST → ORDER_ITEM ( COMMA ORDER_ITEM )*
#
# ORDER_ITEM → IDENTIFIER ( ASC | DESC )

from sql.ast_nodes import (
    SelectNode,
    AllColumnsNode,
    ConditionNode,
    LogicalNode,
    NotNode,
    OrderByNode,
)
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
        SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE WHERE EXPRESSION ORDER BY ORDER_LIST SEMICOLON
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
        # Recursively Descent to parsing table.
        table = self.parse_table()

        ###
        # Optionally parse WHERE clause
        if self.tokens.match("WHERE"):
            where_clause = self.parse_where()
        else:
            where_clause = None

        ###
        # Optionally parse ORDER BY
        if self.tokens.match("ORDER"):
            order_by = self.parse_order()
        else:
            order_by = None

        ###
        # Optionally parse SEMICOLON
        if self.tokens.match("SEMICOLON"):
            self.tokens.consume()

        return SelectNode(columns, table, where_clause, order_by)

    def parse_columns(self):
        """
        Parse the table column.

        CFG:
        COLUMN_LIST → * | IDENTIFIER ( COMMA IDENTIFIER )*
        """
        print("[Parser] Parsing COLUMN_LIST")

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
        print("[Parser] Parsing TABLE")

        # Token must be an identifier, otherwise raise syntax error.
        token = self.tokens.expect("IDENTIFIER")
        table_name = token.value

        # If token is an identifier, consume it and move forward.
        self.tokens.consume()

        return table_name

    def parse_where(self):
        """
        Parse the WHERE statement.
        """

        print("[Parser] Parsing WHERE conditions.")

        # Token must be WHERE, otherwise raise syntax error.
        self.tokens.expect("WHERE")

        # If next token is WHERE, consume it and move forward.
        self.tokens.consume()

        return self.parse_expression()

    def parse_expression(self):
        """
        Parse the expression after WHERE statement.

        CFG:\n
        EXPRESSION → TERM ( (OR) TERM )*
        """

        print("[Parser] Parsing EXPRESSION")

        # Parse TERM
        left = self.parse_term()

        # Next token must be OR, otherwise raise syntax error.
        while self.tokens.match("OR"):

            # If token is OR, consume it and move forward.
            self.tokens.consume()

            # Parse TERM
            right = self.parse_term()

            # If all done correctly, create a LogicalNode.
            left = LogicalNode(left, "OR", right)

        # Return either the simple TERM or a LogicalNode.
        return left

    def parse_term(self):
        """
        Parse the TERM.

        CFG:\n
        TERM → FACTOR ( (AND) FACTOR)*
        """

        print("[Parser] Parsing TERM")

        # Parse FACTOR
        left = self.parse_factor()

        # Next token must be AND, otherwise raise syntax error.
        while self.tokens.match("AND"):

            # If token is AND, consume it and move forward.
            self.tokens.consume()

            # Parse FACTOR
            right = self.parse_factor()

            # If all done correctly, finally create a LogicalNode.
            left = LogicalNode(left, "AND", right)

        # Return either the simple FACTOR or LogicalNode
        return left

    def parse_factor(self):
        """
        Parse the FACTOR.

        CFG:\n
        FACTOR → NOT FACTOR
               | CONDITION
               | LPAREN EXPRESSION RPAREN
        """

        print("[Parser] Parsing FACTOR")

        # Token must be NOT, otherwise raise syntax error.
        if self.tokens.match("NOT"):
            # If token is NOT, consume it and move forward.
            self.tokens.consume()

            # Parse FACTOR recursively
            child = self.parse_factor()

            return NotNode(child)

        # Token must be (, otherwise raise syntax error.
        if self.tokens.match("LPAREN"):
            # If token is (, consume it and move forward.
            self.tokens.consume()

            # Parse EXPRESSION recursively.
            expr = self.parse_expression()

            # Token must be ), otherwise raise syntax error.
            self.tokens.expect("RPAREN")

            # If token is ), consume it and move forward.
            self.tokens.consume()

            # Return EXPRESSION
            return expr

        # If token is not (, then parse CONDITION and return it.
        else:
            return self.parse_condition()

    def parse_condition(self):
        """
        Parse the conditions after WHERE statement.

        CFG:\n
        CONDITION → IDENTIFIER OPERATOR VALUE
        """
        print("[Parser] Parsing CONDITION")

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

    def parse_order(self):
        """
        Parse ORDER BY clause.

        CFG:
        ORDER_BY → ORDER BY ORDER_LIST

        ORDER_LIST → ORDER_ITEM (COMMA ORDER_ITEM)*

        ORDER_ITEM → IDENTIFIER (ASC | DESC)
        """

        print("[Parser] Parsing ORDER BY")

        # Expect ORDER
        self.tokens.expect("ORDER")
        self.tokens.consume()

        # Expect BY
        self.tokens.expect("BY")
        self.tokens.consume()

        items = []

        # First item (mandatory)
        token = self.tokens.expect("IDENTIFIER")
        column_name = token.value
        self.tokens.consume()

        direction = "ASC"
        if self.tokens.match("ASC"):
            self.tokens.consume()
        elif self.tokens.match("DESC"):
            self.tokens.consume()
            direction = "DESC"

        items.append((column_name, direction))

        # Remaining items
        while self.tokens.match("COMMA"):
            self.tokens.consume()

            token = self.tokens.expect("IDENTIFIER")
            column_name = token.value
            self.tokens.consume()

            direction = "ASC"
            if self.tokens.match("ASC"):
                self.tokens.consume()
            elif self.tokens.match("DESC"):
                self.tokens.consume()
                direction = "DESC"

            items.append((column_name, direction))

        return OrderByNode(items)
