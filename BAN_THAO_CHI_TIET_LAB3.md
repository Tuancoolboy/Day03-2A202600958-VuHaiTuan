# Bản thảo chi tiết: Lab 3 - Chatbot vs ReAct Agent

## 1. Tổng quan

Lab 3 tập trung vào việc so sánh hai cách xây dựng ứng dụng AI:

- Chatbot LLM truyền thống: nhận câu hỏi và trả lời trực tiếp bằng năng lực sinh văn bản của mô hình.
- ReAct Agent: kết hợp suy luận từng bước với khả năng gọi công cụ bên ngoài theo vòng lặp `Thought -> Action -> Observation`.

Mục tiêu chính của lab không chỉ là tạo ra một chương trình chạy được, mà là hiểu cách thiết kế một hệ thống AI có khả năng hành động, quan sát kết quả, phân tích lỗi và cải thiện dựa trên dữ liệu đo lường.

Trong phiên bản hiện tại, repository là một bộ khung production prototype. Các thành phần provider LLM, telemetry, logging, rubric và template báo cáo đã được chuẩn bị. Phần agent trong `src/agent/agent.py` vẫn còn các TODO để sinh viên hoàn thiện vòng lặp ReAct.

## 2. Mục tiêu học tập

Sau khi hoàn thành lab, người học cần nắm được các nội dung sau:

1. Hiểu giới hạn của chatbot truyền thống khi gặp bài toán nhiều bước.
2. Hiểu cơ chế ReAct gồm suy nghĩ, chọn hành động, nhận quan sát và lặp lại.
3. Biết cách thiết kế tool description để LLM hiểu khi nào và cách dùng công cụ.
4. Biết chuyển đổi giữa nhiều LLM provider qua interface chung.
5. Biết dùng log JSON có cấu trúc để phân tích lỗi, độ trễ, token và chi phí ước lượng.
6. Biết đánh giá hệ thống bằng dữ liệu thực nghiệm thay vì chỉ dựa vào cảm giác.
7. Biết viết báo cáo nhóm và báo cáo cá nhân dựa trên trace, lỗi và kết quả cải tiến.

## 3. Cấu trúc repository

Repository có các nhóm file chính:

```text
Day-3-Lab-Chatbot-vs-react-agent/
├── README.md
├── INSTRUCTOR_GUIDE.md
├── EVALUATION.md
├── SCORING.md
├── requirements.txt
├── .env.example
├── src/
│   ├── agent/
│   │   └── agent.py
│   ├── core/
│   │   ├── llm_provider.py
│   │   ├── openai_provider.py
│   │   ├── gemini_provider.py
│   │   └── local_provider.py
│   └── telemetry/
│       ├── logger.py
│       └── metrics.py
├── tests/
│   └── test_local.py
└── report/
    ├── group_report/
    │   └── TEMPLATE_GROUP_REPORT.md
    └── individual_reports/
        └── TEMPLATE_INDIVIDUAL_REPORT.md
```

Ý nghĩa tổng quát:

- `README.md`: giới thiệu lab, cách cài đặt, mục tiêu và cách chạy với model local.
- `INSTRUCTOR_GUIDE.md`: hướng dẫn giảng viên tổ chức buổi lab 4 giờ.
- `EVALUATION.md`: mô tả các metric đánh giá hệ thống agent.
- `SCORING.md`: rubric chấm điểm nhóm và cá nhân.
- `src/core/`: chứa abstraction và các provider cho OpenAI, Gemini, local model.
- `src/agent/`: chứa skeleton của ReAct Agent.
- `src/telemetry/`: chứa logging và tracking metric.
- `tests/`: chứa test mẫu cho local provider.
- `report/`: chứa template báo cáo nhóm và cá nhân.

## 4. Nội dung README.md

README xác định lab là "Chatbot vs ReAct Agent (Industry Edition)", thuộc giai đoạn 3 của khóa học Agentic AI. Trọng tâm là đi từ chatbot LLM đơn giản đến ReAct Agent có monitoring theo hướng công nghiệp.

Các phần chính trong README:

