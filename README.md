# Bloomer API

**Bloomer_api** is a Django-based backend API for the Bloomer project — a simple, modular API server for managing resources. It’s designed to provide endpoints for data CRUD, authentication, and business logic, ready to be consumed by frontend clients (web, mobile, etc.).

---

## 📦 Table of Contents

- [Features](#features)  
- [Tech Stack](#tech-stack)  
- [Getting Started](#getting-started)  
  - Prerequisites  
  - Installation  
  - Running Locally  
- [Configuration](#configuration)  
- [API Endpoints](#api-endpoints)  
- [Testing](#testing)  
- [Deployment](#deployment)  
- [Contributing](#contributing)  
- [License](#license)  

---

## 🔧 Features

- RESTful API structure with Django REST Framework  
- CRUD operations for models  
- Authentication (token-based or JWT)  
- Simple project layout (apps, core settings)  
- Ready for deployment (includes `build.sh`, `.gitignore`, etc.)  

---

## 🧰 Tech Stack

- **Backend**: Django, Django REST Framework  
- **Database**: PostgreSQL (recommended)  
- **Static Files**: WhiteNoise (for serving static assets)  
- **Deployment Scripts**: Bash script (`build.sh`)  
- **Dependencies**: Listed in `requirements.txt`  

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

- Python 3.9+  
- PostgreSQL installed (or a hosted Postgres database)  
- Git

### Installation

```bash
git clone https://github.com/Best-wale/Bloomer_api.git
cd Bloomer_api
python -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
pip install -r requirements.txt
