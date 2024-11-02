from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
import shutil
from urllib.parse import urlparse, unquote
import config  # Import the config file with credentials

# Set the base download directory dynamically based on the current user's home directory
user_home_dir = os.path.expanduser("~")
base_download_dir = os.path.join(user_home_dir, "Downloads")
aiub_folder = os.path.join(base_download_dir, "aiub_downloads")


# Ensure the aiub_downloads folder exists
if not os.path.exists(aiub_folder):
    os.makedirs(aiub_folder)

# Initialize the WebDriver (replace with the path to your driver executable if necessary)
driver = webdriver.Chrome()  # Or use `webdriver.Firefox()` if using Firefox

# Open the AIUB portal login page
driver.get("https://portal.aiub.edu/")

# Log in with username and password
driver.find_element(By.ID, "username").send_keys(config.USERNAME)
driver.find_element(By.ID, "password").send_keys(config.PASSWORD)
driver.find_element(By.TAG_NAME, "form").submit()

# Wait for the page to load after login
time.sleep(5)

# Check if login was successful by looking for the text "Welcome" on the page
try:
    # Search for an element that contains "Welcome"
    if "Welcome" in driver.page_source:
        print("Login successful!")
    else:
        print("Login failed.")
        driver.quit()  # Exit if login failed
        exit()
except NoSuchElementException:
    print("Login failed.")
    driver.quit()
    exit()

# Find all links with the text "TSF" and prepare the links list
tsf_links = []
links = driver.find_elements(By.LINK_TEXT, "TSF")
for link in links:
    url = link.get_attribute("href")
    new_url = url.replace("tsfTab", "notesTab")  # Modify link for notesTab
    tsf_links.append(new_url)

# Function to extract filename from URL
def get_filename_from_url(url):
    parsed_url = urlparse(url)
    return unquote(os.path.basename(parsed_url.path))

# Function to move the latest downloaded file to the destination folder
def move_latest_file(destination_folder, filename):
    time.sleep(5)  # Wait for the download to complete
    # Check for the most recent file in the download directory
    latest_file_path = os.path.join(base_download_dir, filename)
    if os.path.exists(latest_file_path):
        shutil.move(latest_file_path, os.path.join(destination_folder, filename))
        print(f"Moved file '{filename}' to '{destination_folder}'")
    else:
        print(f"File '{filename}' not found in download folder.")

# Visit each TSF link, create a folder based on the label, and download files if they don't already exist
for link in tsf_links:
    driver.get(link)
    time.sleep(5)

    # Get the label for the folder name
    label = driver.find_element(By.TAG_NAME, "label").text.strip()
    label_folder = os.path.join(aiub_folder, label)

    # Ensure the label-specific folder exists
    if not os.path.exists(label_folder):
        os.makedirs(label_folder)
        
    #downloading files for course {label}
    print(f"Downloading files for course: {label}")

    # Find download links and download each file if it doesn’t already exist in the label folder
    download_links = driver.find_elements(By.XPATH, "//a[contains(@href, 'DownloadDocument2')]")
    for download_link in download_links:
        download_url = download_link.get_attribute("href")
        filename = download_link.text

        label_file_path = os.path.join(label_folder, filename)
        base_download_file_path = os.path.join(base_download_dir, filename)

        # Check if file already exists in the label folder
        if os.path.exists(label_file_path):
            print(f"File '{filename}' already exists in '{label_folder}', skipping download.")
            continue  # Skip downloading this file

        # Download if file doesn't exist in label folder
        if os.path.exists(base_download_file_path):
            print(f"File '{filename}' already exists in '{base_download_dir}', moving to '{label_folder}'.")
            move_latest_file(label_folder, filename)  # Move the file to the label folder
        else:
            print(f"Downloading: {filename}")
            download_link.click()  # Start the download
            move_latest_file(label_folder, filename)  # Move the downloaded file to the label folder


# Close the browser
driver.quit()