- Cài đặt môi trường bằng cách copy `.env.example` sang `.env`.
- Cài dependency bằng `pip install -r requirements.txt`.
- Nhắc tới thư mục mở rộng `src/tools/` để sinh viên tự thêm custom tools.
- Hướng dẫn chạy local model bằng `llama-cpp-python`.
- Gợi ý model local là Phi-3-mini-4k-instruct dạng GGUF.
- Hướng dẫn đặt model vào thư mục `models/`.
- Hướng dẫn cấu hình `.env` với `DEFAULT_PROVIDER=local` và `LOCAL_MODEL_PATH`.

README cũng liệt kê các mục tiêu lab:

1. Quan sát giới hạn của chatbot baseline.
2. Cài đặt vòng lặp ReAct trong `src/agent/agent.py`.
3. Chuyển đổi provider giữa OpenAI và Gemini qua interface `LLMProvider`.
4. Phân tích lỗi qua structured logs trong `logs/`.
5. Theo rubric trong `SCORING.md` để tối đa điểm và mở rộng metric bonus.

Điểm quan trọng của README là định vị codebase như một production prototype: có telemetry, provider pattern rõ ràng và skeleton để sinh viên tập trung vào reasoning logic.

## 5. Hướng dẫn giảng viên trong INSTRUCTOR_GUIDE.md

File này thiết kế cho buổi lab 240 phút, tức 4 giờ. Mục tiêu sư phạm là giúp sinh viên chuyển từ "viết code chạy được" sang "xây hệ thống có thể suy luận và cải tiến".

Các learning objectives:

- ReAct Mechanics: hiểu chu trình `Thought -> Action -> Observation`.
- Industry Observability: debug "bộ não" LLM qua JSON log có cấu trúc.
- Iterative Refinement: cải thiện hiệu năng bằng cách đọc failure trace.

Timeline đề xuất:

1. The Hook - 15 phút  
   Giảng viên demo chatbot thất bại trước truy vấn nhiều bước, ví dụ tìm giá rẻ nhất rồi tính thuế.

2. Phase 1: Tool Design - 30 phút  
   Sinh viên định nghĩa tool trong `src/tools/`. Điểm nhấn là tool description phải rõ ràng vì LLM chỉ biết tool qua mô tả dạng text.

3. Phase 2: Chatbot Baseline - 30 phút  
   Chạy chatbot baseline với test case phức tạp để thấy prompt engineering đơn thuần không đủ.

4. Phase 3: Building Agent v1 - 60 phút  
   Cài đặt `agent/agent.py`, đặc biệt là logic parse action, gọi tool và đưa observation trở lại prompt.

5. Phase 4: Failure Analysis - 45 phút  
   Mở thư mục `logs/`, tìm event `LLM_METRIC`, phân tích trường hợp chọn sai tool, hallucinate argument hoặc lỗi parser.

6. Phase 5: Group Evaluation - 30 phút  
   Chạy test suite, tạo bảng cho group report và thảo luận agent thắng chatbot ở đâu, chatbot vẫn tốt hơn ở đâu.

Kịch bản khuyến nghị là "Smart E-commerce Assistant" với các tool như:

- `check_stock(item_name)`: kiểm tra tồn kho.
- `get_discount(coupon_code)`: lấy phần trăm giảm giá.
- `calc_shipping(weight, destination)`: tính phí vận chuyển.

Các lỗi thường gặp:

- Infinite loop do agent lặp lại Thought giống nhau.
- JSON/parser error do LLM trả về markdown hoặc format không đúng.
- Empty observation do tool trả về không có dữ liệu.

Thông điệp chính dành cho giảng viên: trace là sự thật. Hãy dạy sinh viên đọc log.

## 6. Đánh giá trong EVALUATION.md

File `EVALUATION.md` nhấn mạnh rằng lab không chỉ hỏi "có chạy không", mà hỏi "chạy tốt đến mức nào".

Các metric chính:

### 6.1 Token Efficiency

Token efficiency đo số lượng token trong prompt và completion. Prompt quá dài, agent sinh quá nhiều chatter hoặc gọi tool lòng vòng đều làm tăng chi phí.

Trong hệ thống production, số token ảnh hưởng trực tiếp đến:

- Chi phí API.
- Tốc độ phản hồi.
- Khả năng scale khi có nhiều người dùng.

### 6.2 Latency

Latency gồm:

- Time-to-First-Token: mô hình bắt đầu trả lời nhanh hay chậm.
- Total duration: tổng thời gian của toàn bộ vòng lặp ReAct, gồm nhiều lần gọi LLM và tool execution.

