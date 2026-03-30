from sql.lexer import Lexer
from sql.token_stream import TokenStream

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
        print("=== Raw SQL ===")
        print(sql)

        lexer = Lexer()

        # Tokenize the Normalized SQL Query
        tokens = lexer.tokenize(sql)
        print("=== Tokens ===")
        for t in tokens:
            print(t)

        # Convert to token stream
        token_stream = TokenStream(tokens)
        # print(token_stream.current())
        # print(token_stream.expect("SELECT"))
        # print(token_stream.expect("SELECT"))
        # print(token_stream.peek(5))
        # print(token_stream.at_end())
        # print(token_stream.consume())
        # token_stream.advance()
        # print(token_stream.current())
        # token_stream.reset()
        # print(token_stream.current())

        # # Determine the query type
        # query_type = lexer.determine_query_type(tokens)
        # print(query_type)
