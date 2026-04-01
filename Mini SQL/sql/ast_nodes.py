# This module represents the nodes of Abstract Syntax Tree (AST)
# These nodes represent the different lexemes of tokens.


class SelectNode:
    """AST Node representing SELECT query."""

    def __init__(self, columns, table, where_clause=None):
        self.columns = columns
        self.table = table
        self.where_clause = where_clause

    def __repr__(self):
        return f"SelectNode(columns={self.columns}, table='{self.table}', where_clause={self.where_clause})"


class AllColumnsNode:
    """AST Node representing '*' (all columns in SELECT)."""

    def __repr__(self):
        return "AllColumnsNode(*)"


class ConditionNode:
    """AST Node representing conditions."""

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        if isinstance(self.right, str):
            right_repr = f"'{self.right}'"
        else:
            right_repr = self.right
        return f"ConditionNode(left={self.left}, operator={self.operator}, right={right_repr})"


class LogicalNode:
    """AST Node representing logical conditions."""

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"LogicalNode(left={self.left}, operator={self.operator}, right={self.right})"
