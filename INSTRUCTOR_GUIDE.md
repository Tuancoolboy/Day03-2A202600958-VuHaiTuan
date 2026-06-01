# Huong dan giang vien: Lab 3 - Tu Chatbot den ReAct Agent

File nay dung de giang vien dan dat buoi lab 240 phut. Muc tieu khong chi la giup sinh vien viet code chay duoc, ma la giup sinh vien hieu cach mot he thong agent tiep nhan thong tin, suy luan, goi cong cu, quan sat ket qua, ghi log, phan tich loi va cai tien bang du lieu.

---

## 1. Ket qua cuoi cung can dat

Sau lab, moi nhom can co cac thanh pham sau:

| Thanh pham | Vi tri goi y | Muc dich |
| --- | --- | --- |
| Chatbot baseline | file/script do nhom tu tao | Lam moc so sanh voi agent |
| ReAct Agent v1 | `src/agent/agent.py` | Cai dat vong lap `Thought -> Action -> Observation` co the goi tool |
| Tool definitions | `src/tools/` neu chua co thi tao moi | Cung cap hanh dong that cho agent |
| Agent v2 | co the cung file hoac tach version | Cai tien dua tren failure trace cua v1 |
| Logs/metrics | `logs/` | Bang chung cho debugging va evaluation |
| Group report | `report/group_report/GROUP_REPORT_[TEAM_NAME].md` | Bao cao ket qua nhom |
| Individual report | `report/individual_reports/REPORT_[YOUR_NAME].md` | Bao cao dong gop va bai hoc ca nhan |

Tieu chi thanh cong quan trong nhat: sinh vien phai chi ra duoc mot trace that, noi ro no thanh cong hoac that bai o dau, va cai tien he thong dua tren bang chung trong log.

---

## 2. Flow thong tin tong quan

Lab nay co 3 dong thong tin chinh: dong hoi-dap cua chatbot, dong hanh dong cua agent, va dong quan sat/danh gia tu telemetry.

### 2.1 Flow chatbot baseline

```text
User input
    |
    v
LLM provider
    |
    v
Direct answer
```

Chatbot baseline chi dua vao nang luc sinh cau tra loi cua LLM. Neu cau hoi don gian, cach nay nhanh va re. Neu cau hoi can du lieu ben ngoai, tinh toan nhieu buoc, hoac can kiem tra dieu kien, chatbot de bia thong tin hoac sai phep tinh.

### 2.2 Flow ReAct Agent

```text
User input
    |
    v
ReActAgent.run()
    |
    v
Build system prompt from tool descriptions
    |
    v
LLM generates Thought + Action
    |
    v
Parse Action
    |
    +--> Neu co Final Answer: tra ket qua va dung
    |
    +--> Neu co Action: goi tool that
                |
                v
            Tool result
                |
                v
            Observation
                |
                v
            Dua Observation vao prompt tiep theo
                |
                v
            Lap lai den khi co Final Answer hoac cham max_steps
```

Diem can nhan manh voi sinh vien: `Observation` khong phai do LLM tu bia ra. `Observation` phai den tu tool, API, database, calculator, search, hoac mot ham Python that.

### 2.3 Flow observability va evaluation

```text
Agent step / LLM call / Tool call
    |
    v
Structured JSON logs in logs/
    |
    v
Metrics: latency, token, cost estimate, loop count, error type
    |
    v
Failure analysis
    |
    v
Prompt/tool/parser improvement
    |
    v
Agent v2 comparison
    |
    v
Group report + individual reports
```

Thong diep su pham: trace la su that. Neu khong co log, sinh vien chi dang doan. Neu co log, sinh vien co the noi chinh xac agent sai vi prompt, tool description, parser, input validation, hay model.

---

## 3. Kien truc repository can giai thich

