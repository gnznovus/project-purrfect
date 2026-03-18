"""
Project Purrfect 2.0 - AI Automation Framework
Main Entry Point

This module initializes and runs the Purrfect automation system.
It handles:
- Loading tools and core components
- Selecting input platform (Terminal or Telegram)
- Processing user input through the core engine
- Managing the main execution loop

Configuration:
- Set INPUT_PLATFORM in config.py to switch between "terminal" and "telegram"
- Customize debug modes and ML settings in config.py

Usage:
    python main.py              # Run in default mode (from config.py)
    
For Telegram bot mode:
    1. Update config.INPUT_PLATFORM = "telegram"
    2. Set TELEGRAM_BOT_TOKEN in config.py
    3. python main.py
"""

from Input_Modules.switch import Switch
from CORE_Modules.core import Core
from Input_Modules.telegram import TelegramBot
from Utils_Modules import toolslist
import config

"""
Main entrypoint (ML disabled).

Supported INPUT_PLATFORM values:
  - "terminal": CLI chat loop
  - "telegram": Telegram bot mode
"""

# ML functionality is disabled for now. Only Terminal and Telegram modes are supported.

# Load tools once (for Core/tool discovery) and start the selected input platform.
tools = toolslist.get_tools_list()  # noqa: F401 (loaded for side effects / future use)
switch = Switch()
core = Core(switch=switch)

if config.INPUT_PLATFORM == "terminal":
    print("[CORE] Running in Terminal Mode.")
    while True:
        user_input = switch.get_input()
        if not user_input:
            continue
        if isinstance(user_input, str) and user_input.lower() in ["exit", "quit"]:
            print("[CORE] Shutting down.")
            break
        response = core.process_input(user_input)
        print("Purr:", response)

elif config.INPUT_PLATFORM == "telegram":
    mode = "DM" if getattr(config, "TELEGRAM_DM", True) else "Group"
    print(f"[CORE] Running in Telegram {mode} Mode.")
    telegram_bot = TelegramBot(switch)
    telegram_bot.run()
else:
    print(f"[CORE] Unsupported INPUT_PLATFORM: {config.INPUT_PLATFORM}. Use 'terminal' or 'telegram'.")

