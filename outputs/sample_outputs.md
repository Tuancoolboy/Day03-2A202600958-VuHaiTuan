# Sample Outputs

This file stores representative outputs from the final chatbot and ReAct Agent runs.

---

## Output 1: Simple Contract Question

**Command**

```bash
python run_agent.py "Hợp đồng thuê nhà là gì? Trả lời ngắn gọn bằng tiếng Việt."
```

**Agent Output**

```text
Hợp đồng thuê nhà là một thỏa thuận pháp lý giữa chủ nhà và người thuê, quy định các điều kiện về quyền sử dụng và trách nhiệm đối với tài sản thuê, bao gồm thời hạn thuê, giá thuê, và các điều kiện khác liên quan. Chú ý, đây không phải lời khuyên pháp lý chính thức.
```

---

## Output 2: Rental Contract Risk Analysis

**Command**

```bash
python run_agent.py "Hợp đồng thuê nhà: Bên A cho Bên B thuê nhà 12 tháng, tiền thuê 8 triệu đồng/tháng, đặt cọc 16 triệu đồng. Nếu Bên B chấm dứt trước hạn thì mất toàn bộ tiền cọc. Hợp đồng không ghi rõ cơ chế giải quyết tranh chấp. Hãy tóm tắt và chỉ ra rủi ro chính."
```

**Agent Output**

```text
Tóm tắt hợp đồng:
- Loại hợp đồng: Hợp đồng thuê nhà
- Thời hạn: 12 tháng
- Tiền thuê: 8 triệu đồng/tháng
- Đặt cọc: 16 triệu đồng
- Điều khoản chấm dứt: Nếu Bên B chấm dứt trước hạn, mất toàn bộ tiền cọc
- Thiếu cơ chế giải quyết tranh chấp

Rủi ro chính:
1. Đặt cọc không hoàn lại: Điều khoản mất toàn bộ tiền cọc có thể bất lợi, đặc biệt nếu chấm dứt trước hạn có lý do chính đáng.
2. Điều khoản chấm dứt không rõ ràng: Cần có thời hạn báo trước và điều kiện chấm dứt rõ ràng.
3. Thiếu cơ chế giải quyết tranh chấp: Cần quy định rõ tòa án, trọng tài hoặc hòa giải khi có tranh chấp.

Lưu ý: Đây không phải là tư vấn pháp lý chính thức.
```

---

## Output 3: Missing Contract Text Guardrail

**Command**

```bash
python run_agent.py "Tóm tắt hợp đồng thuê nhà và chỉ ra rủi ro chính."
```

**Agent Output**

```text
Bạn vui lòng dán nội dung hợp đồng cụ thể để tôi có thể tóm tắt và phân tích rủi ro chính xác hơn. Hiện tại yêu cầu chưa có đủ dữ liệu hợp đồng để gọi công cụ phân tích.
```

---

## Output 4: Out-of-Scope Guardrail

**Command**

```bash
python run_agent.py "Hôm nay thời tiết thế nào?"
```

**Agent Output**

```text
Tôi chỉ hỗ trợ các tác vụ liên quan đến rà soát, tóm tắt và phân tích rủi ro hợp đồng. Vui lòng cung cấp nội dung hợp đồng hoặc câu hỏi liên quan đến hợp đồng.
```
