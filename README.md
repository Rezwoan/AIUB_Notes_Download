Automated Semester File Downloader
This Python script automates the download of all files needed for the current semester from the AIUB portal. It organizes these files by course, creating separate folders for easy access.

Requirements
To run this script, you’ll need Python installed on your system. If you don’t have it installed, you can download it from the official website: https://www.python.org/downloads/.

This script uses Selenium to automate browser interactions. Follow the steps below to set up all necessary dependencies:

1. Install Python Packages
   Run the following command to install the required packages listed in requirements.txt:

pip install -r requirements.txt

Configuration
Before running the script, update the config.py file with your AIUB portal credentials:

# config.py

USERNAME = "your_aiub_id"
PASSWORD = "your_portal_password"
Replace your_aiub_id with your AIUB ID and your_portal_password with your portal password.

How to Use
Open Command Prompt or Terminal.

Navigate to the directory where main.py is located.

Run the Script

Execute the following command:

python main.py
File Organization
The script will download all files for the current semester.
Files will be saved in a new folder, aiub_downloads, created within your system’s Downloads directory.
Inside aiub_downloads, each course will have its own folder containing the respective files, making it easy to locate materials for each subject.
This organized structure ensures all semester materials are accessible in one place.
