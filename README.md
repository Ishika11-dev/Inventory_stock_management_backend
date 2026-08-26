# Inventory Stock Management Backend

A backend REST API for managing inventory, products, categories, and suppliers.

The project is built using **FastAPI**, **PostgreSQL**, **SQLAlchemy**, and **Alembic**. It follows a modular architecture with separate models, schemas, services, routes, utilities, and database configuration.

---

## 🚀 Tech Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Psycopg
- Uvicorn
- Postman
- Git & GitHub

---
## ⚙️ Installation
1. Clone the repository
git clone <your-github-repository-url>

Move into the project:

cd backend
2. Create a virtual environment
python -m venv .venv
3. Activate the virtual environment
Windows PowerShell
.venv\Scripts\activate

If PowerShell blocks activation:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Then:

.venv\Scripts\activate
4. Install dependencies
pip install -r requirements.txt
🔐 Environment Variables

Create a .env file in the project root.

Example:

DATABASE_URL=postgresql+psycopg://postgres:<YOUR_PASSWORD>@localhost:54323/inventory_db

Replace:

<YOUR_PASSWORD>

with your PostgreSQL password.

Important

Do not commit .env to GitHub.

Add this to .gitignore:

.env
.venv/
__pycache__/
*.pyc
🐘 PostgreSQL Setup

Create a PostgreSQL database named:

inventory_db

Make sure PostgreSQL is running.

The database connection contains:

Host     : localhost
Port     : 54323
Database : inventory_db
Username : postgres

If your PostgreSQL installation uses a different port, update the DATABASE_URL accordingly.

## 🔄 Database Migrations

Alembic is used to create and update database tables.

Create migration

After creating or changing SQLAlchemy models:

alembic revision --autogenerate -m "create inventory tables"

Example output:

Detected added table 'categories'
Detected added table 'suppliers'
Detected added table 'products'
Apply migration
alembic upgrade head

This creates the tables in PostgreSQL.

Check migration status
alembic current
View migration history
alembic history
## ▶️ Run the Backend

Start FastAPI using Uvicorn:

uvicorn app.main:app --reload

The backend will normally run at:

http://127.0.0.1:8000

For access from another device on the same network:

uvicorn app.main:app --host 0.0.0.0 --port 8000

Then the backend can be accessed using the computer's local IP:

http://YOUR_LOCAL_IP:8000

Example:

http://192.168.1.32:8000


## 📁 Project Structure

```text
backend/
│
├── app/
│   │
│   ├── main.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   │
│   ├── models/
│   │   ├── category.py
│   │   ├── supplier.py
│   │   └── product.py
│   │
│   ├── schemas/
│   │   ├── category.py
│   │   ├── supplier.py
│   │   └── product.py
│   │
│   ├── services/
│   │   ├── category.py
│   │   ├── supplier.py
│   │   └── product.py
│   │
│   ├── routes/
│   │   ├── category.py
│   │   ├── supplier.py
│   │   └── product.py
│   │
│   └── utils/
│       ├── constraints.py
│       ├── exceptions.py
│       ├── response_handler.py
│       └── status_constants.py
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```
## 👩‍💻 Author

Ishika

Inventory Stock Management Backend developed using FastAPI, PostgreSQL, SQLAlchemy, and Alembic.
