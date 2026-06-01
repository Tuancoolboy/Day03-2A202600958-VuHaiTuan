import argparse
import sys

from run_agent import PROJECT_ROOT, build_llm, load_env_file


def main() -> None:
    load_env_file(PROJECT_ROOT / ".env")

    parser = argparse.ArgumentParser(description="Run the baseline chatbot without tools.")
    parser.add_argument("prompt", nargs="*", help="Question or contract text to send to the chatbot.")
    args = parser.parse_args()

    user_input = " ".join(args.prompt).strip()
    if not user_input:
        user_input = input("User: ").strip()
    if not user_input:
        raise SystemExit("No input provided.")

    llm = build_llm()
    result = llm.generate(
        user_input,
        system_prompt=(
            "Bạn là chatbot hỗ trợ rà soát hợp đồng. "
            "Trả lời bằng tiếng Việt. Không được gọi tool; chỉ dựa trên nội dung người dùng cung cấp."
        ),
    )

    print("\nChatbot:")
    print(str(result.get("content", "")).strip())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nStopped.")
