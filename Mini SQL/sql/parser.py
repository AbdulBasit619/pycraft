# Grammar (Phase 7 - Complete Minimal Parser)
#
# SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE_REF JOIN_CLAUSE* (WHERE EXPRESSION)? ORDER BY ORDER_LIST SEMICOLON?
# CREATE_STATEMENT → CREATE DATABASE IDENTIFIER SEMICOLON?
#                  | CREATE SCHEMA IDENTIFIER SEMICOLON?
#                  | CREATE TABLE TABLE_REF LPAREN COLUMN_LIST RPAREN SEMICOLON?
# INSERT_STATEMENT → INSERT INTO TABLE_REF COLUMN_NAMES? VALUES VALUE_TUPLE ( COMMA VALUE_TUPLE )* SEMICOLON?
# UPDATE_STATEMENT → UPDATE TABLE_REF SET ASSIGNMENT_LIST (WHERE EXPRESSION)? SEMICOLON?
# DELETE_STATEMENT → DELETE FROM TABLE_REF (WHERE EXPRESSION)? SEMICOLON?
# ALTER_STATEMENT → ALTER TABLE TABLE_REF ALTER_ACTION SEMICOLON?
# DROP_STATEMENT → DROP DATABASE IDENTIFIER SEMICOLON?
#                | DROP SCHEMA IDENTIFIER SEMICOLON?
#                | DROP TABLE TABLE_REF SEMICOLON?
#
# COLUMN_LIST → * | SELECT_ITEM ( COMMA SELECT_ITEM )*
# SELECT_ITEM → COLUMN_REF | AGG_FUNC
# COLUMN_DEF_LIST → COLUMN_DEF ( COMMA COLUMN_DEF )*
# COLUMN_DEF → IDENTIFIER DATA_TYPE? (PRIMARY KEY)?
# DATA_TYPE → TYPE_NAME TYPE_PARAM?
# TYPE_PARAM → LPAREN NUMBER RPAREN
#
# ASSIGNMENT_LIST → ASSIGNMENT ( COMMA ASSIGNMENT )*
# ASSIGNMENT → IDENTIFIER OPERATOR VALUE
#
# ALTER_ACTION → ADD COLUMN COLUMN_DEF | DROP COLUMN IDENTIFIER
#
# JOIN_CLAUSE → (INNER)? JOIN TABLE_REF ON CONDITION
#             | LEFT JOIN TABLE_REF ON CONDITION
#             | RIGHT JOIN TABLE_REF ON CONDITION
#
# TABLE_REF → IDENTIFIER (IDENTIFIER)?
#
# COLUMN_REF → IDENTIFIER (DOT IDENTIFIER)?
#
# AGG_FUNC → (COUNT | SUM | AVG | MIN | MAX) LPAREN (STAR | COLUMN_REF) RPAREN
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
# VALUE_TUPLE → LPAREN VALUE_LIST RPAREN
# VALUE_LIST → VALUE (COMMA VALUE)*
# VALUE → NUMBER | STRING
#
# ORDER_LIST → ORDER_ITEM ( COMMA ORDER_ITEM )*
# ORDER_ITEM → IDENTIFIER ( ASC | DESC )

from sql.ast_nodes import (
    SelectNode,
    AllColumnsNode,
    ConditionNode,
    LogicalNode,
    NotNode,
    OrderByNode,
    CreateNode,
    ColumnNode,
    DataTypeNode,
    InsertNode,
    UpdateNode,
    DeleteNode,
    AssignmentNode,
    AlterNode,
    DropNode,
    JoinNode,
    TableRefNode,
    ColumnRefNode,
    AggregateNode,
)
from utils.exceptions import ParserError


# For testing reasons
is_debug = True


def log(msg):
    if is_debug:
        print(msg)


