import json
import re
from typing import Any, Dict, List


DISCLAIMER = (
    "Đây là công cụ hỗ trợ rà soát hợp đồng cho mục đích học tập, không phải tư vấn pháp lý chính thức. "
    "Các hợp đồng quan trọng nên được luật sư đủ chuyên môn kiểm tra."
)


def _json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?。])\s+|\n+|(?:Điều\s+\d+[:.]?)", text)
    return [_normalize(part) for part in parts if _normalize(part)]


def detect_contract_type(contract_text: str) -> str:
    """
    Detect the broad contract type from keyword evidence.
    Input: raw contract text.
    Output: JSON string with contract type and matched evidence.
    """
    text = _normalize(contract_text).lower()
    rules = [
        (
            "rental_contract",
            ["thuê nhà", "bên cho thuê", "bên thuê", "tiền thuê", "đặt cọc"],
            "Hợp đồng thuê nhà / thuê tài sản",
        ),
        (
            "employment_contract",
            ["người lao động", "người sử dụng lao động", "lương", "thử việc", "chấm dứt hợp đồng lao động"],
            "Hợp đồng lao động",
        ),
        (
            "service_contract",
            ["dịch vụ", "freelancer", "bên cung cấp dịch vụ", "nghiệm thu", "phí dịch vụ"],
            "Hợp đồng dịch vụ",
        ),
        (
            "sales_contract",
            ["mua bán", "bên bán", "bên mua", "hàng hóa", "giao hàng"],
            "Hợp đồng mua bán",
        ),
    ]

    best_match = {
        "type": "unknown_contract",
        "label": "Chưa xác định rõ loại hợp đồng",
        "score": 0,
        "evidence": [],
    }

    for contract_type, keywords, label in rules:
        evidence = [keyword for keyword in keywords if keyword in text]
        if len(evidence) > best_match["score"]:
            best_match = {
                "type": contract_type,
                "label": label,
                "score": len(evidence),
                "evidence": evidence,
            }

    return _json(
        {
            "tool": "detect_contract_type",
            "result": best_match,
            "disclaimer": DISCLAIMER,
        }
    )


def extract_clauses(contract_text: str) -> str:
    """
    Extract important clauses from raw contract text by keyword matching.
    Input: raw contract text.
    Output: JSON string with grouped clauses.
    """
    text = _normalize(contract_text)
    sentences = _split_sentences(contract_text)
    clause_rules = {
        "deposit": ["cọc", "đặt cọc", "hoàn cọc", "mất cọc"],
        "payment": ["thanh toán", "tiền thuê", "lương", "phí", "giá trị hợp đồng"],
        "duration": ["thời hạn", "hiệu lực", "ngày bắt đầu", "ngày kết thúc", "12 tháng"],
        "termination": ["chấm dứt", "đơn phương", "trước hạn", "báo trước"],
        "penalty": ["phạt", "phạt vi phạm", "bồi thường", "thiệt hại"],
        "responsibility": ["trách nhiệm", "sửa chữa", "bảo trì", "bàn giao", "nghiệm thu"],
        "confidentiality": ["bảo mật", "thông tin mật", "không tiết lộ"],
        "dispute": ["tranh chấp", "tòa án", "trọng tài", "hòa giải"],
    }

    clauses: Dict[str, List[str]] = {name: [] for name in clause_rules}

    for sentence in sentences:
        lower_sentence = sentence.lower()
        for clause_name, keywords in clause_rules.items():
            if any(keyword in lower_sentence for keyword in keywords):
                clauses[clause_name].append(sentence)

    found_clauses = {
        clause_name: values[:5]
        for clause_name, values in clauses.items()
        if values
    }
    missing_clauses = [
        clause_name
        for clause_name, values in clauses.items()
        if not values
    ]

    return _json(
        {
            "tool": "extract_clauses",
            "contract_length_chars": len(text),
            "clauses": found_clauses,
            "missing_or_not_detected": missing_clauses,
            "disclaimer": DISCLAIMER,
        }
    )