```text
Day-3-Lab-Chatbot-vs-react-agent/
├── README.md
├── INSTRUCTOR_GUIDE.md
├── EVALUATION.md
├── SCORING.md
├── requirements.txt
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

Giai thich nhanh:

| Khu vuc | Vai tro |
| --- | --- |
| `src/core/` | Lop provider cho OpenAI, Gemini, local model. Agent khong can biet dang dung model nao. |
| `src/agent/agent.py` | Trung tam lab. Sinh vien hoan thien ReAct loop tai day. |
| `src/telemetry/` | Ghi log JSON va metric nhu token, latency, cost estimate. |
| `EVALUATION.md` | Dinh nghia cac metric can dung khi so sanh chatbot va agent. |
| `SCORING.md` | Rubric cham diem nhom, ca nhan va bonus. |
| `report/` | Template de nop bao cao cuoi lab. |

Neu README hoac guide nhac den `src/tools/` ma thu muc chua ton tai, giang vien cho sinh vien tao moi thu muc nay. Do la mot phan cua lab.

---

## 4. Chuan bi truoc buoi lab

### Buoc 1: Cai dependency

```bash
pip install -r requirements.txt
```

Neu dung local model qua `llama-cpp-python`, viec cai dat co the lau hon va phu thuoc may. Nen chuan bi truoc de tranh mat thoi gian tren lop.

### Buoc 2: Tao `.env`

```bash
cp .env.example .env
```

Sau do dien provider phu hop:

```env
OPENAI_API_KEY=...
GEMINI_API_KEY=...
LOCAL_MODEL_PATH=./models/Phi-3-mini-4k-instruct-q4.gguf
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o
LOG_LEVEL=INFO
```

### Buoc 3: Chon kich ban demo

Kich ban de day nhat la "Smart E-commerce Assistant" vi no co du cac yeu cau:

| Tool | Input | Output mong doi |
| --- | --- | --- |
| `check_stock(item_name)` | ten san pham | so luong ton kho |
| `get_discount(coupon_code)` | ma giam gia | phan tram giam gia |
| `calc_shipping(weight, destination)` | can nang, dia diem | phi van chuyen |
| `calculate(expression)` | bieu thuc so hoc | ket qua tinh toan |

Test case chinh:

```text
I want to buy 2 iPhones using coupon WINNER and ship to Hanoi. What is the total price?
```

### Buoc 4: Chuan bi mot failure demo

Nen co it nhat mot vi du chatbot tra loi sai:

```text
Find the final cost of buying 2 iPhones with coupon WINNER and shipping to Hanoi.
```

Chatbot thuong se bia gia, bia ton kho, hoac tinh phi ship khong co can cu. Day la diem mo dau de sinh vien thay vi sao agent can tool va observation.

---

## 5. Timeline 240 phut

| Thoi gian | Hoat dong | Ket qua can co |
| --- | --- | --- |
| 0-15m | Hook: chatbot that bai o bai toan nhieu buoc | Sinh vien thay gioi han cua direct-answer chatbot |
| 15-45m | Tool design | Co it nhat 2 tool description ro rang |
| 45-75m | Chatbot baseline | Co ket qua baseline va vi du sai |
| 75-135m | Build Agent v1 | ReAct loop co the goi tool va tra Final Answer |
| 135-180m | Failure analysis | Co failure trace va nguyen nhan goc |
| 180-210m | Agent v2 improvement | Cai tien prompt/tool/parser dua tren log |
| 210-230m | Evaluation | Co bang so sanh chatbot vs agent v1/v2 |
| 230-240m | Wrap-up | Chot report, insight, cau hoi |

---

## 6. Huong dan chi tiet tung buoc

### Buoc 1: Dan nhap bang chatbot baseline

Muc tieu: sinh vien thay chatbot khong co kha nang tu kiem chung hanh dong.

Giang vien lam:

1. Dua mot cau hoi don gian nhu `What is an AI Agent?`.
2. Cho chatbot tra loi va ghi nhan: nhanh, ngan, co the dung.
3. Dua mot cau hoi nhieu buoc can tool, vi du mua hang, tinh thue, kiem tra kho.
4. Hoi sinh vien: chatbot lay gia, ton kho, discount va shipping tu dau?
5. Ket luan: chatbot gioi ve ngon ngu, nhung yeu khi can hanh dong hoac du lieu co can cu.

Ket qua can ghi lai:

| Test case | Chatbot answer | Van de |
| --- | --- | --- |
| Simple Q&A | dung/sat dung | khong can tool |
| Multi-step e-commerce | co the sai | bia du lieu, sai tinh toan, khong co observation |

### Buoc 2: Thiet ke tool

Muc tieu: sinh vien hieu LLM chi biet tool qua description. Description mo ho se lam agent goi sai tool hoac sai tham so.

Yeu cau tool description phai co:

| Thanh phan | Vi du |
| --- | --- |
| Ten tool | `calc_shipping` |
| Khi nao dung | dung khi can tinh phi van chuyen |
| Input format | `weight_kg: float, destination: string` |
| Don vi | VND, USD, kg, phan tram |
| Gioi han | chi ho tro Hanoi, HCMC, Da Nang |
| Output | chuoi mo ta phi ship |

Vi du description kem:

```text
Calculates shipping.
```

Vi du description tot:

```text
Calculates shipping fee in VND. Use when the user asks delivery cost.
Input: weight_kg as float and destination as one of Hanoi, HCMC, Da Nang.
Returns: shipping fee as a number in VND.
```

Checklist:

- Co toi thieu 2 tools.
- Moi tool co name, description, input format.
- Moi tool co ham Python that hoac placeholder ro rang.
- Tool khong duoc tu goi API nguy hiem hoac dung secret trong log.

### Buoc 3: Tao chatbot baseline

Muc tieu: co moc so sanh truoc khi build agent.

Flow baseline:

```text
user_input -> provider.generate() -> answer
```

Yeu cau:

- Dung cung provider voi agent neu co the.
- Chay cung bo test case voi agent.
- Ghi lai latency, token neu provider tra ve usage.
- Ghi lai cau nao chatbot dung, cau nao sai.

Bang ket qua toi thieu:

| Case | Input | Expected behavior | Chatbot result | Pass/Fail |
| --- | --- | --- | --- | --- |
| 1 | Cau hoi don gian | Tra loi truc tiep | ... | ... |
| 2 | Tinh toan | Ket qua dung | ... | ... |
| 3 | Kiem tra kho | Khong bia du lieu | ... | ... |

### Buoc 4: Hoan thien `ReActAgent.get_system_prompt()`

Muc tieu: LLM biet danh sach tool va format bat buoc.

System prompt can co:

1. Vai tro cua agent.
2. Danh sach tool va description.
3. Format output bat buoc.
4. Quy tac khong tu bia observation.
5. Quy tac chi dung tool trong danh sach.
6. Quy tac dung bang `Final Answer`.

Format ReAct de day:

```text
Thought: explain what you need to do next.
Action: tool_name(arguments)
Observation: result returned by the tool.
Final Answer: answer to the user.
```

Neu model hay tra markdown, them quy tac:

```text
Do not wrap Action in markdown code fences.
```

### Buoc 5: Hoan thien parser Action

Muc tieu: code co the doc output cua LLM va tim tool can goi.

Voi v1, regex don gian la du:

```python
r"Action:\s*(\w+)\((.*?)\)"
```

Can xu ly 3 nhanh:

| Truong hop | Hanh dong |
| --- | --- |
| Co `Final Answer:` | Cat lay cau tra loi va return |
| Co `Action:` hop le | Goi `_execute_tool(tool_name, args)` |
| Khong parse duoc | Log `PARSER_ERROR`, co the dung hoac yeu cau model sua format |

Loi thuong gap:

- LLM boc action trong ```json.
- LLM viet `Action Input:` thay vi `Action:`.
- LLM goi tool khong ton tai.
- LLM truyen argument sai format.

