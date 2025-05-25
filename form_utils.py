#!/usr/bin/env python3


import time
import json
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """Set up and return a configured Chrome WebDriver"""
    chrome_options = Options()
    # Uncomment the line below to run in headless mode (no browser window)
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    # Add additional options that might help with loading issues
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def wait_for_page_load(driver, timeout=120):
    """
    Wait for the page to fully load with multiple fallback selectors
    
    Args:
        driver: Selenium WebDriver instance
        timeout: Maximum time to wait in seconds
        
    Returns:
        bool: True if any target element was found, False otherwise
    """
    # List of possible selectors that indicate the form has loaded
    possible_selectors = [
        "[data-automation-id='formField']",
        ".css-1ud5i8o",  # Field labels
        "input[type='text']",
        "button[aria-haspopup='listbox']",
        "[data-automation-id='multiSelectContainer']",
        "fieldset.css-1s9yhc"
    ]
    
    print("Waiting for page to load...")
    start_time = time.time()
    
    for selector in possible_selectors:
        try:
            print(f"Trying to locate elements with selector: {selector}")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            print(f"Found elements with selector: {selector}")
            return True
        except TimeoutException:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                print(f"Timed out after {timeout} seconds")
                return False
            print(f"Selector {selector} not found, trying next...")
            continue
    
    return False

