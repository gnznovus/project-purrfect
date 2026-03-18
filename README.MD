# Tools System — AI Automation Framework (Project Purrfect 2.0)

**Status:** Personal project (Late 2022 - End 2023) | Documented for portfolio (2026)
**Maturity:** Phase 0 prototype | Well-refined, not actively developed

## 📌 Overview

The **Tools System** is a modular AI-driven automation framework designed to execute tasks dynamically based on user intent.

Each tool is implemented as a **self-contained module**, allowing the system to:

* Dynamically discover capabilities
* Map requests to actions
* Execute workflows automatically

This architecture enables scalable automation across multiple domains (e.g., calendar, spreadsheets, reminders) without hardcoded integrations.

---

## 📊 Project Status: Phase 0 Prototype (Late 2022 - End 2023) ⚠️

**Timeline:**
- **Christmas 2022:** v1.0 built as pure learning exploration (no production focus)
- **Mid 2023 - End 2023:** Remade as v2.0 with refined learning goals, added Plug-and-Play system, strict modularization, Hive Mind coordination style
- 2026: Documented for portfolio + lessons learned

**Current Maturity:** Phase 0 (intentionally stopped here)
- Not actively developed
- Well-tested and refined over 2 years
- Code is solid, architecture is sound
- Known limitations accepted and documented

| Component | Status | Notes |
|-----------|--------|-------|
| **Core Architecture** | ✅ Complete | Modular tool system, working intent routing |
| **Terminal Interface** | ✅ Working | Tested, functional CLI chat |
| **Telegram Bot** | ✅ Working | Tested, both DM and group modes |
| **Intent Detection** | ⚠️ ~65% accurate | Works but not production-grade (Phase 1 target: 85%) |
| **Tool Execution** | ⚠️ Framework only | Architecture proven, tools are placeholders |
| **Multi-Tool Coordination** | ⚠️ Basic | Complex workflows need refinement |
| **Response Stability** | ⚠️ GPT-3.5 quirks | Model inconsistency from 2023 era (Phase 1: upgrade) |
| **ML Classification** | ✅ Functional | Works but disabled in main (Phase 1: optimize) |

### What This Means

✅ **You CAN run it** — It works end-to-end with proper credentials
⚠️ **You should NOT expect perfection** — Intent detection is ~65%, responses sometimes inconsistent
🔧 **Tools are placeholders** — Architecture supports real integrations, but Google Calendar etc. aren't implemented yet
📋 **Phase 1 is planned** — Clear roadmap for improvements (see ROADMAP.md)

---

## 🚀 Quick Start (Getting Started in 5 Minutes)

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- API Keys: OpenAI, Google APIs, Telegram Bot Token (optional)

### Installation

**1. Clone the repository:**
```bash
git clone https://github.com/gnznovus/project-purrfect.git
cd Project_Purrfect_2.0
```

**2. Create a Python virtual environment (recommended):**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure API Keys:**
```bash
# Copy the example config
cp config.example.py config.py

# Edit config.py with your actual API keys
#   - OpenAI API key from https://platform.openai.com/
#   - Google credentials from https://console.cloud.google.com/
#   - Telegram bot token from https://t.me/BotFather
```

**5. Run the project:**
```bash
# Uses config.py setting (default)
python main.py

# Or force specific platform:
python main.py --ter          # Terminal mode
python main.py --tele         # Telegram bot mode
```

### First Time Running?
- The project auto-creates necessary folders in `Storage/`
- Debug mode is enabled by default → you'll see what's happening
- Check `config.py` to customize behavior

---

## 🧠 Optional: Machine Learning Intent Classification

The project includes a fully functional **spaCy-based ML classifier** for automatic intent detection (task vs. chat). Currently disabled in main system but available for experimentation.

### Enable ML Mode

**1. In `config.py`, change:**
```python
ML_AUTO_TRAIN = True        # Enable ML training on startup
ML_AUTO_RETRAIN = True      # Enable incremental learning
ML_CLARIFICATION_MODE = True # Ask user to clarify low-confidence predictions
ML_CONFIDENCE_THRESHOLD = 0.70  # Confidence threshold for clarification
```

**2. Test the ML module in isolation:**
```bash
# Run the ML testing script
python Isolated_test.py

# The system will:
# 1. Load training data from Training_Data.txt
# 2. Train the spaCy model
# 3. Enter interactive testing mode for you to test classification
```

**3. Example ML Training Format (`Storage/Models/Training_Data.txt`):**
```
create a calendar event	task
what is the weather	chat
remind me in 30 minutes	task
tell me a joke	chat
```

### What the ML Module Does
- Classifies user input as either `task` (needs tool execution) or `chat` (conversational)
- Supports incremental learning via `Retrain_Data.txt`
- Uses user feedback to improve accuracy
- Built with spaCy's text classification pipeline

**Note:** ML is optional. The system works perfectly fine with just OpenAI's intent understanding!

---

## 🛠️ Expandable Tool System

The `Tools_Modules/` directory is designed as a plug-and-play architecture. Tools are auto-discovered at runtime.

### Structure of a Tool Module

