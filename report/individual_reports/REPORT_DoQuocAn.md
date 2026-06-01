# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Đỗ Quốc An
- **Student ID**: 2A202600952
- **Date**: 01/06/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase.*

- **Modules Implemented**: 
  - `src/agent/agent.py`: Hoàn thiện ReAct Agent loop (v2) với khả năng tự động dọn dẹp chuỗi JSON bị lỗi (loại bỏ markdown backticks) và cơ chế Try-Catch bắt lỗi `JSONDecodeError`.
  - `src/telemetry/metrics.py`: Cập nhật logic tính toán điểm thưởng (Bonus metrics), tự động quy đổi token ra chi phí USD (`estimated_cost_usd`) và `tokens_per_step`.
  - `src/core/openai_provider.py`: Cấu hình LLM Provider linh hoạt để gọi API custom của DeepSeek-v4-flash thông qua OpenAI SDK thay vì bị giới hạn ở Gemini/OpenAI mặc định.
  - `src/chatbot.py` & Scripts: Xây dựng chế độ Interactive Terminal (Chat trực tiếp) cho Chatbot và Agent.
- **Code Highlights**:
  Đoạn code bắt lỗi JSON trong `agent.py`:
  `clean_args = args.strip(" \n'\"`")`
  `if clean_args.lower().startswith("json"): clean_args = clean_args[4:].strip(" \n")`
- **Documentation**: Các module được tích hợp trơn tru. Flow hoạt động bắt đầu từ việc nhận Prompt, gọi DeepSeek API, phân tích logic (Thought), làm sạch dữ liệu đầu vào cho Tools, thực thi, lấy Observation và đệ quy lặp lại quy trình.

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: LLM trả về kết quả Action chứa chuỗi JSON được bọc trong markdown code block (VD: ` ```json {"item_name": "macbook"} ``` `) thay vì JSON thuần túy. Điều này khiến `json.loads()` trong Tool Executor bị crash.
- **Log Source**: 
  `{"event": "TOOL_ERROR", "data": {"tool": "check_stock", "error": "Error: Invalid JSON arguments provided for check_stock. Expected a valid JSON string. Received: ```json {\"item_name\": \"macbook\"} ```"}}`
- **Diagnosis**: Các mô hình LLM (như DeepSeek hay GPT) được huấn luyện để trả về format dễ đọc cho người dùng (Markdown formatting). Tuy nhiên, hệ thống máy tính lại cần JSON thô. Parser mặc định ở phiên bản Agent v1 không lường trước được các ký tự thừa này.
- **Solution**: Cải tiến lên Agent v2. Trong `_execute_tool`, thêm hàm tiền xử lý chuỗi: `strip()` các dấu backticks (```), cắt bỏ tiền tố "json", đồng thời bọc trong khối `try...except json.JSONDecodeError`. Nếu lỗi vẫn xảy ra, hàm sẽ trả về câu báo lỗi rõ ràng thành `Observation` để LLM biết đường tự sửa lại format ở vòng lặp sau.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1. **Reasoning**: Khối `Thought` đóng vai trò như một "bộ nhớ tạm" (scratchpad) cực kỳ quan trọng. Nhờ nó, Agent có thể chia nhỏ một bài toán phức tạp (VD: kiểm tra kho -> lấy mã giảm giá -> tính phí ship) thay vì cố gắng đoán mò toàn bộ kết quả trong 1 lượt như Chatbot.
2. **Reliability**: Trong khi Agent xuất sắc ở các tác vụ đa bước cần dữ liệu thực (Multi-step reasoning), nó lại hoạt động kém hiệu quả hơn Chatbot ở những câu hỏi xã giao thông thường (VD: "Hello", "How are you?"). Agent có thể "overthink", tiêu tốn nhiều thời gian và token hơn cần thiết chỉ để trả lời một câu đơn giản, nguy cơ rơi vào loop gọi tool vô ích nếu System Prompt không chặn.
3. **Observation**: Môi trường phản hồi (`Observation`) là chìa khóa để Agent "mở mắt". Nếu truyền tham số sai, tool trả về lỗi, Observation lập tức báo cho LLM biết để sửa sai (Self-correction). Đối với Chatbot không có Observation, nó chỉ có thể "chém gió" (hallucinate) ra một con số ảo để làm hài lòng người dùng.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability (Khả năng mở rộng)**: Khi hệ thống có hàng trăm Tools, việc nhồi nhét tất cả `description` vào System Prompt sẽ vượt quá Context Window. Giải pháp là kết hợp **RAG (Retrieval-Augmented Generation)** để Agent tự động search (truy xuất) top 3-5 Tools phù hợp với câu hỏi của User rồi mới nhúng vào Prompt.
- **Safety (An toàn)**: Cần thiết lập `Human-in-the-loop` (HITL). Với các Action mang tính thay đổi trạng thái hệ thống (Mutations) như `create_order` hay `charge_credit_card`, hệ thống phải dừng lại và yêu cầu người dùng xác nhận Y/N trước khi Agent thực thi Tool.
- **Performance (Hiệu năng)**: Triển khai gọi Tool song song (Parallel Tool Calling) cho các Action độc lập (Ví dụ: kiểm tra kho và kiểm tra mã giảm giá cùng lúc) và tích hợp Cache (Redis) lưu lại các `Observation` phổ biến để giảm độ trễ (Latency) và chi phí token.