### Buoc 6: Hoan thien `_execute_tool()`

Muc tieu: agent thuc su goi cong cu thay vi chi noi.

Tool dict nen co dang:

```python
{
    "name": "calculate",
    "description": "Evaluate a simple arithmetic expression.",
    "func": calculate,
}
```

Flow goi tool:

```text
tool_name + args
    |
    v
find tool by name
    |
    +--> not found: log UNKNOWN_TOOL, return error observation
    |
    v
parse args
    |
    +--> invalid: log TOOL_ERROR, return error observation
    |
    v
call tool["func"]
    |
    v
return observation string
```

Quy tac an toan:

- Chi goi function nam trong allowlist `self.tools`.
- Validate argument truoc khi goi.
- Tool error phai thanh observation ro rang, khong lam crash agent neu co the.
- Log ca tool call va tool result.

### Buoc 7: Hoan thien `ReActAgent.run()`

Muc tieu: lap toi da `max_steps` va dung khi co final answer.

Pseudo-flow:

```text
log AGENT_START
current_prompt = user_input

for step in range(max_steps):
    result = llm.generate(current_prompt, system_prompt=get_system_prompt())
    content = result["content"]
    log LLM_RESPONSE

    if "Final Answer:" in content:
        log AGENT_END
        return final_answer

    if Action exists:
        observation = execute_tool(...)
        append content + Observation to current_prompt
        continue

    log PARSER_ERROR
    return fallback answer

log MAX_STEPS_EXCEEDED
return safe failure message
```