Mục tiêu production được nêu là người dùng thường kỳ vọng phản hồi trong khoảng 200ms đến 2s.

### 6.3 Loop Count

Loop count đo số chu kỳ `Thought -> Action` mà agent cần để hoàn thành nhiệm vụ.

Metric này giúp đánh giá:

- Agent có suy luận hiệu quả không.
- Agent có biết dừng bằng `Final Answer` không.
- Agent có bị kẹt trong vòng lặp vô hạn không.

### 6.4 Failure Analysis

Các lỗi cần phân loại:

- JSON Parser Error: LLM trả action sai format.
- Hallucination Error: LLM gọi tool không tồn tại.
- Timeout: agent vượt quá `max_steps`.

Log trong thư mục `logs/` là nguồn dữ liệu để tính aggregate reliability giữa agent v1 và agent v2.

## 7. Rubric trong SCORING.md

Tổng điểm lab là 100, gồm:

- Điểm nhóm: tối đa 60 điểm.
- Điểm cá nhân: tối đa 40 điểm.

### 7.1 Điểm nhóm

Điểm nhóm gồm 45 điểm base và 15 điểm bonus, nhưng tổng bị cap ở 60.

Các hạng mục base:

| Hạng mục | Ý nghĩa | Điểm |
| --- | --- | --- |
| Chatbot Baseline | Cài đặt chatbot tối giản, sạch | 2 |
| Agent v1 | Cài đặt ReAct loop hoạt động với ít nhất 2 tools | 7 |
| Agent v2 | Cải thiện agent dựa trên lỗi v1 | 7 |
| Tool Design Evolution | Ghi lại tiến hóa của tool spec | 4 |
| Trace Quality | Có trace thành công và thất bại | 9 |
| Evaluation & Analysis | So sánh bằng dữ liệu chatbot vs agent | 7 |
| Flowchart & Insight | Có sơ đồ logic và bài học nhóm | 5 |
| Code Quality | Code sạch, module rõ, có telemetry | 4 |

Bonus:

- Extra Monitoring: thêm metric công nghiệp như cost, token ratio.
- Extra Tools: thêm tool nâng cao như search hoặc browsing.
- Failure Handling: retry logic hoặc guardrails.
- Live System Demo: demo live thành công.
- Ablation Experiments: so sánh biến thể prompt/tool.

### 7.2 Điểm cá nhân

Báo cáo cá nhân có 40 điểm:

| Hạng mục | Ý nghĩa | Điểm |
| --- | --- | --- |
| Technical Contribution | Nêu module, tool, test mình làm | 15 |
| Debugging Case Study | Phân tích ít nhất một failure bằng log | 10 |
| Personal Insights | So sánh chatbot và ReAct agent từ trải nghiệm lab | 10 |
| Future Improvements | Đề xuất hướng production/RAG/multi-agent | 5 |

Điểm cuối cùng:

```text
Total = MIN(60, Group Base + Group Bonus) + Individual Score
```

Thông điệp rubric rất rõ: failure analysis có giá trị ngang với code chạy được.

## 8. Core abstraction: LLMProvider

File `src/core/llm_provider.py` định nghĩa abstract base class cho các provider LLM.

Interface chính:

```python
class LLMProvider(ABC):
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        pass
```

Ý nghĩa:

- Mọi provider phải có `generate()` để trả completion không streaming.
- Mọi provider phải có `stream()` để trả từng chunk token/text.
- Agent không cần biết đang dùng OpenAI, Gemini hay local model.
- Provider pattern giúp thay model mà không phải sửa logic agent.

Kết quả `generate()` được chuẩn hóa thành dictionary có các thông tin:

- `content`: nội dung phản hồi.
- `usage`: số token prompt, completion và total.
- `latency_ms`: thời gian xử lý.
- `provider`: tên provider.

## 9. OpenAIProvider

File `src/core/openai_provider.py` triển khai provider cho OpenAI.

Đặc điểm:

- Model mặc định là `gpt-4o`.
- Dùng client `OpenAI(api_key=self.api_key)`.
- Khi có `system_prompt`, provider đưa vào message role `system`.
- User prompt được đưa vào message role `user`.
- Gọi API qua `self.client.chat.completions.create()`.
- Trích xuất nội dung từ `response.choices[0].message.content`.
- Trích xuất token usage từ `response.usage`.

