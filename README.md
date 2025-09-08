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

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI/Starlette app with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
```

Set environment variables in `.env`:

```env
REDIS_URL=redis://localhost:6379/0
DESCOPE_CLIENT_ID=<your_client_id>
DESCOPE_CLIENT_SECRET=<your_client_secret>
DESCOPE_PROJECT_KEY=<your_project_key>
DESCOPE_TOKEN_URL=<descope_token_url>
CLAUDE_API_KEY=<CLAUDE_KEY>
```

---

## Running the Service

After activating your virtual environment:

```bash
# Run the FastAPI/Starlette app with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8003 --reload
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
