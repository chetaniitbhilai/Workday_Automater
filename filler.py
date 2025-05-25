import json
import google.generativeai as genai  # pip install google-generativeai
from selenium.webdriver.common.by import By
import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
import re 
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


info = {
    "Legal Name - first_name": "Chetan",
    "Legal Name - last_name": "Arora",
    "Preferred_name": " No",
    "email": "chetan@iitbhilai.ac.in",
    "secondary_email": "chetan@iitbhilai.ac.in",
    "linkedin": "https://www.linkedin.com/in/chetan-arora-119098267/",
    "github": "https://github.com/chetaniitbhilai",
    "portfolio": "https://portfolio-pi-lilac-37.vercel.app/",
    "resume_software": "data/resume1.pdf",
    "resume_ml_ai": "data/resume2.pdf",
    "cover_letter_software": "data/cover_letter_template.pdf",
    "cover_letter_ml_ai": "data/cover_letter_template.pdf",
    "How Did You Hear About Us?": "linkedin",
    "Have you ever been a regular employee or contingent worker": "Always No",
    "Country": "India",
    "Address Line 1": "Kanhar Hostel",
    "Address Line 2": "IIT Bhilai, Kutelabhata",
    "City or town": "Durg",
    "Postal code": "491002",
    "Country Phone Code": "India",
    "phone": "9355844091",
    "Phone extension": "None"
}

