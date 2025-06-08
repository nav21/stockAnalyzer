# Simple React + Flask Application with PostgreSQL

This is a simple full-stack application using React for the frontend, Flask for the backend, and PostgreSQL for the database.

## Project Structure
- `backend/`: Contains the Flask backend and database models
- `frontend/`: Contains the React frontend

## Setup Instructions

### PostgreSQL Setup
1. Install PostgreSQL on your system if you haven't already
2. Create a new database:
   ```sql
   CREATE DATABASE fooddb;
   ```
3. Update the database connection string in `backend/config.py` if your PostgreSQL setup is different:
   ```python
   DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fooddb"
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```
2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the Flask server:
   ```
   python app.py
   ```
   The backend will run on http://localhost:5000

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```
3. Start the development server:
   ```
   npm start
   ```
   The frontend will run on http://localhost:3000

## Features
- PostgreSQL database with a foods table
- API endpoints for getting and adding foods
- React frontend that displays the list of foods
- Ability to add new foods to the database
- CORS enabled for local development 