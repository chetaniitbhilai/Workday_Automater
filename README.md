# 🚀 Workday Automater

This project automates the job application process on Workday portals using Selenium and Google Gemini for intelligent field completion.

## 📂 Project Structure

```
Workday_Automater/
│
├── data/                           # Contains resumes and cover letters
│   ├── resume1.pdf
│   └── cover_letter_template.pdf
│
├── my_info.json                    # JSON file with user info (see example below)
├── links.txt                       # List of Workday application links
├── main.py                         # Entry point for automation
├── form_utils.py                   # Extracts questions and prepares Gemini prompts
├── filler.py                       # Fills the form fields with appropriate answers
├── resume.py                       # Uploads resume and cover letter
├── signin.py                       # Signs in to Workday portals
├── requirements.txt                # Required Python packages
├── .env                            # Environment variables (not committed)
└── setup.py                        # Project setup (if converting to pip module)
```

## 🧠 Features

- ✅ Auto-signin to Workday job applications
- 📑 Intelligent form field parsing
- 🤖 Answer generation using Google Gemini based on personal info
- 📄 Resume & cover letter upload
- 🔗 Link-driven job applications via `links.txt`

## 🔐 Example `my_info.json` (dummy data)

```json
{
  "Legal Name - first_name": "John",
  "Legal Name - last_name": "Doe",
  "Preferred_name": "No",
  "email": "john@example.com",
  "linkedin": "https://www.linkedin.com/in/johndoe/",
  "github": "https://github.com/johndoe",
  "portfolio": "https://johndoe.dev",
  "resume_software": "data/resume1.pdf",
  "cover_letter_software": "data/cover_letter_template.pdf",
  "How Did You Hear About Us?": "LinkedIn",
  "Country": "USA",
  "Address Line 1": "123 Main St",
  "City or town": "San Francisco",
  "Postal code": "94101",
  "Country Phone Code": "USA",
  "phone": "1234567890"
}
```

## 🔧 Environment Setup

Create a `.env` file in the root directory with the following content:

```
password=your_account_password
GEMINI_API_KEY=your_google_gemini_api_key
```

## ⚙️ How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your_username>/Workday_Automater.git
   cd Workday_Automater
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add your details**:
   - Fill `my_info.json` with your actual data.
   - Add Workday application links in `links.txt`.

4. **Run the main script**:
   ```bash
   python main.py
   ```

## ⚠️ Limitations

- ✅ Fills up to the third form automatically (common fields).
- ⚠️ Further dynamic forms vary across companies — you must manually complete them.
- 🔐 Each application may require sign-in or email verification. Sign in once before starting the bot.

## 📌 Notes

- Make sure you’ve already signed up on the job portal or are ready to handle verification manually.
- Designed for job portals using **Workday** only.
