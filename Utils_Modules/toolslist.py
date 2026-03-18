from Tools_Modules import get_tools  # Import tool detection function

def get_tools_list():
    """Return the current tools dictionary (always fresh on startup)."""
    return get_tools()  # Always fresh

def get_tool_labels():
    """Returns dynamically generated labels for ML using CORE's tool loading."""
    from CORE_Modules.core import Core
    from Input_Modules.switch import Switch

    # ✅ Initialize CORE to reuse tool loading
    switch = Switch()
    core = Core(switch)
    tools = core.load_tools()  # ✅ Fetch pre-flattened tool data from CORE

    # ✅ Convert tool names and actions to use underscores for SpaCy
    main_labels = [tool.replace(" ", "_") for tool in tools] + ["chat"]
    subcategories = {tool.replace(" ", "_"): [action.replace(" ", "_") for action in tools[tool].get("actions", [])] for tool in tools}
    all_labels = main_labels + [label for sublist in subcategories.values() for label in sublist]

    return main_labels, subcategories, all_labels
