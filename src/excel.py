"""
Excel operations with user-based row-level access control.
"""
import pandas as pd
import json
import re
from pathlib import Path
from . import llm
from . import auth
from . import config

EXCEL_PATH = Path("excel_data")
EXCEL_PATH.mkdir(exist_ok=True)

ALLOWED_FILES = {
    "employee_data.xlsx": "username",
    "project_tracker.xlsx": "assigned_user",
    "time_tracking.xlsx": "employee",
    "performance_review.xlsx": "username"
}


def get_user_row(username: str, excel_file: str, target_user: str = None) -> int:
    """Find user's row in Excel file."""
    if excel_file not in ALLOWED_FILES:
        return None
    
    file_path = EXCEL_PATH / excel_file
    if not file_path.exists():
        return None
    
    df = pd.read_excel(file_path)
    user_col = ALLOWED_FILES[excel_file]
    
    if user_col not in df.columns:
        return None
    
    search_user = target_user if target_user and auth.is_admin(username) else username
    rows = df[df[user_col].astype(str).str.lower() == search_user.lower()]
    
    return rows.index[0] if not rows.empty else None


def get_columns(excel_file: str) -> list:
    """Get editable columns for file."""
    if excel_file not in ALLOWED_FILES:
        return []
    
    file_path = EXCEL_PATH / excel_file
    if not file_path.exists():
        return []
    
    df = pd.read_excel(file_path)
    user_col = ALLOWED_FILES[excel_file]
    return [c for c in df.columns if c != user_col]


def update_cell(username: str, excel_file: str, column: str, value: str, target_user: str = None) -> tuple:
    """Update a cell in user's row."""
    if excel_file not in ALLOWED_FILES:
        return False, f"File '{excel_file}' not allowed."
    
    file_path = EXCEL_PATH / excel_file
    if not file_path.exists():
        return False, f"File '{excel_file}' not found."
    
    df = pd.read_excel(file_path)
    edit_user = target_user if target_user and auth.is_admin(username) else username
    
    row = get_user_row(username, excel_file, target_user)
    if row is None:
        return False, f"No row for user '{edit_user}'."
    
    if column not in df.columns:
        return False, f"Column '{column}' not found."
    
    if column == ALLOWED_FILES[excel_file]:
        return False, "Cannot edit user identifier column."
    
    old_value = df.loc[row, column]
    df.loc[row, column] = value
    df.to_excel(file_path, index=False)
    
    msg = f"Updated '{column}' from '{old_value}' to '{value}'"
    if target_user and auth.is_admin(username):
        msg = f"Updated {target_user}'s " + msg[8:]
    
    return True, msg


def get_user_data(username: str, excel_file: str, target_user: str = None) -> tuple:
    """Get user's data from file."""
    if excel_file not in ALLOWED_FILES:
        return None, f"File '{excel_file}' not allowed."
    
    file_path = EXCEL_PATH / excel_file
    if not file_path.exists():
        return None, f"File '{excel_file}' not found."
    
    df = pd.read_excel(file_path)
    user_col = ALLOWED_FILES[excel_file]
    
    search_user = target_user if target_user and auth.is_admin(username) else username
    rows = df[df[user_col].astype(str).str.lower() == search_user.lower()]
    
    if rows.empty:
        return None, f"No data for '{search_user}'."
    
    return rows.iloc[0].to_dict(), "OK"


def get_all_data(username: str, excel_file: str) -> tuple:
    """Get all users' data (admin only)."""
    if not auth.is_admin(username):
        return None, "Admin access required."
    
    if excel_file not in ALLOWED_FILES:
        return None, f"File '{excel_file}' not allowed."
    
    file_path = EXCEL_PATH / excel_file
    if not file_path.exists():
        return None, f"File '{excel_file}' not found."
    
    df = pd.read_excel(file_path)
    return df.to_dict('records'), f"{len(df)} users"


def list_files() -> list:
    """List available Excel files."""
    return [f for f in ALLOWED_FILES if (EXCEL_PATH / f).exists()]