def legal_lookup(topic: str) -> str:
    """
    Return static, lab-friendly legal references for a contract topic.
    This is intentionally not a live legal search tool.
    Input: contract type or topic keyword.
    Output: JSON string with reference hints that students can verify later.
    """
    query = _normalize(topic).lower()
    references = {
        "deposit": [
            {
                "source": "Bộ luật Dân sự 2015",
                "hint": "Điều 328 thường được dùng khi tham khảo quy định về đặt cọc.",
                "verify": "Kiểm tra lại văn bản pháp luật chính thức trước khi sử dụng.",
            }
        ],
        "penalty": [
            {
                "source": "Bộ luật Dân sự 2015",
                "hint": "Các điều khoản phạt vi phạm và bồi thường cần ghi rõ căn cứ, mức phạt và điều kiện áp dụng.",
                "verify": "Kiểm tra lại giới hạn áp dụng theo từng loại hợp đồng.",
            }
        ],
        "rental_contract": [
            {
                "source": "Bộ luật Dân sự 2015 / luật chuyên ngành về nhà ở",
                "hint": "Nên kiểm tra điều khoản thuê, đặt cọc, bàn giao, sửa chữa, chấm dứt và hoàn trả tài sản.",
                "verify": "Đối chiếu văn bản pháp luật hiện hành và địa phương áp dụng.",
            }
        ],
        "employment_contract": [
            {
                "source": "Bộ luật Lao động 2019",
                "hint": "Nên kiểm tra lương, thử việc, thời giờ làm việc, bảo hiểm, chấm dứt và bồi thường.",
                "verify": "Đối chiếu với văn bản hướng dẫn còn hiệu lực.",
            }
        ],
        "service_contract": [
            {
                "source": "Bộ luật Dân sự 2015 / luật thương mại nếu có yếu tố thương mại",
                "hint": "Nên kiểm tra phạm vi dịch vụ, nghiệm thu, thanh toán, bảo mật, sở hữu sản phẩm và chấm dứt.",
                "verify": "Xác minh theo loại dịch vụ cụ thể.",
            }
        ],
    }

    matched_keys = [
        key
        for key in references
        if key in query or query in key
    ]
    if not matched_keys:
        matched_keys = ["penalty", "deposit"]

    results: List[Dict[str, str]] = []
    for key in matched_keys:
        results.extend(references[key])

    return _json(
        {
            "tool": "legal_lookup",
            "query": topic,
            "references": results,
            "disclaimer": DISCLAIMER,
        }
    )


def analyze_risks(contract_text_or_clauses: str) -> str:
    """
    Flag common contract risks from raw text or extracted-clause JSON.
    Input: raw contract text or JSON returned by extract_clauses.
    Output: JSON string with risk items.
    """
    text = _normalize(contract_text_or_clauses)
    lower_text = text.lower()
    risk_rules = [
        {
            "id": "non_refundable_deposit",
            "severity": "high",
            "keywords": ["mất toàn bộ tiền cọc", "không hoàn cọc", "mất cọc"],
            "issue": "Điều khoản cọc có thể bất lợi cho bên đặt cọc.",
            "why": "Cần làm rõ trường hợp nào được hoàn cọc, mất cọc hoặc khấu trừ cọc.",
            "question": "Nếu chấm dứt trước hạn và báo trước hợp lý thì có được hoàn cọc không?",
        },
        {
            "id": "unclear_termination",
            "severity": "medium",
            "keywords": ["chấm dứt", "đơn phương", "trước hạn"],
            "issue": "Điều khoản chấm dứt cần được kiểm tra kỹ.",
            "why": "Nên có thời hạn báo trước, điều kiện chấm dứt và hậu quả pháp lý rõ ràng.",
            "question": "Mỗi bên cần báo trước bao nhiêu ngày và có khoản phạt nào không?",
        },
        {
            "id": "high_penalty",
            "severity": "high",
            "keywords": ["phạt", "phạt vi phạm", "bồi thường toàn bộ", "chịu mọi thiệt hại"],
            "issue": "Điều khoản phạt/bồi thường có thể quá rộng hoặc thiếu giới hạn.",
            "why": "Cần nêu rõ mức phạt, cách tính thiệt hại và chứng cứ cần có.",
            "question": "Mức phạt tối đa là bao nhiêu và căn cứ tính thiệt hại là gì?",
        },
        {
            "id": "missing_repair_responsibility",
            "severity": "medium",
            "keywords": ["sửa chữa", "bảo trì", "hư hỏng", "bàn giao"],
            "issue": "Trách nhiệm sửa chữa/bảo trì cần được làm rõ.",
            "why": "Nếu không rõ, hai bên dễ tranh chấp khi tài sản hư hỏng.",
            "question": "Ai chịu phí sửa chữa trong từng trường hợp hư hỏng?",
        },
        {
            "id": "one_sided_change",
            "severity": "high",
            "keywords": ["có quyền thay đổi", "tự ý thay đổi", "không cần thông báo"],
            "issue": "Một bên có quyền thay đổi điều kiện hợp đồng quá rộng.",
            "why": "Điều khoản đơn phương thay đổi dễ làm mất cân bằng quyền lợi.",
            "question": "Mọi thay đổi có cần thông báo và có phụ lục bằng văn bản không?",
        },
        {
            "id": "missing_dispute_resolution",
            "severity": "low",
            "keywords": ["tranh chấp", "tòa án", "trọng tài", "hòa giải"],
            "issue": "Cần kiểm tra cơ chế giải quyết tranh chấp.",
            "why": "Nên nêu rõ nơi giải quyết, trình tự ưu tiên và luật áp dụng.",
            "question": "Nếu có tranh chấp thì giải quyết tại tòa án/trọng tài nào?",
        },
    ]

    risks = []
    for rule in risk_rules:
        matched = [keyword for keyword in rule["keywords"] if keyword in lower_text]
        if matched:
            risks.append(
                {
                    "id": rule["id"],
                    "severity": rule["severity"],
                    "matched_keywords": matched,
                    "issue": rule["issue"],
                    "why": rule["why"],
                    "suggested_question": rule["question"],
                }
            )

    if "tranh chấp" not in lower_text and "tòa án" not in lower_text and "trọng tài" not in lower_text:
        risks.append(
            {
                "id": "missing_dispute_resolution",
                "severity": "medium",
                "matched_keywords": [],
                "issue": "Chưa thấy điều khoản giải quyết tranh chấp.",
                "why": "Thiếu cơ chế giải quyết tranh chấp có thể làm việc xử lý mâu thuẫn chậm và tốn chi phí.",
                "suggested_question": "Nếu có tranh chấp thì hai bên sẽ hòa giải, trọng tài hay tòa án nào?",
            }
        )

    if not risks:
        risks.append(
            {
                "id": "no_obvious_risk_detected",
                "severity": "info",
                "matched_keywords": [],
                "issue": "Không phát hiện rủi ro rõ ràng bằng bộ luật keyword hiện tại.",
                "why": "Kết quả này không đảm bảo hợp đồng an toàn; cần đọc thủ công hoặc dùng chuyên gia.",
                "suggested_question": "Có điều khoản nào hai bên muốn sửa hoặc giải thích thêm trước khi ký không?",
            }
        )

    return _json(
        {
            "tool": "analyze_risks",
            "risk_count": len(risks),
            "risks": risks,
            "disclaimer": DISCLAIMER,
        }
    )


