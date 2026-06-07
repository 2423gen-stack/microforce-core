import ast
import os
from typing import Dict, Tuple

def extract_model_definitions(tree: ast.AST) -> Dict[str, str]:
    """
    Extracts class definitions as string representations of their AST,
    to easily check if existing models are modified or deleted.
    """
    models = {}
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            models[node.name] = ast.unparse(node)
    return models

def validate_schema_code(new_code: str, current_code_path: str) -> Tuple[bool, str]:
    """
    Validates that:
    1. The new code only imports allowed modules (sqlalchemy, src.database.models_core).
    2. The new code does not contain malicious executions (only imports and class definitions).
    3. Existing models are not modified or deleted (Plan A).
    """
    try:
        new_tree = ast.parse(new_code)
    except SyntaxError as e:
        return False, f"Syntax error in new schema: {e}"

    allowed_imports = {"sqlalchemy", "src.database.models_core"}
    
    for node in ast.iter_child_nodes(new_tree):
        # Allow import statements
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            module_name = node.module if isinstance(node, ast.ImportFrom) else None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    is_allowed = False
                    for allowed in allowed_imports:
                        if alias.name == allowed or alias.name.startswith(allowed + "."):
                            is_allowed = True
                            break
                    if not is_allowed:
                        return False, f"Security Error: Import of module '{alias.name}' is not allowed."
            elif module_name:
                is_allowed = False
                for allowed in allowed_imports:
                    if module_name == allowed or module_name.startswith(allowed + "."):
                        is_allowed = True
                        break
                if not is_allowed:
                    return False, f"Security Error: Import from module '{module_name}' is not allowed."
        
        # Allow class definitions (must inherit from Base)
        elif isinstance(node, ast.ClassDef):
            base_names = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    base_names.append(base.id)
                elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                    base_names.append(base.attr)
            
            if "Base" not in base_names:
                return False, f"Validation Error: Class '{node.name}' must inherit from 'Base'."
                
        # Reject anything else at module level (assignments, function calls, etc.)
        else:
            return False, f"Security Error: Statement of type '{type(node).__name__}' is not allowed at module level."

    # Plan A validation (Append-only schema changes)
    if os.path.exists(current_code_path):
        with open(current_code_path, "r") as f:
            current_code = f.read()
        
        try:
            current_tree = ast.parse(current_code)
            current_models = extract_model_definitions(current_tree)
            new_models = extract_model_definitions(new_tree)
            
            for model_name, old_source in current_models.items():
                if model_name not in new_models:
                    return False, f"Plan A Violation: Table/Model '{model_name}' cannot be deleted."
                
                # Check if the class definition changed (comparing unparsed source code)
                if new_models[model_name] != old_source:
                    return False, f"Plan A Violation: Table/Model '{model_name}' cannot be modified. Only new tables can be added."
        except Exception:
            # If current models_ai.py is corrupt or empty, we allow overwriting with valid code
            pass

    return True, "Success"
