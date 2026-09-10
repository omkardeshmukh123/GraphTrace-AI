# E-Commerce Sample App

A sample Python + JavaScript e-commerce application used as the GraphTrace AI Phase 1 test repository.

## Technologies

Python, FastAPI, JavaScript, React, Neo4j, PostgreSQL

## Architecture

The application is structured into three main layers:
- **Backend** (Python / FastAPI): handles authentication, orders, and payments
- **Frontend** (JavaScript / React): user interface
- **Database** (PostgreSQL + Neo4j): relational + graph storage

## Modules

- `AuthService` — JWT-based user authentication
- `OrderService` — Order management and processing
- `PaymentService` — Payment gateway integration
- `UserRepository` — User data access layer

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env`
3. Run: `uvicorn main:app --reload`
