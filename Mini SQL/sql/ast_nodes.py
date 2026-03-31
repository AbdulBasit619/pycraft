# This module represents the nodes of Abstract Syntax Tree (AST)
# These nodes represent the different lexemes of tokens.


class SelectNode:
    """AST Node representing SELECT query."""

    def __init__(self, columns, table):
        self.columns = columns
        self.table = table

    def __repr__(self):
        return f"SelectNode(columns={self.columns}, table='{self.table}')"


class AllColumnsNode:
    """AST Node representing '*' (all columns in SELECT)."""

    def __repr__(self):
        return "AllColumnsNodes(*)"
