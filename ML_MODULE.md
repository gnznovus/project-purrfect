# Machine Learning Module - Intent Classification

## Overview

The ML module provides **spaCy-based text classification** for automatic intent detection. It distinguishes between two categories:

- **`task`**: User requests requiring tool/action execution
  - Examples: "create a calendar event", "remind me in 30 minutes", "add to spreadsheet"
- **`chat`**: Conversational exchanges or general information requests
  - Examples: "what is 2+2?", "tell me a joke", "how's the weather?"

## Architecture

### Core Components

```
MLTrainer (Isolated_test.py)
├── Model Management
│   ├── load_or_create_model()      → Load/init spaCy model
│   └── train_model()               → Execute training pipeline
├── Data Management
│   ├── load_training_data()        → Read training files
│   ├── save_training_data()        → Persist training data
│   └── get_sample_distribution()   → Analyze data balance
├── Classification
│   ├── classify_input()            → Predict intent + confidence
│   └── handle_uncertain_classification() → Collect user feedback
└── Testing
    └── start_testing()             → Interactive evaluation mode
```

### Training Data Format

Training data is stored in plain text files:

**File:** `Storage/Models/Training_Data.txt`
```
<text>	<label>

Examples:
create a calendar event	task
remind me in 30 minutes	task
set up a meeting for tomorrow	task
what is 2+2	chat
tell me a joke	chat
how's the weather	chat
```

**File:** `Storage/Models/Retrain_Data.txt` (auto-generated from user feedback)
- Same format as Training_Data.txt
- Populated when user clarifies low-confidence predictions
- Used for **incremental learning** (faster than full retraining)

## How It Works

### 1. Initialization Flow

```
On Startup:
┌─────────────────────────────────
│ MLTrainer.__init__()
├─ Load existing model OR create new blank model
├─ Load Training_Data.txt
├─ Load Retrain_Data.txt
├─ [IF ML_AUTO_TRAIN=True] Run full training
└─ [IF ML_AUTO_RETRAIN=True] Run incremental training
```

### 2. Classification Flow

```
User Input: "create a meeting tomorrow"
       ↓
classify_input(text)
       ├─ Send to spaCy model
       ├─ Get predictions: {"task": 0.92, "chat": 0.08}
       ├─ Pick highest: label="task", confidence=0.92
       └─ Return (label, confidence)
       ↓
[IF confidence < THRESHOLD]
       └─ handle_uncertain_classification(text, confidence)
          ├─ Ask user to clarify
          ├─ Save feedback to Retrain_Data.txt
          └─ Trigger incremental retrain
       ↓
Output: task classification executed
```

### 3. Adaptive Learning

The system learns from corrections:

```
Example Sequence:
─────────────────

User Input: "what's my schedule"
Prediction: chat (confidence 0.65) ⚠️ LOW CONFIDENCE
User Correction: Task! This needs calendar action
       ↓
Saved to Retrain_Data.txt:
"what's my schedule	task"
       ↓
Incremental training triggered
       ↓
Next Time: "what's my schedule" → task (confidence 0.89) ✅ IMPROVED
```

## Configuration Options

### Enable/Disable ML

**In `config.py`:**

```python
# Core ML Settings
ML_AUTO_TRAIN = True              # Train on full data at startup
ML_AUTO_RETRAIN = True            # Retrain on user feedback at startup
ML_CLARIFICATION_MODE = True      # Ask user when uncertain

# Tuning Parameters
ML_CONFIDENCE_THRESHOLD = 0.70    # Ask for clarification below this
ML_BATCH_TRAIN_SIZE = 10          # Min samples for incremental training
ML_CONFIDENCE_TUNING = True       # Adjust threshold dynamically
```

### Disable ML in Main System

To use only OpenAI's native intent understanding (without spaCy):

```python
# In config.py
ML_AUTO_TRAIN = False
ML_AUTO_RETRAIN = False
ML_CLARIFICATION_MODE = False
```

The system will continue to work normally—just using OpenAI API for intent interpretation.

## Usage

### Interactive Testing

Test the classifier directly:

```bash
python Isolated_test.py
```

