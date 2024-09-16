import os
import sys
from datetime import datetime, timedelta

def create_folders(start_date_str, end_date_str):
    # Parse the input strings into datetime objects
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    # Loop through each day and create a folder for each date
    current_date = start_date
    while current_date <= end_date:
        folder_name = current_date.strftime('%Y-%m-%d')  # Format the folder name
        os.makedirs(folder_name, exist_ok=True)  # Create the folder if it doesn't exist
        print(f"Created folder: {folder_name}")
        current_date += timedelta(days=1)  # Move to the next day

if __name__ == '__main__':
    # Check if the correct number of arguments are passed
    if len(sys.argv) != 3:
        print("Usage: python script.py <start_date> <end_date>")
        print("Example: python script.py 2024-09-10 2024-09-20")
    else:
        start_date = sys.argv[1]
        end_date = sys.argv[2]
        create_folders(start_date, end_date)