def extract_form_fields(driver):
    
    # Wait for the page to load with increased timeout and better error handling
    if not wait_for_page_load(driver, timeout=120):
        print("Could not detect any form elements. Taking a screenshot for debugging...")
        try:
            driver.save_screenshot("page_load_error.png")
            print("Screenshot saved as 'page_load_error.png'")
        except Exception as e:
            print(f"Failed to save screenshot: {str(e)}")
        return []
        
    # Save the page source to a file for further analysis
    try:
        page_source = driver.page_source
        with open("page_source.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("Page source saved to 'page_source.html'")
    except Exception as e:
        print(f"Failed to save page source: {str(e)}")
    
    # Allow some extra time for all fields to render
    print("Form detected. Allowing extra time for complete rendering...")
    time.sleep(10)
    
    form_fields = []
    print("Beginning to extract form fields...")
    
    # Process standard form fields
    try:
        field_containers = driver.find_elements(By.CSS_SELECTOR, "[data-automation-id^='formField']")
        print(f"Found {len(field_containers)} potential form fields")
        
        if not field_containers:
            # Try alternative selectors if the main one didn't work
            print("Trying alternative selectors...")
            field_containers = driver.find_elements(By.CSS_SELECTOR, ".css-1s9yhc")
            print(f"Found {len(field_containers)} fields with alternative selector")
    except Exception as e:
        print(f"Error finding field containers: {str(e)}")
        field_containers = []
    
    for i, container in enumerate(field_containers):
        try:
            print(f"Processing field {i+1}/{len(field_containers)}...")
            field_info = {}
            
            # Extract label and required status
            try:
                label_element = container.find_element(By.CSS_SELECTOR, ".css-1ud5i8o")
                if label_element:
                    field_info["name"] = label_element.text.strip().replace("*", "")
                    field_info["required"] = "*" in label_element.text
                    print(f"Found field: {field_info['name']}")
                else:
                    print("No label found for this field, skipping")
                    continue
            except NoSuchElementException:
                # Try alternative label selectors
                try:
                    label_element = container.find_element(By.CSS_SELECTOR, "[aria-label]")
                    field_info["name"] = label_element.get_attribute("aria-label").strip()
                    field_info["required"] = False  # Can't determine from this method
                    print(f"Found field using alternative selector: {field_info['name']}")
                except NoSuchElementException:
                    print("No label found with alternative selector, skipping")
                    continue
            
            # Identify field type and current value
            field_type = "unknown"
            value = "Empty"
            
            # Check for various input types
            try:
                # Text input
                input_elem = container.find_element(By.CSS_SELECTOR, "input[type='text']")
                field_type = "text"
                value = input_elem.get_attribute("value") or "Empty"
            except NoSuchElementException:
                pass
                
            if field_type == "unknown":
                try:
                    # Dropdown
                    dropdown = container.find_element(By.CSS_SELECTOR, "button[aria-haspopup='listbox']")
                    field_type = "dropdown"
                    value = dropdown.text.strip() or "Not selected"
                except NoSuchElementException:
                    pass
            
            if field_type == "unknown":
                try:
                    # Checkbox
                    checkbox = container.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                    field_type = "checkbox"
                    value = "Checked" if checkbox.get_attribute("aria-checked") == "true" else "Not checked"
                except NoSuchElementException:
                    pass
            
            if field_type == "unknown":
                try:
                    # Multiselect
                    multiselect = container.find_element(By.CSS_SELECTOR, "[data-automation-id='multiSelectContainer']")
                    field_type = "multiselect"
                    
                    # Try to get selected values
                    try:
                        selected_items = multiselect.find_elements(By.CSS_SELECTOR, "[data-automation-id='selectedItem']")
                        if selected_items:
                            value = ", ".join([item.get_attribute("title") for item in selected_items])
                        else:
                            value = "None selected"
                    except Exception:
                        value = "None selected"
                except NoSuchElementException:
                    pass
            
            if field_type == "unknown":
                try:
                    # Textarea
                    textarea = container.find_element(By.CSS_SELECTOR, "textarea")
                    field_type = "textarea"
                    value = textarea.get_attribute("value") or "Empty"
                except NoSuchElementException:
                    pass
            
            field_info["field_type"] = field_type
            field_info["value"] = value
            
            # Get field ID if available
            try:
                field_id = container.get_attribute("data-fkit-id") or container.get_attribute("id")
                if field_id:
                    field_info["id"] = field_id
            except Exception:
                pass
                
            form_fields.append(field_info)
            print(f"Successfully processed field: {field_info['name']}")
            
        except Exception as e:
            print(f"Error processing field {i+1}: {str(e)}")
    
    # Process radio button groups separately
    try:
        radio_groups = driver.find_elements(By.CSS_SELECTOR, "fieldset.css-1s9yhc")
        print(f"Found {len(radio_groups)} radio button groups")
        
        for i, group in enumerate(radio_groups):
            try:
                print(f"Processing radio group {i+1}/{len(radio_groups)}...")
                field_info = {}
                
                # Extract label
                try:
                    legend = group.find_element(By.CSS_SELECTOR, "legend")
                    if legend:
                        try:
                            label_element = legend.find_element(By.CSS_SELECTOR, ".css-1ud5i8o")
                            field_info["name"] = label_element.text.strip().replace("*", "")
                            field_info["required"] = "*" in label_element.text
                        except NoSuchElementException:
                            field_info["name"] = legend.text.strip()
                            field_info["required"] = False
                        
                        # Find selected value
                        field_info["field_type"] = "radio"
                        
                        try:
                            selected_radio = group.find_element(By.CSS_SELECTOR, "input[aria-checked='true']")
                            field_info["value"] = selected_radio.get_attribute("value") or "Selected"
                        except NoSuchElementException:
                            field_info["value"] = "Not selected"
                        
                        form_fields.append(field_info)
                        print(f"Successfully processed radio group: {field_info['name']}")
                except NoSuchElementException:
                    print("Could not find legend element for radio group")
            except Exception as e:
                print(f"Error processing radio group {i+1}: {str(e)}")
    except Exception as e:
        print(f"Error finding radio groups: {str(e)}")
    
    print(f"Extraction complete. Found {len(form_fields)} form fields in total.")
    return form_fields

def save_to_file(fields, output_file="workday_form_fields"):
    """
    Save extracted form fields to text and JSON files
    
    Args:
        fields (list): List of field information dictionaries
        output_file (str): Path to the output file
    """
    with open(output_file+".txt", 'w') as f:
        f.write("WORKDAY FORM FIELD PLACEHOLDERS\n")
        f.write("==============================\n\n")
        
        for field in fields:
            f.write(f"Field: {field['name']}\n")
            f.write(f"Type: {field['field_type']}\n")
            f.write(f"Required: {'Yes' if field.get('required') else 'No'}\n")
            f.write(f"Current Value: {field['value']}\n")
            if 'id' in field:
                f.write(f"Field ID: {field['id']}\n")
            f.write("\n")
            
    # Also save as JSON for programmatic use
    with open(output_file + ".json", 'w') as f:
        json.dump(fields, f, indent=2)
    
    print(f"Results saved to {output_file} and {output_file}.json")

def main():
    """Main function to handle command line arguments and run the extractor"""
    parser = argparse.ArgumentParser(description="Extract form fields from a Workday job application page")
    parser.add_argument("url", help="URL of the Workday job application page")
    parser.add_argument("-o", "--output", default="workday_form_fields.txt", 
                        help="Output file name (default: workday_form_fields.txt)")
    parser.add_argument("--timeout", type=int, default=120,
                        help="Maximum timeout in seconds for page to load (default: 120)")
    
    args = parser.parse_args()
    
    try:
        driver = setup_driver()
        fields = extract_form_fields(driver, args.url)
        
        if fields:
            print(f"Successfully extracted {len(fields)} form fields.")
            save_to_file(fields, args.output)
        else:
            print("No form fields were extracted. Check the URL and try again.")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        if 'driver' in locals():
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    main()