Prompt sau moi observation co the co dang:

```text
Original question: ...

Thought: ...
Action: ...
Observation: ...

Continue from the latest observation.
```

Dieu quan trong: vong tiep theo phai nhin thay observation truoc do, neu khong agent se lap lai action cu.

### Buoc 8: Ghi telemetry dung cach

Muc tieu: moi loi va moi cai tien deu co bang chung.

Event nen co:

| Event | Khi nao log | Du lieu nen co |
| --- | --- | --- |
| `AGENT_START` | bat dau request | input, model |
| `LLM_RESPONSE` | sau moi lan goi LLM | step, content, latency |
| `TOOL_CALL` | truoc khi goi tool | step, tool_name, args |
| `TOOL_RESULT` | sau khi tool tra ve | step, observation |
| `PARSER_ERROR` | khong doc duoc action | raw content |
| `UNKNOWN_TOOL` | LLM goi tool khong ton tai | tool_name |
| `MAX_STEPS_EXCEEDED` | vuot gioi han lap | max_steps |
| `AGENT_END` | ket thuc | steps, status |
| `LLM_METRIC` | moi request LLM | token, latency, cost estimate |

Khi huong dan sinh vien doc log, yeu cau ho tra loi 4 cau:

1. Agent dang o step may?
2. LLM da nghi gi va chon action nao?
3. Observation that su tra ve la gi?
4. Sau observation, agent co thay doi hanh vi khong?

### Buoc 9: Chay test case va tao bang so sanh

Bo test case toi thieu:

| Case | Muc tieu | Ky vong |
| --- | --- | --- |
| Simple Q&A | Kiem tra cau hoi khong can tool | Chatbot co the thang vi nhanh va it token |
| Math | Kiem tra tinh toan | Agent nen dung hon neu co calculator |
| E-commerce multi-step | Kiem tra nhieu tool | Agent nen thang |
| Unknown product | Kiem tra khong bia du lieu | Agent phai noi khong tim thay |
| Parser stress | Kiem tra format action | Agent v2 nen it loi hon v1 |

Bang ket qua goi y:

| Test case | Chatbot | Agent v1 | Agent v2 | Winner | Evidence |
| --- | --- | --- | --- | --- | --- |
| Simple Q&A | correct | correct | correct | Chatbot | latency thap hon |
| Multi-step math | partial | correct | correct | Agent | calculator observation |
| Unknown stock | hallucinated | failed safely | failed safely | Agent | `No data found` observation |

### Buoc 10: Phan tich failure trace

Muc tieu: sinh vien khong chi sua prompt theo cam tinh.

Template phan tich loi:

```text
Input:
...

Expected:
...

Actual:
...

Log evidence:
...

Failure type:
Parser Error / Unknown Tool / Invalid Argument / Infinite Loop / Hallucination / Timeout

Root cause:
...

Fix:
...

Result after fix:
...
```

Vi du:

```text
Problem: Agent called calc_tax(amount=500, region="Asia").
Expected: calc_tax(amount=500, country_code="VN").
Root cause: Tool description did not specify country_code format.
Fix: Updated tool description and added a few-shot example.
Result: Invalid argument errors dropped from 4/10 to 1/10.
```

### Buoc 11: Cai tien Agent v2

Agent v2 phai cai tien dua tren failure v1. Mot so huong cai tien:

| Loi v1 | Cai tien v2 |
| --- | --- |
| Sai ten tool | Them rule "Only use tools from the provided list" |
| Sai argument | Them schema va vi du input |
| Parser error | Yeu cau raw format, them fallback parser |
| Infinite loop | Luu action da thu, dung khi lap lai |
| Tool no data | Bat agent tra loi trung thuc thay vi bia |
| Prompt qua dai | Tom tat history hoac gioi han step |