def parse_command(message: str) -> dict:
    """Parse Excel command from message."""
    result = {"action": "unknown", "file": None, "column": None, 
              "value": None, "target_user": None, "confidence": 0.0}
    
    msg = message.lower()
    
    # File extraction
    xlsx_match = re.search(r'(\w+\.xlsx)', message)
    if xlsx_match:
        result["file"] = xlsx_match.group(1)
    
    # Target user extraction
    for pattern in [r"for (\w+)", r"(\w+)'s", r"user (\w+)"]:
        match = re.search(pattern, msg)
        if match:
            result["target_user"] = match.group(1)
            break
    
    if any(w in msg for w in ["update", "change", "set", "edit", "modify"]):
        result["action"] = "update"
        if "to" in msg:
            parts = msg.split("to")
            if len(parts) >= 2:
                result["value"] = parts[-1].strip().strip("'\"").split(" in ")[0].strip()
        result["confidence"] = 0.7
    elif any(w in msg for w in ["show", "display", "get", "read", "what"]):
        result["action"] = "read_all" if any(w in msg for w in ["all users", "everyone"]) else "read"
        result["confidence"] = 0.6
    
    # Use Claude for better parsing if available
    if not llm.is_mock_mode() and result["confidence"] < 0.5:
        try:
            prompt = f"""Parse this Excel command and respond with JSON only:
            "{message}"
            
            Extract: action (update/read/read_all/list), file (.xlsx), column, value, target_user, confidence (0-1)
            Valid files: employee_data.xlsx, project_tracker.xlsx, time_tracking.xlsx, performance_review.xlsx
            """
            
            response = llm.chat([{"role": "user", "content": prompt}], 
                               system="You are a JSON parser. Respond only with valid JSON.")
            result = json.loads(response.strip())
        except:
            pass
    
    return result


def handle_excel_command(message: str, username: str) -> str:
    """Handle Excel command."""
    is_admin = auth.is_admin(username)
    cmd = parse_command(message)
    
    if cmd["confidence"] < 0.3:
        files = list_files()
        if files:
            examples = ["• 'Update my status to completed in project_tracker.xlsx'",
                       "• 'Show my data in employee_data.xlsx'"]
            if is_admin:
                examples.append("• 'Show all users in project_tracker.xlsx'")
            return f"ℹ️ Couldn't understand command. Files: {', '.join(files)}\n\nExamples:\n" + "\n".join(examples)
        return "ℹ️ No Excel files available."
    
    action = cmd.get("action")
    file_name = cmd.get("file")
    target_user = cmd.get("target_user")
    
    if action == "list":
        files = list_files()
        return f"📋 Available files: {', '.join(files)}" if files else "📋 No files available."
    
    if action == "read_all":
        if not is_admin:
            return "❌ Admin access required."
        if not file_name:
            return "❌ Please specify the file."
        
        data, msg = get_all_data(username, file_name)
        if data:
            lines = [f"{i+1}. " + " | ".join(f"{k}: {v}" for k, v in row.items()) for i, row in enumerate(data)]
            return f"📊 All users in {file_name}:\n" + "\n".join(lines)
        return f"❌ {msg}"
    
    if action == "read":
        if not file_name:
            return "❌ Please specify the file."
        if target_user and not is_admin:
            return "❌ Admin access required for other users' data."
        
        data, msg = get_user_data(username, file_name, target_user)
        if data:
            formatted = "\n".join(f"• {k}: {v}" for k, v in data.items())
            who = f"{target_user}'s" if target_user and is_admin else "Your"
            return f"📊 {who} data in {file_name}:\n{formatted}"
        return f"❌ {msg}"
    
    if action == "update":
        if not file_name:
            return "❌ Please specify the file."
        if target_user and not is_admin:
            return "❌ Admin access required to modify other users."
        
        column = cmd.get("column")
        value = cmd.get("value")
        
        if not column or not value:
            cols = get_columns(file_name)
            return f"❌ Specify column and value. Available: {', '.join(cols)}" if cols else "❌ Cannot get columns."
        
        success, msg = update_cell(username, file_name, column, value, target_user)
        return f"✅ {msg}" if success else f"❌ {msg}"
    
    return "ℹ️ Didn't understand the command."
