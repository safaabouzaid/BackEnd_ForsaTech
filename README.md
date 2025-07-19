# 🗂️ Forsa-Tech Backend API

This repository contains the **Backend API** for the Forsa-Tech platform.  
The backend is built with **Django REST Framework (DRF)** and serves multiple roles:
- 🔒 **Admin:** Platform Owner functionalities.
- 👥 **HR Managers:** Manage hiring workflows.
- 👨‍💻 **Developers (Job Seekers):** Build resumes, apply for jobs, and track progress.

---

## 📌 Key Features

**🔹 Platform Owner (Admin):**
- Manage companies (Add / Edit / Delete).
- Handle subscription plans and requests.
- Manage ads and job postings.
- View and respond to user complaints.
- Access statistics and export reports.

**🔹 HR Manager:**
- Filter and shortlist CVs.
- Accept or reject job applications.
- Schedule interviews.
- Analyze market trends.

**🔹 Developer (Job Seeker):**
- Create an ATS-compliant resume.
- Evaluate & improve CVs.
- Convert traditional resumes to ATS format.
- Apply for jobs and track applications.
- Get job recommendations.
- Take skill assessments.
- Receive acceptance notifications by email.

---

## ⚙️ Tech Stack

- **Framework:** Django 4.x
- **API:** Django REST Framework
- **Database:** PostgreSQL (recommended) / SQLite (for development)
- **Auth:** JWT Authentication (or Session Authentication)
- **Other:** Celery (optional, for async tasks), Firebase for notifications (if used)

---

## 🚀 Getting Started

### 📥 Clone the Repository

```bash
git clone https://github.com/safaabouzaid/BackEnd_ForsaTech
cd forsa-tech-backend
