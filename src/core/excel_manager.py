"""
Excel Manager for LLM HV Search application.
Handles Excel file operations with user-based row-level access control.
"""
import pandas as pd
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import re
from ..config.settings import Config
from .llm_client import get_claude_client, get_chat_model, is_mock_mode
from ..auth.authentication import is_admin_user


class ExcelManager:
    """Manages Excel file operations with user-based access control."""
    
    def __init__(self):
        """Initialize Excel manager with default paths."""
        self.excel_files_path = Path("excel_data")
        self.excel_files_path.mkdir(exist_ok=True)
        
        # Define allowed Excel files and their user column names
        self.allowed_files = {
            "employee_data.xlsx": "username",
            "project_tracker.xlsx": "assigned_user", 
            "time_tracking.xlsx": "employee",
            "performance_review.xlsx": "username"
        }
    
    def get_user_row(self, username: str, excel_file: str, target_user: str = None) -> Optional[int]:
        """
        Get the row number that belongs to a specific user.
        
        Args:
            username: The logged-in user's username (for permission checking)
            excel_file: Name of the Excel file
            target_user: The user whose row to find (for admin access)
            
        Returns:
            Row index if found, None otherwise
        """
        try:
            if excel_file not in self.allowed_files:
                return None
                
            file_path = self.excel_files_path / excel_file
            if not file_path.exists():
                return None
                
            df = pd.read_excel(file_path)
            user_column = self.allowed_files[excel_file]
            
            if user_column not in df.columns:
                return None
                
            # Determine which user to search for
            search_user = target_user if target_user and is_admin_user(username) else username
            
            # Find rows where user column matches username (case-insensitive)
            user_rows = df[df[user_column].astype(str).str.lower() == search_user.lower()]
            if not user_rows.empty:
                return user_rows.index[0]
            return None
            
        except Exception as e:
            print(f"Error finding user row: {e}")
            return None
    
    def get_available_columns(self, excel_file: str) -> List[str]:
        """Get list of editable columns for a file."""
        try:
            if excel_file not in self.allowed_files:
                return []
                
            file_path = self.excel_files_path / excel_file
            if not file_path.exists():
                return []
                
            df = pd.read_excel(file_path)
            user_column = self.allowed_files[excel_file]
            
            # Return all columns except the user identifier column
            return [col for col in df.columns if col != user_column]
            
        except Exception as e:
            print(f"Error getting columns: {e}")
            return []
    
    def update_user_cell(self, username: str, excel_file: str, 
                        column: str, new_value: str, target_user: str = None) -> Tuple[bool, str]:
        """
        Update a specific cell for a user's row.
        
        Args:
            username: The logged-in user's username
            excel_file: Name of the Excel file
            column: Column name to update
            new_value: New value to set
            target_user: The user whose row to update (for admin access)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if excel_file not in self.allowed_files:
                return False, f"File '{excel_file}' is not allowed for editing."
            
            file_path = self.excel_files_path / excel_file
            if not file_path.exists():
                return False, f"File '{excel_file}' does not exist."
            
            df = pd.read_excel(file_path)
            
            # Determine target user and check permissions
            edit_user = target_user if target_user and is_admin_user(username) else username
            
            # Find user's row
            user_row = self.get_user_row(username, excel_file, target_user)
            if user_row is None:
                return False, f"No row found for user '{edit_user}' in '{excel_file}'."
            
            # Check if column exists
            if column not in df.columns:
                available_cols = self.get_available_columns(excel_file)
                return False, f"Column '{column}' not found. Available columns: {', '.join(available_cols)}"
            
            # Prevent editing of user identifier column
            user_column = self.allowed_files[excel_file]
            if column == user_column:
                return False, f"Cannot edit user identifier column '{column}'."
            
            # Update the cell
            old_value = df.loc[user_row, column]
            df.loc[user_row, column] = new_value
            
            # Save back to Excel
            df.to_excel(file_path, index=False)
            
            # Create appropriate success message
            if target_user and is_admin_user(username):
                return True, f"Successfully updated {target_user}'s '{column}' from '{old_value}' to '{new_value}'"
            else:
                return True, f"Successfully updated '{column}' from '{old_value}' to '{new_value}'"
            
        except Exception as e:
            return False, f"Error updating Excel: {str(e)}"
    
    def get_user_data(self, username: str, excel_file: str, target_user: str = None) -> Tuple[Optional[Dict], str]:
        """
        Get all data for a specific user.
        
        Args:
            username: The logged-in user's username
            excel_file: Name of the Excel file
            target_user: The user whose data to retrieve (for admin access)
            
        Returns:
            Tuple of (user_data: Dict or None, message: str)
        """
        try:
            if excel_file not in self.allowed_files:
                return None, f"File '{excel_file}' is not allowed for access."
                
            file_path = self.excel_files_path / excel_file
            if not file_path.exists():
                return None, f"File '{excel_file}' does not exist."
                
            df = pd.read_excel(file_path)
            user_column = self.allowed_files[excel_file]
            
            if user_column not in df.columns:
                return None, f"User column '{user_column}' not found in file."
            
            # Determine which user's data to retrieve
            search_user = target_user if target_user and is_admin_user(username) else username
            
            user_rows = df[df[user_column].astype(str).str.lower() == search_user.lower()]
            if not user_rows.empty:
                user_data = user_rows.iloc[0].to_dict()
                return user_data, "Data retrieved successfully"
            
            return None, f"No data found for user '{search_user}' in '{excel_file}'"
            
        except Exception as e:
            return None, f"Error getting user data: {str(e)}"
    
    def get_all_users_data(self, username: str, excel_file: str) -> Tuple[Optional[List[Dict]], str]:
        """
        Get data for all users in a file (admin only).
        
        Args:
            username: The logged-in user's username (must be admin)
            excel_file: Name of the Excel file
            
        Returns:
            Tuple of (all_data: List[Dict] or None, message: str)
        """
        try:
            if not is_admin_user(username):
                return None, "Admin access required to view all users' data."
            
            if excel_file not in self.allowed_files:
                return None, f"File '{excel_file}' is not allowed for access."
                
            file_path = self.excel_files_path / excel_file
            if not file_path.exists():
                return None, f"File '{excel_file}' does not exist."
                
            df = pd.read_excel(file_path)
            all_data = df.to_dict('records')
            
            return all_data, f"Retrieved data for {len(all_data)} users"
            
        except Exception as e:
            return None, f"Error getting all users data: {str(e)}"
    
    def get_available_users(self, username: str, excel_file: str) -> Tuple[Optional[List[str]], str]:
        """
        Get list of all users in a file (admin only).
        
        Args:
            username: The logged-in user's username (must be admin)
            excel_file: Name of the Excel file
            
        Returns:
            Tuple of (users_list: List[str] or None, message: str)
        """
        try:
            if not is_admin_user(username):
                return None, "Admin access required to list users."
            
            if excel_file not in self.allowed_files:
                return None, f"File '{excel_file}' is not allowed for access."
                
            file_path = self.excel_files_path / excel_file
            if not file_path.exists():
                return None, f"File '{excel_file}' does not exist."
                
            df = pd.read_excel(file_path)
            user_column = self.allowed_files[excel_file]
            
            if user_column not in df.columns:
                return None, f"User column '{user_column}' not found in file."
            
            users_list = df[user_column].astype(str).tolist()
            unique_users = list(set([u for u in users_list if u.strip()]))
            
            return unique_users, f"Found {len(unique_users)} users"
            
        except Exception as e:
            return None, f"Error getting users list: {str(e)}"
    
    def list_available_files(self) -> List[str]:
        """List all Excel files that the user can access."""
        available_files = []
        for filename in self.allowed_files.keys():
            file_path = self.excel_files_path / filename
            if file_path.exists():
                available_files.append(filename)
        return available_files


def parse_excel_command(message: str) -> Dict:
    """
    Parse natural language message to extract Excel operation intent.
    
    Args:
        message: User's natural language message
        
    Returns:
        Dictionary with parsed command details
    """
    if is_mock_mode():
        # Simple regex-based parsing for demo mode
        message_lower = message.lower()
        
        result = {
            "action": "unknown",
            "file": None,
            "column": None,
            "value": None,
            "target_user": None,
            "confidence": 0.0
        }
        
        # Check for update operations
        if any(word in message_lower for word in ["update", "change", "set", "edit", "modify"]):
            result["action"] = "update"
            
            # Extract file name (look for .xlsx files)
            xlsx_match = re.search(r'(\w+\.xlsx)', message)
            if xlsx_match:
                result["file"] = xlsx_match.group(1)
            
            # Try to extract target user for admin commands
            for pattern in ["for (\\w+)", "(\\w+)'s", "user (\\w+)"]:
                user_match = re.search(pattern, message_lower)
                if user_match:
                    result["target_user"] = user_match.group(1)
                    break
            
            # Try to extract column and value
            if "to" in message_lower:
                parts = message_lower.split("to")
                if len(parts) >= 2:
                    result["value"] = parts[-1].strip().strip("'\"")
            
            result["confidence"] = 0.7
            
        # Check for read operations  
        elif any(word in message_lower for word in ["show", "display", "get", "read", "what"]):
            # Check if it's a request for all users data (admin only)
            if any(word in message_lower for word in ["all users", "everyone", "all data", "everyone's"]):
                result["action"] = "read_all"
            else:
                result["action"] = "read"
            
            xlsx_match = re.search(r'(\w+\.xlsx)', message)
            if xlsx_match:
                result["file"] = xlsx_match.group(1)
            
            # Try to extract target user for admin commands
            for pattern in ["for (\\w+)", "(\\w+)'s", "user (\\w+)"]:
                user_match = re.search(pattern, message_lower)
                if user_match:
                    result["target_user"] = user_match.group(1)
                    break
                
            result["confidence"] = 0.6
            
        return result
    
    # Use Claude for better parsing when available
    try:
        client = get_claude_client()
        
        extraction_prompt = f"""
        Parse this user request for Excel operations and respond with JSON only:
        "{message}"
        
        Extract:
        - action: "update", "read", "read_all", or "list"  
        - file: Excel filename mentioned (must end with .xlsx)
        - column: Column name to modify (for updates)
        - value: New value to set (for updates)
        - target_user: Username mentioned for admin operations (optional)
        - confidence: Float between 0.0-1.0 for parsing confidence
        
        Example valid filenames: employee_data.xlsx, project_tracker.xlsx, time_tracking.xlsx
        
        Respond only with valid JSON, no other text.
        """
        
        response = client.messages.create(
            model=get_chat_model(),
            max_tokens=512,
            system="You are a JSON parser. Respond only with valid JSON.",
            messages=[{"role": "user", "content": extraction_prompt}]
        )
        
        parsed = json.loads(response.content[0].text.strip())
        return parsed
        
    except Exception as e:
        print(f"Error parsing with OpenAI: {e}")
        # Fallback to simple parsing
        return {
            "action": "unknown",
            "file": None, 
            "column": None,
            "value": None,
            "target_user": None,
            "confidence": 0.0
        }


def handle_excel_command(message: str, username: str) -> str:
    """
    Handle Excel editing commands through natural language.
    
    Args:
        message: User's natural language message
        username: Current logged-in username
        
    Returns:
        Response message for the user
    """
    excel_manager = ExcelManager()
    user_is_admin = is_admin_user(username)
    
    # Parse the command
    parsed_command = parse_excel_command(message)
    
    if parsed_command["confidence"] < 0.3:
        available_files = excel_manager.list_available_files()
        if available_files:
            files_list = ", ".join(available_files)
            base_examples = [
                "• 'Update my status to completed in project_tracker.xlsx'",
                "• 'Show my data in employee_data.xlsx'", 
                "• 'Set my progress to 75% in project_tracker.xlsx'"
            ]
            
            admin_examples = []
            if user_is_admin:
                admin_examples = [
                    "• 'Update juan's status to completed in project_tracker.xlsx'",
                    "• 'Show maria's data in employee_data.xlsx'",
                    "• 'Show all users in project_tracker.xlsx'"
                ]
            
            all_examples = base_examples + admin_examples
            examples_text = "\n".join(all_examples)
            
            return (f"ℹ️ I couldn't understand your Excel command clearly. "
                   f"Available files: {files_list}\n\n"
                   f"Try commands like:\n{examples_text}")
        else:
            return "ℹ️ No Excel files are currently available for editing."
    
    action = parsed_command.get("action")
    file_name = parsed_command.get("file")
    target_user = parsed_command.get("target_user")
    
    # Handle list action
    if action == "list":
        available_files = excel_manager.list_available_files()
        if available_files:
            return f"📋 Available Excel files: {', '.join(available_files)}"
        else:
            return "📋 No Excel files are currently available."
    
    # Handle read all users action (admin only)
    if action == "read_all":
        if not user_is_admin:
            return "❌ Admin access required to view all users' data."
            
        if not file_name:
            return "❌ Please specify which Excel file to read from."
        
        all_data, message_result = excel_manager.get_all_users_data(username, file_name)
        if all_data:
            # Format the data nicely
            formatted_data = []
            for i, user_data in enumerate(all_data, 1):
                user_line = f"{i}. " + " | ".join([f"{key}: {value}" for key, value in user_data.items()])
                formatted_data.append(user_line)
            
            return f"📊 All users in {file_name}:\n" + "\n".join(formatted_data)
        else:
            return f"❌ {message_result}"
    
    # Handle read action
    if action == "read":
        if not file_name:
            return "❌ Please specify which Excel file to read from."
        
        # Check if admin is trying to read another user's data
        if target_user and not user_is_admin:
            return "❌ Admin access required to view other users' data."
            
        user_data, message_result = excel_manager.get_user_data(username, file_name, target_user)
        if user_data:
            # Format the data nicely
            formatted_data = "\n".join([f"• {key}: {value}" for key, value in user_data.items()])
            
            if target_user and user_is_admin:
                return f"📊 {target_user}'s data in {file_name}:\n{formatted_data}"
            else:
                return f"📊 Your data in {file_name}:\n{formatted_data}"
        else:
            return f"❌ {message_result}"
    
    # Handle update action
    if action == "update":
        if not file_name:
            return "❌ Please specify which Excel file to update."
        
        # Check if admin is trying to update another user's data
        if target_user and not user_is_admin:
            return "❌ Admin access required to modify other users' data."
            
        column = parsed_command.get("column")
        value = parsed_command.get("value")
        
        if not column or not value:
            available_columns = excel_manager.get_available_columns(file_name)
            if available_columns:
                return (f"❌ Please specify both column and value to update. "
                       f"Available columns in {file_name}: {', '.join(available_columns)}")
            else:
                return f"❌ Could not access columns for {file_name}."
        
        success, result_message = excel_manager.update_user_cell(username, file_name, column, value, target_user)
        
        if success:
            return f"✅ {result_message}"
        else:
            return f"❌ {result_message}"
    
    return "ℹ️ I didn't understand the Excel operation. Please try again with a clearer command."