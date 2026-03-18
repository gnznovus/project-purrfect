from Utils_Modules.toolslist import get_tool_labels
import config

class Classifier:
    def __init__(self, nlp):
        """Initialize Classifier with NLP model."""
        self.nlp = nlp
        self.MAIN_LABELS, self.SUBCATEGORIES, self.ALL_LABELS = get_tool_labels()

    def classify_input(self, text):
        """Classify user input while ensuring only ONE main label is selected."""
        doc = self.nlp(text)
        scores = doc.cats

        # ✅ Step 1: Extract Main Label Scores
        main_label_scores = {label: scores[label] for label in self.MAIN_LABELS if label in scores}
        if not main_label_scores:
            return ["unknown"], {}
        
        print(f"🛠 DEBUG: Step 1 (Main Label Scores) - {main_label_scores}")
        print(f"Selected Main Label: {max(main_label_scores, key=main_label_scores.get)}")

        # ✅ Step 2: Force-Select Only the **Strongest** Main Label
        highest_main_label = max(main_label_scores, key=main_label_scores.get)
        highest_main_conf = main_label_scores[highest_main_label]

        # ✅ Choose the label with the highest confidence score
        selected_main_label = {max(main_label_scores, key=main_label_scores.get): max(main_label_scores.values())}

        # ✅ Step 3: Process Actions Based on the Selected Tool
        action_scores = {}
        if highest_main_label != "chat":  # ✅ Chat has no actions
            valid_actions = self.SUBCATEGORIES.get(highest_main_label, [])
            raw_action_scores = {label: scores[label] for label in valid_actions if label in scores}

            # ✅ Scale actions relative to the selected main label's confidence
            max_action_conf = max(raw_action_scores.values(), default=0)
            if max_action_conf > 0:
                for label, score in raw_action_scores.items():
                    action_scores[label] = (score / max_action_conf) * highest_main_conf

            # ✅ Remove Actions Below 0.10 Confidence
            action_scores = {label: conf for label, conf in action_scores.items() if conf >= 0.10}

        print(f"🛠 DEBUG: Step 2 (Actions) - {action_scores}")

        # ✅ Step 4: Merge Final Classification
        final_classification = {**selected_main_label, **action_scores}

        print(f"🛠 DEBUG: Final Classification - {final_classification}")
        return list(final_classification.keys()), final_classification
