import os
import config
import random
from Utils_Modules.toolslist import get_tool_labels

class DataHandler:
    def __init__(self):
        """Initialize DataHandler with training & retraining paths."""
        self.TRAINING_DATA_PATH = config.TRAINING_DATA_PATH
        self.RETRAIN_DATA_PATH = config.RETRAIN_DATA_PATH
        self.MAX_TRAIN_SIZE = config.ML_MAX_TRAIN_SIZE

        self.MAIN_LABELS, self.SUBCATEGORIES, self.ALL_LABELS = get_tool_labels()

    def _load_data(self, file_path):
        """Load training data dynamically with multi-label support."""
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as _:
                return []

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        training_data = []
        for line in lines:
            try:
                text, labels = line.strip().split("|")
                label_list = [label.strip() for label in labels.split(",")]

                # ✅ Only allow valid labels from toolslist
                valid_labels = [label for label in label_list if label in self.ALL_LABELS]
                if not valid_labels:
                    print(f"⚠️ Skipping invalid entry: {line.strip()}")
                    continue

                annotations = {"cats": {label: 1.0 for label in valid_labels}}
                training_data.append((text, annotations))
            except ValueError:
                print(f"⚠️ Skipping malformed training entry: {line.strip()}")

        return training_data

    def load_training_data(self):
        """Load main training data from the configured path."""
        return self._load_data(self.TRAINING_DATA_PATH)

    def load_retrain_data(self):
        """Load retraining data from the configured path."""
        return self._load_data(self.RETRAIN_DATA_PATH)

    def _save_data(self, file_path, data):
        """Generic method to save training data with multi-label support."""
        with open(file_path, "w", encoding="utf-8") as file:
            for text, annotations in data:
                labels = [label for label, value in annotations["cats"].items() if value == 1.0]
                file.write(f"{text} | {' , '.join(labels)}\n")  # ✅ Fix: Save all active labels

    def save_training_data(self, data):
        """Save main training data to the configured path."""
        self._save_data(self.TRAINING_DATA_PATH, data)

    def save_retrain_data(self, data):
        """Save retraining data to the configured path."""
        self._save_data(self.RETRAIN_DATA_PATH, data)

    # 🔹 Merge Retrained Data into Training Set (No Duplicates)
    def merge_retrain_data(self):
        """Merge Retrain_Data.txt into Training_Data.txt while ensuring no data is lost."""
        print("🔄 Merging retrained data into Training_Data.txt...")

        with open(self.TRAINING_DATA_PATH, "r+", encoding="utf-8") as train_file, open(self.RETRAIN_DATA_PATH, "r", encoding="utf-8") as retrain_file:
            existing_data = {line.strip() + "\n" for line in train_file.readlines()}
            new_data = {line.strip() + "\n" for line in retrain_file.readlines()}

            merged_data = existing_data.union(new_data)

            train_file.seek(0)
            train_file.writelines(merged_data)
            train_file.truncate()

        open(self.RETRAIN_DATA_PATH, "w").close()
        print(f"✅ Retrained data merged successfully ({len(new_data)} new samples added)!")

        # ✅ Only balance & limit training data **if new data was added**
        if new_data:
            self.balance_training_data()
            self.limit_training_size()

    # 🔹 Auto-Balance Dataset
    def balance_training_data(self):
        """Ensure equal representation of each category in Training_Data.txt using random sampling."""
        with open(self.TRAINING_DATA_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()

        category_counts = {"task": 0, "chat": 0}
        data_by_category = {"task": [], "chat": []}

        for line in lines:
            try:
                text, label = line.strip().split("|")
                if label in category_counts:
                    category_counts[label] += 1
                    data_by_category[label].append(line)
            except ValueError:
                print(f"⚠️ Skipping invalid training entry: {line.strip()}")

        min_samples = min(category_counts.values())

        # ✅ Use random.sample() to select a diverse subset instead of just truncating
        balanced_data = random.sample(data_by_category["task"], min_samples) + random.sample(data_by_category["chat"], min_samples)

        # Save balanced dataset
        with open(self.TRAINING_DATA_PATH, "w", encoding="utf-8") as file:
            file.writelines(balanced_data)

        print("✅ Training data balanced using random sampling!")

    # 🔹 Limit Training Data Size
    def limit_training_size(self):
        """Limit Training_Data.txt to a maximum number of samples."""
        with open(self.TRAINING_DATA_PATH, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if len(lines) > self.MAX_TRAIN_SIZE:
            print(f"⚠️ Training data too large ({len(lines)} samples). Trimming to {self.MAX_TRAIN_SIZE}...")
            lines = lines[-self.MAX_TRAIN_SIZE:]

        with open(self.TRAINING_DATA_PATH, "w", encoding="utf-8") as file:
            file.writelines(lines)

        print("✅ Training data size limited to", self.MAX_TRAIN_SIZE)