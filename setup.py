import os
import json

def setup_files():
    """Create necessary directories and placeholder files if they don't exist."""
    print("[INFO] Setting up necessary files and directories...")
    
    # Make sure the data directory exists
    if not os.path.exists("data"):
        print("[INFO] Creating data directory...")
        os.makedirs("data")
    
    # Create placeholder resume files if they don't exist
    resume_files = {
        "data/resume1.pdf": "Software Engineering Resume",
        "data/resume2.pdf": "ML/AI Resume",
        "data/cover_letter_template.pdf": "Cover Letter Template"
    }
    
    # Check for my_info.json
    if not os.path.exists("my_info.json"):
        print("[INFO] Creating my_info.json with default values...")
        default_info = {
            "first_name": "Chetan",
            "last_name": "Arora",
            "email": "chetanar1707@gmail.com",
            "secondary_email": "chetan@iitbhilai.ac.in",
            "phone": "9355844091",
            "linkedin": "https://www.linkedin.com/in/chetan-arora-119098267/",
            "github": "https://github.com/chetaniitbhilai",
            "portfolio": "https://portfolio-pi-lilac-37.vercel.app/",
            "resume_software": "data/resume1.pdf",
            "resume_ml_ai": "data/resume2.pdf",
            "cover_letter_software": "data/cover_letter_template.pdf",
            "cover_letter_ml_ai": "data/cover_letter_template.pdf"
        }
        
        with open("my_info.json", "w") as f:
            json.dump(default_info, f, indent=4)
    
    # Check for links.txt
    if not os.path.exists("links.txt"):
        print("[INFO] Creating empty links.txt file...")
        with open("links.txt", "w") as f:
            f.write("# Paste your job application URL below\n")
    
    # Check for .env file
    if not os.path.exists(".env"):
        print("[INFO] Creating .env file template...")
        with open(".env", "w") as f:
            f.write("# Add your Workday password here\npassword=your_password_here\n")
    
    # Check for actual resume files
    found_resumes = []
    for file_path, file_desc in resume_files.items():
        if not os.path.exists(file_path):
            print(f"[INFO] {file_desc} not found at {file_path}")
        else:
            found_resumes.append((file_path, file_desc))
    
    if found_resumes:
        print("\n[INFO] Found the following resume/cover letter files:")
        for path, desc in found_resumes:
            print(f"  - {desc}: {path}")
    else:
        print("\n[!] No resume or cover letter files found in the data directory.")
        print("   Please place your resume files in the data directory with the following names:")
        for file_path, file_desc in resume_files.items():
            print(f"   - {file_desc}: {file_path}")
    
    print("\n[INFO] Setup complete. You can now run main.py to upload your resume.")

if __name__ == "__main__":
    setup_files()