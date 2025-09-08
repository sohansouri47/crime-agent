import uvicorn
from a2a.types import AgentSkill, AgentCard, AgentCapabilities
from a2a.server.request_handlers import DefaultRequestHandler
from src.agents.CrimeAgent.agent_executor import CrimeAgentExecutor
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.apps import A2AStarletteApplication
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from descope import DescopeClient
from descope.exceptions import AuthException
from src.common.logger.logger import get_logger
from src.common.config.config import Auth

logger = get_logger("CrimeAgent-M2M_Validation")
descope_client = DescopeClient(project_id=Auth.Descope.DESCOPE_PROJECT_KEY)


class M2MMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify Machine-to-Machine (M2M) Bearer tokens
    """

    def __init__(self, app, required_scope: str = "crime_agent"):
        super().__init__(app)
        self.required_scope = required_scope

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/.well-known"):
            logger.info("Accessing public endpoint: %s", request.url.path)
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.info("Missing or invalid Authorization header")
            raise HTTPException(status_code=401, detail="Missing bearer token")

        token = auth_header.split(" ", 1)[1].strip()
        logger.info("Received token, validating...")

        try:
            claims = descope_client._auth._validate_token(
                token, audience=Auth.Descope.DESCOPE_PROJECT_KEY
            )
            logger.info("VALID M2M token for Agent: %s", self.required_scope)
        except AuthException as e:
            logger.info("Invalid M2M token: %s", e)
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

        # Check required scope
        token_scope = claims.get("scope", "")
        if isinstance(token_scope, str):
            token_scope = token_scope.split()

        if self.required_scope not in token_scope:
            logger.info(
                "Token missing required scope '%s', token scopes: %s",
                self.required_scope,
                token_scope,
            )
            raise HTTPException(
                status_code=403, detail=f"Missing required scope: {self.required_scope}"
            )

        logger.info("Token scope verified, continuing request")
        return await call_next(request)


def main():
    """Main function to create and run the crime agent."""

    skills = [
        AgentSkill(
            id="crime_emergency_response",
            name="Crime Emergency Response",
            description="Handle active crime emergencies such as robbery, assault, or burglary in progress",
            tags=["crime", "emergency", "safety", "response"],
            examples=[
                "Guidance during an armed robbery",
                "Steps to stay safe during an assault",
                "Burglary in progress response",
            ],
        ),
        AgentSkill(
            id="crime_complaint_intake",
            name="Crime Complaint Intake",
            description="Take in and process user complaints such as theft, vandalism, fraud, or disturbances",
            tags=["complaint", "report", "documentation", "resolution"],
            examples=[
                "Report a stolen bicycle",
                "File a noise complaint against neighbors",
                "Log a vandalism complaint for broken windows",
            ],
        ),
    ]

    agent_card = AgentCard(
        name="crime_agent",
        description="Specialized crime response and complaint-handling agent, covering emergencies, general complaints (e.g., theft, noise, vandalism), and prevention guidance.",
        url="http://localhost:8003/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=skills,
        capabilities=AgentCapabilities(streaming=True),
    )

    request_handler = DefaultRequestHandler(
        agent_executor=CrimeAgentExecutor(), task_store=InMemoryTaskStore()
    )

    server = A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )
    app = server.build()
    app.add_middleware(M2MMiddleware)
    uvicorn.run(app, host="0.0.0.0", port=8003)


if __name__ == "__main__":
    main()
