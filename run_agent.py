import argparse
import os
import sys
from pathlib import Path

from src.agent.agent import ReActAgent
from src.tools.contract_tools import CONTRACT_TOOLS


PROJECT_ROOT = Path(__file__).resolve().parent


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def env_value(name: str) -> str:
    value = os.getenv(name, "").strip()
    if value.startswith("your_") or value.endswith("_here"):
        return ""
    return value


def build_llm():
    provider = env_value("DEFAULT_PROVIDER").lower() or "google"
    model_name = env_value("DEFAULT_MODEL")

    if provider in {"google", "gemini"}:
        try:
            from src.core.gemini_provider import GeminiProvider
        except ModuleNotFoundError as exc:
            raise SystemExit("Missing package. Run: python -m pip install google-generativeai") from exc

        api_key = env_value("GEMINI_API_KEY")
        if not api_key:
            raise SystemExit("Missing GEMINI_API_KEY in .env")
        return GeminiProvider(model_name=model_name or "gemini-1.5-flash", api_key=api_key)

    if provider == "openai":
        try:
            from src.core.openai_provider import OpenAIProvider
        except ModuleNotFoundError as exc:
            raise SystemExit("Missing package. Run: python -m pip install openai") from exc

        api_key = env_value("OPENAI_API_KEY")
        if not api_key:
            raise SystemExit("Missing OPENAI_API_KEY in .env")
        return OpenAIProvider(model_name=model_name or "gpt-4o", api_key=api_key)

    if provider == "local":
        try:
            from src.core.local_provider import LocalProvider
        except ModuleNotFoundError as exc:
            raise SystemExit("Missing package. Run: python -m pip install llama-cpp-python") from exc

        model_path = env_value("LOCAL_MODEL_PATH") or "./models/Phi-3-mini-4k-instruct-q4.gguf"
        return LocalProvider(model_path=model_path)

    raise SystemExit(f"Unsupported DEFAULT_PROVIDER={provider}. Use google, openai, or local.")


def main() -> None:
    load_env_file(PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description="Run the ReAct contract-review agent.")
    parser.add_argument("prompt", nargs="*", help="Question or contract text to send to the agent.")
    parser.add_argument("--max-steps", type=int, default=5)
    args = parser.parse_args()

    user_input = " ".join(args.prompt).strip()
    if not user_input:
        user_input = input("User: ").strip()
    if not user_input:
        raise SystemExit("No input provided.")

    agent = ReActAgent(llm=build_llm(), tools=CONTRACT_TOOLS, max_steps=args.max_steps)
    answer = agent.run(user_input)
    print("\nAgent:")
    print(answer)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped.")
