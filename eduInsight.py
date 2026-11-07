#!/usr/bin/env python3
"""
Prepare EduInsight for GitHub and optionally push it to a GitHub repository.

Usage:
    python upload_to_github.py
    python upload_to_github.py "C:/path/to/EduInsight-main"

The script deliberately excludes virtual environments, secrets, local databases,
cache files, and runtime artifacts from Git.
"""

from pathlib import Path
import subprocess
import sys

PROJECT_NAME = "EduInsight"

README = """# EduInsight

EduInsight is a student academic performance monitoring and prediction web
application. It helps educators understand student progress using academic
records such as attendance, study hours, previous grades, and learning-support
details.

## Features

- Admin and student login modes
- Student record management and CSV import
- Academic dashboard with average grade, attendance, and at-risk student counts
- Student search, filtering, sorting, and pagination
- Grade prediction based on academic and learning-related inputs
- Potential-grade and improvement estimates
- Personalized recommendations for attendance and study habits
- Student-specific performance insights
- Optional email updates through Gmail SMTP

## Technology Stack

- **Backend:** Python, Flask, Flask-CORS
- **Database:** SQLite, Flask-SQLAlchemy
- **Frontend:** HTML, CSS, JavaScript
- **Data:** CSV student-performance dataset

## Project Structure

```text
EduInsight/
├── app.py
├── config.py
├── database.py
├── models/
├── routes/
├── services/
├── templates/
├── static/
├── data/
├── requirements.txt
└── README.md
```

## Setup

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file if needed. Configure a strong `SECRET_KEY`.
   Gmail email functionality is optional; configure `GMAIL_ADDRESS` and
   `GMAIL_APP_PASSWORD` only if you want to enable it.

5. Start the application:

   ```bash
   python app.py
   ```

6. Open the local address printed by Flask in your browser.

## Data and Security Notes

- Do not commit `.env`, passwords, API keys, virtual environments, or local
  database files.
- Use synthetic or anonymized student data in public repositories.
- Change the development secret key before deployment.
- Grade predictions are estimates based on the application's scoring logic;
  they should not be treated as guaranteed academic outcomes.
"""

GITIGNORE = """# Secrets and environment configuration
.env
.env.*
!.env.example
*.pem
*.key

# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage

# Virtual environments
.venv/
venv/
env/
ENV/

# Local databases and runtime files
*.db
*.sqlite
*.sqlite3
.server.pid
*.log

# OS and editor files
.DS_Store
Thumbs.db
.vscode/
.idea/

# Build artifacts
build/
dist/
"""


def run(command, cwd):
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def main():
    default_folder = Path(__file__).resolve().parent
    raw_folder = sys.argv[1] if len(sys.argv) > 1 else input(
        f"EduInsight project folder [{default_folder}]: "
    ).strip()
    project = Path(raw_folder).expanduser().resolve() if raw_folder else default_folder

    if not project.is_dir():
        print(f"Error: project folder does not exist: {project}")
        return 1

    if not (project / "app.py").exists():
        print("Error: app.py was not found. Select the EduInsight project root.")
        return 1

    (project / "README.md").write_text(README, encoding="utf-8")
    (project / ".gitignore").write_text(GITIGNORE, encoding="utf-8")

    print("\nCreated README.md and .gitignore.")

    # Remove sensitive files from Git's index if they were previously tracked.
    if (project / ".git").exists():
        for pattern in (".env", "*.db", "*.sqlite", "*.sqlite3"):
            subprocess.run(
                ["git", "rm", "--cached", "-r", "--ignore-unmatch", pattern],
                cwd=project, check=False
            )

    try:
        run(["git", "init"], project)
        run(["git", "add", "."], project)
        run(["git", "status", "--short"], project)

        message = input("\nCommit message [Initial commit - EduInsight]: ").strip()
        if not message:
            message = "Initial commit - EduInsight"
        run(["git", "commit", "-m", message], project)

        remote = input(
            "\nPaste your GitHub repository URL (leave blank to skip push): "
        ).strip()
        if remote:
            existing = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project, capture_output=True, text=True
            )
            if existing.returncode == 0:
                run(["git", "remote", "set-url", "origin", remote], project)
            else:
                run(["git", "remote", "add", "origin", remote], project)

            run(["git", "branch", "-M", "main"], project)
            run(["git", "push", "-u", "origin", "main"], project)
            print("\nEduInsight was pushed to GitHub successfully.")
        else:
            print("\nLocal Git repository created. Add a GitHub remote and push later.")

    except FileNotFoundError:
        print("Error: Git is not installed or is not available in PATH.")
        return 1
    except subprocess.CalledProcessError as error:
        print(f"\nGit command failed with exit code {error.returncode}.")
        print("Check the error above, GitHub repository URL, and Git authentication.")
        return error.returncode

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
