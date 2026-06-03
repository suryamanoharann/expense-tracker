# Expense Tracker

A clean, single-user personal expense tracker built with Python (Flask), MySQL (XAMPP), and plain HTML/CSS/JS. No framework, no build step, runs locally.

---

## How to Run

### Prerequisites

* Python 3.9+
* XAMPP installed with **MySQL service running**

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/expense-tracker.git
cd expense-tracker

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your MySQL password in app.py
# Open app.py and update DB_CONFIG:
# 'password': 'your_xampp_mysql_password'  ← change this

# 5. Run
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

> The app automatically creates the `expense_tracker` database and `expenses` table on first run. No manual SQL needed.

---

## Project Structure

```text
expense-tracker/
├── app.py                  # Flask backend + all API routes
├── requirements.txt        # Python dependencies
├── static/
│   └── style.css           # All styles
└── templates/
    └── index.html          # Single page UI + inlined JS
```

---

## Stack Choices and Tradeoffs

| Layer    | Choice                  | Reason                                                    |
| -------- | ----------------------- | --------------------------------------------------------- |
| Backend  | Python + Flask          | Minimal boilerplate, fast to write, easy to read          |
| Database | MySQL via XAMPP         | Requirement; relational structure suits expense data well |
| Frontend | Vanilla HTML / CSS / JS | No build step, no dependencies, runs in any browser       |
| Driver   | mysql-connector-python  | Official MySQL driver, pure Python, no extras needed      |

**Tradeoffs:**

* **Flask over FastAPI** — Flask is simpler for a single-user local app. FastAPI would be better for async/concurrent use.
* **Vanilla JS over React/Vue** — No build tooling needed. The list re-renders on every filter change which is fast enough at this scale but would need virtual DOM at larger scale.
* **No ORM** — Raw SQL keeps things transparent and avoids migration complexity for a small schema. Would use SQLAlchemy for a larger project.
* **Single `expenses` table** — Simple and sufficient. A multi-user version would need a `users` table and foreign keys.

---

## What's Done

| # | Features                                                 | Status |
| - | ------------------------------------------------------- | ------ |
| 1 | Add expense — title, amount (₹), category, date, note   | ✅ Done |
| 2 | List all expenses sorted by date, newest first          | ✅ Done |
| 3 | Edit any expense — pre-filled modal                     | ✅ Done |
| 4 | Delete any expense — confirmation dialog                | ✅ Done |
| 5 | Monthly summary — total spent + per-category bar chart  | ✅ Done |
| 6 | Filter by category, date range, title partial search    | ✅ Done |
| 7 | Empty states — no expenses, no results, no monthly data | ✅ Done |
| 8 | Input validation — backend + frontend both              | ✅ Done |
| 9 | Month navigator — browse any past or future month       | ✅ Done |

---

## What's Skipped and Why

| Feature           | Reason skipped                                                    |
| ----------------- | ----------------------------------------------------------------- |
| Authentication    | Explicitly out of scope per spec — single user, local only        |
| Test suite        | Explicitly out of scope per spec — manual end-to-end testing done |
| Pagination        | Not needed at personal scale — all matching rows load fine        |
| CSV / PDF export  | not required by spec                                |
| Deployment config | Local only per spec — no gunicorn, nginx, or Docker needed        |
| Multi-currency    | Explicitly out of scope per spec                                  |

---

## Known Rough Edges

* **MySQL must be running before starting the app** — if XAMPP MySQL is not started, `python app.py` will throw a connection error. Fix: start MySQL in XAMPP control panel first.
* **Password in plain text** — `DB_CONFIG` in `app.py` contains the MySQL password as a plain string. Fine for local use, would use `.env` + `python-dotenv` in production.
* **No pagination** — the expense list loads all matching rows. Perfectly fine for personal use but would need `LIMIT/OFFSET` with hundreds of records.
* **Future months in summary** — the month navigator allows going forward in time; it just shows ₹0.00 with an empty state, which is harmless but slightly odd.
* **No offline support** — the app requires a running Flask server and MySQL. No PWA or service worker.
