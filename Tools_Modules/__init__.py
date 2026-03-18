import os
import importlib.util
import inspect
import config

TOOLS_DIR = os.path.dirname(__file__)  # Path to Tools_Modules

def get_tools():
    """Dynamically load tools, available actions, and required parameters from Tools_Modules."""
    tools = {}  # Dictionary to hold tools categorized

    # Loop through each folder (category) in Tools_Modules
    for category in os.listdir(TOOLS_DIR):
        category_path = os.path.join(TOOLS_DIR, category)

        # Skip non-directory files and internal folders like '__pycache__'
        if not os.path.isdir(category_path) or category.startswith("__"):
            continue

        tools[category] = {}  # Store tools for this category

        # Loop through each Python file in the category folder
        for filename in os.listdir(category_path):
            if filename.endswith(".py") and filename != "__init__.py":
                tool_name = filename.replace(".py", "").lower()  # Use lowercase for consistency
                tool_path = os.path.join(category_path, filename)

                # Dynamically load the tool module
                spec = importlib.util.spec_from_file_location(tool_name, tool_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Get tool metadata (name, description, actions)
                meta_name = getattr(module, "NAME", tool_name).lower()
                tool_class_name = meta_name.replace("-", " ").title().replace(" ", "")  # Format class name
                tool_class = getattr(module, tool_class_name, None)  # Get class by name
                tool_actions = getattr(module, "ACTIONS", {})  # Fetch available actions
                tool_defined_params = getattr(module, "PARAMS", {})  # Allow manual parameter definitions

                # Extract required parameters dynamically from each action
                action_params = {}
                if tool_class:
                    for action_name in tool_actions.keys():
                        if hasattr(tool_class, action_name):
                            method = getattr(tool_class, action_name)
                            sig = inspect.signature(method)

                            # Extract only required parameters (ignore `self`)
                            required_params = [
                                param for param, param_obj in sig.parameters.items()
                                if param != "self" and param_obj.default is param_obj.empty  # ✅ Only required params
                            ]
                            action_params[action_name] = required_params

                # Merge manual PARAMS definitions (manual overrides dynamic detection if needed)
                for action_name, param_list in tool_defined_params.items():
                    if action_name not in action_params:  # If not dynamically extracted, use manual definition
                        action_params[action_name] = param_list

                # Register tool if class is found
                if tool_class:
                    tools[category][meta_name] = {
                        "name": meta_name,
                        "display_name": getattr(module, "NAME", meta_name),
                        "description": getattr(module, "DESCRIPTION", "No description available."),
                        "module_path": f"Tools_Modules.{category}.{tool_name}",
                        "module_class": tool_class,  # Store actual class reference
                        "actions": tool_actions,  # Store available actions
                        "params": action_params  # ✅ Store extracted required parameters without `self`
                    }
                else:
                    print(f"[Error] Could not find class '{tool_class_name}' in {module.__name__}")

    # ✅ Unified Debug Output: Print all tools, actions, and parameters in one place
    if config.TOOLS_DEBUG_MODE:
        print("\n[Debug] 🔍 Loaded Tools Summary:")
        for category, category_tools in tools.items():
            print(f"\n📂 Category: {category}")
            for tool in category_tools.values():
                class_status = "✅ Found" if tool["module_class"] else "❌ Not Found"
                print(f"- 🛠️ {tool['display_name']} → {tool['module_path']} ({class_status})")
                print(f"  🔹 Actions: {list(tool['actions'].keys())}")  # Print available actions
                print(f"  🔹 Params: {tool['params']}")  # ✅ Print extracted parameters

    return tools  # Return tools categorized dictionary
