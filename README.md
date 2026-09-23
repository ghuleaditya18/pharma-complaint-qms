# Pharma Complaint QMS

A pharmaceutical complaint management web application designed to streamline complaint intake, documentation, and risk assessment for quality management teams. The platform combines a conversational AI assistant with structured complaint forms to capture complaint information from customer reports, uploaded documents, and manual entries.

## Purpose

Pharma complaint handling requires fast, accurate, and traceable intake of issues related to products, batches, customers, and defects. This project provides a lightweight QMS workflow where:

- complaint details can be captured through a guided form
- uploaded complaint emails or PDF/TXT documents can be analyzed automatically
- AI-driven conversation helps complete missing information
- risk and severity are assessed based on available complaint details
- complaint records can be stored and retrieved via a backend API

This is especially useful for pharmaceutical quality and regulatory teams that need to log complaints, assess impact, and identify follow-up actions in a structured way.

## What this project includes

### Frontend
- React + Vite application
- Modern UI for complaint intake and AI-assisted chat
- Redux-based state management
- Tailwind styling for a clean QMS dashboard

### Backend
- FastAPI REST API
- SQLAlchemy ORM for complaint persistence
- SQLite default database with MySQL support available
- AI-powered complaint processing using Groq + LangGraph
- PDF/TXT document parsing for complaint intake

### Sample data
- sample complaint text for real-world complaint logging workflow
- sample PDF document for demonstrating document ingestion

## Key functionality

- Complaint intake through an interactive form
- Conversational AI agent to collect missing fields and interpret complaint messages
- PDF/TXT upload support for extracting complaint details from documents
- Auto-generated complaint IDs
- Severity and action recommendation outputs
- Complaint list and detail retrieval
- Health check and API endpoints for the QMS backend

## Tech stack

### Frontend
- React 19
- Vite
- Redux Toolkit
- Tailwind CSS
- Axios
- Lucide React

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Groq
- LangChain / LangGraph
- PyMySQL
- PyPDF

## Repository structure

```text
pharma-complaint-qms/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   ├── routes/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── .env.example
│   ├── requirements.txt
│   └── test_*.py
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── README.md
├── sample_data/
│   ├── complaint_amoxicillin.txt
│   └── metformin_api_defect.pdf
├── .gitignore
├── LICENSE
└── README.md
```

## Example business use case

A customer reports a complaint such as a discolored capsule, packaging defect, or batch-related issue. The application can:

1. ingest the complaint text or document
2. extract complaint metadata such as customer, product, batch, quantity, and defect description
3. populate a structured complaint form
4. ask clarifying questions through the chat interface
5. evaluate severity and classify the issue
6. create and store the complaint record for QMS tracking

## Setup instructions

### 1. Clone the repository

```bash
git clone https://github.com/ghuleaditya18/pharma-complaint-qms.git
cd pharma-complaint-qms
```

### 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows
pip install -r requirements.txt
cp .env.example .env
```

Update the `.env` file with your Groq API key and database configuration.

Start the backend:

```bash
 python -m uvicorn app.main:app --reload
```

### 3. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The frontend typically runs on:

- http://localhost:5173

## API overview

The backend exposes API endpoints under `/api` for complaint handling and AI chat:

- `POST /api/chat` — send a complaint message or conversational update to the AI assistant
- `POST /api/upload` — upload a PDF/TXT complaint document for text extraction and intelligence
- `POST /api/complaints` — create a complaint record
- `GET /api/complaints` — list all complaints
- `GET /api/complaints/{id}` — fetch a complaint by ID or complaint code
- `GET /health` — health check endpoint

## Notes

- SQLite is the default database setup for local development and testing.
- MySQL is supported via the `DATABASE_URL` configuration.
- The project is intended as a practical QMS demo and can be extended with stronger audit trails, approval workflows, CAPA linkage, and regulatory reporting.

## License

This project is currently distributed without an explicit repository license file. If needed, add a suitable license before production use.

## Summary

Pharma Complaint QMS is a Python + React application for managing pharmaceutical complaints in a structured, AI-assisted workflow. It is built to reduce manual effort in complaint intake, improve data completeness, and provide a clear path for risk-based evaluation and complaint tracking in a quality management environment.
