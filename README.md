# CrimeAgent Microservice

**CrimeAgent** is a specialized AI agent designed to handle crime-related emergencies and complaints. It supports real-time guidance during emergencies (e.g., robbery, assault, burglary) and structured complaint intake (e.g., theft, vandalism, fraud, noise disturbances).

---

## Features

* **Emergency Response:** Step-by-step guidance for immediate safety in crime situations.
* **Complaint Intake:** Structured collection and documentation of crime-related complaints.
* **M2M Authentication:** Machine-to-Machine token verification using Descope OAuth2.
* **Token Caching:** Redis caching for efficient token reuse.
* **Streaming Responses:** Stepwise, conversational guidance instead of full responses at once.
* **Routing Rules:** Flexible routing between `CrimeAgent`, `OrchestratorAgent`, and `finish`.

---

## Technologies

* Python 3.11+
* FastAPI / Starlette
* Redis (async)
* aiohttp
* Uvicorn
* Descope OAuth2 for M2M authentication
* Custom middleware for secure token validation

---

## Installation

```bash
# Activate your virtual environment first
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install dependencies using Poetry (ensure pyproject.toml is present)
poetry install

# Copy .env.example to .env and fill in your actual keys
cp .env.example .env
# Ensure .env contains:
# ANTHROPIC_API_KEY
# DESCOPE_PROJECT_KEY
# DATABASE_URL
# DESCOPE_CLIENT_ID
# DESCOPE_CLIENT_SECRET
# DESCOPE_TOKEN_URL

# Run the CrimeAgent FastAPI app
python3 -m src.agents.CrimeAgent

# Option 2: Run using Docker image
# --------------------------------
# Pull the pre-built CrimeAgent Docker image
docker pull ghcr.io/sohansouri47/crime_agent:1.0.0

# Run the container (make sure your .env is configured)
docker run --name crime_agent \
  --env-file .env \
  -p 8003:8003 \
  ghcr.io/sohansouri47/crime_agent:1.0.0
```

Set environment variables in `.env`:

```env
# ANTHROPIC_API_KEY
# DESCOPE_PROJECT_KEY
# DATABASE_URL
# DESCOPE_CLIENT_ID
# DESCOPE_CLIENT_SECRET
# DESCOPE_TOKEN_URL
```

---

## Running the Service

After activating your virtual environment:

```bash
# Run the FastAPI/Starlette app with Uvicorn
python3 -m src.agents.CrimeAgent
```

**Parameters:**

* `main:app` → `main` is your Python file (`main.py`) and `app` is the Starlette/FastAPI app object.
* `--host 0.0.0.0` → accessible from other machines on the network.
* `--port 8003` → the port the agent runs on.
* `--reload` → auto-reloads on code changes (useful for development).

## Middleware

`M2MMiddleware` ensures that only valid machine-to-machine tokens with the required scope (`crime_agent`) can access protected endpoints.

---

## Token Management

`OAuth` class provides:

* M2M token generation using Descope OAuth2 `client_credentials` grant.
* Redis caching of tokens to avoid repeated authentication requests.
* Automatic handling of token expiration with a buffer.

