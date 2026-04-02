# This module represents the nodes of Abstract Syntax Tree (AST)
# These nodes represent the different lexemes of tokens.


class SelectNode:
    """AST Node representing SELECT query."""

    def __init__(self, columns, table, where_clause=None, order_by=None):
        self.columns = columns
        self.table = table
        self.where_clause = where_clause
        self.order_by = order_by

    def __repr__(self):
        return f"SelectNode(columns={self.columns}, table='{self.table}', where_clause={self.where_clause}, order_by={self.order_by})"


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


class NotNode:
    """AST Node representing negation."""

    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"NotNode({self.child})"


class OrderByNode:
    """AST Node representing ORDER BY clause."""

    def __init__(self, items):
        self.items = items

    def __repr__(self):
        parts = [f"{col}: {dir}" for col, dir in self.items]
        return f"OrderByNode({', '.join(parts)})"
