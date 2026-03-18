"""
ML Training Module - spaCy-based Intent Classification

This module provides a complete pipeline for training and testing
a text classification model that distinguishes between:
- "task": User requests for tool/action execution
- "chat": Conversational exchanges

Features:
- Auto-training from Training_Data.txt on startup
- Incremental learning from user feedback (Retrain_Data.txt)
- Adaptive confidence thresholds
- Interactive testing mode with user clarification

Usage:
    python Isolated_test.py
"""

import spacy
import random
import os
from typing import List, Tuple, Dict, Optional
import config  # Import your configuration settings

class MLTrainer:
    """
    Machine Learning Trainer for Intent Classification.
    
    Manages the full ML pipeline:
    - Model loading/creation
    - Training data management
    - Model training with adaptive learning
    - Classification and confidence scoring
    - User feedback collection for continuous improvement
    
    Attributes:
        MODEL_PATH: Path to saved spaCy model
        TRAINING_DATA_PATH: Path to initial training data
        RETRAIN_DATA_PATH: Path to incremental training data
        BATCH_SIZE: Size of batches for incremental training
        nlp: The spaCy language model
    """
    def __init__(self) -> None:
        """Initialize the ML Trainer"""
        self.MODEL_PATH = config.MODEL_PATH
        self.TRAINING_DATA_PATH = config.TRAINING_DATA_PATH
        self.RETRAIN_DATA_PATH = config.RETRAIN_DATA_PATH
        self.BATCH_SIZE = config.ML_BATCH_TRAIN_SIZE

        self.nlp = self.load_or_create_model()
        self.training_data = self.load_training_data(self.TRAINING_DATA_PATH)
        self.retrain_data = self.load_training_data(self.RETRAIN_DATA_PATH)

        # Auto-train on startup if enabled
        if config.ML_AUTO_TRAIN:
            if self.train_model(self.training_data, full_train=True):
                print("🔄 Bulk training completed from Training_Data.txt!")

        # Auto-retrain on startup if enabled
        if config.ML_AUTO_RETRAIN:
            if self.train_model(self.retrain_data, full_train=False):
                print("🔄 Bulk retraining completed from Retrain_Data.txt!")

    # 🔹 Load or Create Model
    def load_or_create_model(self) -> spacy.language.Language:
        """Load existing model or create a new one.
        
        Returns:
            spacy.language.Language: The loaded or newly created spaCy model
        """
        if os.path.exists(self.MODEL_PATH) and os.path.exists(os.path.join(self.MODEL_PATH, "meta.json")):
            print(f"🔄 Loading existing model from {self.MODEL_PATH}...")
            return spacy.load(self.MODEL_PATH)
        else:
            print("🚀 Creating a new blank model...")
            nlp = spacy.blank("en")
            if "textcat" not in nlp.pipe_names:
                textcat = nlp.add_pipe("textcat", last=True)
                textcat.add_label("task")
                textcat.add_label("chat")
            return nlp

    # 🔹 Load Data from Files
    def load_training_data(self, file_path: str) -> List[Tuple[str, Dict]]:
        """Load training data, ensuring the file exists to prevent errors.
        
        Args:
            file_path: Path to training data file
            
        Returns:
            List of tuples (text, annotations) for training
        """
        if not os.path.exists(file_path):
            open(file_path, "w").close()  # Create empty file if missing
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        training_data = []
        for line in lines:
            try:
                text, label = [part.strip() for part in line.strip().replace("\t", "|").split("|")]

                if label not in ["task", "chat"]:
                    print(f"⚠️ Skipping invalid training entry (Invalid Label): {line.strip()}")
                    continue

                annotations = {"cats": {"task": 1.0, "chat": 0.0} if label == "task" else {"task": 0.0, "chat": 1.0}}
                training_data.append((text, annotations))
            except ValueError:
                print(f"⚠️ Skipping invalid training entry (Bad Format): {line.strip()}")

        return training_data

    # 🔹 Save Training Data
    def save_training_data(self, file_path: str, data: List[Tuple[str, Dict]]) -> None:
        """Save training data while ensuring file is closed properly.
        
        Args:
            file_path: Path to save training data to
            data: Training data to save
        """
        with open(file_path, "w", encoding="utf-8") as file:
            for text, annotations in data:
                label = "task" if annotations["cats"]["task"] == 1.0 else "chat"
                file.write(f"{text}\t{label}\n")

    # 🔹 Smart Sample Selection
    def get_sample_distribution(self, data: List[Tuple[str, Dict]]) -> Dict[str, int]:
        """Determine how many samples to take per type based on total available data.
        
        Args:
            data: Training data to analyze
            
        Returns:
            Dict mapping label types to sample counts
        """
        type_counts = {"task": 0, "chat": 0}

        # Count samples per type
        for _, annotations in data:
            if annotations["cats"]["task"] == 1.0:
                type_counts["task"] += 1
            else:
                type_counts["chat"] += 1

        total_samples = sum(type_counts.values())

        if total_samples == 0:
            return {}  # No data to train

        # Calculate even sample distribution per type
        per_type_sample = max(total_samples // len(type_counts), 1)
        return {t: min(count, per_type_sample) for t, count in type_counts.items()}

    # 🔹 Filter Low-Sample Types
    def filter_low_sample_types(self, data: List[Tuple[str, Dict]], distribution: Dict[str, int]) -> List[Tuple[str, Dict]]:
        """Skip underrepresented types until more samples exist and redistribute skipped quota.
        
        Args:
            data: Training data to filter
            distribution: Sample distribution per type
            
        Returns:
            Filtered training data
        """
        min_threshold = max(sum(distribution.values()) // len(distribution), 1)

        # Identify low-sample types
        low_types = [t for t, count in distribution.items() if count < min_threshold]

        if not low_types:
            return data  # No need to adjust

        print(f"⚠️ Skipping low-sample types: {', '.join(low_types)}")

        # Remove skipped types & redistribute
        adjusted_data = [d for d in data if d[1]["cats"][low_types[0]] == 0.0]
        return adjusted_data

    # 🔹 Train Model with Smart Sampling
    def train_model(self, data: List[Tuple[str, Dict]], full_train: bool = False) -> bool:
        """Train model with Smart Sample Selection & Adaptive Learning.
        
        Args:
            data: Training data
            full_train: Whether to do full training (more iterations) vs incremental
            
        Returns:
            bool: True if training completed successfully
        """
        if not full_train and len(data) < self.BATCH_SIZE:
            return False  # Skip retraining if not enough samples

        print(f"🎯 Training model with {len(data)} samples...")

        # 🚀 Step 2: Get sample distribution
        sample_distribution = self.get_sample_distribution(data)

        # 🚀 Step 2.5: Skip underrepresented types & redistribute
        data = self.filter_low_sample_types(data, sample_distribution)

        optimizer = self.nlp.begin_training()
        iterations = 20 if full_train else 5  # Fewer iterations for small updates

        for i in range(iterations):
            random.shuffle(data)
            losses = {}
            for text, annotations in data:
                doc = self.nlp.make_doc(text)
                example = spacy.training.Example.from_dict(doc, {"cats": annotations["cats"]})
                self.nlp.update([example], drop=0.6, losses=losses)
            print(f"🔄 Iteration {i+1} - Losses: {losses}")

        print("✅ Training Complete! Saving model...")
        self.nlp.to_disk(self.MODEL_PATH)

        # If retraining, clear retraining data
        if not full_train:
            self.save_training_data(self.RETRAIN_DATA_PATH, [])  # Clear retraining file

        return True

    # 🔹 Classify Input
    def classify_input(self, text: str) -> Tuple[str, float]:
        """Classify user input as 'task' or 'chat'.
        
        Args:
            text: User input to classify
            
        Returns:
            Tuple of (predicted_label, confidence_score)
        """
        doc = self.nlp(text)
        scores = doc.cats
        label = max(scores, key=scores.get)  # Pick highest confidence label
        confidence = scores[label]
        return label, confidence

    # 🔹 Handle Uncertain Classifications
    def handle_uncertain_classification(self, text: str, confidence: float) -> None:
        """Handles low-confidence predictions by asking for user input.
        
        Args:
            text: The text that was classified with low confidence
            confidence: The confidence score of the classification
        """
        print("\n🤔 AI is unsure. Help me classify this:")
        print("1️⃣ Task")
        print("2️⃣ Chat")
        print("3️⃣ Flag for Review")
        choice = input("👉 Select (1, 2, or 3): ").strip()

        if choice == "1":
            self.retrain_data.append((text, {"cats": {"task": 1.0, "chat": 0.0}}))
        elif choice == "2":
            self.retrain_data.append((text, {"cats": {"task": 0.0, "chat": 1.0}}))
        elif choice == "3":
            print("🚩 Flagged for later review.")

        # Save data & retrain if needed
        self.save_training_data(self.RETRAIN_DATA_PATH, self.retrain_data)
        self.train_model(self.retrain_data, full_train=False)  # Trigger batch training if enough data

    # 🔹 Run User Testing Mode
    def start_testing(self) -> None:
        """Interactive testing mode for classification.
        
        Allows users to test classification accuracy and provide feedback
        for model improvement.
        """
        while True:
            user_input = input("\n📝 Enter a test phrase (or type 'exit' to quit): ").strip()
            if user_input.lower() == "exit":
                break

            label, confidence = self.classify_input(user_input)
            print(f"🤖 Classification: {label} (Confidence: {confidence:.2f})")

            # Handle uncertain predictions
            if config.ML_CLARIFICATION_MODE and confidence < 0.70:
                self.handle_uncertain_classification(user_input, confidence)

        print("👋 Exiting test mode!")

# 🔹 Start the ML Trainer
if __name__ == "__main__":
    trainer = MLTrainer()
    trainer.start_testing()
