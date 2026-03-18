import spacy
import os
import shutil
import config
from Utils_Modules import toolslist

class ModelLoader:
    def __init__(self, model_name=None):
        """
        Initialize ModelLoader.
        - model_name: If provided, loads the specified model instead of the default.
        """
        self.model_path = os.path.join(config.MODEL_PATH, model_name) if model_name else config.MODEL_PATH
        self.nlp = self.load_or_create_model()

    def load_or_create_model(self):
        """Load existing model or create a new one if ML_SELF_DESTRUCTION is enabled."""
        
        # ✅ Fetch dynamic labels from tools
        MAIN_LABELS, SUBCATEGORIES, ALL_LABELS = toolslist.get_tool_labels()  

        # 🚨 Self-Destruct Mode: Deletes and recreates the model
        if config.ML_SELF_DESTRUCTION:
            print("💥 ML SELF DESTRUCTION ACTIVATED: Deleting and recreating the model...")
            if os.path.exists(self.model_path):
                shutil.rmtree(self.model_path)  # ✅ Deletes the model folder
            config.ML_SELF_DESTRUCTION = False  # 🚨 Auto-reset to prevent loops

        # ✅ Normal Model Loading
        if os.path.exists(self.model_path) and os.path.exists(os.path.join(self.model_path, "meta.json")):
            print(f"🔄 Loading existing model from {self.model_path}...")
            return spacy.load(self.model_path)

        print("🚀 Creating a new blank multi-label model...")
        nlp = spacy.blank("en")

        if "textcat_multilabel" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat_multilabel", last=True)

        # ✅ Use ALL_LABELS from `toolslist`
        for label in ALL_LABELS:
            textcat.add_label(label.replace(" ", "_"))  # ✅ Ensure consistent format

        return nlp
    
    def _create_blank_model(self):
        """Create a new blank multi-label model with the necessary pipeline components."""
        print("🚀 Creating a new blank multi-label model at:", self.model_path)
        nlp = spacy.blank("en")

        # ✅ Change `textcat` to `textcat_multilabel`
        if "textcat_multilabel" not in nlp.pipe_names:
            textcat = nlp.add_pipe("textcat_multilabel", last=True)

        # ✅ Add ALL tool-based labels
        for label in config.ALL_LABELS:
            textcat.add_label(label.replace(" ", "_"))  # Ensure consistency

        return nlp