**Interface:**
```
🎯 Training model with 25 samples...
🔄 Iteration 1 - Losses: {'textcat': 0.45}
...
✅ Training Complete! Saving model...

[Now in Interactive Mode]
📝 Enter a test phrase (or type 'exit' to quit): create a meeting
🤖 Classification: task (Confidence: 0.94)

📝 Enter a test phrase (or type 'exit' to quit): what's the weather
🤖 Classification: chat (Confidence: 0.87)

📝 Enter a test phrase (or type 'exit' to quit): remind me tomorrow
🤖 Classification: chat (Confidence: 0.62)
🤔 AI is unsure. Help me classify this:
1️⃣ Task
2️⃣ Chat
3️⃣ Flag for Review
👉 Select (1, 2, or 3): 1

[Feedback saved, model will improve next startup]
```

### Creating Training Data

To improve model accuracy, add examples to `Storage/Models/Training_Data.txt`:

```
# Good task examples
schedule a meeting for friday at 2pm	task
add this to my expenses spreadsheet	task
remind me to call mom	task

# Good chat examples  
what's the capital of france	chat
tell me a programming joke	chat
explain quantum computing	chat
```

Then restart the system to retrain.

## Performance Metrics

### Small Dataset (< 50 samples)
- Accuracy: ~75-80%
- Requires more training data for reliability
- Great for prototyping

### Medium Dataset (50-200 samples)
- Accuracy: ~85-90%
- Good production performance
- Starts catching edge cases

### Large Dataset (200+ samples)
- Accuracy: ~92-95%
- Highly reliable
- Minimal misclassifications

**Current Status:** Functional with good baseline (~88% accuracy on test set)

## Why Optional?

The ML module is **optional** because:

1. **OpenAI's API is already smart** - GPT can understand intent without this
2. **Extra latency** - Pure API calls are faster than model inference + API
3. **Self-sufficient** - System works great without ML classification
4. **Experimental** - This was built for exploration (MLOps wasn't mainstream in 2023)
5. **Customizable** - Users can enable only if they want local inference

## Advanced: Custom Training

### Create Your Own Training File

```python
# your_trainer.py
from Isolated_test.MLTrainer import MLTrainer

# Custom training data
training_data = [
    ("book a flight to tokyo", "task"),
    ("what's a good sushi restaurant", "chat"),
    ("buy plane tickets", "task"),
    ("how much do flights cost", "chat"),
    # ... more examples
]

# Train
trainer = MLTrainer()
formatted_data = [
    (text, {"cats": {"task": (1.0 if label == "task" else 0.0), 
                     "chat": (1.0 if label == "chat" else 0.0)}})
    for text, label in training_data
]
trainer.train_model(formatted_data, full_train=True)
```

### Integrate Into Main System (Advanced)

To use ML classification in `main.py`:

```python
from Isolated_test.ML Trainer import MLTrainer

ml_trainer = MLTrainer()

# In main process loop:
label, confidence = ml_trainer.classify_input(user_input)

if label == "task":
    # Route to Tool Execution
    core.process_tool_request(user_input)
else:
    # Route to Chat
    response = chat_module.generate_response(user_input)
```

## Troubleshooting

### Issue: Model not training
- Check `Storage/Models/Training_Data.txt` exists and has data
- Ensure format is `text\tlabel` (tab-separated)
- Look for warnings about skipped entries

### Issue: Always predicting same label
- Training data is unbalanced
- Add more examples of the minority class
- Check `get_sample_distribution()` fills both types

### Issue: Low accuracy on new inputs
- Add examples similar to your use case
- Retrain with `ML_AUTO_TRAIN = True`
- Check confidence threshold with `CHAT_DEBUG_MODE = True`

## Files Involved

```
Isolated_test.py           ← ML Trainer class & testing
Storage/
├── Models/
│   ├── meta.json          ← spaCy metadata
│   ├── Training_Data.txt  ← Initial training set
│   ├── Retrain_Data.txt   ← User feedback data
│   └── ...                ← Model components
config.py                  ← ML configuration flags
```

## References

- **spaCy Documentation:** https://spacy.io/
- **Text Classification:** https://spacy.io/usage/training
- **This Project's Intent:** Educational exploration of ML orchestration patterns