Kết quả trả về gồm:

```python
{
    "content": content,
    "usage": usage,
    "latency_ms": latency_ms,
    "provider": "openai"
}
```

Hàm `stream()` cũng dùng OpenAI streaming API và yield từng `delta.content`.

Vai trò trong lab:

- Là provider cloud chính.
- Phù hợp để so sánh chất lượng và latency với Gemini hoặc local model.
- Có usage metadata rõ ràng để phục vụ telemetry.

## 10. GeminiProvider

File `src/core/gemini_provider.py` triển khai provider cho Google Gemini.

Đặc điểm:

- Model mặc định là `gemini-1.5-flash`.
- Dùng thư viện `google.generativeai`.
- Gọi `genai.configure(api_key=self.api_key)`.
- Khởi tạo model bằng `genai.GenerativeModel(model_name)`.
- Vì Gemini xử lý system instruction khác OpenAI, file này prepend system prompt vào full prompt theo dạng:

```text
System: ...

User: ...
```

Hàm `generate()` gọi:

```python
response = self.model.generate_content(full_prompt)
```

Token usage lấy từ `response.usage_metadata`:

- `prompt_token_count`
- `candidates_token_count`
- `total_token_count`

Kết quả trả về có `provider` là `google`.

Hàm `stream()` gọi `generate_content(..., stream=True)` và yield `chunk.text`.

Vai trò trong lab:

- Cho phép sinh viên thực hành provider switching.
- Là lựa chọn model cloud có thể so sánh với OpenAI về latency, chi phí, chất lượng parse action.

## 11. LocalProvider

File `src/core/local_provider.py` triển khai provider chạy local model qua `llama-cpp-python`.

Đặc điểm:

- Nhận `model_path` trỏ đến file `.gguf`.
- Mặc định context window `n_ctx=4096`.
- Có thể cấu hình `n_threads`, nếu không truyền thì dùng toàn bộ CPU cores khả dụng.
- Nếu model file không tồn tại, raise `FileNotFoundError`.

Provider dùng class `Llama`:

```python
self.llm = Llama(
    model_path=model_path,
    n_ctx=n_ctx,
    n_threads=n_threads,
    verbose=False
)
```

Prompt được format theo style Phi-3/Llama:

```text
<|system|>
...system prompt...<|end|>
<|user|>
...user prompt...<|end|>
<|assistant|>
```

Tham số generation:

- `max_tokens=1024`
- `stop=["<|end|>", "Observation:"]`
- `echo=False`

Điểm đáng chú ý là stop sequence có `"Observation:"`. Điều này giúp model dừng trước khi tự bịa observation, vì observation nên đến từ kết quả tool thật chứ không phải từ LLM.

Vai trò trong lab:

- Cho phép chạy offline hoặc không cần API key.
- Hữu ích để thảo luận trade-off giữa chất lượng, latency và chi phí.
- Thường chậm hơn cloud model trên CPU nhưng rẻ và kiểm soát dữ liệu tốt hơn.

## 12. ReActAgent skeleton

File `src/agent/agent.py` là trung tâm của lab.

Class chính:

```python
class ReActAgent:
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []
```

Agent nhận:

- `llm`: provider theo interface `LLMProvider`.
- `tools`: danh sách tool, mỗi tool có ít nhất `name` và `description`.
- `max_steps`: giới hạn số vòng lặp để tránh infinite loop.
- `history`: nơi có thể lưu trace các bước agent.

### 12.1 System prompt

Hàm `get_system_prompt()` hiện đã tạo mô tả tool:

```python
tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
```

Sau đó yêu cầu agent dùng format:

```text
Thought: your line of reasoning.
Action: tool_name(arguments)
Observation: result of the tool call.
... (repeat Thought/Action/Observation if needed)
Final Answer: your final response.
```

Đây là phần cực kỳ quan trọng vì ReAct Agent phụ thuộc vào format ổn định để code có thể parse action.

### 12.2 Hàm run()

Hàm `run()` hiện vẫn là TODO.

Flow mong muốn:

1. Log event `AGENT_START`.
2. Đặt `current_prompt = user_input`.
3. Lặp tối đa `max_steps`.
4. Gọi LLM bằng `self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())`.
5. Parse output để tìm:
   - `Final Answer`
   - hoặc `Action: tool_name(arguments)`
