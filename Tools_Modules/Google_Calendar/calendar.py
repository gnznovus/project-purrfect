import os
import json
from datetime import datetime
from config import CALENDAR_STORAGE_PATH  # Import storage path from config

# Tool Metadata
NAME = "Google Calendar"
ACTIONS = {
    "create_event": "Create a new calendar event",
    "delete_event": "Delete an existing event",
    "update_event": "Modify an existing event",
    "get_events": "Retrieve events for a specific date"
}

class GoogleCalendar:
    def __init__(self):
        self.storage_path = CALENDAR_STORAGE_PATH

    def _get_file_path(self, date_str):
        """Generate storage path based on the given date (YYYY-MM-DD)."""
        year, month, day = date_str.split("-")
        folder_path = os.path.join(self.storage_path, year, month)
        file_path = os.path.join(folder_path, f"{day}.json")
        return folder_path, file_path

    def _load_events(self, file_path):
        """Load existing events from a file or return a new structure."""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        return {"last_id": 0, "events": []}

    def _save_events(self, file_path, folder_path, data):
        """Save event data to the JSON file."""
        os.makedirs(folder_path, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def create_event(self, title, time, description, date):
        """Create a new calendar event."""
        date = date or datetime.today().strftime("%Y-%m-%d")
        folder_path, file_path = self._get_file_path(date)
        data = self._load_events(file_path)

        # Generate new event ID
        last_id = data["last_id"] + 1
        event_id = f"{date[2:].replace('-', '')}{last_id:02d}"
        new_event = {"id": event_id, "title": title, "time": time, "description": description}

        # Update and save
        data["last_id"] = last_id
        data["events"].append(new_event)
        self._save_events(file_path, folder_path, data)

        return {"status": "success", "event_id": event_id, "message": "Event created successfully"}

    def delete_event(self, event_id, date):
        """Delete an event by its ID."""
        folder_path, file_path = self._get_file_path(date)
        data = self._load_events(file_path)

        events = [event for event in data["events"] if event["id"] != event_id]
        if len(events) == len(data["events"]):
            return {"status": "error", "message": "Event not found"}

        data["events"] = events
        self._save_events(file_path, folder_path, data)
        return {"status": "success", "event_id": event_id, "message": "Event deleted successfully"}

    def update_event(self, event_id, date, **updates):
        """Update an existing event."""
        folder_path, file_path = self._get_file_path(date)
        data = self._load_events(file_path)

        for event in data["events"]:
            if event["id"] == event_id:
                event.update(updates)
                self._save_events(file_path, folder_path, data)
                return {"status": "success", "message": "Event updated successfully"}

        return {"status": "error", "message": "Event not found"}

    def get_events(self, date):
        """Retrieve events dynamically based on the granularity of the given date (year, month, or day)."""

        path_parts = date.split("-")  # ✅ Automatically split based on format (YYYY / YYYY-MM / YYYY-MM-DD)
        
        # 🔹 **Case 1: Full Date (YYYY-MM-DD) → Retrieve specific day's events**
        if len(path_parts) == 3:
            _, file_path = self._get_file_path(date)
            data = self._load_events(file_path)
            return {"status": "success", "events": data["events"], "message": f"Events for {date}"}

        # 🔹 **Case 2: Month Only (YYYY-MM) → Retrieve all events in that month**
        elif len(path_parts) == 2:
            year, month = path_parts
            folder_path = os.path.join(self.storage_path, year, month)

        # 🔹 **Case 3: Year Only (YYYY) → Retrieve all events in that year**
        elif len(path_parts) == 1:
            year = path_parts[0]
            folder_path = os.path.join(self.storage_path, year)

        else:
            return {"status": "error", "message": "Invalid date format"}

        # ✅ **If folder doesn't exist, return empty**
        if not os.path.exists(folder_path):
            return {"status": "success", "events": [], "message": f"No events found for {date}"}

        # ✅ **Read all events inside the folder (recursive)**
        all_events = []
        for root, _, files in os.walk(folder_path):
            for filename in sorted(files):
                if filename.endswith(".json"):
                    file_path = os.path.join(root, filename)
                    data = self._load_events(file_path)
                    all_events.extend(data["events"])  # ✅ Merge all events

        return {"status": "success", "events": all_events, "message": f"Events for {date}"}

    def execute(self, action, task_details):
        """Dynamically execute an action based on the task details."""
        if action == "create_event":
            return self.create_event(**task_details)
        elif action == "delete_event":
            return self.delete_event(**task_details)
        elif action == "update_event":
            return self.update_event(**task_details)
        elif action == "get_events":
            return self.get_events(**task_details)
        else:
            return {"status": "error", "message": f"Action '{action}' not found."}