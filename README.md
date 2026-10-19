# Financial Data Analytics & RPA Automation Pipeline 🚀

An end-to-end data pipeline and robotic process automation (RPA) solution built with **Python**, **Selenium**, and **SQLite**. Designed to automate invoice data extraction, validate fiscal compliance, streamline Accounts Payable workflows, and maintain an audit-ready relational database.

---

## 📌 Business Overview & Problem Statement

Corporate financial and tax operations often face heavy bottlenecks when handling tens of thousands of payment records manually:
- Repetitive, manual validation across institutional ERP systems.
- Inefficient handling of unstructured document attachments (PDF invoices, receipts).
- High risk of human error during fiscal and tax status verification.
- Lack of centralized, queryable logs for auditing and workflow status tracking.

**Objective:** Design and deploy an automated, secure, and fault-tolerant pipeline to parse financial records, validate compliance, interact with the ERP via DOM automation, and persist clean operational data for business intelligence.

---

## 🛠️ Tech Stack & Key Libraries

- **Language:** Python 3.10+
- **Database & Persistence:** SQLite (WAL mode, parameterized queries, RBAC logic)
- **RPA & Web Scraping:** Selenium WebDriver, Headless Browser execution, DOM injection
- **Document Processing (OCR):** PyMuPDF (fitz), Tesseract OCR
- **Data Wrangling:** Pandas, NumPy
- **APIs & Networking:** Asynchronous REST requests, Rate-limiting throttles

---

## 🏛️ System Architecture

1. **Document Ingestion & OCR:**
   - Automatically polls incoming financial files (PDFs/images).
   - Uses PyMuPDF and Tesseract OCR to extract supplier metadata, invoice numbers, amounts, and tax withholdings.
2. **Fiscal & Compliance Validation:**
   - Integrates with external registry endpoints via REST APIs to verify active company standing and tax compliance before clearing transactions.
3. **ERP DOM Automation (RPA):**
   - Headless browser automated sessions navigate the ERP interface.
   - Executes DOM scripts to reconcile accounts, confirm batch postings, and log transaction tokens.
4. **Data Persistence & Audit Trail:**
   - Writes transactional status and timestamps to a secured SQLite database with Write-Ahead Logging (WAL).
   - Generates structured event logs for auditing, error tracing, and downstream financial reporting.

---

## 📈 Key Results & Impact

- **Volume Handled:** Automated verification and data processing across **20,000+ financial records**.
- **Efficiency:** Drastically reduced manual data entry and repetitive verification tasks.
- **Accuracy:** Enforced standardized validation checks, mitigating risks of incorrect payments or tax non-compliance.
- **Traceability:** Implemented a structured relational audit trail accessible for management reporting and analytics.

---

## 🔒 Confidentiality & Sanitization Notice

*Note: All proprietary endpoints, sensitive corporate credentials, company identifiers, and proprietary ERP references have been completely sanitized and replaced with synthetic/mock data in accordance with strict corporate data governance and NDA policies.*

---

## 👨‍💻 Author

**João Pedro Campello**  
*Data Science Student @ FIAP | Financial & Tax Background*  
- **LinkedIn:** [linkedin.com/in/joapedrobarbo](https://www.linkedin.com/in/joapedrobarbo)  
- **GitHub:** [github.com/joaopedrojpb-ops](https://github.com/joaopedrojpb-ops)
