from .table import Table

# Create Database Class


class Database:
    """A class to create database, store and manage tables."""

    def __init__(self):
        """Initialize a tables dictionary."""
        self.tables = {}

    def create_table(self, name, columns):
        """Add table to tables dictionary."""
        self.tables[name] = Table(name, columns)

    def drop_table(self, name):
        """Remove table from tables dictionary."""
        del self.tables[name]

    def get_table(self, name):
        """Return a table from tables dictionary."""
        return self.tables[name]
