from AI_Modules.ML_models.data_handler import DataHandler
from AI_Modules.ML_models.training import Trainer
from Utils_Modules.toolslist import get_tool_labels

class UserInteraction:
    def __init__(self, nlp):
        """Initialize UserInteraction with NLP model and supporting modules."""
        self.nlp = nlp
        self.data_handler = DataHandler()
        self.trainer = Trainer(nlp)

        self.MAIN_LABELS, self.SUBCATEGORIES, self.ALL_LABELS = get_tool_labels()

    def handle_uncertain_classification(self, text, confidence):
        """Handle low-confidence predictions by asking for user input with multi-label support."""
        print(f"\n🤔 AI is unsure (Confidence: {confidence:.2f}). Please classify this text:")
        print(f"📜 \"{text}\"")

        # ✅ Show dynamically loaded labels
        print("\n🔹 Available Categories:")
        for idx, label in enumerate(self.ALL_LABELS, 1):
            print(f"{idx}️⃣ {label}")

        print("\n💡 You can select multiple labels (e.g., '1,3,5') or type 'exit' to cancel.")
        choice = input("👉 Select categories: ").strip()

        if choice.lower() == "exit":
            print("🚪 Classification canceled.")
            return

        selected_indices = choice.split(",")
        selected_labels = []

        # ✅ Convert numeric input to labels
        for idx in selected_indices:
            idx = idx.strip()
            if idx.isdigit():
                idx = int(idx)
                if 1 <= idx <= len(self.ALL_LABELS):
                    selected_labels.append(self.ALL_LABELS[idx - 1])

        if not selected_labels:
            print("⚠️ Invalid input. Skipping classification.")
            return

        # ✅ Build training format for multiple labels
        annotations = {label: 1.0 if label in selected_labels else 0.0 for label in self.ALL_LABELS}

        # ✅ Append to retrain_data.txt
        retrain_data = self.data_handler.load_retrain_data()
        retrain_data.append((text, {"cats": annotations}))
        self.data_handler.save_retrain_data(retrain_data)

        print(f"✅ Classified as {', '.join(selected_labels)}. Added to retraining data.")

    def recall_entry(self, phrase):
        """Search and allow correction for past trained data from both Training_Data.txt and Retrain_Data.txt."""
        found_entries = []

        # Load training and retraining data
        training_data = self.data_handler.load_training_data()
        retrain_data = self.data_handler.load_retrain_data()

        # 🔹 Search in training data
        for text, annotations in training_data:
            if phrase.lower() in text.lower():
                active_labels = [label for label, value in annotations["cats"].items() if value == 1.0]
                found_entries.append((text, active_labels, "training"))

        # 🔹 Search in retraining data
        for text, annotations in retrain_data:
            if phrase.lower() in text.lower():
                active_labels = [label for label, value in annotations["cats"].items() if value == 1.0]
                found_entries.append((text, active_labels, "retrain"))

        if not found_entries:
            print("❌ No matching entries found.")
            return

        # Display matching entries
        print("\n🔍 Found matches:")
        for idx, (text, active_labels, source) in enumerate(found_entries, 1):
            file_label = "Training_Data.txt" if source == "training" else "Retrain_Data.txt"
            print(f"{idx}️⃣ {text} | Labels: {', '.join(active_labels)} (Source: {file_label})")

        choice = input("\n👉 Select entry to review (or type 'exit' to cancel): ").strip()
        if choice.lower() == "exit":
            return

        try:
            selected_text, current_labels, source = found_entries[int(choice) - 1]
            file_label = "Training_Data.txt" if source == "training" else "Retrain_Data.txt"

            # 🔹 Show available categories for correction
            print(f"\nChange labels for: \"{selected_text}\" (From {file_label})")
            print("\n🔹 Available Categories:")
            for idx, label in enumerate(self.ALL_LABELS, 1):
                print(f"{idx}️⃣ {label}")

            print("\n💡 Select multiple new labels (e.g., '1,3,5') or type 'exit' to cancel.")
            new_choice = input("👉 Select new categories: ").strip()

            if new_choice.lower() == "exit":
                print("🚪 Update canceled.")
                return

            new_indices = new_choice.split(",")
            new_labels = []

            # ✅ Convert numeric input to labels
            for idx in new_indices:
                idx = idx.strip()
                if idx.isdigit():
                    idx = int(idx)
                    if 1 <= idx <= len(self.ALL_LABELS):
                        new_labels.append(self.ALL_LABELS[idx - 1])

            if not new_labels:
                print("⚠️ Invalid choice. No changes made.")
                return

            # ✅ Build new training entry
            updated_annotations = {label: 1.0 if label in new_labels else 0.0 for label in self.ALL_LABELS}

            # ✅ Update the correct data file
            if source == "training":
                updated_data = [(text, {"cats": updated_annotations}) if text == selected_text else (text, annotations)
                                for text, annotations in training_data]
                self.data_handler.save_training_data(updated_data)
            else:
                updated_data = [(text, {"cats": updated_annotations}) if text == selected_text else (text, annotations)
                                for text, annotations in retrain_data]
                self.data_handler.save_retrain_data(updated_data)

            print(f"✅ Entry updated to '{', '.join(new_labels)}' in {file_label} & retrained.")
            self.trainer.train_model(full_train=True if source == "training" else False)

        except (IndexError, ValueError):
            print("❌ Invalid selection.")