Khong can bien v2 thanh he thong qua phuc tap. Dieu quan trong la co truoc-sau va co so lieu chung minh.

### Buoc 12: Hoan thien bao cao

Bao cao nhom can dua theo `report/group_report/TEMPLATE_GROUP_REPORT.md`.

Noi dung bat buoc:

- Muc tieu agent.
- Kien truc va flow ReAct.
- Danh sach tool.
- Provider da dung.
- Bang metric: success rate, latency, token, cost estimate neu co.
- It nhat mot trace thanh cong.
- It nhat mot trace that bai.
- Root cause analysis.
- Agent v1 vs Agent v2.
- Bai hoc ve chatbot vs agent.

Bao cao ca nhan can dua theo `report/individual_reports/TEMPLATE_INDIVIDUAL_REPORT.md`.

Noi dung bat buoc:

- Sinh vien da sua file nao, them module nao.
- Dong gop ky thuat cu the.
- Mot debugging case study dua tren log.
- Insight ca nhan ve ReAct.
- Huong cai tien production.

---

## 7. Diem nghen thuong gap va cach go

| Van de | Dau hieu | Cach xu ly |
| --- | --- | --- |
| Agent lap vo han | cung mot Thought/Action lap lai | tang chat luong observation, them max_steps, log action da thu |
| Parser loi | output co markdown/code fence | prompt "raw format only", them regex/JSON extraction |
| Hallucinated tool | LLM goi tool khong ton tai | danh sach tool ro hon, validate allowlist |
| Sai argument | tool bao thieu field hoac sai type | mo ta schema, them vi du, dung Pydantic neu can |
| Observation rong | tool tra `No data found` | yeu cau agent fail safely, khong bia |
| Token cao | prompt/history qua dai | rut gon tool description, tom tat history |
| Latency cao | agent goi qua nhieu step | cai thien prompt, them stopping rule, cache tool result |

---

## 8. Rubric giang vien can nhac lai

Tong diem la 100:

| Nhom diem | Diem |
| --- | --- |
| Group base | 45 |
| Group bonus | toi da 15, group score cap o 60 |
| Individual score | 40 |

Cong thuc:

```text
Total = MIN(60, Group Base + Group Bonus) + Individual Score
```

Cac hang muc co gia tri cao:

- Agent v1 hoat dong.
- Agent v2 cai tien co bang chung.
- Trace thanh cong va that bai.
- Evaluation bang metric.
- Bao cao ca nhan co debugging case study that.

Can nhac sinh vien: mot failure trace duoc phan tich tot co gia tri hon mot demo trong co ve dung nhung khong giai thich duoc.

---

## 9. Checklist chot lab

Truoc khi ket thuc buoi lab, moi nhom tu tick:

- [ ] Cai dat dependency thanh cong.
- [ ] Chon duoc provider: OpenAI, Gemini, hoac local.
- [ ] Co chatbot baseline.
- [ ] Co it nhat 2 tools.
- [ ] Tool description co input/output ro rang.
- [ ] `ReActAgent.run()` co vong lap generate -> parse -> tool -> observation.
- [ ] `_execute_tool()` goi tool that hoac xu ly loi ro rang.
- [ ] Agent dung khi co `Final Answer`.
- [ ] Agent co `max_steps`.
- [ ] Log co agent start/end, LLM response, tool call/result, loi neu co.
- [ ] Co test case chatbot thang.
- [ ] Co test case agent thang.
- [ ] Co failure trace.
- [ ] Co cai tien v1 -> v2.
- [ ] Co bang metric.
- [ ] Group report da dien.
- [ ] Individual report cua tung thanh vien da dien.

---

## 10. Loi ket cho giang vien

Hay dan sinh vien theo thu tu: thay chatbot that bai, thiet ke tool, build ReAct loop, doc log, sua dua tren trace, roi moi viet bao cao. Neu sinh vien chi tap trung vao prompt, hay keo ho quay lai cau hoi: "Bang chung trong observation va log noi gi?"

Thong diep cuoi cung cua lab: agent khong manh vi no noi dai hon chatbot. Agent manh vi no biet chia viec thanh buoc, goi cong cu that, quan sat ket qua that, va cai tien dua tren trace that.
