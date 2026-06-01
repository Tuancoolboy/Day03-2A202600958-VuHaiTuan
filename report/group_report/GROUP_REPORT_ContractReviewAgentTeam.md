# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Contract Review Agent Team
- **Team Members**: Vu Hai Tuan
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

Our team built a Vietnamese contract-review ReAct Agent. The agent receives Vietnamese contract text, reasons through a `Thought -> Action -> Observation` loop, calls contract-analysis tools, and returns a Vietnamese final answer with a summary and key legal-risk warnings. The final version also includes deterministic guardrails for out-of-domain questions and missing contract content.

- **Success Rate**: 3/3 ReAct smoke tests produced a valid `Final Answer`; 2/2 guardrail checks returned safe responses without unnecessary LLM/tool calls.
- **Key Outcome**: The agent performed better than the baseline chatbot on multi-step contract analysis because it used structured tool observations from `summarize_contract` and `analyze_risks` before generating the final response. V2 also reduced avoidable failures by asking for contract text when the user did not provide enough information.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

The main loop is implemented in `src/agent/agent.py`:

```text
User input in Vietnamese
  -> System prompt with tool inventory and ReAct format
  -> LLM returns either Thought + Action or Final Answer
  -> Parser extracts Action: tool_name(argument)
  -> Agent executes an allowlisted Python tool
  -> Tool result is appended as Observation
  -> The updated prompt is sent back to the LLM
  -> Repeat until Final Answer or max_steps
```

The agent uses `max_steps=5` to prevent infinite loops. Each important event is logged as structured JSON, including `AGENT_START`, `AGENT_LLM_RESPONSE`, `AGENT_TOOL_CALL`, and `AGENT_END`.
Before entering the LLM loop, V2 runs domain/input guardrails:

- out-of-domain requests are rejected politely;
- analysis requests without actual contract text ask the user to paste the contract first;
- valid contract-review requests continue into the ReAct loop.

### 2.2 Tool Definitions (Inventory)

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `detect_contract_type` | `string` | Detect the broad contract type from Vietnamese contract text. |
| `extract_clauses` | `string` | Extract important clause groups such as deposit, payment, duration, termination, penalty, responsibility, and dispute. |
| `legal_lookup` | `string` | Return static legal-reference hints for a contract type or topic. |
| `analyze_risks` | `string` | Detect common contract risks from raw contract text or extracted-clause output. |
| `generate_questions` | `string` | Generate questions the user should ask before signing. |
| `summarize_contract` | `string` | Produce a short structured summary and identify missing or unclear clause groups. |

### 2.3 LLM Providers Used

- **Primary**: GPT-4o through `OpenAIProvider`
- **Secondary (Backup)**: Gemini 1.5 Flash through `GeminiProvider`
- **Local Option**: Phi-3 GGUF through `LocalProvider`; not used in the final test run because it requires a separately downloaded local model.

---

## 3. Telemetry & Performance Dashboard

Metrics were collected from `logs/2026-06-01.log` during the final 3 agent smoke tests:

- **Average Latency (P50)**: 1837ms per LLM call
- **Max Latency (P99 approximation)**: 5102ms
- **Average Tokens per Task**: approximately 1976 tokens per agent task
- **Total Tokens for Agent Tests**: 5929 tokens across 7 LLM calls
- **Total Cost of Test Suite**: V2 adds `LLM_METRIC.cost_estimate_usd`, configurable through model-specific environment variables such as `GPT_4O_PROMPT_USD_PER_1K` and `GPT_4O_COMPLETION_USD_PER_1K`. Exact billing should still be verified in the provider dashboard.

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Missing Contract Content

- **Input**: `Tóm tắt hợp đồng thuê nhà và chỉ ra rủi ro chính.`
- **V1 Observation**: The agent called `summarize_contract(contract_text)` and `analyze_risks(contract_text)` even though the user did not provide the actual contract text. The tools returned many missing clause groups and a generic dispute-resolution risk.
- **Root Cause**: The system prompt did not explicitly tell the agent to ask for clarification when the input does not contain enough contract content. Also, `_resolve_tool_args()` maps the alias `contract_text` to the current user input, so the tools analyzed the request itself instead of an actual contract.
- **Impact**: The agent still produced a final answer, but the answer was generic and not reliable for a specific contract.
- **V2 Fix**: Added pre-tool validation in `ReActAgent._guardrail_response()`. If the input is too short or does not look like contract text, the agent returns a safe Vietnamese clarification request before calling the LLM or tools.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2

- **Diff**: Prompt v2 added rules to use only allowlisted tools, call exactly one action per turn, never fabricate observations, answer in Vietnamese, include a legal-disclaimer note, and reject out-of-domain requests.
- **Result**: In the final 3 smoke tests, the agent had no parser errors, ended with `Final Answer` in every run, and responded in Vietnamese.

### Experiment 2: Agent v1 vs Agent v2 Guardrails

- **Diff**: V2 added deterministic guardrails before the LLM loop for out-of-scope requests and missing contract content.
- **Result**: `Hôm nay thời tiết thế nào?` is rejected as out of scope. `Tóm tắt hợp đồng thuê nhà...` without actual contract text returns a clarification request instead of wasting tool calls.

### Experiment 3 (Bonus): Chatbot vs Agent

| Case | Chatbot Result | Agent Result | Winner |
| :--- | :--- | :--- | :--- |
| Simple Q: `Hợp đồng thuê nhà là gì?` | Correctly explained the concept in Vietnamese. | Correctly answered without using tools. | Draw |
| Vietnamese rental contract with non-refundable deposit and missing dispute clause | Summarized the contract and mentioned deposit/dispute risks. | Called `summarize_contract` and `analyze_risks`, then identified 3 structured risks: non-refundable deposit, unclear termination, and missing/unclear dispute resolution. | **Agent** |
| Missing actual contract text | Asked the user to provide the contract and gave a general checklist. | V2 returns a deterministic clarification request before LLM/tool calls. | **Agent v2** |

---

## 6. Production Readiness Review

- **Security**: Tool execution is limited to an allowlist from `self.tools`; the agent does not execute arbitrary functions. Input-size limits and stricter validation should be added.
- **Guardrails**: `max_steps=5` prevents infinite loops and uncontrolled billing. The parser accepts only the `Action: tool_name(argument)` format. V2 also blocks out-of-domain requests and missing-contract analysis requests before the LLM loop.
- **Observability**: Structured logs capture LLM responses, tool calls, observations, and termination status.
- **Reliability**: Tool-argument validation should be improved so the model cannot pass vague aliases or insufficient text into analysis tools.
- **Scaling**: A graph-based workflow such as LangGraph would be useful for more contract types, branching policies, and human-in-the-loop review.
- **Cost Control**: `LLM_METRIC` logs token usage, latency, and configurable `cost_estimate_usd`.

---

> [!NOTE]
> This report has been renamed for submission as `GROUP_REPORT_ContractReviewAgentTeam.md`.
