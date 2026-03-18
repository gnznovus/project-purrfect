class TerminalInput:
    """Handles input from the command-line interface (CLI)."""

    def get_input(self):
        """Gets user input from the terminal."""
        return input("You: ").strip()