def generate_questions(risks_text: str) -> str:
    """
    Generate signing questions from risk-analysis JSON or raw risk text.
    Input: output of analyze_risks or raw text.
    Output: JSON string with suggested questions.
    """
    text = str(risks_text or "")
    questions: List[str] = []

    try:
        parsed = json.loads(text)
        for risk in parsed.get("risks", []):
            question = risk.get("suggested_question")
            if question:
                questions.append(question)
    except json.JSONDecodeError:
        lower_text = text.lower()
        if "cọc" in lower_text:
            questions.append("Điều kiện hoàn cọc, mất cọc và khấu trừ cọc được quy định cụ thể thế nào?")
        if "phạt" in lower_text or "bồi thường" in lower_text:
            questions.append("Mức phạt hoặc bồi thường tối đa là bao nhiêu và được tính theo căn cứ nào?")
        if "chấm dứt" in lower_text:
            questions.append("Mỗi bên có quyền chấm dứt trước hạn trong trường hợp nào và cần báo trước bao lâu?")

    default_questions = [
        "Các điều khoản quan trọng đã có phụ lục hoặc bằng chứng kèm theo chưa?",
        "Nếu phát sinh tranh chấp thì cơ chế giải quyết và chi phí được quy định thế nào?",
        "Có điều khoản nào cho phép một bên thay đổi nghĩa vụ mà không cần sự đồng ý của bên còn lại không?",
    ]

    for question in default_questions:
        if question not in questions:
            questions.append(question)

    return _json(
        {
            "tool": "generate_questions",
            "questions": questions[:8],
            "disclaimer": DISCLAIMER,
        }
    )


def summarize_contract(contract_text: str) -> str:
    """
    Create a short structured summary using simple extraction rules.
    Input: raw contract text.
    Output: JSON string with a concise summary.
    """
    text = _normalize(contract_text)
    contract_type = json.loads(detect_contract_type(text))["result"]
    clauses = json.loads(extract_clauses(text))

    return _json(
        {
            "tool": "summarize_contract",
            "summary": {
                "contract_type": contract_type["label"],
                "detected_clause_groups": list(clauses["clauses"].keys()),
                "missing_or_unclear_clause_groups": clauses["missing_or_not_detected"],
                "short_note": "Nên phân tích rủi ro tiếp để xác định các điều khoản cần làm rõ trước khi ký.",
            },
            "disclaimer": DISCLAIMER,
        }
    )


def get_contract_tools() -> List[Dict[str, Any]]:
    """
    Return tool metadata for ReActAgent.
    The agent can show name/description to the LLM and call function(args).
    """
    tools: List[Dict[str, Any]] = [
        {
            "name": "detect_contract_type",
            "description": "Detect broad contract type from raw contract text. Input: contract_text string.",
            "function": detect_contract_type,
        },
        {
            "name": "extract_clauses",
            "description": "Extract important clauses such as deposit, payment, duration, termination, penalty, responsibility and dispute. Input: contract_text string.",
            "function": extract_clauses,
        },
        {
            "name": "legal_lookup",
            "description": "Return static legal reference hints for a contract type or topic. Input: topic string such as rental_contract, employment_contract, deposit, penalty.",
            "function": legal_lookup,
        },
        {
            "name": "analyze_risks",
            "description": "Detect common risky clauses from raw contract text or extracted clause JSON. Input: contract_text or extract_clauses output.",
            "function": analyze_risks,
        },
        {
            "name": "generate_questions",
            "description": "Generate questions the user should ask before signing. Input: analyze_risks output or raw risk text.",
            "function": generate_questions,
        },
        {
            "name": "summarize_contract",
            "description": "Create a short structured summary from raw contract text. Input: contract_text string.",
            "function": summarize_contract,
        },
    ]
    return tools


CONTRACT_TOOLS: List[Dict[str, Any]] = get_contract_tools()
