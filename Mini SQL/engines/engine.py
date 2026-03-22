from sql.lexer import Lexer

# A class to build the engine layer,
# responsible for interacting with database
# using SQL strings instead of Python methods
# Conceptual Architecture:
# User -> Engine -> Database -> Table -> Row


class Engine:
    """Engine layer for executing SQL strings on a database."""

    def __init__(self, database):
        """Initialize the engine with a database."""
        self.database = database

    def execute(self, sql):
        """Execute an SQL command, after normalization, tokenization and parsing."""
        # This is a placeholder for SQL parsing and execution logic.
        # In a real implementation, this method would need to parse the SQL string,
        # determine the command type (SELECT, INSERT, UPDATE, DELETE, etc.),
        # and then call the appropriate methods on the database and tables.
        print(f"Executing SQL: {sql}")

        lexer = Lexer()

        # Tokenize the Normalized SQL Query
        tokens = lexer.tokenize(sql)

        # Determine the query type
        query_type = lexer.determine_query_type(tokens)
        print(query_type)
