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
# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd backend
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

## 3. Activate the virtual environment

### Windows PowerShell

```bash
.venv\Scripts\activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:54323/inventory_db
```

Replace `YOUR_PASSWORD` with your PostgreSQL password.

> Do not upload `.env` to GitHub.

## 6. Run database migrations

```bash
alembic upgrade head
```

## 7. Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

---



# 📖 API Documentation

Once the server is running, open:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

---

## 🌐 Frontend Integration

The Angular frontend communicates with the FastAPI backend through HTTP APIs.

### 1. Clone the Frontend Repository

Clone the frontend project:

```bash
git clone <frontend-github-repository-url>
cd <frontend-project-folder>
```

Install the frontend dependencies:

```bash
npm install
```

Start the Angular application:

```bash
ng serve
```

The frontend will normally run at:

```text
http://localhost:4200
```

---

### 2. Backend URL

Start the FastAPI backend:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For a frontend running on the same computer, use:

```text
http://127.0.0.1:8000
```

For a frontend running on another computer on the same network, use the backend computer's IPv4 address:

```text
http://192.168.1.32:8000
```

Replace `192.168.1.32` with the backend computer's current IPv4 address.

---

### 3. API Base URL

The Angular frontend should use the backend URL as its API base URL.

Example:

```typescript
private apiUrl = 'http://192.168.1.32:8000';
```

---

### 4. API Endpoints

#### Categories

```text
GET    /categories
POST   /categories
GET    /categories/{category_id}
PUT    /categories/{category_id}
DELETE /categories/{category_id}
```

#### Suppliers

```text
GET    /suppliers
POST   /suppliers
GET    /suppliers/{supplier_id}
PUT    /suppliers/{supplier_id}
DELETE /suppliers/{supplier_id}
```

#### Products

```text
GET    /products
POST   /products
GET    /products/{product_id}
PUT    /products/{product_id}
DELETE /products/{product_id}
GET    /products/summary
```

Example:

```text
GET http://192.168.1.32:8000/products
```

---

### 5. Frontend → Backend Flow

```text
Angular Frontend
       ↓
   HttpClient
       ↓
   FastAPI API
       ↓
  Service Layer
       ↓
   SQLAlchemy
       ↓
  PostgreSQL
       ↓
   FastAPI Response
       ↓
 Angular Frontend
```

---

### 6. Testing the Backend

Swagger documentation:

```text
http://192.168.1.32:8000/docs
```

Example API:

```text
http://192.168.1.32:8000/products/summary
```

---

### ⚠️ LAN Testing

If the frontend is running on another laptop:

- Both computers must be connected to the same Wi-Fi/LAN.
- The backend must be running with:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- Port `8000` must be allowed through Windows Firewall.
- The frontend must use the backend computer's LAN IP.

Example:

```text
http://192.168.1.32:8000
```

> The backend computer's IP address may change when reconnecting to Wi-Fi. Check it using `ipconfig`.

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
