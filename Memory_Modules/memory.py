class MemoryBuffer:
    def __init__(self, buffer_size=5):
        self.buffer_size = buffer_size
        self.memory = []
        self.task_buffer = []

    def add_message(self, role, message):
        """Stores conversation history in memory buffer."""
        self.memory.append({"role": role, "message": message})

        # Keep memory within buffer size
        if len(self.memory) > self.buffer_size:
            self.memory.pop(0)

    def get_context(self):
        """Returns conversation history as context."""
        return "\n".join([f"{m['role']}: {m['message']}" for m in self.memory])

    def get_recent_tasks(self):
        """Retrieves the last executed structured task."""
        return self.task_buffer if self.task_buffer else None

    def add_recent_tasks(self, task):
        """Stores recent tasks (up to 5)."""
        if len(self.task_buffer) >= self.buffer_size:
            self.task_buffer.pop(0)  # ✅ Remove the oldest task
        self.task_buffer.append(task)

    def clear_recent_tasks(self):
        """Clears last task to prevent unintended follow-up inheritance."""
        self.last_task = None  # ✅ Resets stored last_task
