# Create table class
# Responsible for:
# - Schema
# - Rows
# - Insert/Update/Delete operations


class Table:
    """A class to create tables and manage rows and columns."""

    def __init__(self, name, columns):
        """Initialize a table with a name and columns."""
        self.name = name
        self.columns = columns  # list of column names
        self.rows = []  # list of dictionaries where each dictionary represents a row

    def insert(self, row):
        """Insert a row into the table."""
        self.rows.append(row)

    def select(self, columns=None, condition=None):
        """Select rows from the table based on the given criteria."""
        result = []
        for row in self.rows:
            if condition is None or condition(row):
                if columns:
                    result.append({col: row[col] for col in columns})
                else:
                    result.append(row.copy())
        return result

    def update(self, updates, condition=None):
        """Update rows in the table based on the given criteria."""
        for row in self.rows:
            if condition is None or condition(row):
                for col, val in updates.items():
                    row[col] = val

    def delete(self, condition=None):
        """Delete rows from the table based on the given criteria."""
        self.rows = [row for row in self.rows if not (condition and condition(row))]

    def print_table(self):
        """Print the table in a neatly formatted, tabular style with dynamic spacing."""
        if not self.rows:
            print("Table is empty.")
            return

        # Calculate column widths
        widths = {}
        for col in self.columns:
            widths[col] = max(
                len(col), max(len(str(row.get(col, ""))) for row in self.rows)
            )

        # Print header
        header = " | ".join(col.ljust(widths[col]) for col in self.columns)
        print(header)
        print("-" * len(header))

        # Print rows
        for row in self.rows:
            row_str = " | ".join(
                str(row.get(col, "")).ljust(widths[col]) for col in self.columns
            )
            print(row_str)