6. Nếu có action, gọi `_execute_tool()`.
7. Lấy kết quả tool làm `Observation`.
8. Append Thought/Action/Observation vào prompt.
9. Nếu có final answer thì dừng.
10. Log event `AGENT_END`.

Hiện tại code mới tăng `steps` rồi trả:

```python
return "Not implemented. Fill in the TODOs!"
```

Do đó, đây là phần sinh viên phải hoàn thiện để đạt điểm Agent v1.

### 12.3 Hàm _execute_tool()

Hàm `_execute_tool(tool_name, args)` duyệt qua danh sách tool và tìm tool có tên trùng.

Hiện tại nếu tìm được tool thì trả về placeholder:

```python
return f"Result of {tool_name}"
```

Nếu không tìm thấy tool:

```python
return f"Tool {tool_name} not found."
```

Cần cải thiện để:

- Gọi function thật được lưu trong tool dict, ví dụ `tool["func"]`.
- Parse argument từ string hoặc JSON.
- Validate input.
- Log lỗi khi tool không tồn tại hoặc argument sai.
- Trả observation rõ ràng cho agent.

## 13. ReAct loop đề xuất

Một flow chuẩn có thể mô tả như sau:

```text
User input
    |
    v
Build system prompt with tool descriptions
    |
    v
LLM generates Thought + Action
    |
    v
Parse Action
    |
    +--> If Final Answer exists: return answer
    |
    +--> If Action exists: execute tool
                |
                v
            Tool result
                |
                v
            Append Observation to prompt
                |
                v
            Continue next loop
    |
    +--> If parse fails: log parser error and recover/stop
```

Điểm cốt lõi là LLM không được tự tạo observation. Observation phải đến từ môi trường hoặc tool thật.

## 14. Telemetry logger

File `src/telemetry/logger.py` tạo logger dạng công nghiệp.

Class `IndustryLogger`:

- Ghi log ra console.
- Ghi log ra file trong thư mục `logs/`.
- Tạo file log theo ngày dạng `YYYY-MM-DD.log`.
- Mỗi event là JSON có:
  - `timestamp`
  - `event`
  - `data`

Hàm chính:

```python
def log_event(self, event_type: str, data: Dict[str, Any]):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "data": data
    }
    self.logger.info(json.dumps(payload))
```

Trong `agent.py`, logger đã được dùng để ghi:

- `AGENT_START`
- `AGENT_END`

Nên mở rộng thêm:

- `LLM_RESPONSE`
- `TOOL_CALL`
- `TOOL_RESULT`
- `PARSER_ERROR`
- `UNKNOWN_TOOL`
- `MAX_STEPS_EXCEEDED`

Các event này giúp báo cáo có bằng chứng cụ thể khi phân tích lỗi.

## 15. Performance metrics

File `src/telemetry/metrics.py` định nghĩa `PerformanceTracker`.

Tracker lưu metric mỗi request:

- provider
- model
- prompt_tokens
- completion_tokens
- total_tokens
- latency_ms
- cost_estimate

Hàm `track_request()` thêm metric vào `session_metrics` và log event `LLM_METRIC`.

Chi phí hiện tại là mock:

```python
return (usage.get("total_tokens", 0) / 1000) * 0.01
```

Đây là điểm có thể mở rộng để đạt bonus Extra Monitoring:

- Tính cost theo bảng giá thật của từng model.
- Tính token ratio.
- Tính P50/P95/P99 latency.
- Tính success rate theo test case.
- Tính số vòng lặp trung bình mỗi task.

## 16. Cấu hình môi trường

File `.env.example` cung cấp các biến:

```env
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
LOG_LEVEL=INFO
```

Ý nghĩa:

- `OPENAI_API_KEY`: key cho OpenAIProvider.
- `GEMINI_API_KEY`: key cho GeminiProvider.
- `LOCAL_MODEL_PATH`: đường dẫn file GGUF khi chạy LocalProvider.
- `DEFAULT_PROVIDER`: chọn provider mặc định, gồm `openai`, `google`, `local`.
- `DEFAULT_MODEL`: chọn tên model mặc định.
- `LOG_LEVEL`: mức log.