def fill_workday_form(driver, gemini_response):
    wait = WebDriverWait(driver, 10)
    
    # Convert list of dicts to a lookup dictionary
    response_data = {item['name']: item['answer'] for item in gemini_response}

    def safe_get(field_name, default=""):
        return response_data.get(field_name, default).strip() if response_data.get(field_name, default) else ""

    def safe_fill_text_field(element_id, value):
        """Safely fill a text field with retry mechanism for stale elements"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Re-find the element each time to avoid stale reference
                element = wait.until(EC.presence_of_element_located((By.ID, element_id)))
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Re-find element again after scroll to ensure freshness
                element = driver.find_element(By.ID, element_id)
                
                # Clear field using multiple methods
                element.click()
                time.sleep(0.2)
                
                # Re-find element after click
                element = driver.find_element(By.ID, element_id)
                element.clear()
                time.sleep(0.2)
                
                # Select all and delete (backup method)
                element = driver.find_element(By.ID, element_id)
                driver.execute_script("arguments[0].select();", element)
                time.sleep(0.2)
                
                element = driver.find_element(By.ID, element_id)
                element.send_keys("")
                time.sleep(0.2)
                
                # Use Ctrl+A and Delete as final backup
                from selenium.webdriver.common.keys import Keys
                element = driver.find_element(By.ID, element_id)
                element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.1)
                
                element = driver.find_element(By.ID, element_id)
                element.send_keys(Keys.DELETE)
                time.sleep(0.2)
                
                if value and value != "Empty":
                    element = driver.find_element(By.ID, element_id)
                    element.send_keys(str(value))
                    print(f"Filled {element_id} with: {value}")
                else:
                    print(f"Cleared {element_id}")
                
                # If we get here, operation was successful
                return
                    
            except Exception as e:
                if "stale element reference" in str(e) and attempt < max_retries - 1:
                    print(f"Stale element detected for {element_id}, retrying... (attempt {attempt + 1})")
                    time.sleep(1)
                    continue
                else:
                    print(f"Exception filling {element_id} after {attempt + 1} attempts: {e}")
                    break

    def safe_select_dropdown(element_id, option_text):
        """Safely select from dropdown using the provided pattern"""
        try:
            dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_btn)
            time.sleep(0.5)
            dropdown_btn.click()
            time.sleep(1)
            
            # Try multiple selectors for the option
            option_selectors = [
                f"//ul[contains(@class,'css')]/li[normalize-space()='{option_text}']",
                f"//li[normalize-space()='{option_text}']",
                f"//div[normalize-space()='{option_text}']",
                f"//*[normalize-space()='{option_text}']"
            ]
            
            for selector in option_selectors:
                try:
                    option = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                    option.click()
                    time.sleep(1)
                    print(f"Selected '{option_text}' from dropdown {element_id}")
                    return
                except:
                    continue
            
            print(f"Could not find option '{option_text}' in dropdown {element_id}")
        except Exception as e:
            print(f"Exception selecting dropdown {element_id} with option '{option_text}': {e}")

    def safe_select_radio(field_name, value):
        """Safely select radio button with enhanced selectors and retry mechanism"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Multiple selectors for finding the "No" radio button
                radio_selectors = [
                    # Try ID-based selectors first
                    "//input[@type='radio' and contains(@id, 'previousWorker') and (@value='false' or @value='no' or @value='No')]",
                    "//input[@type='radio' and contains(@id, 'previousWorker')][@value='false']",
                    "//input[@type='radio' and contains(@id, 'candidateIsPreviousWorker') and (@value='false' or @value='no')]",
                    
                    # Try label-based selectors
                    "//label[contains(text(), 'No') or contains(text(), 'NO')]/input[@type='radio']",
                    "//label[contains(text(), 'No') or contains(text(), 'NO')]//input[@type='radio']",
                    "//input[@type='radio']//following-sibling::*[contains(text(), 'No')]/../input",
                    "//input[@type='radio']//preceding-sibling::*[contains(text(), 'No')]/../input",
                    
                    # Try data attribute selectors
                    "//input[@type='radio' and @data-automation-id='radio_1']",
                    "//input[@type='radio' and @data-automation-id='radio_2']",
                    
                    # Try value-based selectors
                    "//input[@type='radio' and @value='false']",
                    "//input[@type='radio' and @value='no']",
                    "//input[@type='radio' and @value='No']",
                    
                    # Try positional selectors (often "No" is the second radio button)
                    "(//input[@type='radio'])[2]",
                    "(//input[@type='radio'])[last()]",
                    
                    # Generic radio button selectors as last resort
                    "//input[@type='radio' and not(@checked)]",
                ]
                
                for i, selector in enumerate(radio_selectors):
                    try:
                        print(f"Trying radio selector {i+1}: {selector}")
                        
                        # Wait for element and scroll into view
                        radio_btn = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                        driver.execute_script("arguments[0].scrollIntoView(true);", radio_btn)
                        time.sleep(0.5)
                        
                        # Re-find element to avoid stale reference
                        radio_btn = driver.find_element(By.XPATH, selector)
                        
                        # Check if already selected
                        if radio_btn.is_selected():
                            print(f"Radio button already selected with selector: {selector}")
                            return
                        
                        # Try different click methods
                        try:
                            # Method 1: Regular click
                            radio_btn.click()
                            print(f"Successfully clicked radio button with selector: {selector}")
                            return
                        except:
                            # Method 2: JavaScript click
                            driver.execute_script("arguments[0].click();", radio_btn)
                            print(f"Successfully clicked radio button with JavaScript using selector: {selector}")
                            return
                            
                    except Exception as inner_e:
                        print(f"Selector {i+1} failed: {str(inner_e)[:100]}")
                        continue
                
                # If no selector worked, try to find all radio buttons and click the appropriate one
                try:
                    all_radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                    print(f"Found {len(all_radios)} radio buttons total")
                    
                    for i, radio in enumerate(all_radios):
                        try:
                            # Get the radio button's context (nearby text)
                            parent = radio.find_element(By.XPATH, "./..")
                            context_text = parent.text.lower()
                            print(f"Radio {i+1} context: {context_text}")
                            
                            if "no" in context_text or "previous" in context_text:
                                driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                                time.sleep(0.5)
                                radio.click()
                                print(f"Successfully clicked radio button {i+1} based on context")
                                return
                        except:
                            continue
                            
                except Exception as e:
                    print(f"Failed to find radio buttons generically: {e}")
                
                print(f"Could not find 'No' radio button on attempt {attempt + 1}")
                
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    break
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Radio button selection failed on attempt {attempt + 1}, retrying: {e}")
                    time.sleep(2)
                    continue
                else:
                    print(f"Exception selecting radio for {field_name} after {max_retries} attempts: {e}")
                    break

    def safe_handle_checkbox(element_id, should_check):
        """Safely handle checkbox"""
        try:
            checkbox = wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            is_checked = checkbox.is_selected()
            
            if should_check and not is_checked:
                checkbox.click()
            elif not should_check and is_checked:
                checkbox.click()
        except Exception as e:
            print(f"Exception handling checkbox {element_id}: {e}")

    # Fill form fields based on the provided IDs
    
    # How Did You Hear About Us?
    how_hear_value = safe_get("How Did You Hear About Us?", info.get("How Did You Hear About Us?", ""))
    if "linkedin" in how_hear_value.lower():
        safe_select_dropdown("source--source", "LinkedIn")
    
    # Previously worked for company - Radio button
    prev_worker_value = safe_get("Have you previously worked for Automation Anywhere? If Yes, please answer the questions below.", 
                                info.get("Have you ever been a regular employee or contingent worker", ""))
    safe_select_radio("Have you previously worked for Automation Anywhere? If Yes, please answer the questions below.", prev_worker_value)
    
    # Country
    country_value = safe_get("Country", info.get("Country", ""))
    if country_value:
        safe_select_dropdown("country--country", country_value)
    
    # Name fields
    safe_fill_text_field("name--legalName--firstName", 
                        safe_get("Given Name(s)", info.get("Legal Name - first_name", "")))
    
    safe_fill_text_field("name--legalName--lastName", 
                        safe_get("Family Name", info.get("Legal Name - last_name", "")))
    
    safe_fill_text_field("name--legalName--firstNameLocal", 
                        safe_get("Local Given Name(s)", ""))
    
    safe_fill_text_field("name--legalName--lastNameLocal", 
                        safe_get("Local Family Name", ""))
    
    # Preferred name checkbox
    preferred_name = safe_get("I have a preferred name", info.get("Preferred_name", ""))
    should_check_preferred = "yes" in preferred_name.lower() if preferred_name else False
    safe_handle_checkbox("name--preferredCheck", should_check_preferred)
    
    # Address fields
    safe_fill_text_field("address--addressLine1", 
                        safe_get("Address Line 1", info.get("Address Line 1", "")))
    
    safe_fill_text_field("address--city", 
                        safe_get("City", info.get("City or town", "")))
    
    safe_fill_text_field("address--postalCode", 
                        safe_get("Postal Code", info.get("Postal code", "")))
    
    # Phone fields
    phone_type = safe_get("Phone Device Type", "Mobile")
    if phone_type:
        safe_select_dropdown("phoneNumber--phoneType", phone_type)
    
    # Country Phone Code
    country_phone = safe_get("Country Phone Code", info.get("Country Phone Code", ""))
    if country_phone:
        if "india" in country_phone.lower():
            safe_select_dropdown("phoneNumber--countryPhoneCode", "India (+91)")
    
    # Phone Number (remove any existing country code formatting)
    phone_number = safe_get("Phone Number", info.get("phone", ""))
    if phone_number:
        # Clean phone number - remove country codes and special characters
        clean_phone = phone_number.replace("+91-", "").replace("+91", "").replace("-", "").strip()
        safe_fill_text_field("phoneNumber--phoneNumber", clean_phone)
    
    # Phone Extension
    extension = safe_get("Phone Extension", info.get("Phone extension", ""))
    if extension and extension.lower() != "none":
        safe_fill_text_field("phoneNumber--extension", extension)
    
    # Click Save and Continue button
    try:
        save_continue_selectors = [
            "//button[contains(text(), 'Save and Continue')]",
            "//button[contains(text(), 'Save & Continue')]",
            "//button[@data-automation-id='saveAndContinue']",
            "//button[@data-automation-id='continueButton']",
            "//input[@type='submit' and contains(@value, 'Continue')]",
            "//button[contains(@class, 'continue')]"
        ]
        
        for selector in save_continue_selectors:
            try:
                save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
                time.sleep(1)
                save_btn.click()
                print("Clicked 'Save and Continue' button")
                time.sleep(2)
                break
            except:
                continue
        else:
            print("Could not find 'Save and Continue' button")
            
    except Exception as e:
        print(f"Exception clicking Save and Continue: {e}")
    
    print("Form filling completed!")

