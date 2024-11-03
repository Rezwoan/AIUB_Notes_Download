from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import os
import shutil
from urllib.parse import urlparse, unquote


class AIUBDownloader:
    def __init__(self):
        # Set up Chrome options for headless background execution
        chrome_options = Options()
        chrome_options.add_argument("--headless")        
        chrome_options.add_argument("--disable-gpu")     
        chrome_options.add_argument("--no-sandbox")      
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")     
        chrome_options.add_argument("--window-size=1920,1080")  

        # Suppress the "DevTools listening on..." message by redirecting logs
        service = Service(log_path=os.devnull)

        # Initialize the WebDriver
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Set up download paths
        user_home_dir = os.path.expanduser("~")
        self.base_download_dir = os.path.join(user_home_dir, "Downloads")
        self.aiub_folder = os.path.join(self.base_download_dir, "aiub_downloads")
        self.script_directory = os.path.dirname(os.path.abspath(__file__))

        # Ensure the aiub_downloads folder exists
        if not os.path.exists(self.aiub_folder):
            os.makedirs(self.aiub_folder)

    def login(self, user_id, password):
        """Log into the AIUB portal using the provided user ID and password."""
        self.driver.get("https://portal.aiub.edu/")
        time.sleep(3)
        
        self.driver.find_element(By.ID, "username").send_keys(user_id)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.TAG_NAME, "form").submit()
        
        time.sleep(3)

        # Check if login was successful
        if "Welcome" in self.driver.page_source:
            print("Login successful!")
            return True
        else:
            print("Login failed. Please try again.")
            return False

    def get_tsf_links(self):
        """Find all TSF links and prepare a list of modified URLs."""
        tsf_links = []
        links = self.driver.find_elements(By.LINK_TEXT, "TSF")
        for link in links:
            url = link.get_attribute("href")
            new_url = url.replace("tsfTab", "notesTab")  # Modify link for notesTab
            tsf_links.append(new_url)
        return tsf_links

    def get_filename_from_url(self, url):
        """Extract filename from the given URL."""
        parsed_url = urlparse(url)
        return unquote(os.path.basename(parsed_url.path))

    def move_latest_file(self, destination_folder, filename):
        """Move the latest downloaded file to the destination folder."""
        time.sleep(5)  # Wait for the download to complete
        latest_file_path = os.path.join(self.base_download_dir, filename)
        if os.path.exists(latest_file_path):
            shutil.move(latest_file_path, os.path.join(destination_folder, filename))
            print(f"Moved file '{filename}' to '{destination_folder}'")
        else:
            print(f"File '{filename}' not found in download folder.")

    def download_files(self, tsf_links):
        """Visit each TSF link, download files, and organize them into folders."""
        for link in tsf_links:
            self.driver.get(link)
            time.sleep(5)
            
            # Get the label for the folder name
            label = self.driver.find_element(By.TAG_NAME, "label").text.strip()
            label_folder = os.path.join(self.aiub_folder, label)

            # Ensure the label-specific folder exists
            if not os.path.exists(label_folder):
                os.makedirs(label_folder)
            
            print(f"Downloading files for course: {label}")

            # Find download links and download each file if it doesn’t already exist
            download_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'DownloadDocument2')]")
            for download_link in download_links:
                download_url = download_link.get_attribute("href")
                filename = download_link.text

                label_file_path = os.path.join(label_folder, filename)
                base_download_file_path = os.path.join(self.base_download_dir, filename)

                # Check if file already exists in the label folder
                if os.path.exists(label_file_path):
                    print(f"File '{filename}' already exists, skipping download.")
                    continue

                # Download if file doesn't exist in label folder
                if os.path.exists(base_download_file_path):
                    print(f"File '{filename}' already exists in '{self.base_download_dir}', moving to '{label_folder}'.")
                    self.move_latest_file(label_folder, filename)
                else:
                    print(f"Downloading: {filename}")
                    download_link.click()
                    self.move_latest_file(label_folder, filename)

    def move_folder_to_script_directory(self):
        """Move the AIUB downloads folder to the script directory."""
        try:
            shutil.move(self.aiub_folder, self.script_directory)
            print(f"Folder moved successfully to {self.script_directory}")
        except FileNotFoundError:
            print("Source folder does not exist.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        """Close the WebDriver."""
        self.driver.quit()


def main():
    downloader = AIUBDownloader()
    
    # Ask for user input for ID and password
    while True:
        user_id = input("Enter your AIUB ID (or type 'q' to quit): ")
        if user_id.lower() in ["q", "quit"]:
            print("Exiting the script.")
            downloader.close()
            exit()
        
        password = input("Enter your password: ")
        if downloader.login(user_id, password):
            break

    # Download files
    tsf_links = downloader.get_tsf_links()
    downloader.download_files(tsf_links)

    # Move the folder to the script directory
    downloader.move_folder_to_script_directory()

    # Close the browser
    downloader.close()


if __name__ == "__main__":
    main()