File `.gitignore` loại bỏ:

- `.env`
- `logs/`
- `__pycache__/`
- `*.log`
- `.DS_Store`
- `models/`

Điều này hợp lý vì `.env` chứa secret, logs có thể lớn hoặc nhạy cảm, models có dung lượng lớn.

## 17. Dependencies

File `requirements.txt` gồm:

```text
openai>=1.0.0
google-generativeai>=0.5.0
python-dotenv>=1.0.0
pydantic>=2.0.0
requests>=2.31.0
pytest>=7.4.0
llama-cpp-python>=0.2.0
```

Vai trò:

- `openai`: gọi OpenAI API.
- `google-generativeai`: gọi Gemini API.
- `python-dotenv`: load biến môi trường từ `.env`.
- `pydantic`: phù hợp để validate schema/tool arguments, dù hiện chưa dùng nhiều.
- `requests`: có thể dùng cho tool gọi HTTP API.
- `pytest`: chạy test.
- `llama-cpp-python`: chạy local GGUF model.

## 18. Test local provider

File `tests/test_local.py` là script kiểm tra local model Phi-3.

Flow:

1. Load `.env`.
2. Lấy `LOCAL_MODEL_PATH`, mặc định là `./models/Phi-3-mini-4k-instruct-q4.gguf`.
3. Nếu file model không tồn tại, in lỗi và hướng dẫn tải model.
4. Nếu tồn tại, khởi tạo `LocalProvider`.
5. Gửi prompt: "Explain what an AI Agent is in one sentence."
6. Stream output ra terminal.
7. In thông báo local provider hoạt động.

Điểm lưu ý:

- Đây không phải test unit khắt khe kiểu assert.
- Nó giống smoke test/manual test để kiểm tra local inference.
- Muốn dùng trong CI cần thêm assert, mock hoặc model nhỏ hơn.

## 19. Template báo cáo nhóm

File `report/group_report/TEMPLATE_GROUP_REPORT.md` hướng dẫn cấu trúc báo cáo nhóm.

Các phần chính:

1. Executive Summary  
   Tóm tắt mục tiêu agent, success rate, kết quả nổi bật.

2. System Architecture & Tooling  
   Mô tả ReAct loop, danh sách tool, provider dùng chính/phụ.

3. Telemetry & Performance Dashboard  
   Phân tích latency, tokens, cost.

4. Root Cause Analysis  
   Phân tích failure trace cụ thể.

5. Ablation Studies & Experiments  
   So sánh prompt v1/v2, chatbot vs agent.

6. Production Readiness Review  
   Bàn về security, guardrails, scaling.

Báo cáo nhóm nên đổi tên thành:

```text
GROUP_REPORT_[TEAM_NAME].md
```

## 20. Template báo cáo cá nhân

File `report/individual_reports/TEMPLATE_INDIVIDUAL_REPORT.md` hướng dẫn báo cáo cá nhân.

Các phần:

1. Technical Contribution  
   Mô tả đóng góp cụ thể: module, tool, parser, test, docs.

2. Debugging Case Study  
   Phân tích một lỗi thật bằng log.

3. Personal Insights  
   Suy ngẫm về khác biệt giữa chatbot và ReAct Agent.

4. Future Improvements  
   Đề xuất mở rộng lên production, RAG hoặc multi-agent.

Báo cáo cá nhân nên đổi tên thành:

```text
REPORT_[YOUR_NAME].md
```

## 21. Các phần còn thiếu hoặc cần hoàn thiện

Repository hiện là skeleton, vì vậy có một số điểm cần làm tiếp:

1. Chưa có thư mục `src/tools/` dù README và instructor guide nhắc tới.
2. Chưa có chatbot baseline file riêng.
3. `ReActAgent.run()` chưa được implement.
4. `_execute_tool()` chưa gọi function thật.
5. Chưa có parser robust cho action.
6. Chưa có retry logic khi parse lỗi.
7. Chưa track metric trong provider calls thông qua `PerformanceTracker`.
8. Chưa có test tự động cho agent loop.
9. Chưa có ví dụ tool cụ thể như calculator, search, stock checker.
10. Chưa có script chạy so sánh chatbot vs agent.

Các thiếu hụt này phù hợp với mục tiêu lab: sinh viên sẽ tự triển khai và ghi lại tiến trình cải thiện.

