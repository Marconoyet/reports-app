class DatabaseError(Exception):
    """Custom exception for database errors."""

    def __init__(self, message="Database error occurred"):
        self.message = message
        super().__init__(self.message)
