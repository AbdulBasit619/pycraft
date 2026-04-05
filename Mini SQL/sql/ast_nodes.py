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


class CreateNode:
    """AST Node representing all CREATE query."""

    def __init__(self, object_type, name, definition=None):
        self.object_type = object_type
        self.name = name
        self.definition = definition

    def __repr__(self):
        if self.definition is not None:
            return f"CreateNode(type={self.object_type}, name='{self.name}', definition={self.definition})"
        return f"CreateNode(type={self.object_type}, name='{self.name}')"


class ColumnNode:
    """AST Node representing column name, with optional data type and type parameters."""

    def __init__(self, name, data_type, is_primary=False):
        self.name = name
        self.data_type = data_type
        self.is_primary = is_primary

    def __repr__(self):
        return f"ColumnNode(name={self.name}, data_type={self.data_type}, is_primary={self.is_primary})"


class DataTypeNode:
    """AST Node representing a data type."""

    def __init__(self, name, param=None):
        self.name = name
        self.param = param

    def __repr__(self):
        return f"DataTypeNode(name={self.name}, param={self.param})"


class InsertNode:
    """AST Node representing INSERT query."""

    def __init__(
        self,
        table_name,
        value_tuples,
        columns=None,
    ):
        self.table_name = table_name
        self.columns = columns
        self.value_tuples = value_tuples

    def __repr__(self):
        if self.columns:
            return f"InsertNode(table_name={self.table_name}, value_tuples={self.value_tuples}, columns={self.columns})"
        return (
            f"InsertNode(table_name={self.table_name}, value_list={self.value_tuples})"
        )


class UpdateNode:
    """AST Node representing UPDATE query."""

    def __init__(self, table, assignments, where_clause=None):
        self.table = table
        self.assignments = assignments
        self.where_clause = where_clause

    def __repr__(self):
        if self.where_clause:
            return f"UpdateNode(table={self.table}, assignments={self.assignments}, where_clause={self.where_clause})"
        return f"UpdateNode(table={self.table}, assignments={self.assignments})"


class DeleteNode:
    """AST Node representing DELETE query."""

    def __init__(self, table, where_clause=None):
        self.table = table
        self.where_clause = where_clause

    def __repr__(self):
        if self.where_clause:
            return f"DeleteNode(table={self.table}, where_clause={self.where_clause})"
        return f"DeleteNode(table={self.table})"
