"""
Sample Excel file generator for testing the Excel Manager functionality.
Run this script to create sample Excel files with user data.
"""
import pandas as pd
from pathlib import Path

def create_sample_excel_files():
    """Create sample Excel files for testing."""
    excel_data_path = Path("excel_data")
    excel_data_path.mkdir(exist_ok=True)
    
    # Employee Data
    employee_data = {
        "username": ["admin", "juan", "maria", "carlos", "ana"],
        "full_name": ["Admin User", "Juan Pérez", "María González", "Carlos Rodríguez", "Ana López"],
        "department": ["Management", "IT", "HR", "QA", "Development"],
        "position": ["System Admin", "Developer", "HR Manager", "QA Tester", "Senior Developer"],
        "status": ["Active", "Active", "Active", "Active", "On Leave"],
        "email": ["admin@company.com", "juan@company.com", "maria@company.com", "carlos@company.com", "ana@company.com"]
    }
    
    # Project Tracker
    project_data = {
        "assigned_user": ["admin", "juan", "maria", "carlos", "ana"],
        "project_name": ["System Oversight", "Web App Redesign", "Employee Onboarding", "Test Automation", "API Development"],
        "status": ["Ongoing", "In Progress", "Completed", "Planning", "In Progress"],
        "progress": ["90%", "75%", "100%", "25%", "60%"],
        "deadline": ["2025-12-31", "2025-12-15", "2025-11-30", "2025-12-31", "2025-11-25"],
        "notes": ["Monitoring all projects", "UI mockups completed", "Process documented", "Framework selection pending", "Authentication module done"]
    }
    
    # Time Tracking
    time_data = {
        "employee": ["admin", "juan", "maria", "carlos", "ana"],
        "date": ["2025-11-12", "2025-11-12", "2025-11-12", "2025-11-12", "2025-11-12"],
        "hours_worked": [8.0, 8.0, 7.5, 8.0, 6.0],
        "project": ["System Administration", "Web App Redesign", "Employee Onboarding", "Test Automation", "API Development"],
        "task_description": ["System monitoring", "Frontend development", "Documentation", "Test planning", "API endpoints"],
        "status": ["Approved", "Submitted", "Approved", "Draft", "Submitted"]
    }
    
    # Performance Review
    performance_data = {
        "username": ["admin", "juan", "maria", "carlos", "ana"],
        "review_period": ["Q3 2025", "Q3 2025", "Q3 2025", "Q3 2025", "Q3 2025"],
        "overall_rating": ["Outstanding", "Excellent", "Good", "Very Good", "Excellent"],
        "goals_achieved": ["5/5", "4/4", "3/4", "3/3", "5/5"],
        "feedback": ["Exceptional leadership", "Outstanding performance", "Consistent delivery", "Good technical skills", "Leadership qualities"],
        "next_review": ["2026-02-15", "2026-02-15", "2026-02-15", "2026-02-15", "2026-02-15"]
    }
    
    # Create DataFrames and save to Excel
    files_data = {
        "employee_data.xlsx": employee_data,
        "project_tracker.xlsx": project_data,
        "time_tracking.xlsx": time_data,
        "performance_review.xlsx": performance_data
    }
    
    for filename, data in files_data.items():
        df = pd.DataFrame(data)
        file_path = excel_data_path / filename
        df.to_excel(file_path, index=False)
        print(f"✅ Created {filename} with {len(df)} rows")

if __name__ == "__main__":
    create_sample_excel_files()
    print("🎉 All sample Excel files created successfully!")