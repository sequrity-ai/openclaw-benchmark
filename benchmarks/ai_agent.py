"""Pydantic AI agent for simulating user interactions in benchmark scenarios."""

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent

logger = logging.getLogger(__name__)


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""

    turn_number: int
    user_message: str
    bot_response: str | None
    timestamp: float
    success: bool
    error: str | None = None
    # Token usage for this turn's bot response
    input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cache_read_tokens: int = 0


@dataclass
class ConversationResult:
    """Result of a multi-turn conversation."""

    task_name: str
    task_description: str
    conversation_turns: list[ConversationTurn] = field(default_factory=list)
    total_turns: int = 0
    success: bool = False
    completion_reason: str = ""  # "goal_achieved", "max_turns", "timeout", "error"
    total_latency: float = 0.0
    error_message: str | None = None

    def add_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn to the result."""
        self.conversation_turns.append(turn)
        self.total_turns += 1

    @property
    def total_input_tokens(self) -> int:
        return sum(t.input_tokens for t in self.conversation_turns)

    @property
    def total_output_tokens(self) -> int:
        return sum(t.output_tokens for t in self.conversation_turns)

    @property
    def total_reasoning_tokens(self) -> int:
        return sum(t.reasoning_tokens for t in self.conversation_turns)

    @property
    def total_cache_read_tokens(self) -> int:
        return sum(t.cache_read_tokens for t in self.conversation_turns)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_name": self.task_name,
            "task_description": self.task_description,
            "conversation_turns": [
                {
                    "turn_number": turn.turn_number,
                    "user_message": turn.user_message,
                    "bot_response": turn.bot_response,
                    "timestamp": turn.timestamp,
                    "success": turn.success,
                    "error": turn.error,
                    "input_tokens": turn.input_tokens,
                    "output_tokens": turn.output_tokens,
                    "reasoning_tokens": turn.reasoning_tokens,
                }
                for turn in self.conversation_turns
            ],
            "total_turns": self.total_turns,
            "success": self.success,
            "completion_reason": self.completion_reason,
            "total_latency": self.total_latency,
            "error_message": self.error_message,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_reasoning_tokens": self.total_reasoning_tokens,
        }


class BenchmarkAgent:
    """AI agent that simulates a user interacting with the bot."""

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        openai_api_key: str = "",
        max_turns: int = 10,
        conversation_timeout: float = 300.0,
    ):
        """Initialize the benchmark agent.

        Args:
            model_name: OpenAI model to use for the agent
            openai_api_key: OpenAI API key
            max_turns: Maximum number of conversation turns
            conversation_timeout: Maximum time for conversation in seconds
        """
        self.model_name = model_name
        self.max_turns = max_turns
        self.conversation_timeout = conversation_timeout
        self.openai_api_key = openai_api_key

        # Initialize Pydantic AI agent
        # Pass API key via model string format: "openai:model-name"
        self.agent = Agent(
            model=f"openai:{model_name}",
            system_prompt=(
                "You are a user testing a Telegram bot's capabilities. "
                "Your goal is to interact naturally with the bot to accomplish a given task.\n\n"
                "CRITICAL INSTRUCTIONS FOR FIRST MESSAGE:\n"
                "- In your FIRST message, you MUST convey the COMPLETE task requirements EXACTLY as given\n"
                "- Include ALL specific details: file paths, exact filenames, data sources, formatting requirements\n"
                "- Do NOT simplify, paraphrase, or omit any details from the task description\n"
                "- Do NOT replace specific paths/names with placeholders or examples\n"
                "- Copy any technical specifications verbatim (paths, formats, etc.)\n\n"
                "After the first message:\n"
                "1. Follow the bot's instructions and respond appropriately\n"
                "2. Ask clarifying questions if needed\n"
                "3. Provide additional information when the bot asks\n"
                "4. Acknowledge when the task is complete\n"
                "5. Be patient and helpful\n\n"
                "Format your responses as plain text messages to send to the bot. "
                "Do not include any meta-commentary or explanations."
            ),
        )

    async def run_conversation_async(
        self, task_name: str, task_description: str, session: Any, task_timeout: float = 90.0
    ) -> ConversationResult:
        """Run a multi-turn conversation to accomplish a task.

        Args:
            task_name: Name of the task
            task_description: Description of what the user should accomplish
            session: TelegramSession or LocalSession for sending messages

        Returns:
            Conversation result with all turns and outcome
        """
        result = ConversationResult(
            task_name=task_name, task_description=task_description
        )

        start_time = time.time()
        conversation_history = []

        try:
            # Initial prompt to the agent
            initial_context = (
                f"Task: {task_description}\n\n"
                "Send your first message to the bot. Remember: you MUST include ALL details from the task description above. "
                "Do not simplify or paraphrase - include exact file paths, filenames, and all technical requirements."
            )

            # Log the initial context sent to the AI agent
            logger.info(f"[{task_name}] ===== AI AGENT INITIAL CONTEXT =====")
            logger.info(f"{initial_context}")
            logger.info(f"[{task_name}] ========================================")

            for turn_num in range(1, self.max_turns + 1):
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > self.conversation_timeout:
                    result.completion_reason = "timeout"
                    result.error_message = f"Conversation timeout after {elapsed:.1f}s"
                    logger.warning(
                        f"[{task_name}] Conversation timeout after {turn_num - 1} turns"
                    )
                    break

                turn_start = time.time()
                logger.info(f"[{task_name}] Starting turn {turn_num}/{self.max_turns}")

                try:
                    # Get agent's message using Pydantic AI
                    if turn_num == 1:
                        # First turn: use initial context
                        agent_response = await self.agent.run(initial_context)
                    else:
                        # Subsequent turns: provide conversation history
                        context = self._build_context(
                            task_description, conversation_history
                        )
                        agent_response = await self.agent.run(context)

                    # Extract the response text from Pydantic AI result
                    # The result has an 'output' attribute in the new API
                    if hasattr(agent_response, 'output'):
                        user_message = str(agent_response.output).strip()
                    elif hasattr(agent_response, 'data'):
                        user_message = str(agent_response.data).strip()
                    else:
                        user_message = str(agent_response).strip()

                    # Log FULL user message for debugging
                    logger.info(f"[{task_name}] ===== TURN {turn_num} REQUEST =====")
                    logger.info(f"[{task_name}] AI Agent → Bot (full message):")
                    logger.info(f"{user_message}")
                    logger.info(f"[{task_name}] ========================================")

                    # Send message to bot and wait for response
                    bot_response = await session.send_message_async(
                        user_message, wait_for_response=True, timeout=task_timeout
                    )

                    turn_success = bot_response is not None and bot_response.text
                    bot_text = bot_response.text if bot_response else None

                    # Extract token usage from bot response
                    input_tokens = output_tokens = reasoning_tokens = cache_read_tokens = 0
                    if bot_response and hasattr(bot_response, 'token_usage') and bot_response.token_usage:
                        input_tokens = bot_response.token_usage.input
                        output_tokens = bot_response.token_usage.output
                        reasoning_tokens = bot_response.token_usage.reasoning
                        cache_read_tokens = bot_response.token_usage.cache_read

                    # Log FULL bot response for debugging
                    logger.info(f"[{task_name}] ===== TURN {turn_num} RESPONSE =====")
                    if bot_text:
                        logger.info(f"[{task_name}] Bot → AI Agent (full response):")
                        logger.info(f"{bot_text}")
                        logger.info(f"[{task_name}] Token usage: in={input_tokens} out={output_tokens} reasoning={reasoning_tokens} cache={cache_read_tokens}")
                    else:
                        logger.warning(f"[{task_name}] Bot → AI Agent: NO RESPONSE RECEIVED")
                    logger.info(f"[{task_name}] =========================================")

                    # Record turn
                    turn = ConversationTurn(
                        turn_number=turn_num,
                        user_message=user_message,
                        bot_response=bot_text,
                        timestamp=time.time(),
                        success=turn_success,
                        error=None if turn_success else "No response from bot",
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        reasoning_tokens=reasoning_tokens,
                        cache_read_tokens=cache_read_tokens,
                    )
                    result.add_turn(turn)

                    # Update conversation history for next turn
                    conversation_history.append(
                        {"user": user_message, "bot": bot_text or "[no response]"}
                    )

                    # Check if agent indicates task completion
                    if self._is_task_complete(user_message, bot_text):
                        result.success = True
                        result.completion_reason = "goal_achieved"
                        logger.info(
                            f"[{task_name}] Task completed successfully after {turn_num} turns"
                        )
                        break

                except Exception as e:
                    logger.error(f"[{task_name}] Error on turn {turn_num}: {e}")
                    turn = ConversationTurn(
                        turn_number=turn_num,
                        user_message="",
                        bot_response=None,
                        timestamp=time.time(),
                        success=False,
                        error=str(e),
                    )
                    result.add_turn(turn)
                    result.completion_reason = "error"
                    result.error_message = str(e)
                    break

            # If loop completed without breaking
            if result.completion_reason == "":
                result.completion_reason = "max_turns"
                logger.info(f"[{task_name}] Reached max turns ({self.max_turns})")

        except Exception as e:
            logger.error(f"[{task_name}] Conversation error: {e}")
            result.completion_reason = "error"
            result.error_message = str(e)

        result.total_latency = time.time() - start_time
        return result

    def run_conversation_sync(
        self, task_name: str, task_description: str, session: Any, task_timeout: float = 90.0
    ) -> ConversationResult:
        """Run a multi-turn conversation synchronously.

        This is a wrapper around run_conversation_async using asyncio.run().

        Args:
            task_name: Name of the task
            task_description: Description of what the user should accomplish
            session: TelegramSession or LocalSession for sending messages
            task_timeout: Timeout per message send in seconds

        Returns:
            Conversation result
        """
        import asyncio

        # Run the async method synchronously using asyncio.run()
        return asyncio.run(
            self.run_conversation_async(task_name, task_description, session, task_timeout=task_timeout)
        )

    def _build_context(
        self, task_description: str, conversation_history: list[dict[str, str]]
    ) -> str:
        """Build context prompt for the agent based on conversation history.

        Args:
            task_description: Original task description
            conversation_history: List of previous turns

        Returns:
            Context prompt for the agent
        """
        context = f"Task: {task_description}\n\nConversation so far:\n"

        for i, turn in enumerate(conversation_history, 1):
            context += f"\nTurn {i}:\n"
            context += f"You: {turn['user']}\n"
            context += f"Bot: {turn['bot']}\n"

        context += (
            "\nBased on the conversation so far, what is your next message to the bot? "
            "If the task is complete, send a message acknowledging completion."
        )

        return context

    def _is_task_complete(
        self, user_message: str, bot_response: str | None
    ) -> bool:
        """Check if the task appears to be complete based on messages.

        Args:
            user_message: Latest user message
            bot_response: Latest bot response

        Returns:
            True if task seems complete
        """
        # Simple heuristic: look for completion indicators
        completion_phrases = [
            "thank you",
            "thanks",
            "done",
            "complete",
            "finished",
            "perfect",
            "great",
            "excellent",
        ]

        user_lower = user_message.lower()
        bot_lower = (bot_response or "").lower()

        # Check if user is expressing satisfaction/completion
        if any(phrase in user_lower for phrase in completion_phrases):
            return True

        # Check if bot indicates completion
        if bot_response and any(
            phrase in bot_lower
            for phrase in ["task complete", "all done", "successfully completed"]
        ):
            return True

        return False
