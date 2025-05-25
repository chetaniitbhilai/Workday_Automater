from resume import upload_resume, load_user_info
from form_utils import extract_form_fields , save_to_file
from filler import generate_answers_gemini, fill_workday_form
from signin import select_country, read_first_link, sign_in_workday
import traceback

if __name__ == "__main__":
    job_url = read_first_link()
    driver = sign_in_workday(job_url)

    if driver:
        try:
            print("\n[INFO] Starting resume upload process...")
            upload_success = upload_resume(driver, resume_type="resume_software")

            if upload_success:
                print("[✔] Resume upload process completed!")
            else:
                print("[!] Resume upload process couldn't be completed automatically.")
                print("[INFO] You might need to complete the process manually.")

            print("\n[INFO] Starting form field extraction...")

            
            select_country(driver)


            fields = extract_form_fields(driver)
            save_to_file(fields)

            print("\n[INFO] Generating answers using Gemini...")
            answers = generate_answers_gemini("workday_form_fields.json", "my_info.json")
            print(answers)
            print("\n[INFO] Auto-filling the form fields with Gemini-generated answers...")
            fill_workday_form(driver, answers)
            print("[✔] Form fields filled successfully!")

        except Exception as e:
            print(f"[❌] General error: {e}")
            traceback.print_exc()


        finally:
            input("[INFO] Press Enter to close the browser...")
            driver.quit()

    else:
        print("[❌] Sign in failed or browser was closed. Cannot proceed.")