## 22. Đề xuất triển khai Agent v1

Agent v1 nên tập trung vào correctness cơ bản:

- System prompt rõ format.
- Tool list có description cụ thể.
- LLM output có thể parse bằng regex đơn giản.
- Tool call hoạt động với ít nhất 2 tools.
- Có `Final Answer` để dừng.
- Có `max_steps` để tránh loop vô hạn.
- Có log cho mỗi bước.

Parser action đơn giản có thể nhận dạng:

```text
Action: tool_name(arguments)
```

Ví dụ regex:

```python
r"Action:\s*(\w+)\((.*?)\)"
```

Tuy nhiên parser này chỉ phù hợp cho argument đơn giản. Nếu argument phức tạp, nên yêu cầu LLM xuất JSON:

```json
{
  "thought": "...",
  "action": {
    "name": "tool_name",
    "args": {
      "amount": 500,
      "country": "VN"
    }
  }
}
```

## 23. Đề xuất triển khai Agent v2

Agent v2 nên cải thiện dựa trên lỗi thực tế từ v1:

- Thêm few-shot examples trong system prompt.
- Chuẩn hóa tool schema bằng Pydantic.
- Bắt lỗi JSON/parser và yêu cầu LLM sửa format.
- Log toàn bộ Thought/Action/Observation.
- Thêm retry giới hạn khi tool call sai.
- Chặn tool không tồn tại.
- Chặn argument thiếu field bắt buộc.
- Tóm tắt history khi prompt quá dài.
- Tính metric tổng hợp sau mỗi test suite.

Agent v2 không nhất thiết phải phức tạp hơn nhiều. Điều quan trọng là cải thiện phải dựa trên failure trace, ví dụ:

- V1 hay hallucinate tool name -> V2 thêm danh sách tool hợp lệ và rule "only use tools from list".
- V1 hay sai argument format -> V2 thêm schema và ví dụ.
- V1 bị loop -> V2 thêm memory về action đã thử và rule dừng.

## 24. Gợi ý tool cho lab

Một số tool nên có để đủ điểm và dễ demo:

### 24.1 Calculator tool

Mục đích:

- Tính toán số học.
- So sánh chatbot hallucinate phép tính với agent dùng tool.

Ví dụ:

```python
calculate(expression: str) -> str
```

### 24.2 Tax tool

Mục đích:

- Tính thuế theo quốc gia hoặc vùng.
- Dễ tạo lỗi argument format để phân tích.

Ví dụ:

```python
calc_tax(amount: float, country_code: str) -> str
```

### 24.3 Inventory tool

Mục đích:

- Kiểm tra tồn kho sản phẩm.
- Phù hợp kịch bản e-commerce.

Ví dụ:

```python
check_stock(item_name: str) -> str
```

### 24.4 Shipping tool

Mục đích:

- Tính phí ship dựa trên cân nặng và địa chỉ.
- Phù hợp test nhiều bước.

Ví dụ:

```python
calc_shipping(weight: float, destination: str) -> str
```

## 25. Gợi ý test case so sánh Chatbot vs Agent

### Test case 1: Câu hỏi đơn giản

Input:

```text
What is an AI Agent?
```

Kỳ vọng:

- Chatbot trả lời tốt.
- Agent cũng trả lời tốt nhưng có thể tốn nhiều token hơn.
- Winner có thể là chatbot vì đơn giản và nhanh.

### Test case 2: Bài toán tính toán

Input:

```text
Calculate the final price of a 120 USD item after 10% tax and 15% discount.
```

Kỳ vọng:

- Chatbot có thể tính đúng hoặc sai.
- Agent nên gọi calculator/tax tool.
- Winner thường là agent nếu tool hoạt động.

### Test case 3: E-commerce nhiều bước

Input:

```text
I want to buy 2 iPhones using coupon WINNER and ship to Hanoi. What is the total price?
```

Kỳ vọng:

- Agent cần check stock, lấy discount, tính shipping, tính tổng.
- Chatbot dễ bịa giá hoặc bịa tồn kho.
- Đây là test case tốt để chứng minh ReAct.

### Test case 4: Tool không có dữ liệu

Input:

```text
Check the stock for a product that does not exist.
```

Kỳ vọng:

