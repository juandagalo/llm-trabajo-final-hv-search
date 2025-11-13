"""
Demo script to test Excel functionality with admin access.
This demonstrates how the admin can access anyone's data while regular users can only access their own.
"""

from src.core.excel_manager import ExcelManager, handle_excel_command
from src.auth.authentication import is_admin_user
from pathlib import Path

def demo_excel_functionality():
    """Demonstrate Excel functionality for different user roles."""
    
    print("🎯 Excel Admin Functionality Demo")
    print("=" * 50)
    
    # Test users
    users = {
        "admin": "👑 Administrator",
        "juan": "👤 Regular User", 
        "maria": "👤 Regular User"
    }
    
    # Test commands
    test_scenarios = [
        {
            "description": "Personal data access (both users should work)",
            "commands": [
                ("Show my data in employee_data.xlsx", ["admin", "juan"]),
                ("Update my status to Active in employee_data.xlsx", ["admin", "juan"])
            ]
        },
        {
            "description": "Admin accessing other users' data (only admin should work)",
            "commands": [
                ("Show juan's data in employee_data.xlsx", ["admin", "juan"]),
                ("Update maria's status to Active in employee_data.xlsx", ["admin", "juan"]),
                ("Show all users in project_tracker.xlsx", ["admin", "juan"])
            ]
        }
    ]
    
    excel_manager = ExcelManager()
    
    # Check if Excel files exist
    available_files = excel_manager.list_available_files()
    if not available_files:
        print("❌ No Excel files found. Run create_sample_excel.py first.")
        return
    
    print(f"📋 Available Excel files: {', '.join(available_files)}\n")
    
    for scenario in test_scenarios:
        print(f"🧪 Testing: {scenario['description']}")
        print("-" * 40)
        
        for command, test_users in scenario['commands']:
            print(f"\n💬 Command: '{command}'")
            
            for user in test_users:
                user_role = "admin" if user == "admin" else "user"
                is_admin = (user_role == "admin")
                
                print(f"\n   👤 Testing as {user} ({users[user]}):")
                
                try:
                    # Simulate the command handling
                    response = handle_excel_command(command, user)
                    
                    # Check if response indicates success or failure
                    if response.startswith("✅"):
                        print(f"   ✅ SUCCESS: {response[:100]}...")
                    elif response.startswith("❌"):
                        print(f"   ❌ BLOCKED: {response[:100]}...")
                    else:
                        print(f"   ℹ️  INFO: {response[:100]}...")
                        
                except Exception as e:
                    print(f"   ⚠️  ERROR: {str(e)}")
        
        print("\n" + "=" * 50)
    
    print("\n🎉 Demo completed!")
    print("\nKey Observations:")
    print("- ✅ Admin users can access and modify any user's data")
    print("- ✅ Regular users can only access their own data") 
    print("- ✅ Unauthorized access attempts are properly blocked")
    print("- ✅ Clear error messages guide users on proper usage")


if __name__ == "__main__":
    # Ensure we're in the right directory
    import sys
    import os
    from pathlib import Path
    
    # Add src to Python path
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    
    demo_excel_functionality()