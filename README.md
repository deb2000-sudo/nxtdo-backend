# NxtDo Backend

A FastAPI backend application with Firebase authentication.

## Project Structure

```
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── api/
│   │   └── tasks.py     # Task-related API endpoints
│   └── core/
│       ├── config.py    # Application configuration
│       ├── database.py  # Database connection setup
│       └── firebase.py  # Firebase integration
├── Dockerfile           # Docker container configuration
├── pyproject.toml       # Python dependencies and project metadata
├── uv.lock              # uv lockfile for reproducible builds
├── .env.example         # Environment variables template
└── .python-version      # Python version specification (3.12)
```

## Prerequisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) - Fast Python package manager
- Firebase project with service account credentials
- (Optional) Azure AD for authentication

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd nxtdo-backend
```

### 2. Install uv (if not already installed)

```bash
# On Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 3. Install dependencies

```bash
# This creates a virtual environment and installs all dependencies
uv sync
```

### 4. Configure environment variables

```bash
# Copy the example environment file
cp .env.example .env
```

Update the `.env` file with your configuration:

| Variable | Description |
|----------|-------------|
| `ENVIRONMENT` | `development` or `production` |
| `GCP_PROJECT_ID` | Your Google Cloud Project ID |
| `FIREBASE_SERVICE_ACCOUNT_KEY` | Firebase service account JSON (as a single line) |
| `AZURE_CLIENT_ID` | (Optional) Azure AD Client ID |
| `AZURE_TENANT_ID` | (Optional) Azure AD Tenant ID |

### 5. Run the application

```bash
# Using uv run (recommended)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or activate the virtual environment first
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# Then run uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running with Docker

```bash
# Build the image
docker build -t nxtdo-backend .

# Run the container
docker run -p 8080:8080 --env-file .env nxtdo-backend
```

> **Note:** The Docker container runs on port `8080` by default.

## Development

### Adding new dependencies

```bash
uv add <package-name>
```

### Running tests

```bash
uv run pytest
```

### Code checks

```bash
uv run python .github/check.py
```
