from typing import List, Dict, Any, Optional

class MemoryBuffer:
    """
    Manages conversation history and recent task execution context.
    
    Maintains two buffers:
    1. message buffer: Stores conversation history (user/assistant messages)
    2. task_buffer: Stores recently executed tool calls (for context in follow-ups)
    
    This enables the AI to:
    - Understand conversation context
    - Reference previously executed tasks
    - Prevent accidental repetition of tasks
    
    Attributes:
        buffer_size: Maximum number of items to retain (older items are removed)
        memory: List of conversation messages
        task_buffer: List of recently executed tasks
    """
    
    def __init__(self, buffer_size: int = 5) -> None:
        self.buffer_size = buffer_size
        self.memory = []
        self.task_buffer = []

    def add_message(self, role: str, message: str) -> None:
        """Stores conversation history in memory buffer.
        
        Args:
            role: Role of speaker ("user" or "assistant")
            message: Message content
        """
        self.memory.append({"role": role, "message": message})

        # Keep memory within buffer size
        if len(self.memory) > self.buffer_size:
            self.memory.pop(0)

    def get_context(self) -> str:
        """Returns conversation history as context.
        
        Returns:
            str: Formatted conversation history
        """
        return "\n".join([f"{m['role']}: {m['message']}" for m in self.memory])

    def get_recent_tasks(self) -> Optional[List[Dict[str, Any]]]:
        """Retrieves the last executed structured task.
        
        Returns:
            List of recent tasks or None if empty
        """
        return self.task_buffer if self.task_buffer else None

    def add_recent_tasks(self, task: Dict[str, Any]) -> None:
        """Stores recent tasks (up to buffer_size).
        
        Args:
            task: Task object to store
        """
        if len(self.task_buffer) >= self.buffer_size:
            self.task_buffer.pop(0)  # ✅ Remove the oldest task
        self.task_buffer.append(task)

    def clear_recent_tasks(self) -> None:
        """Clears last task to prevent unintended follow-up inheritance."""
        self.last_task = None  # ✅ Resets stored last_task
