# Grammar (Phase 7 - improved SELECT)
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
# COLUMN_LIST → * | COLUMN_REF ( COMMA COLUMN_REF )*
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
    AlterNode,
    DropNode,
    JoinNode,
    ColumnRefNode,
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
        elif self.tokens.match("CREATE"):
            return self.parse_create()
        elif self.tokens.match("INSERT"):
            return self.parse_insert()
        elif self.tokens.match("UPDATE"):
            return self.parse_update()
        elif self.tokens.match("DELETE"):
            return self.parse_delete()
        elif self.tokens.match("ALTER"):
            return self.parse_alter()
        elif self.tokens.match("DROP"):
            return self.parse_drop()

    def parse_select(self):
        """
        Parse the SELECT statement.

        CFG:\n
        SELECT_STATEMENT → SELECT COLUMN_LIST FROM TABLE JOIN_CLAUSE* (WHERE EXPRESSION)? ORDER BY ORDER_LIST SEMICOLON
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
        table = self.parse_table_ref()

        ###
        # Optionally parse JOIN clause.
        joins = []
        while (
            self.tokens.match("JOIN")
            or self.tokens.match("INNER")
            or self.tokens.match("LEFT")
            or self.tokens.match("RIGHT")
        ):
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

        print("[Parser] Parsing CREATE")

        # Next token must be CREATE, otherwise raise syntax error.
        self.tokens.expect("CREATE")
        # If token is CREATE, consume it and move forward.
        self.tokens.consume()

        ###
        # Next token can either be DATABASE, SCHEMA or TABLE

        # Next token must be DATABASE, otherwise raise syntax error.
        if self.tokens.match("DATABASE"):

            # If token is DATABASE, consume it and move forward.
            self.tokens.consume()

            # Next token must be IDENTIFIER. If it is, store it's value, consume it and move forward.
            database_name = self.tokens.expect("IDENTIFIER").value
            self.tokens.consume()

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

            return CreateNode("DATABASE", database_name)

        # Next token must be SCHEMA, otherwise raise syntax error.
        elif self.tokens.match("SCHEMA"):

            # If token is SCHEMA, consume it and move forward.
            self.tokens.consume()

            # Next token must be SCHEMA. If it is, store it's value, consume it and move forward.
            schema_name = self.tokens.expect("IDENTIFIER").value
            self.tokens.consume()

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

            return CreateNode("SCHEMA", schema_name)

        # Next token must be DATABASE, otherwise raise syntax error.
        elif self.tokens.match("TABLE"):
            self.tokens.consume()

            table_name = self.tokens.expect("IDENTIFIER").value
            self.tokens.consume()

            self.tokens.expect("LPAREN")
            self.tokens.consume()

            columns = self.parse_column_def_list()

            self.tokens.expect("RPAREN")
            self.tokens.consume()

            ###
            # Optionally parse SEMICOLON
            self.parse_semicolon()

            return CreateNode("TABLE", table_name, columns)

        else:
            raise ParserError("Expected DATABASE, SCHEMA or TABLE")

    def parse_insert(self):
        """Parse the INSERT query.

        CFG:\n
        INSERT_STATEMENT → INSERT INTO TABLE_NAME ( COLUMN_NAMES )? VALUES VALUE_TUPLE (COMMA VALUE_TUPLE)* SEMICOLON?
        """

        print("[Parser] Parsing INSERT query.")

        self.tokens.expect("INSERT")
        self.tokens.consume()

        self.tokens.expect("INTO")
        self.tokens.consume()

        table_name = self.parse_table_ref()

        columns = None
        if self.tokens.match("LPAREN"):
            self.tokens.consume()
            columns = self.parse_column_names()

            self.tokens.expect("RPAREN")
            self.tokens.consume()

        self.tokens.expect("VALUES")
        self.tokens.consume()

        rows = []

        rows.append(self.parse_valuetuple())

        # Additional tuples.
        while self.tokens.match("COMMA"):
            self.tokens.consume()
            rows.append(self.parse_valuetuple())

        self.parse_semicolon()

        return InsertNode(table_name, rows, columns)

    def parse_update(self):
        """
        Parse UPDATE query.

        CFG:\n
        UPDATE_STATEMENT → UPDATE TABLE_NAME SET ASSIGNMENT_LIST (WHERE EXPRESSION)? SEMICOLON?
        """

        print("[Parser] Parsing UPDATE")

        self.tokens.expect("UPDATE")
        self.tokens.consume()

        table_name = self.parse_table_ref()

        self.tokens.expect("SET")
        self.tokens.consume()

        assignment_list = self.parse_assignmentlist()

        where_clause = None
        if self.tokens.match("WHERE"):
            where_clause = self.parse_where()

        if self.tokens.match("SEMICOLON"):
            self.parse_semicolon()

        return UpdateNode(table_name, assignment_list, where_clause)

    def parse_delete(self):
        """
        Parse DELETE query.

        CFG:\n
        DELETE_STATEMENT → DELETE FROM TABLE_NAME (WHERE EXPRESSION)? SEMICOLON?
        """

        print("[Parser] Parsing DELETE query.")

        self.tokens.expect("DELETE")
        self.tokens.consume()

        self.tokens.expect("FROM")
        self.tokens.consume()

        table_name = self.parse_table_ref()

        where_clause = None
        if self.tokens.match("WHERE"):
            where_clause = self.parse_where()

        if self.tokens.match("SEMICOLON"):
            self.parse_semicolon()

        return DeleteNode(table_name, where_clause)

    def parse_alter(self):
        """
        Parse ALTER query.

        CFG:\n
        ALTER_STATEMENT → ALTER TABLE TABLE_NAME ALTER_ACTION SEMICOLON?
        ALTER_ACTION → ADD COLUMN COLUMN_DEF | DROP COLUMN IDENTIFIER
        """

        print("[Parser] Parsing ALTER")

        self.tokens.expect("ALTER")
        self.tokens.consume()

        self.tokens.expect("TABLE")
        self.tokens.consume()

        table_name = self.parse_table_ref()

        action = payload = None

        if self.tokens.match("ADD"):
            self.tokens.consume()

            self.tokens.expect("COLUMN")
            self.tokens.consume()

            column_def = self.parse_column_def()

            action = "ADD"
            payload = column_def

        elif self.tokens.match("DROP"):
            self.tokens.consume()

            self.tokens.expect("COLUMN")
            self.tokens.consume()

            column_name = self.tokens.expect("IDENTIFIER").value

            action = "DROP"
            payload = column_name

        else:
            current = self.tokens.current()
            raise ParserError(
                f"Expected ADD or DROP, but found {current.value}",
                position=current.position,
            )

        if self.tokens.match("SEMICOLON"):
            self.parse_semicolon()

        return AlterNode(table_name, action, payload)

    def parse_drop(self):
        """
        Parsing DROP query.

        CFG:\n
        DROP_STATEMENT → DROP DATABASE IDENTIFIER SEMICOLON?
                       | DROP SCHEMA IDENTIFIER SEMICOLON?
                       | DROP TABLE TABLE_NAME SEMICOLON?
        """

        print("[Parser] Parsing DROP query.")

        self.tokens.expect("DROP")
        self.tokens.consume()

        object_type = object_name = None

        if self.tokens.match("DATABASE"):
            self.tokens.consume()

            object_type = "DATABASE"
            object_name = self.tokens.expect("IDENTIFIER").value

            if self.tokens.match("SEMICOLON"):
                self.parse_semicolon()

        elif self.tokens.match("SCHEMA"):
            self.tokens.consume()

            object_type = "SCHEMA"
            object_name = self.tokens.expect("IDENTIFIER").value

            if self.tokens.match("SEMICOLON"):
                self.parse_semicolon()

        elif self.tokens.match("TABLE"):
            self.tokens.consume()

            object_type = "TABLE"
            object_name = self.tokens.expect("IDENTIFIER").value

            if self.tokens.match("SEMICOLON"):
                self.parse_semicolon()

        else:
            pass

        return DropNode(object_type, object_name)

    def parse_columns(self):
        """
        Parse the table column.

        CFG:
        COLUMN_LIST → * | COLUMN_REF ( COMMA COLUMN_REF )*
        """
        print("[Parser] Parsing COLUMN_LIST")

        if self.tokens.match("STAR"):
            self.tokens.consume()
            return AllColumnsNode()

        columns = []

        columns.append(self.parse_column_ref())

        while self.tokens.match("COMMA"):
            self.tokens.consume()
            columns.append(self.parse_column_ref())

        return columns

    def parse_column_names(self):
        """
        Parse column names.

        CFG:\n
        COLUMN_NAMES → IDENTIFIER (COMMA IDENTIFIER)*
        """

        print("[Parser] Parsing COLUMN_NAMES")
        columns = []

        column_name = self.tokens.expect("IDENTIFIER").value
        self.tokens.consume()
        columns.append(column_name)

        while self.tokens.match("COMMA"):
            self.tokens.consume()
            column_name = self.tokens.expect("IDENTIFIER").value
            self.tokens.consume()
            columns.append(column_name)

        return columns

    def parse_column_def_list(self):
        """
        Parse column definitions list.

        CFG:\n
        COLUMN_DEF_LIST → COLUMN_DEF (COMMA COLUMN_DEF)*
        """

        print("[Parser] Parsing COLUMN_DEF_LIST")

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

        print("[Parser] Parsing COLUMN_DEF")

        # Token must be an identifier, otherwise raise syntax error.
        column_name = self.tokens.expect("IDENTIFIER").value
        self.tokens.consume()

        data_type = None
        if self.tokens.match(
            "IDENTIFIER"
        ) and self.tokens.current().value.upper() not in ("PRIMARY",):
            data_type = self.parse_datatype()

        is_primary = False
        if self.tokens.match("PRIMARY"):
            self.tokens.consume()

            self.tokens.expect("KEY")
            self.tokens.consume()

            is_primary = True

        return ColumnNode(column_name, data_type, is_primary)

    def parse_datatype(self):
        """
        Parse DATATYPE.

        CFG:\n
        DATA_TYPE → IDENTIFIER ( TYPE_PARAM )?
        """

        print("[Parser] Parsing DATA_TYPE")

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

        print("[Parser] Parsing TYPE_PARAM")

        self.tokens.expect("LPAREN")
        self.tokens.consume()

        size = int(self.tokens.expect("NUMBER").value)
        self.tokens.consume()

        self.tokens.expect("RPAREN")
        self.tokens.consume()

        return size

    def parse_table_ref(self):
        """
        Parse TABLE_REF.

        CFG:\n
        TABLE_REF → IDENTIFIER (IDENTIFIER)?
        """
        print("[Parser] Parsing TABLE_REF")

        # Token must be an identifier, otherwise raise syntax error.
        table_name = self.tokens.expect("IDENTIFIER").value

        # If token is an identifier, consume it and move forward.
        self.tokens.consume()

        alias = None

        if self.tokens.match("IDENTIFIER"):
            alias = self.tokens.consume().value

        return (table_name, alias)

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
        CONDITION → COLUMN_REF OPERATOR (VALUE | COLUMN_REF)
        """
        print("[Parser] Parsing CONDITION")

        ###
        # Parse COLUMN_REF.
        column_name = self.parse_column_ref()

        ###
        # Next token must be OPERATOR, otherwise raise syntax error.
        operator = self.tokens.expect("OPERATOR").value

        # If token is an OPERATOR, consume it and move forward.
        self.tokens.consume()

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
                f"Expected COLUMN_REF or VALUE, but found {current.type}",
                position=current.position,
            )

        return ConditionNode(column_name, operator, value)

    def parse_column_ref(self):
        """
        Parse COLUMN_REF.

        CFG:\n
        COLUMN_REF → IDENTIFIER (DOT IDENTIFIER)?
        """

        print("[Parser] Parsing COLUMN_REF")

        left = self.tokens.expect("IDENTIFIER").value
        self.tokens.consume()

        if self.tokens.match("DOT"):
            self.tokens.consume()

            right = self.tokens.expect("IDENTIFIER").value
            self.tokens.consume()

            return ColumnRefNode(left, right)

        return ColumnRefNode(left)

    def parse_valuetuple(self):
        """
        Parse VALUE_TUPLE.

        CFG:\n
        VALUE_TUPLE → LPAREN VALUE_LIST RPAREN
        """

        print("[Parser] Parsing VALUE_TUPLE")

        self.tokens.expect("LPAREN")
        self.tokens.consume()

        row = self.parse_valuelist()

        self.tokens.expect("RPAREN")
        self.tokens.consume()

        return row

    def parse_valuelist(self):
        """
        Parse value list.

        CFG:\n
        VALUE_LIST → VALUE (COMMA VALUE)*
        """

        print("[Parser] Parsing VALUE_LIST")

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

        print("[Parser] Parsing VALUEs")

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

    def parse_assignmentlist(self):
        """
        Parse ASSIGNMENT_LIST.

        CFG:\n
        ASSIGNMENT_LIST → ASSIGNMENT ( COMMA ASSIGNMENT )*
        """

        print("[Parser] Parsing ASSIGNMENT_LIST")

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

        print("[Parser] Parsing ASSIGNMENT")

        column = self.tokens.expect("IDENTIFIER").value
        self.tokens.consume()

        operator = self.tokens.expect("OPERATOR").value

        if operator != "=":
            pass
        self.tokens.consume()

        value = self.parse_value()

        return (column, value)

    def parse_join(self):
        """
        Parse JOIN clause.

        CFG:\n
        JOIN_CLAUSE → (INNER)? JOIN TABLE_NAME ON CONDITION
                    | LEFT JOIN TABLE_NAME ON CONDITION
                    | RIGHT JOIN TABLE_NAME ON CONDITION
        """

        print("[Parser] Parsing JOIN")

        join_type = "INNER"
        if self.tokens.match("INNER"):
            self.tokens.consume()
            join_type = "INNER"
        elif self.tokens.match("LEFT"):
            self.tokens.consume()
            join_type = "LEFT"
        elif self.tokens.match("RIGHT"):
            self.tokens.consume()
            join_type = "RIGHT"

        self.tokens.expect("JOIN")
        self.tokens.consume()

        table_name = self.parse_table_ref()

        self.tokens.expect("ON")
        self.tokens.consume()

        condition = self.parse_condition()

        return JoinNode(join_type, table_name, condition)

    def parse_orderby(self):
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

    def parse_semicolon(self):
        """
        Parse the SEMICOLON (optional).
        """
        if self.tokens.match("SEMICOLON"):
            self.tokens.consume()
