# NoBurnout ITFest Backend

This is the backend service for the NoBurnout application, built with FastAPI. It handles document processing, summary generation, presentation creation, and user authentication via Supabase.

## Prerequisites

Before you begin, ensure you have the following installed:
- [Python 3.11+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv): A fast Python package installer and resolver.

## Setup and Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repository-url>
    cd noburnout-itfest-be
    ```

2.  **Create a Virtual Environment**
    It's highly recommended to use a virtual environment. With `uv`, you can create it easily:
    ```bash
    uv venv
    ```
    Activate it:
    ```bash
    source .venv/bin/activate
    ```

3.  **Configure Environment Variables**
    Create a `.env` file by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Now, open the `.env` file and fill in the required values.

    **Supabase Configuration:**
    - `SUPABASE_URL`: Find this in your Supabase project dashboard under **Project Settings > API > Project URL**.
    - `SUPABASE_KEY`: Use the `anon` key from your Supabase project dashboard under **Project Settings > API > Project API Keys**.

    **Azure Configuration:**
    - `AZURE_STORAGE_CONNECTION_STRING`: Your connection string for Azure Blob Storage.
    - `AZURE_SPEECH_KEY` & `AZURE_SPEECH_REGION`: Credentials for Azure Speech Service.
    - `AZURE_LANGUAGE_ENDPOINT` & `AZURE_LANGUAGE_KEY`: Credentials for Azure Language Service (for text analysis).

4.  **Install Dependencies**
    Use `uv` to install all the required packages from `requirements.txt`:
    ```bash
    uv pip install -r requirements.txt
    ```

## Running the Application

To run the FastAPI server with live reloading (ideal for development), use the following command:
```bash
uv run uvicorn app.main:app --reload
```
The application will be available at `http://127.0.0.1:8000`.

## API Usage

You can access the interactive API documentation (Swagger UI) by navigating to `http://127.0.0.1:8000/docs`.

### Authentication Endpoints

The authentication is handled via Supabase.

- **`POST /api/v1/auth/signup`**: Register a new user.
  - **Body**: `{ "email": "user@example.com", "password": "your_password" }`
  - **Behavior**:
    - If email confirmation is **enabled** in your Supabase project, it will return a `200 OK` with the message: `"Signup successful. Please check your email to confirm your account."`
    - If email confirmation is **disabled**, it will return a `201 Created` with an `access_token`.

- **`POST /api/v1/auth/login`**: Log in an existing user.
  - **Body**: `{ "email": "user@example.com", "password": "your_password" }`
  - **Success Response**: Returns a `200 OK` with an `access_token` and `token_type`.

---
This README should provide your team with a clear path to get the project up and running.
