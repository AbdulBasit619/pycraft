# Create Row class


class Row:
    """A class to create rows and manage data."""

    def __init__(self, data):
        """Initialize a row with data."""
        self.data = data

    def get(self, column):
        """Get the value of a specific column."""
        return self.data[column]