class Parser:
    """Recursive Descent Parser for mini MySQL clone."""

    def __init__(self, token_stream):
        self.tokens = token_stream

    def parse(self):
        """Parse the token stream and return an AST"""
        token_type = self.tokens.current().type

        if token_type == "SELECT":
            return self.parse_select()
        elif token_type == "CREATE":
            return self.parse_create()
        elif token_type == "INSERT":
            return self.parse_insert()
        elif token_type == "UPDATE":
            return self.parse_update()
        elif token_type == "DELETE":
            return self.parse_delete()
        elif token_type == "ALTER":
            return self.parse_alter()
        elif token_type == "DROP":
            return self.parse_drop()
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected a valid SQL statement (SELECT, INSERT, UPDATE, DELETE, ALTER, DROP)",
                position=current.position,
            )

    def parse_select(self):
        """
        Parse the SELECT statement.

        CFG:\n
        SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE JOIN_CLAUSE* (WHERE EXPRESSION)? ORDER BY ORDER_LIST SEMICOLON
        """
        log("[Parser] Parsing SELECT statement")

        ###
        # First token must be SELECT, otherwise raise syntax error. If first token is SELECT, consume it and move forward.
        self._eat("SELECT")

        ###
        # Recursively Descent to parsing column.
        columns = self.parse_columns()

        ###
        # Next token must be FROM, otherwise raise syntax error. # If next token is FROM, consume it and move forward.
        self._eat("FROM")

        ###
        # Recursively Descent to parsing table.
        table = self.parse_table_ref()

        ###
        # Optionally parse JOIN clause.
        joins = []
        while self.tokens.match_any("JOIN", "INNER", "LEFT", "RIGHT"):
            joins.append(self.parse_join())

        ###
        # Optionally parse WHERE clause
        if self.tokens.match("WHERE"):
            where_clause = self.parse_where()
        else:
            where_clause = None

        ###
        # Optionally parse ORDER BY
        if self.tokens.match("ORDER"):
            order_by = self.parse_orderby()
        else:
            order_by = None

        ###
        # Optionally parse SEMICOLON
        self.parse_semicolon()

        return SelectNode(columns, table, joins, where_clause, order_by)

    def parse_create(self):
        """
        Parse the CREATE query.

        CFG:\n
        CREATE_STATEMENT → CREATE DATABASE IDENTIFIER SEMICOLON | CREATE SCHEMA IDENTIFIER SEMICOLON | CREATE TABLE TABLE_NAME LPAREN COLUMN_LIST RPAREN SEMICOLON
        """

        log("[Parser] Parsing CREATE")

        # Next token must be CREATE, otherwise raise syntax error. If token is CREATE, consume it and move forward.
        self._eat("CREATE")

        ###
        # Next token can either be DATABASE, SCHEMA or TABLE

        # Next token must be DATABASE, otherwise raise syntax error.
        if self.tokens.match("DATABASE"):
            # If token is DATABASE, consume it and move forward.
            self.tokens.consume()

            # Next token must be IDENTIFIER. If it is, store it's value, consume it and move forward.
            database_name = self._eat("IDENTIFIER").value

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

            return CreateNode("DATABASE", database_name)

        # Next token must be SCHEMA, otherwise raise syntax error.
        elif self.tokens.match("SCHEMA"):
            # If token is SCHEMA, consume it and move forward.
            self.tokens.consume()

            # Next token must be SCHEMA. If it is, store it's value, consume it and move forward.
            schema_name = self._eat("IDENTIFIER").value

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

            return CreateNode("SCHEMA", schema_name)

        # Next token must be DATABASE, otherwise raise syntax error.
        elif self.tokens.match("TABLE"):
            # If token is TABLE, consume it and move forward.
            self.tokens.consume()

            # Next token must be IDENTIFIER. If it is, store it's value, consume it and move forward.
            table_name = self._eat("IDENTIFIER").value

            # Next token must be (. If it is, store it's value, consume it and move forward.
            self._eat("LPAREN")

            # Recursively descent to parsing columns.
            columns = self.parse_column_def_list()

            # Next token must be ). If it is, store it's value, consume it and move forward.
            self._eat("RPAREN")

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

            return CreateNode("TABLE", table_name, columns)

        # Otherwise raise syntax error.
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected DATABASE, SCHEMA or TABLE",
                position=current.position,
            )

    def parse_insert(self):
        """Parse the INSERT query.

        CFG:\n
        INSERT_STATEMENT → INSERT INTO TABLE_NAME ( COLUMN_NAMES )? VALUES VALUE_TUPLE (COMMA VALUE_TUPLE)* SEMICOLON?
        """

        log("[Parser] Parsing INSERT query.")

        ###
        # Next token must be INSERT, otherwise raise syntax error. If token is INSERT, consume it and move forward.
        self._eat("INSERT")

        ###
        # Next token must be INTO, otherwise raise syntax error. If token is INTO, consume it and move forward.
        self._eat("INTO")

        ###
        # Recursively descent to parsing table.
        table_name = self.parse_table_ref()

        ###
        columns = None
        # Next token must be (, otherwise raise syntax error.
        if self.tokens.match("LPAREN"):
            # If token is (, consume it and move forward.
            self.tokens.consume()

            # Recursively descent to parsing columns.
            columns = self.parse_column_names()
            # Next token must be ), otherwise raise syntax error. If token is ), consume it and move forward.
            self._eat("RPAREN")

        # Next token must be VALUES, otherwise raise syntax error. # If token is VALUES, consume it and move forward.
        self._eat("VALUES")

        ###
        # Recursively descent to parse rows.
        rows = []

        rows.append(self.parse_valuetuple())

        # Additional tuples.
        while self.tokens.match("COMMA"):
            self.tokens.consume()
            rows.append(self.parse_valuetuple())

        ###
        # Optionally parse SEMICOLON
        self.parse_semicolon()

        return InsertNode(table_name, rows, columns)

    def parse_update(self):
        """
        Parse UPDATE query.

        CFG:\n
        UPDATE_STATEMENT → UPDATE TABLE_NAME SET ASSIGNMENT_LIST (WHERE EXPRESSION)? SEMICOLON?
        """

        log("[Parser] Parsing UPDATE")

        ###
        # Next token must be UPDATE, otherwise raise syntax error. If token is UPDATE, consume it and move forward.
        self._eat("UPDATE")

        ###
        # Recursively descent to parsing table.
        table_name = self.parse_table_ref()

        ###
        # Next token must be SET, otherwise raise syntax error. If token is SET, consume it and move forward.
        self._eat("SET")

        ###
        # Recursively descent to parsing assignment list.
        assignment_list = self.parse_assignmentlist()

        ###
        # Optionally parse WHERE clause
        where_clause = None

        # Next token must be WHERE, otherwise raise syntax error.
        if self.tokens.match("WHERE"):
            ### Recursively descent to parsing WHERE clause.
            where_clause = self.parse_where()

        ###
        # Optionally parse SEMICOLON
        self.parse_semicolon()

        return UpdateNode(table_name, assignment_list, where_clause)

    def parse_delete(self):
        """
        Parse DELETE query.

        CFG:\n
        DELETE_STATEMENT → DELETE FROM TABLE_NAME (WHERE EXPRESSION)? SEMICOLON?
        """

        log("[Parser] Parsing DELETE query.")

        ###
        # Next token must be DELETE, otherwise raise syntax error. If token is DELETE, consume it and move forward.
        self._eat("DELETE")

        ###
        # Next token must be FROM, otherwise raise syntax error. If token is FROM, consume it and move forward.
        self._eat("FROM")

        ###
        # Recursively descent to parsing table.
        table_name = self.parse_table_ref()

        ###
        # Optionally parse WHERE clause.
        where_clause = None

        # Next token must be WHERE, otherwise raise syntax error.
        if self.tokens.match("WHERE"):
            # Recursively descent to parsing WHERE ckause.
            where_clause = self.parse_where()

        ###
        # Optionally parse SEMICOLON
        self.parse_semicolon()

        return DeleteNode(table_name, where_clause)

    def parse_alter(self):
        """
        Parse ALTER query.

        CFG:\n
        ALTER_STATEMENT → ALTER TABLE TABLE_NAME ALTER_ACTION SEMICOLON?
        ALTER_ACTION → ADD COLUMN COLUMN_DEF | DROP COLUMN IDENTIFIER
        """

        log("[Parser] Parsing ALTER")

        ###
        # Next token must be ALTER, otherwise raise syntax error. If token is ALTER, consume it and move forward.
        self._eat("ALTER")

        ###
        # Next token must be TABLE, otherwise raise syntax error. If token is TABLE, consume it and move forward.
        self._eat("TABLE")

        ###
        # Recursively descent to parsing table.
        table_name = self.parse_table_ref()

        action = payload = None

        ###
        # Recursively descent to parse ALTER_ACTION.

        # Next token can either be ADD or DROP, otherwise raise syntax error.

        # Next token must be ADD, otherwise raise syntax error.
        if self.tokens.match("ADD"):
            # If token is ADD, consume it and move forward.
            self.tokens.consume()

            # Next token must be COLUMN, otherwise raise syntax error. If token is COLUMN, consume it and move forward.
            self._eat("COLUMN")

            ###
            # Recursively descent to parsing columns.
            column_def = self.parse_column_def()

            action = "ADD"
            payload = column_def

        # Next token must be DROP, otherwise raise syntax error.
        elif self.tokens.match("DROP"):
            # If token is ADD, consume it and move forward.
            self.tokens.consume()

            # Next token must be COLUMN, otherwise raise syntax error. If token is COLUMN, consume it and move forward.
            self._eat("COLUMN")

            ###
            # Parse column name.
            column_name = self.tokens.expect("IDENTIFIER").value

            action = "DROP"
            payload = column_name

        # Otherwise raise syntax error.
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected ADD or DROP",
                position=current.position,
            )

        ###
        # Optionally parse SEMICOLON
        self.parse_semicolon()

        return AlterNode(table_name, action, payload)

    def parse_drop(self):
        """
        Parsing DROP query.

        CFG:\n
        DROP_STATEMENT → DROP DATABASE IDENTIFIER SEMICOLON? | DROP SCHEMA IDENTIFIER SEMICOLON? | DROP TABLE TABLE_NAME SEMICOLON?
        """

        log("[Parser] Parsing DROP query.")

        ###
        # Next token must be DROP, otherwise raise syntax error. If token is DROP, consume it and move forward.
        self._eat("DROP")

        object_type = object_name = None

        ###
        # Next token can either be DATABASE, SCHEMA or TABLE.

        # Next token must be DATABASE, otherwise raise syntax error.
        if self.tokens.match("DATABASE"):
            # If token is DATABASE, consume it and move forward.
            self.tokens.consume()

            # Parse object type and name
            object_type = "DATABASE"
            object_name = self.tokens.expect("IDENTIFIER").value

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

        # Next token must be SCHEMA, otherwise raise syntax error.
        elif self.tokens.match("SCHEMA"):
            # If token is SCHEMA, consume it and move forward.
            self.tokens.consume()

            # Parse object type and name
            object_type = "SCHEMA"
            object_name = self.tokens.expect("IDENTIFIER").value

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

        # Next token must be TABLE, otherwise raise syntax error.
        elif self.tokens.match("TABLE"):
            # If token is TABLE, consume it and move forward.
            self.tokens.consume()

            # Parse object type and name
            object_type = "TABLE"
            object_name = self.tokens.expect("IDENTIFIER").value

            ###
            # Optionally parse SEMICOLON

            self.parse_semicolon()

        # Otherwise raise syntax error.
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected DATABASE, SCHEMA or TABLE",
                position=current.position,
            )

        return DropNode(object_type, object_name)

    def parse_columns(self):
        """
        Parse the table column.

        CFG:
        COLUMN_LIST → * | SELECT_ITEM ( COMMA SELECT_ITEM )*
        """
        log("[Parser] Parsing COLUMN_LIST")

        # Next token can either be * or select item.

        # Next token must be *, otherwise raise syntax error.
        if self.tokens.match("STAR"):
            # If token is *, consume it and move forward.
            self.tokens.consume()

            return AllColumnsNode()

        ###
        # Recursively descent to parsing columns.
        columns = []

        columns.append(self.parse_select_item())

        # Next token must be COMMA, otherwise raise syntax error.
        while self.tokens.match("COMMA"):
            # If token is COMMA, consume it and move forward.
            self.tokens.consume()
            columns.append(self.parse_select_item())

        return columns

    def parse_column_names(self):
        """
        Parse column names.

        CFG:\n
        COLUMN_NAMES → IDENTIFIER (COMMA IDENTIFIER)*
        """

        log("[Parser] Parsing COLUMN_NAMES")

        columns = []

        # Parse column name.  Consume current token and move forward.
        column_name = self._eat("IDENTIFIER").value

        columns.append(column_name)

        # Next token must be COMMA, otherwise raise syntax error.
        while self.tokens.match("COMMA"):
            # If next token is COMMA, consume it and move forward.
            self.tokens.consume()

            # Parse column name. Consume it and move forward.
            column_name = self._eat("IDENTIFIER").value

            columns.append(column_name)

        return columns

    def parse_select_item(self):
        """
        SELECT_ITEM → COLUMN_REF | AGG_FUNC
        """

        AGG_FUNCS = {"COUNT", "SUM", "AVG", "MIN", "MAX"}

        if self.tokens.current().type in AGG_FUNCS:
            return self.parse_aggregate_function()

        return self.parse_column_ref()

    def parse_column_def_list(self):
        """
        Parse column definitions list.

        CFG:\n
        COLUMN_DEF_LIST → COLUMN_DEF (COMMA COLUMN_DEF)*
        """

        log("[Parser] Parsing COLUMN_DEF_LIST")

        columns = []

        # First column is mandatory
        columns.append(self.parse_column_def())

        # Parse the next columns if separated by COMMAs.
        while self.tokens.match("COMMA"):
            # While the current token is COMMA,
            # consume it and advance to the next COLUMN_DEF
            # until there is no COMMA
            self.tokens.consume()
            columns.append(self.parse_column_def())

        return columns

    def parse_column_def(self):
        """
        Parse column definitions.

        CFG:\n
        COLUMN_DEF → IDENTIFIER DATA_TYPE (PRIMARY_KEY)?
        """

        log("[Parser] Parsing COLUMN_DEF")

        # Token must be an identifier, otherwise raise syntax error. If token is IDENTIFIER, consume it and move forward.
        column_name = self._eat("IDENTIFIER").value

        # Parse data type.
        data_type = None
        if self.tokens.match("IDENTIFIER"):
            data_type = self.parse_datatype()

        ###
        # Optionally parse PRIMARY KEY flag.

        # flag if primary key or not.
        is_primary = False

        # Next token must be PRIMARY, otherwise raise syntax error.
        if self.tokens.match("PRIMARY"):
            # If token is PRIMARY, consume it and move forward.
            self.tokens.consume()

            # Next token must be KEY, otherwise raise syntax error. If token is KEY, consume it and move forward.
            self._eat("KEY")

            is_primary = True

        return ColumnNode(column_name, data_type, is_primary)

    def parse_datatype(self):
        """
        Parse DATATYPE.

        CFG:\n
        DATA_TYPE → IDENTIFIER ( TYPE_PARAM )?
        """

        log("[Parser] Parsing DATA_TYPE")

        data_type = self.tokens.expect("IDENTIFIER").value
        self.tokens.consume()

        type_param = None
        if self.tokens.match("LPAREN"):
            type_param = self.parse_typeparam()

        return DataTypeNode(data_type, type_param)

    def parse_typeparam(self):
        """
        Parse TYPE_PARAM.

        CFG:\n
        TYPE_PARAM → LPAREN NUMBER RPAREN
        """

        log("[Parser] Parsing TYPE_PARAM")

        # Next token must be (, otherwise raise syntax error. If token is (, consume it and move forward.
        self._eat("LPAREN")

        # Parse NUMBER
        size = int(self._eat("NUMBER").value)

        # Next token must be ), otherwise raise syntax error. If token is ), consume it and move forward.
        self._eat("RPAREN")

        return size

    def parse_table_ref(self):
        """
        Parse TABLE_REF.

        CFG:\n
        TABLE_REF → IDENTIFIER (IDENTIFIER)?
        """
        log("[Parser] Parsing TABLE_REF")

        ###
        # Parse table name.  Consume the current token and move forward.
        table_name = self._eat("IDENTIFIER").value

        ###
        # Parse alias
        alias = None

        # Next token must be IDENTIFIER, otherwise raise syntax error.
        if self.tokens.match("IDENTIFIER"):
            alias = self._eat("IDENTIFIER").value

        return TableRefNode(table_name, alias)

    def parse_where(self):
        """
        Parse the WHERE clause.
        """

        log("[Parser] Parsing WHERE conditions.")

        # Token must be WHERE, otherwise raise syntax error. If next token is WHERE, consume it and move forward.
        self._eat("WHERE")

        return self.parse_expression()

    def parse_expression(self):
        """
        Parse the expression after WHERE statement.

        CFG:\n
        EXPRESSION → TERM ( (OR) TERM )*
        """

        log("[Parser] Parsing EXPRESSION")

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

        log("[Parser] Parsing TERM")

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
        FACTOR → NOT FACTOR | CONDITION | LPAREN EXPRESSION RPAREN
        """

        log("[Parser] Parsing FACTOR")

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

            # Token must be ), otherwise raise syntax error. If token is ), consume it and move forward.
            self._eat("RPAREN")

            # Return EXPRESSION
            return expr

        # If token is not (, then parse CONDITION and return it.
        else:
            return self.parse_condition()

    def parse_condition(self):
        """
        Parse the conditions after WHERE statement.

        CFG:\n
        CONDITION → COLUMN_REF OPERATOR (VALUE | COLUMN_REF)
        """
        log("[Parser] Parsing CONDITION")

        ###
        # Parse COLUMN_REF.
        column_name = self.parse_column_ref()

        ###
        # Next token must be OPERATOR, otherwise raise syntax error.  If token is an OPERATOR, consume it and move forward.
        operator = self._eat("OPERATOR").value

        ###
        # Next token can either be IDENTIFIER or VALUE, otherwise raise syntax error.

        # Token must be IDENTIFIER
        if self.tokens.match("IDENTIFIER"):
            value = self.parse_column_ref()

        # Token must be VALUE
        elif self.tokens.match("NUMBER") or self.tokens.match("STRING"):
            value = self.parse_value()

        # Otherwise raise, syntax error.
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected column name or literal value",
                position=current.position,
            )

        return ConditionNode(column_name, operator, value)

    def parse_column_ref(self):
        """
        Parse COLUMN_REF.

        CFG:\n
        COLUMN_REF → IDENTIFIER (DOT IDENTIFIER)?
        """

        log("[Parser] Parsing COLUMN_REF")

        # Parse left. # Consume current token and move forward.
        left = self._eat("IDENTIFIER").value

        ###
        # Optionally parse (DOT IDENTIFIER)?

        # Next token must be DOT, otherwise raise syntax error.
        if self.tokens.match("DOT"):
            # If next token is DOT, consume it and move forward.
            self.tokens.consume()

            # Parse right. Consume current token and move forward.
            right = self._eat("IDENTIFIER").value

            return ColumnRefNode(left, right)

        return ColumnRefNode(left)

    def parse_valuetuple(self):
        """
        Parse VALUE_TUPLE.

        CFG:\n
        VALUE_TUPLE → LPAREN VALUE_LIST RPAREN
        """

        log("[Parser] Parsing VALUE_TUPLE")

        # Next token must be (, otherwise raise syntax error. If next token is (, consume it and move forward.
        self._eat("LPAREN")

        # Recursively descent to parse value list.
        row = self.parse_valuelist()

        # Next token must be ), otherwise raise syntax error. If next token is ), consume it and move forward.
        self._eat("RPAREN")

        return row

    def parse_valuelist(self):
        """
        Parse value list.

        CFG:\n
        VALUE_LIST → VALUE (COMMA VALUE)*
        """

        log("[Parser] Parsing VALUE_LIST")

        value_list = []

        value_list.append(self.parse_value())

        while self.tokens.match("COMMA"):
            self.tokens.consume()
            value_list.append(self.parse_value())

        return tuple(value_list)

    def parse_value(self):
        """
        Parse the condition VALUEs.

        CFG:\n
        VALUE → NUMBER | STRING
        """

        log("[Parser] Parsing VALUEs")

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

        # Otherwise raise syntax error.
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected numeric or string value",
                position=current.position,
            )

    def parse_assignmentlist(self):
        """
        Parse ASSIGNMENT_LIST.

        CFG:\n
        ASSIGNMENT_LIST → ASSIGNMENT ( COMMA ASSIGNMENT )*
        """

        log("[Parser] Parsing ASSIGNMENT_LIST")

        assignments = []

        assignments.append(self.parse_assignment())

        while self.tokens.match("COMMA"):
            self.tokens.consume()
            assignments.append(self.parse_assignment())

        return assignments

    def parse_assignment(self):
        """
        Parse ASSIGNMENT.

        CFG:\n
        ASSIGNMENT → IDENTIFIER OPERATOR VALUE
        """

        log("[Parser] Parsing ASSIGNMENT")

        # Parse column name. Consume current token and move forward.
        column = self._eat("IDENTIFIER").value

        # Parse operator. # If operator is '=', consume it and move forward.
        operator = self._eat("OPERATOR")

        ###
        # Only '=' operator is allowed in assignment, otherwise raise syntax error.
        if operator.value != "=":
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected '=' in assignment",
                position=current.position,
            )

        # Parse value.
        value = self.parse_value()

        return AssignmentNode(column, value)

    def parse_join(self):
        """
        Parse JOIN clause.

        CFG:\n
        JOIN_CLAUSE → (INNER)? JOIN TABLE_NAME ON CONDITION | LEFT JOIN TABLE_NAME ON CONDITION | RIGHT JOIN TABLE_NAME ON CONDITION
        """

        log("[Parser] Parsing JOIN")

        ### Starting token can either be INNER, LEFT or RIGHT, otherwise raise syntax error.
        join_type = "INNER"
        if self.tokens.match("INNER"):
            self.tokens.consume()
            self._eat("JOIN")
        elif self.tokens.match("LEFT"):
            self.tokens.consume()
            self._eat("JOIN")
            join_type = "LEFT"
        elif self.tokens.match("RIGHT"):
            self.tokens.consume()
            join_type = "RIGHT"
            self._eat("JOIN")
        elif self.tokens.match("JOIN"):
            self.tokens.consume()
        else:
            current = self.tokens.current()
            raise ParserError(
                f"Syntax error near '{current.value}': expected INNER, JOIN LEFT or RIGHT",
                position=current.position,
            )

        ###
        # Recursively descent to parsing table.
        table_name = self.parse_table_ref()

        ###
        # Next token must be ON, otherwise raise syntax error. If token is ON, consume it and move forward.
        self._eat("ON")

        # Recursively descent to parsing cod=ndition.
        condition = self.parse_condition()

        return JoinNode(join_type, table_name, condition)

    def parse_aggregate_function(self):
        """
        Parse AGG_FUNC.

        CFG:\n
        AGG_FUNC → (COUNT | SUM | AVG | MIN | MAX) LPAREN (STAR | COLUMN_REF) RPAREN
        """

        log("[Parser] Parsing AGG_FUNC")

        # Determine function type.
        func = self.tokens.consume().type

        # Next token must be (, otherwise raise syntax error. If token is (, consume it and move forward.
        self._eat("LPAREN")

        # Argument: * or column
        if self.tokens.match("STAR"):
            self.tokens.consume()
            argument = "*"
        else:
            argument = self.parse_column_ref()

        # Next token must be ), otherwise raise syntax error. If token is ), consume it and move forward.
        self._eat("RPAREN")

        return AggregateNode(func, argument)

    def parse_orderby(self):
        """
        Parse ORDER BY clause.

        CFG:
        ORDER_BY → ORDER BY ORDER_LIST
        ORDER_LIST → ORDER_ITEM (COMMA ORDER_ITEM)*
        ORDER_ITEM → IDENTIFIER (ASC | DESC)
        """

        log("[Parser] Parsing ORDER BY")

        ###
        # Next token must be ORDER, otherwise raise syntax error. If token is ORDER, consume it and move forward.
        self._eat("ORDER")

        ###
        # Next token must be BY, otherwise raise syntax error. If token is BY, consume it and move forward.
        self._eat("BY")

        ###
        # Parse items
        items = []

        # First item (mandatory)
        column_name = self._eat("IDENTIFIER").value

        # Determine sorting direction
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

            column_name = self._eat("IDENTIFIER").value

            direction = "ASC"
            if self.tokens.match("ASC"):
                self.tokens.consume()
            elif self.tokens.match("DESC"):
                self.tokens.consume()
                direction = "DESC"

            items.append((column_name, direction))

        return OrderByNode(items)

    def parse_semicolon(self):
        """
        Parse the SEMICOLON (optional).
        """
        if self.tokens.match("SEMICOLON"):
            self.tokens.consume()

    def _eat(self, token_type):
        """
        Helper for expect and consume code.
        """
        token = self.tokens.expect(token_type)
        self.tokens.consume()
        return token
