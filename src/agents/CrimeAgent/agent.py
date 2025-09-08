from google.adk.agents import LlmAgent
from google.adk.tools.function_tool import FunctionTool
from src.common.config.prompts import AgentPrompts
from src.common.config.constants import LlmConfig
from google.adk.models.lite_llm import LiteLlm
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from collections.abc import AsyncIterable
import uuid
from src.common.db.Postgre import ConversationHistoryManager
from src.common.logger.logger import get_logger
import json
import asyncio
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
import re

logger = get_logger("CrimeAgent-Agent")


class CrimeAgent:
    def __init__(self):
        self._agent = None
        self.history_manger = ConversationHistoryManager()
        self._runner = None
        self._user_id = None

    async def _initialize(self):
        self._agent = await self._build_agent()
        self._runner = Runner(
            app_name=AgentPrompts.CrimeAgent.NAME,
            agent=self._agent,
            session_service=InMemorySessionService(),
        )

    async def call_cops(self, reason: str):
        logger.info("Tool Call - Called cops")
        response = {
            "agent": "crime_agent",
            "response": "we have called the cops and gave them necesary information",
            "next_agent": "crime_agent",
        }
        logger.info(f"Here is the reason given to cops:{reason}")
        return response

    async def _build_agent(self) -> LlmAgent:
        conversation_history = await self.history_manger.fetch_last_n(
            self._context_id, 8
        )
        logger.info(f"Fetch Conversation History:{conversation_history}")
        return LlmAgent(
            name=AgentPrompts.CrimeAgent.NAME,
            instruction=AgentPrompts.CrimeAgent.INSTRUCTION.format(
                conversation_history=conversation_history
            ),
            description=AgentPrompts.CrimeAgent.DESCRIPTION,
            model=LiteLlm(model=LlmConfig.Anthropic.SONET_4_MODEL),
            tools=[self.call_cops],
        )

    async def invoke(self, query: str, context_id: str) -> AsyncIterable[dict]:
        try:
            payload: dict[str, str] = json.loads(query)
            self._user_id = payload.get("user")
            self._context_id = context_id
            self._role = payload.get("role")
            user_query = payload.get("msg")
            logger.info([self._user_id, self._context_id, self._role, user_query])
        except (json.JSONDecodeError, AttributeError):
            self._user_id = None
            self._context_id = context_id
        await self._initialize()
        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            session_id=self._context_id,
            user_id=self._user_id,
        )

        if not session:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                session_id=self._context_id,
                user_id=self._user_id,
            )

        user_content = types.Content(
            role=self._role, parts=[types.Part.from_text(text=user_query)]
        )

        async for event in self._runner.run_async(
            user_id=self._user_id, new_message=user_content, session_id=self._context_id
        ):
            if event.is_final_response():
                final_response = ""
                if (
                    event.content
                    and event.content.parts
                    and event.content.parts[-1].text
                ):
                    final_response = event.content.parts[-1].text

                logger.info("Answer received from the agent")
                yield {"is_task_complete": True, "content": final_response}
            else:
                yield {
                    "is_task_complete": False,
                    "updates": "Crime Agent is assessing the emergency...",
                }
