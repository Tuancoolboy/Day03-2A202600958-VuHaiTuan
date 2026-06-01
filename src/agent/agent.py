import ast
import re
from typing import List, Dict, Any, Optional, Tuple
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        Build the system prompt that instructs the model to follow ReAct.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
You are a ReAct-style AI assistant for contract review and analysis.
You can reason step by step and call tools when you need factual checks or structured extraction.

Available tools:
{tool_descriptions}

Rules:
- Use only the tools listed above.
- Use exactly one Action at a time.
- After writing an Action, stop. The program will execute the tool and add the Observation.
- If you have enough information, do not call a tool; write Final Answer.
- Tool arguments are plain strings. For contract tools, pass the original contract text or a previous Observation.
- If a tool returns missing data, say that clearly instead of inventing facts.
- Reply in Vietnamese unless the user explicitly asks for another language.
- Always include a short Vietnamese note that this is not official legal advice for important legal decisions.

Format:
Thought: brief reasoning about what to do next.
Action: tool_name(argument)

Or:
Thought: brief reasoning about why you can answer now.
Final Answer: your final response to the user in Vietnamese.
""".strip()

    def run(self, user_input: str) -> str:
        """
        Implement the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation to prompt and repeat until Final Answer.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        scratchpad = ""
        self._current_user_input = user_input
        self._last_observation = ""

        for step in range(1, self.max_steps + 1):
            current_prompt = self._build_prompt(user_input, scratchpad)
            result = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            content = str(result.get("content", "")).strip()

            logger.log_event(
                "AGENT_LLM_RESPONSE",
                {
                    "step": step,
                    "content": content,
                    "usage": result.get("usage", {}),
                    "latency_ms": result.get("latency_ms"),
                    "provider": result.get("provider"),
                },
            )
            self.history.append({"step": step, "llm_response": content})

            final_answer = self._extract_final_answer(content)
            if final_answer:
                logger.log_event("AGENT_END", {"steps": step, "status": "final_answer"})
                return final_answer

            action = self._parse_action(content)
            if not action:
                observation = (
                    "Parser error: no valid Action found. Use format "
                    "Action: tool_name(argument), or return Final Answer."
                )
                logger.log_event("AGENT_PARSE_ERROR", {"step": step, "content": content})
            else:
                tool_name, args = action
                observation = self._execute_tool(tool_name, args)
                logger.log_event(
                    "AGENT_TOOL_CALL",
                    {
                        "step": step,
                        "tool": tool_name,
                        "args_preview": args[:500],
                        "observation_preview": observation[:1000],
                    },
                )

            scratchpad += f"\n{content}\nObservation: {observation}\n"
            self._last_observation = observation
            self.history.append({"step": step, "observation": observation})

        logger.log_event("AGENT_END", {"steps": self.max_steps, "status": "max_steps_exceeded"})
        return (
            "I could not produce a final answer within the allowed steps. "
            "Please review the trace/logs or increase max_steps."
        )

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Helper method to execute tools by name.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                tool_fn = tool.get("function") or tool.get("func")
                if not callable(tool_fn):
                    logger.log_event("TOOL_ERROR", {"tool_name": tool_name, "error": "missing_callable"})
                    return f"Tool {tool_name} has no callable function."

                try:
                    return str(tool_fn(self._resolve_tool_args(args)))
                except Exception as exc:
                    logger.log_event("TOOL_ERROR", {"tool_name": tool_name, "args": args, "error": str(exc)})
                    return f"Tool {tool_name} failed with error: {exc}"
        logger.log_event("UNKNOWN_TOOL", {"tool_name": tool_name})
        return f"Tool {tool_name} not found."

    def _resolve_tool_args(self, args: str) -> str:
        normalized_args = args.strip().lower()
        user_input_aliases = {
            "contract_text",
            "user_input",
            "original_contract_text",
            "original contract text",
            "the contract text",
        }
        observation_aliases = {
            "observation",
            "last_observation",
            "previous_observation",
            "previous observation",
        }

        if normalized_args in user_input_aliases:
            return getattr(self, "_current_user_input", args)
        if normalized_args in observation_aliases:
            return getattr(self, "_last_observation", args)
        return args

    def _build_prompt(self, user_input: str, scratchpad: str) -> str:
        if not scratchpad.strip():
            return f"User request:\n{user_input}\n\nStart your first Thought."

        return (
            f"User request:\n{user_input}\n\n"
            f"Previous reasoning and observations:\n{scratchpad}\n"
            "Continue with the next Thought. If ready, provide Final Answer."
        )

    def _extract_final_answer(self, text: str) -> Optional[str]:
        match = re.search(r"Final Answer\s*:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return None
        return match.group(1).strip()

    def _parse_action(self, text: str) -> Optional[Tuple[str, str]]:
        """
        Parse Action lines like:
        Action: tool_name(argument)
        Action: tool_name("argument")
        """
        action_text = re.split(r"\nObservation\s*:", text, maxsplit=1, flags=re.IGNORECASE)[0]
        match = re.search(
            r"Action\s*:\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)\s*$",
            action_text.strip(),
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return None

        tool_name = match.group(1).strip()
        raw_args = match.group(2).strip()
        return tool_name, self._clean_tool_args(raw_args)

    def _clean_tool_args(self, raw_args: str) -> str:
        if not raw_args:
            return ""

        try:
            parsed = ast.literal_eval(raw_args)
            if isinstance(parsed, str):
                return parsed
        except (ValueError, SyntaxError):
            pass

        return raw_args.strip().strip('"').strip("'")
