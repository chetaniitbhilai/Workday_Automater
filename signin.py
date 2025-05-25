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
import traceback

# Load credentials
load_dotenv()
EMAIL = None
PASSWORD = os.getenv("password")


def select_country(driver, country_name="India"):
    try:
        wait = WebDriverWait(driver, 10)

        # Step 1: Click the dropdown button
        dropdown_btn = wait.until(EC.element_to_be_clickable((By.ID, "country--country")))
        dropdown_btn.click()
        time.sleep(1)

        # Step 2: Type into the hidden text input (the sibling <input> element)
        india_option = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//ul[contains(@class,'css')]/li[normalize-space()='India']")
        ))
        india_option.click()
        time.sleep(1)


    except Exception as e:
        print("Exception: Could not select country")
        print(e)






def read_first_link(file_path="links.txt"):
    with open(file_path, "r") as f:
        for line in f:
            link = line.strip()
            if link:
                return link
    return None

def sign_in_workday(url):
    # Load user info to get email
    user_info = load_user_info()
    if user_info:
        global EMAIL
        EMAIL = user_info.get("email", "chetan@iitbhilai.ac.in")
    else:
        EMAIL = "chetan@iitbhilai.ac.in"  # Fallback email
    
    if PASSWORD is None:
        print("[❌] Password not found in .env file.")
        return None
    if url is None:
        print("[❌] No URL found in links.txt.")
        return None

    print(f"[INFO] Using Email: {EMAIL}")
    print(f"[INFO] Opening URL: {url}")

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-web-security")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        try:
            print("[INFO] Looking for 'Already have an account? Sign In' link...")
            try:
                account_sign_in = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//text()[contains(., 'Already have an account')]/following::*[contains(text(), 'Sign In')][1]")))
                print("[INFO] Found the 'Sign In' link after 'Already have an account?'")
            except TimeoutException:
                try:
                    account_text = driver.find_element(By.XPATH, "//*[contains(text(), 'Already have an account')]")
                    print("[INFO] Found 'Already have an account' text")

                    sign_in_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'Sign In')]")
                    if sign_in_links:
                        account_sign_in = sign_in_links[0]
                        print("[INFO] Found a Sign In link near the account text")
                    else:
                        account_sign_in = driver.find_element(By.LINK_TEXT, "Sign In")
                        print("[INFO] Found a general Sign In link")
                except:
                    account_sign_in = driver.find_element(By.XPATH, "//*[contains(text(), 'Sign In')]")
                    print("[INFO] Found a generic element with 'Sign In' text")

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", account_sign_in)
            time.sleep(1)
            print("[INFO] Clicking on the 'Sign In' link...")
            try:
                account_sign_in.click()
            except:
                driver.execute_script("arguments[0].click();", account_sign_in)
            print("[INFO] Clicked on 'Sign In' link")
            time.sleep(2)
        except Exception as e:
            print(f"[INFO] Error finding 'Sign In' link: {e}")
            print("[INFO] Might already be on sign-in page or trying alternative approach...")

        print("[INFO] Waiting for email field...")
        try:
            email_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='email' or @name='email' or @id='email']")))
        except TimeoutException:
            email_field = wait.until(EC.presence_of_element_located((By.XPATH, "//label[contains(text(),'Email') or contains(text(),'Username')]/following::input[1]")))

        print("[INFO] Entering email...")
        email_field.clear()
        email_field.send_keys(EMAIL)

        print("[INFO] Entering password...")
        try:
            password_field = driver.find_element(By.XPATH, "//input[@type='password' or @name='password' or @id='password']")
        except:
            password_field = driver.find_element(By.XPATH, "//label[contains(text(),'Password')]/following::input[1]")

        password_field.clear()
        password_field.send_keys(PASSWORD)

        try:
            remember_me = driver.find_element(By.XPATH, "//input[@type='checkbox']")
            if not remember_me.is_selected():
                try:
                    remember_me.click()
                except:
                    driver.execute_script("arguments[0].click();", remember_me)
                print("[INFO] Checked 'Remember Me' box")
        except:
            print("[INFO] No 'Remember Me' checkbox found")

        print("[INFO] Looking for Sign In button after inputting credentials...")

        sign_in_buttons = []
        strategies = [
            # Prioritize custom div-based button
            (By.XPATH, "//div[@aria-label='Sign In' and @role='button']"),

            # Common fallback buttons
            (By.XPATH, "//button[contains(text(), 'Sign In') or contains(text(), 'Log In')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.XPATH, "//div[contains(text(), 'Sign In') or contains(text(), 'Log In')][contains(@class, 'button') or @role='button']"),
            (By.XPATH, "//*[contains(text(), 'Sign In') or contains(text(), 'Log In')]")
        ]

        for strategy in strategies:
            try:
                buttons = driver.find_elements(*strategy)
                for button in buttons:
                    if button.is_displayed() and button not in sign_in_buttons:
                        sign_in_buttons.append(button)
                if buttons:
                    print(f"[INFO] Found {len(buttons)} button(s) using strategy: {strategy}")
            except:
                continue

        print("[DEBUG] Buttons found:")
        for i, btn in enumerate(sign_in_buttons):
            try:
                print(f"  [{i+1}] tag={btn.tag_name}, text='{btn.text.strip()}', class='{btn.get_attribute('class')}'")
            except:
                pass

        password_location = password_field.location['y']
        sign_in_button = None
        for btn in sign_in_buttons:
            try:
                btn_y = btn.location['y']
                if btn_y > password_location:
                    sign_in_button = btn
                    print("[INFO] Found a Sign In button below the password field.")
                    break
            except:
                continue

        if sign_in_button is None and sign_in_buttons:
            sign_in_button = sign_in_buttons[-1]
            print("[INFO] Falling back to the last found Sign In button.")

        if sign_in_button:
            print("[INFO] Scrolling to Sign In button...")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sign_in_button)
            time.sleep(2)

            print("[INFO] Attempting to click Sign In button...")
            try:
                sign_in_button.click()
                print("[INFO] Standard click worked!")
            except Exception as click_error:
                print(f"[!] Standard click failed: {click_error}")
                try:
                    driver.execute_script("arguments[0].click();", sign_in_button)
                    print("[INFO] JavaScript click worked!")
                except Exception as js_click_error:
                    print(f"[!] JavaScript click failed: {js_click_error}")
                    actions = ActionChains(driver)
                    actions.move_to_element(sign_in_button).click().perform()
                    print("[INFO] ActionChains click attempted!")

            print("[✔] Attempted to submit Sign In form.")
            print("[INFO] Waiting to see if we successfully signed in...")
            time.sleep(10)

            if "Sign In" in driver.page_source or "Log In" in driver.page_source:
                print("[!] We might still be on the sign-in page. Checking for errors...")
                try:
                    error_messages = driver.find_elements(By.XPATH, "//*[contains(@class, 'error') or contains(@class, 'alert')]")
                    if error_messages:
                        print("[!] Found potential error messages:")
                        for msg in error_messages:
                            if msg.text.strip():
                                print(f"    - {msg.text}")
                except:
                    print("[!] No specific error messages found.")
                return None
            else:
                print("[✔] Successfully signed in!")
                return driver
        else:
            print("[❌] Could not find any Sign In buttons.")
            return None

    except Exception as e:
        print(f"[❌] Error: {e}")
        return None
