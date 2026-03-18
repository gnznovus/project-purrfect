# Usage Guide - Project Purrfect 2.0

This guide shows you how to use the Purrfect AI Automation System with real examples.

## Running the System

### Terminal Mode

Start the system in terminal mode:
```bash
python main.py --ter    # Force Terminal mode
# OR
python main.py          # If config.INPUT_PLATFORM = "terminal"
```

You'll see:
```
[CORE] Running in Terminal Mode.
You: 
```

---

## Example Interactions

### Example 1: Simple Chat

```
You: what is 2 + 2?
Purr: The sum of 2 + 2 equals 4.
```

**What happened:**
1. Your input → Core processes it
2. Intent detected → "general chat" with no tools needed
3. AI generates response using ChatGPT
4. Memory stores this for context

---

### Example 2: Tool-Based Request (Calendar)

```
You: create a meeting tomorrow at 3pm called standup
Purr: Event "standup" scheduled for tomorrow at 3:00 PM on your calendar.
```

**What happened:**
1. Input analyzed → Calendar tool detected
2. Tool loaded → "Google_Calendar" module initialized  
3. Parameters extracted → date=tomorrow, time=3pm, title=standup
4. Tool executed → Calendar API call made
5. Result formatted → Success message returned
6. Memory updated → Recent task stored for context

---

### Example 3: Multi-Step Request

```
You: remind me to call mom every monday at 10am
Purr: I've set up a recurring reminder for every Monday at 10:00 AM to call mom.
```

**What happened:**
1. System identifies: Reminder tool + Calendar tool
2. Both tools invoked in sequence
3. Reminder created in system
4. Calendar event created (recurring)
5. Both results combined for user

---

## Configuration Options

### Input Platforms

**Terminal Mode (Default):**
```python
INPUT_PLATFORM = "terminal"  # in config.py
```
- CLI-based interaction
- Good for testing & development

**Telegram Bot Mode:**
```python
INPUT_PLATFORM = "telegram"  # in config.py
```
- Chat via Telegram app
- Get token from @BotFather on Telegram
- Set `TELEGRAM_BOT_TOKEN = "your-token"`
- Set `BOT_USERNAME = "YourBotName"`

---

## Debug Mode

Enable debug output to see what's happening:

```python
# In config.py - enable any of these:
CHAT_DEBUG_MODE = True          # See AI prompts
CORE_DEBUG_MODE = True          # See tool loading & execution
SWITCH_DEBUG_MODE = True        # See input detection
TOOLS_DEBUG_MODE = True         # See tool details
```

When enabled, you'll see:
```
[CORE] 🔥 Initialization Complete
=================================
[CORE] 🛠️ Loaded Tools:
  ✅ Calendar (Actions: create_event, delete_event, update_event)
    🔹 create_event: ['date', 'time', 'title']
=================================

[CORE] 🚀 Running Calendar.create_event with:
      🔹 Parameters: {'date': 'tomorrow', 'time': '3pm', 'title': 'standup'}
```

---

## Supported Tools

### 1. Calendar Tool
**What it does:** Manage Google Calendar events

Available actions:
- `create_event` - Add new event
- `delete_event` - Remove event
- `update_event` - Modify existing event
- `list_events` - View upcoming events

Example:
```
You: add lunch meeting Friday 12pm
Purr: Event added to your calendar.
```

---

### 2. Google Sheets Tool
**What it does:** Read/write to Google Sheets

Available actions:
- `read_sheet` - Get data from sheet
- `write_sheet` - Update values
- `append_row` - Add new row

Example:
```
You: add my expenses to the sheet
Purr: Saved your expense data to the spreadsheet.
```

---

### 3. Reminder Tool
**What it does:** Set reminders and notifications

Available actions:
- `create_reminder` - Set one-time reminder
- `create_recurring_reminder` - Repeating reminders
- `list_reminders` - View all reminders
- `delete_reminder` - Cancel reminder

Example:
```
You: remind me in 30 minutes to check email
Purr: Reminder set for 30 minutes from now.
```

---

## Troubleshooting

### Issue: "OpenAI API Error"
**Solution:** Check your `OPENAI_API_KEY` in config.py
```python
OPENAI_API_KEY = "sk-your-actual-key-here"
```
Get one from: https://platform.openai.com/account/api-keys

---

### Issue: "Tool not found"
**Solution:** Ensure tool is in `Tools_Modules/` folder and has proper initialization
Check debug output with `CORE_DEBUG_MODE = True`

---

### Issue: "No input received"
**Solution:** In terminal mode, make sure to press Enter after typing

---

## Advanced: Adding Your Own Tool

1. Create new file: `Tools_Modules/my_tool.py`
2. Define class with actions:
```python
class MyTool:
    NAME = "my_tool"
    ACTIONS = {
        "do_something": "Description of action"
    }
    
    def do_something(self, param1: str, param2: int) -> str:
        """Execute the action."""
        return f"Done with {param1} and {param2}"
```

3. The system auto-discovers it next startup!

---
## Machine Learning Intent Classification (Optional)

The project includes a standalone ML classifier for intent detection. This is **optional**—the system works fine without it!

### Test the ML Module

```bash
python Isolated_test.py
```

This will:
1. Load/train the spaCy text classifier
2. Enter interactive testing mode
3. Let you test classification accuracy
4. Collect feedback for model improvement

### Example Session

```
🎯 Training model with 15 samples...
✅ Training Complete!

📝 Enter a test phrase (or type 'exit' to quit): create a calendar event
🤖 Classification: task (Confidence: 0.93)

📝 Enter a test phrase (or type 'exit' to quit): what time is it
🤖 Classification: chat (Confidence: 0.81)

📝 Enter a test phrase (or type 'exit' to quit): remind me later
🤖 Classification: chat (Confidence: 0.65)    ← Low confidence!
🤔 AI is unsure. Help me classify this:
1️⃣ Task
2️⃣ Chat
3️⃣ Flag for Review
👉 Select (1, 2, or 3): 1            ← User feedback saved!
```

### Enable ML in Main System

To use ML classification with the main system:

```python
# In config.py
ML_AUTO_TRAIN = True
ML_AUTO_RETRAIN = True
ML_CLARIFICATION_MODE = True
```

Then restart main.py. The system will use ML to classify user input before routing to tools.

**Note:** See [ML_MODULE.md](ML_MODULE.md) for detailed ML documentation!

---

## Advanced: Adding Your Own Tool

1. Create `Tools_Modules/my_tool.py`
2. Define class with actions:
```python
class MyTool:
    NAME = "my_tool"
    ACTIONS = {
        "do_something": "Description of action"
    }
    
    def do_something(self, param1: str, param2: int) -> str:
        """Execute the action."""
        return f"Done with {param1} and {param2}"
```

3. The system auto-discovers it next startup! 🚀

---
## Questions?

- Check `config.py` for all available settings
- Enable `DEBUG_MODE = True` for detailed output
- Review examples in `Isolated_test.py`
