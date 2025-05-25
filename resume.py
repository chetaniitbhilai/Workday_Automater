from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time
import json

def load_user_info(file_path="my_info.json"):
    """Load user information from the JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[❌] Error: {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"[❌] Error: {file_path} is not a valid JSON file.")
        return None


def upload_resume(driver,resume_type="resume_software"):
    file_input = driver.find_element("css selector", "input[data-automation-id='file-upload-input-ref']")
    file_input.send_keys('/home/chetan/Documents/projects/resume_filler/data/resume1.pdf')

    time.sleep(10)

    continue_button = driver.find_element(By.CSS_SELECTOR, "button[data-automation-id='pageFooterNextButton']")
    continue_button.click()