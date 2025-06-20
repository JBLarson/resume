# resume - * coming soon *

A modular, end-to-end system for tailoring and submitting your HTML resume (`index.html`) to job postings. It:

- **Scrapes** job descriptions from any URL  
- **Extracts** and ranks keywords via Google Gemini (or local embeddings)  
- **Injects** top keywords into a Jinja2-templated resume sidebar  
- **Renders** a pixel-perfect, full-page PDF (`JB_Larson_Resume.pdf`)  
- **(Optional)** Automates ATS form-filling with Playwright drivers  
- **Orchestrates** everything as Prefect flows or CLI scripts  

---

## 🚀 Features

- **crawler/**: Scrapy + Playwright spiders  
- **nlp/**: `extract_keywords()` calls Gemini & caches results  
- **resume/**: `toPdf.py` + Jinja2 template + Tailwind CSS  
- **apply_bot/**: site-specific YAML selectors + `autofill.py`  
- **orchestrator/**: Prefect 2 flows in `flows.py`  
- **data/**: raw HTML, JSON, PDFs, logs  

---

## 🔧 Requirements

- Python 3.12+, venv, `pip install -r requirements.txt`  
- Chrome/Chromium on PATH  
- Poppler & `pdf2image` for PDF→JPEG conversion (optional)  
- Docker & Docker Compose (for containerized workers)  

---

## ⚙️ Configuration

1. Copy `.env.example → .env`  
2. Set `GEMINI_API_KEY`, DB URL, ATS credentials  

---

## 🛠️ Quickstart

```bash
# Render a job-tailored resume PDF
python3 main.py https://company.com/job/123

# Or run entire Prefect pipeline
prefect deploy --project resume
prefect work queue execute resume/flow
