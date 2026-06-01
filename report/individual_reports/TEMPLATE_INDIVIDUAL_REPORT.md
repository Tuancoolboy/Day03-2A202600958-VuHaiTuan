# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Vu Hai Tuan
- **Student ID**: Not provided yet
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

- **Modules Implemented**:
  - `src/agent/agent.py`
  - `src/tools/contract_tools.py`
  - `run_agent.py`
  - `run_chatbot.py`

- **Code Highlights**:
  - Implemented the ReAct loop: generate LLM response, parse `Final Answer`, parse `Action`, execute the tool, append `Observation`, and continue until completion.
  - Implemented allowlisted tool execution using metadata from `CONTRACT_TOOLS`.
  - Added Vietnamese-first behavior in the system prompt while keeping the code/report structure in English.
  - Added `run_agent.py` to run the ReAct Agent from the terminal.
  - Added `run_chatbot.py` as a no-tool baseline chatbot for the bonus comparison.

- **Documentation**:
  - The agent receives Vietnamese user input and a system prompt containing available tools.
  - If the model returns `Action: tool_name(argument)`, the parser extracts the tool name and argument.
  - The agent executes the real Python tool and appends the returned value as `Observation`.
  - The next LLM call sees the previous observation and decides whether to call another tool or return `Final Answer`.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: When the user entered `Tóm tắt hợp đồng thuê nhà và chỉ ra rủi ro chính.` without pasting actual contract text, the agent still called analysis tools instead of asking for clarification.
- **Log Source**: `logs/2026-06-01.log`, events from `2026-06-01T09:22:50` to `2026-06-01T09:22:55`.
- **Diagnosis**:
  - The LLM generated `Action: summarize_contract(contract_text)`.
  - `_resolve_tool_args()` mapped `contract_text` to the current user input.
  - Since the user input was only a request and not real contract content, the tool found missing clause groups and returned a generic risk analysis.
  - The root cause was missing pre-tool validation and a prompt that did not strongly require clarification for insufficient input.
- **Solution**:
  - The current report documents this as a limitation and failure trace.
  - The next improvement is to add validation before tool execution: if the input is too short or does not look like a contract, the agent should ask the user to provide the full contract text before calling tools.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: The `Thought` block helped the agent split the problem into smaller steps. For a contract with several clauses, the agent first used `summarize_contract`, then used `analyze_risks`, and only then produced the final Vietnamese answer.

2. **Reliability**: The agent can perform worse than the chatbot when the input is incomplete. In the missing-contract case, the chatbot correctly asked for more information, while the agent still tried to use tools and produced a generic answer.

3. **Observation**: Observations made the final response more grounded than pure LLM guessing. For example, after `analyze_risks` returned non-refundable deposit and unclear termination risks, the agent used those observations to generate a structured final answer.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Move tool execution into a separate service or asynchronous queue for large batches of contracts.
- **Safety**: Add a validator that checks whether the input actually contains contract text before running contract-analysis tools.
- **Performance**: Cache `extract_clauses` and `analyze_risks` results for repeated analysis of the same contract.
- **Reliability**: Replace regex-based tool argument parsing with structured tool schemas.
- **Observability**: Add explicit cost tracking based on token usage and provider pricing.

---

> [!NOTE]
> Submit this report by renaming it to `REPORT_[YOUR_NAME].md` and placing it in this folder.