- Agent nhận observation "No data found".
- Agent không nên bịa câu trả lời.
- Agent nên trả lời trung thực rằng không tìm thấy dữ liệu.

### Test case 5: Parser stress

Input:

```text
Use the available tools to calculate shipping and tax, then explain the result.
```

Kỳ vọng:

- Kiểm tra LLM có tuân thủ format action không.
- Dễ sinh lỗi parser để phân tích trong report.

## 26. Gợi ý nội dung báo cáo nhóm

Một bản báo cáo nhóm tốt nên có:

1. Bảng so sánh success rate giữa chatbot và agent.
2. Bảng latency/token/cost theo từng test case.
3. Ít nhất một trace thành công đầy đủ.
4. Ít nhất một trace thất bại đầy đủ.
5. Phân tích nguyên nhân gốc rễ, không chỉ nói "model sai".
6. Mô tả thay đổi từ Agent v1 sang Agent v2.
7. Kết quả sau cải thiện.
8. Sơ đồ flow ReAct.
9. Bài học nhóm về tool design và observability.

Ví dụ bảng:

| Test case | Chatbot result | Agent v1 result | Agent v2 result | Winner |
| --- | --- | --- | --- | --- |
| Simple Q&A | Correct | Correct | Correct | Chatbot |
| Multi-step math | Partially correct | Correct | Correct | Agent |
| Unknown stock | Hallucinated | Failed safely | Failed safely | Agent |

## 27. Gợi ý nội dung báo cáo cá nhân

Báo cáo cá nhân nên tập trung vào việc chứng minh người viết thật sự hiểu hệ thống.

Nên ghi rõ:

- Mình đã sửa file nào.
- Mình đã thêm tool nào.
- Mình đã gặp lỗi gì.
- Log nào chứng minh lỗi đó.
- Mình đã chẩn đoán nguyên nhân ra sao.
- Mình đã sửa thế nào.
- Sau khi sửa metric thay đổi thế nào.

Ví dụ case study:

```text
Problem: Agent gọi Action: calc_tax(500, "Asia") trong khi tool chỉ nhận country_code như "VN".
Root cause: Tool description không nói rõ format country_code.
Fix: Cập nhật mô tả tool và thêm few-shot example.
Result: Invalid argument errors giảm từ 4/10 xuống 1/10.
```

## 28. Góc nhìn production readiness

Để đưa hệ thống này gần production hơn, cần cân nhắc:

### 28.1 Safety

- Validate mọi tool argument.
- Không cho LLM gọi function tùy ý ngoài allowlist.
- Redact secret trong log.
- Thêm guardrail cho prompt injection nếu tool có truy cập dữ liệu thật.

### 28.2 Reliability

- Retry có giới hạn.
- Circuit breaker cho tool lỗi liên tục.
- Timeout cho tool execution.
- Fallback provider nếu model chính lỗi.

### 28.3 Observability

- Structured trace theo request id.
- Dashboard latency/token/error.
- So sánh version prompt.
- Lưu input/output có kiểm soát để phục vụ debugging.

### 28.4 Scalability

- Async tool calls nếu có nhiều request.
- Queue cho tác vụ dài.
- Cache kết quả tool phổ biến.
- Tool retrieval khi số lượng tool lớn.

### 28.5 Maintainability

- Tách tool schema khỏi system prompt.
- Unit test parser.
- Integration test agent loop.
- Version prompt và tool spec.

## 29. Kết luận

Lab 3 là bước chuyển quan trọng từ chatbot sang agentic system. Chatbot phù hợp với câu hỏi đơn giản, nơi không cần dữ liệu ngoài hoặc hành động cụ thể. ReAct Agent phù hợp hơn với bài toán nhiều bước, cần gọi công cụ, cần quan sát kết quả thật và cần giải thích quá trình xử lý.

Điểm mạnh của codebase hiện tại là đã có sẵn provider abstraction, telemetry logger, performance tracker và rubric đánh giá. Điểm cần hoàn thiện là phần agent loop, tool execution, parser, test case và báo cáo dựa trên trace.

Thông điệp lớn nhất của lab là: một agent tốt không chỉ được tạo ra bằng prompt hay hơn, mà bằng chu trình kỹ thuật gồm thiết kế tool rõ ràng, ghi log đầy đủ, phân tích lỗi thật và cải thiện có đo lường.