# Alternative function that uses the info dictionary directly
def fill_workday_form_direct(driver):
    """Fill form using info dictionary directly without gemini_response"""
    wait = WebDriverWait(driver, 10)
    
    def safe_fill_text_field(element_id, value):
        """Safely fill a text field with retry mechanism for stale elements"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Re-find the element each time to avoid stale reference
                element = wait.until(EC.presence_of_element_located((By.ID, element_id)))
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(0.5)
                
                # Re-find element again after scroll to ensure freshness
                element = driver.find_element(By.ID, element_id)
                
                # Clear field using multiple methods
                element.click()
                time.sleep(0.2)
                
                # Re-find element after click
                element = driver.find_element(By.ID, element_id)
                element.clear()
                time.sleep(0.2)
                
                # Select all and delete (backup method)
                element = driver.find_element(By.ID, element_id)
                driver.execute_script("arguments[0].select();", element)
                time.sleep(0.2)
                
                element = driver.find_element(By.ID, element_id)
                element.send_keys("")
                time.sleep(0.2)
                
                # Use Ctrl+A and Delete as final backup
                
                element = driver.find_element(By.ID, element_id)
                element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.1)
                
                element = driver.find_element(By.ID, element_id)
                element.send_keys(Keys.DELETE)
                time.sleep(0.2)
                
                if value:
                    element = driver.find_element(By.ID, element_id)
                    element.send_keys(str(value))
                    print(f"Filled {element_id} with: {value}")
                else:
                    print(f"Cleared {element_id}")
                
                # If we get here, operation was successful
                return
                    
            except Exception as e:
                if "stale element reference" in str(e) and attempt < max_retries - 1:
                    print(f"Stale element detected for {element_id}, retrying... (attempt {attempt + 1})")
                    time.sleep(1)
                    continue
                else:
                    print(f"Exception filling {element_id} after {attempt + 1} attempts: {e}")
                    break

    def safe_select_dropdown(element_id, option_text):
        try:
            dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, element_id)))
            dropdown_btn.click()
            time.sleep(1)
            
            option = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f"//ul[contains(@class,'css')]/li[normalize-space()='{option_text}']")
            ))
            option.click()
            time.sleep(1)
            print(f"Selected '{option_text}' from dropdown {element_id}")
        except Exception as e:
            print(f"Exception selecting dropdown {element_id}: {e}")

    # Fill using info dictionary
    safe_fill_text_field("name--legalName--firstName", info["Legal Name - first_name"])
    safe_fill_text_field("name--legalName--lastName", info["Legal Name - last_name"])
    safe_fill_text_field("address--addressLine1", info["Address Line 1"])
    safe_fill_text_field("address--city", info["City or town"])
    safe_fill_text_field("address--postalCode", info["Postal code"])
    safe_fill_text_field("phoneNumber--phoneNumber", info["phone"])
    
    # Dropdowns
    safe_select_dropdown("country--country", info["Country"])
    safe_select_dropdown("source--source", "LinkedIn")
    safe_select_dropdown("phoneNumber--countryPhoneCode", "India (+91)")
    safe_select_dropdown("phoneNumber--phoneType", "Mobile")
    
    # Radio button for previous worker
    try:
        radio_selectors = [
            "//input[@type='radio' and contains(@id, 'previousWorker') and @value='false']",
            "//input[@type='radio' and @value='false']",
            "//label[contains(text(), 'No')]/input[@type='radio']",
            "//label[contains(text(), 'No')]//input[@type='radio']",
            "//input[@type='radio'][2]"
        ]
        
        for selector in radio_selectors:
            try:
                radio_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                driver.execute_script("arguments[0].scrollIntoView(true);", radio_btn)
                time.sleep(0.5)
                radio_btn.click()
                print(f"Selected 'No' radio button")
                break
            except:
                continue
    except Exception as e:
        print(f"Exception selecting 'No' radio button: {e}")
    
    # Click Save and Continue button
    try:
        save_continue_selectors = [
            "//button[contains(text(), 'Save and Continue')]",
            "//button[contains(text(), 'Save & Continue')]",
            "//button[@data-automation-id='saveAndContinue']",
            "//button[@data-automation-id='continueButton']",
            "//input[@type='submit' and contains(@value, 'Continue')]",
            "//button[contains(@class, 'continue')]"
        ]
        
        for selector in save_continue_selectors:
            try:
                save_btn = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                driver.execute_script("arguments[0].scrollIntoView(true);", save_btn)
                time.sleep(1)
                save_btn.click()
                print("Clicked 'Save and Continue' button")
                time.sleep(2)
                break
            except:
                continue
        else:
            print("Could not find 'Save and Continue' button")
            
    except Exception as e:
        print(f"Exception clicking Save and Continue: {e}")
    
    print("Direct form filling completed!")









load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=gemini_api_key)

def generate_answers_gemini(form_fields_path, my_info_path):
    with open(form_fields_path, "r") as f:
        form_fields = json.load(f)
    with open(my_info_path, "r") as f:
        my_info = json.load(f)

    prompt = (
        "Given the following job application fields and my profile info, "
        "generate appropriate answers for each field.\n\n"
        f"Profile:\n{json.dumps(my_info, indent=2)}\n\n"
        f"Fields:\n{json.dumps(form_fields, indent=2)}\n\n"
        "Output a list of dictionaries with 'name' and 'answer'."
    )
    print(prompt)
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    print(response)
    try:
        raw_text = response.text  # .text is correct for Gemini output

        # Extract JSON content from inside the Markdown-style triple backticks
        match = re.search(r"```(?:json)?\n(.*?)```", raw_text, re.DOTALL)
        if match:
            json_string = match.group(1)
            return json.loads(json_string)
        else:
            print("[❌] Could not extract JSON from Gemini response.")
            print("[DEBUG] Raw Gemini text:", raw_text)
            return []
    except Exception as e:
        print("[❌] Failed to parse Gemini output")
        print("[DEBUG]", str(e))
        return []