```python
# Tools_Modules/my_action.py
class MyAction:
    """Tool for doing something specific."""
    
    # Metadata for discovery
    NAME = "My Action"
    ACTIONS = {
        "do_something": "Do something with params",
        "do_another": "Do another thing"
    }
    
    # Implementation
    def do_something(self, param1: str, param2: int) -> str:
        """Execute the action."""
        return f"Done with {param1} and {param2}"
```

### Adding a New Tool

1. Create `Tools_Modules/my_tool.py`
2. Define your tool class with `NAME` and `ACTIONS` metadata
3. Implement action methods
4. System auto-discovers it on next restart! 🚀

No registration files needed. No imports to add. Just follows the pattern.

---

### First Time Running?
- The project auto-creates necessary folders in `Storage/`
- Debug mode is enabled by default → you'll see what's happening
- Check `config.py` to customize behavior

---

## 🚀 Example: AI Automation System

### Problem

Many operational tasks (calendar management, data updates, reminders) require repetitive manual interaction across different systems.

### Solution

Designed a modular automation system that:

* Interprets user intent
* Dynamically selects appropriate tools
* Executes actions through structured modules

### Flow

User Input
→ Intent Mapping (AI / rule-based logic)
→ Tool Selection (dynamic module loading)
→ Action Execution (tool module)
→ Output (structured response / API-like result)

### Result

* Reduced repetitive manual workflows
* Enabled scalable tool integration
* Simplified extension for new automation use cases

### Tech

Python, modular architecture, dynamic module loading, API-style design

---

## 🗺️ What's Next?

**This is Phase 0. See [ROADMAP.md](ROADMAP.md) for Phase 1+ improvements:**

- Token optimization (reduce API costs)
- Intent accuracy boost (65% → 85%)
- Response stability improvements
- Real tool implementations (Google Calendar, Sheets, etc.)
- Multi-tool coordination

Phase 1 is planned but not urgent—architecture is solid, just needs refinement.

---

## 🧠 System Design Context

This system was developed before modern AI orchestration frameworks became widely available.

Core concepts implemented here — such as:

* Tool abstraction
* Dynamic execution
* Workflow orchestration

are now commonly seen in frameworks like LangChain and similar ecosystems.

This reflects a foundational understanding of automation system design without relying on prebuilt abstractions.

---

## 🏗️ Folder Structure

```
Project_Purrfect_2.0/
│── Tools_Modules/
│   ├── calendar.py        # Calendar-related actions
│   ├── sheet.py           # Google Sheets operations
│   ├── reminder.py        # Notifications & reminders
│   ├── __init__.py
│── Utils_Modules/
│── config.py              # Configuration and paths
│── main.py                # Core execution logic
│── README.md
```

---

## ⚙️ Tool System Architecture

### 1. Modular Tool Design

Each tool exists as a standalone file inside `Tools_Modules/`.

Example:

* `calendar.py` → handles all calendar operations
* `sheet.py` → handles spreadsheet interactions

---

### 2. Tool Metadata & Action Mapping

Each module defines its capabilities via metadata:

```python
NAME = "Calendar"
ACTIONS = {
    "create_event": "Create a new calendar event",
    "delete_event": "Delete an existing event",
    "update_event": "Modify an existing event"
}
```

This allows the system to:

* Discover available actions
* Map intent → executable function

---

### 3. Dynamic Tool Loading

Tools are automatically discovered and registered at runtime.

Benefits:

* No manual imports
* Plug-and-play extensibility
* Scalable architecture

---

### 4. Execution Layer

Each tool encapsulates its own logic:

```python
class MyTool:
    def do_something(self, params):
        return f"Doing something with {params}"
    
    def do_another_thing(self, params):
        return f"Doing another thing with {params}"
```

This design keeps:

* Logic isolated
* Interfaces consistent
* System maintainable

---

### 5. Configuration Management

Centralized configuration via `config.py`:

```python
TOOLS_STORAGE_PATH = "Storage/Tools/"
CALENDAR_STORAGE_PATH = TOOLS_STORAGE_PATH + "Calendar/"
SHEET_STORAGE_PATH = TOOLS_STORAGE_PATH + "Sheet/"
```

---

## 🛠️ Extending the System

### Add a New Tool

1. Create a new module in `Tools_Modules/`
2. Define metadata and actions
3. Implement logic inside the class

The system will automatically detect and integrate the tool.

---

## 🔄 Future Enhancements

* Integration with real external APIs
* Improved logging and error handling
* Multi-step workflow orchestration
* AI-driven decision-making improvements

---

## 💡 Key Design Principles

* **Modularity** — each tool is isolated and self-contained
* **Scalability** — new tools can be added without modifying core logic
* **Extensibility** — system grows via modules, not rewrites
* **Abstraction** — unified interface across different domains
* **Automation-first mindset** — reduce manual operations

---

## 🎯 Summary

This project demonstrates the design of a practical automation system that:

* Bridges user intent with executable actions
* Encapsulates logic into scalable modules
* Lays the foundation for AI-driven workflow automation

It reflects a system-level approach to building automation tools rather than relying on prebuilt frameworks.
