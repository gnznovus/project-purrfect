import spacy
import random
import config
from AI_Modules.ML_models.data_handler import DataHandler
from Utils_Modules.toolslist import get_tool_labels

class Trainer:
    def __init__(self, nlp):
        """Initialize Trainer with NLP model and DataHandler."""
        self.nlp = nlp
        self.data_handler = DataHandler()
        self.batch_size = config.ML_BATCH_TRAIN_SIZE
        self.auto_train_threshold = config.ML_AUTO_TRAIN_THRESHOLD

    def get_sample_distribution(self, data):
        """Determine how many samples to take per type based on available data."""
        category_counts = {label: 0 for label in self.ALL_LABELS}  # ✅ Initialize for all labels

        for _, annotations in data:
            for label, value in annotations["cats"].items():
                if value == 1.0:
                    category_counts[label] += 1

        total_samples = sum(category_counts.values())
        if total_samples == 0:
            return {}

        per_type_sample = max(total_samples // len(category_counts), 1)
        return {t: min(count, per_type_sample) for t, count in category_counts.items()}

    def filter_low_sample_types(self, data, distribution):
        """Skip underrepresented types and redistribute quota."""
        min_threshold = max(sum(distribution.values()) // len(distribution), 1)

        low_types = [t for t, count in distribution.items() if count < min_threshold]

        if not low_types:
            return data  # No underrepresented types, continue as usual

        print(f"⚠️ Skipping low-sample types: {', '.join(low_types)}")

        # ✅ Remove samples that only contain low-count labels
        filtered_data = []
        for text, annotations in data:
            valid_labels = {label: value for label, value in annotations["cats"].items() if label not in low_types}
            if valid_labels:  # ✅ Keep entries that have at least one valid label
                filtered_data.append((text, {"cats": valid_labels}))

        return filtered_data

    def train_model(self, full_train=False):
        """Train model with adaptive learning, batch training, and class balancing."""
        data = self.data_handler.load_training_data() if full_train else self.data_handler.load_retrain_data()
        print(f"🛠 Starting {'full training' if full_train else 'retraining'} with {len(data)} samples...")  # ✅ Debug print

        # ✅ Ensure enough data is available before training
        if not data or len(data) < self.batch_size:
            print(f"⚠️ Not enough data ({len(data)}/{self.batch_size}) for {'full training' if full_train else 'retraining'}. Skipping...")
            return False

        # ✅ Get all valid labels from toolslist
        self.MAIN_LABELS, self.SUBCATEGORIES, self.ALL_LABELS = get_tool_labels()

        # ✅ Print dataset distribution before Smart Sampling
        category_counts = {label: 0 for label in self.ALL_LABELS}  # ✅ Initialize all label counters

        for _, annotations in data:
            for label, value in annotations["cats"].items():
                if value == 1.0:
                    category_counts[label] += 1

        print(f"📊 Pre-Sampling Data Distribution: {category_counts}")

        # ✅ Always balance dataset (even for small datasets)
        print("🛠 Running Smart Sampling to balance class distribution...")
        sample_distribution = self.get_sample_distribution(data)
        balanced_data = self.filter_low_sample_types(data, sample_distribution)

        if len(balanced_data) != len(data):  # ✅ Only print if changes occur
            data = balanced_data
            new_category_counts = {label: sum(1 for _, ann in data if ann["cats"].get(label, 0.0) == 1.0) for label in self.ALL_LABELS}
            print(f"📊 Adjusted Data Distribution After Sampling: {new_category_counts}")

        print(f"🎯 Final Training Data Size: {len(data)} samples.")

        optimizer = self.nlp.begin_training()

        # ✅ Iteration logic with batch_size consideration
        iterations = max(self.batch_size, min(len(data), 100))  # ✅ At least batch_size, max 100 iterations
        print(f"🔄 Running {iterations} iterations of training...")  # ✅ Debug print

        for i in range(iterations):
            random.shuffle(data)
            losses = {}
            for batch_start in range(0, len(data), self.batch_size):  # ✅ Train in batches
                batch = data[batch_start: batch_start + self.batch_size]
                for text, annotations in batch:
                    doc = self.nlp.make_doc(text)

                    # ✅ Find the strongest label (most confident)
                    max_label = max(annotations["cats"], key=annotations["cats"].get)

                    # ✅ Set only the strongest label to 1.0, others to 0.0
                    for label in annotations["cats"]:
                        annotations["cats"][label] = 1.0 if label == max_label else 0.0

                    example = spacy.training.Example.from_dict(doc, {"cats": annotations["cats"]})
                    self.nlp.update([example], drop=0.6, losses=losses)

            print(f"🔄 Iteration {i+1}/{iterations} - Losses: {losses}")

        print("✅ Training Complete! Saving model...")
        self.nlp.to_disk(config.MODEL_PATH)

        # ✅ Merge retrain data & trigger full training if necessary
        if not full_train:
            self.data_handler.merge_retrain_data()
            self.train_model(full_train=True)

        return True  # ✅ Ensure it returns True when successful
