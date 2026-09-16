# AI SPEC — ScriptScout (Tìm tài liệu & viết kịch bản video có dẫn nguồn) · Nhóm HelloWorld · Lớp 3A · Phòng E402

Hướng: [x] Track C — Lesson Studio (C3 · ScriptScout)  
Loại: [x] Tính năng mới

---

## 📌 CANVAS CP1 (Nộp lúc 19:30 · 16/9)

### Canvas 7 dòng (Theo Guide §1.5)
1. **Hướng:** Track C — Lesson Studio (Đề C3: ScriptScout — Agent tự tìm tài liệu và viết kịch bản video có dẫn nguồn).
2. **Job executor:** Người viết kịch bản video giáo dục (Studio Team / Content Creator) & Giảng viên / Lab Coach duyệt kịch bản.
3. **Pain cụ thể (1 câu):** Người viết kịch bản video AI khi soạn nội dung từ tài liệu/web mất nhiều giờ tổng hợp nhưng câu viết ra không chứng minh được lấy từ nguồn nào, khiến người duyệt không thể kiểm chứng tính chính xác, kịch bản dễ chứa ảo giác (hallucination) hoặc số liệu lỗi thời.
4. **1-2 Bằng chứng đầu tiên:**
   - *Mining dữ liệu mẫu (`data/studio-pack/c3-scriptscout/`):* Kịch bản chuẩn 40 câu tốn từ 2-3 ngày nghiên cứu thủ công; 100% tài liệu hiện tại chỉ để danh sách nguồn ở cuối, không ánh xạ được từng câu thoại cụ thể tới đoạn trích gốc.
   - *Khảo sát nhanh trong khoá:* Khi soạn bài giảng về AI, thông tin kỹ thuật thay đổi liên tục hàng tháng; người duyệt mất trung bình 30-45 phút fact-check một kịch bản ngắn nếu không có trích dẫn trực tiếp.
5. **Lát cắt MỘT CÂU:**
   > **Một người viết kịch bản · cần 5 câu mở đầu cho 1 chủ đề AI · AI tìm tài liệu trên mạng, đánh giá độ tin cậy và viết 5 câu văn nói kèm link trích dẫn nguồn gốc chính xác · người duyệt loại 1 nguồn thì AI chỉ viết lại các câu phụ thuộc nguồn đó.**
6. **Automation dự kiến & Lý do:**
   - **Augment (AI gợi ý + trích dẫn, Người duyệt quyết định)**.
   - *Lý do theo cost-of-error:* Sai sót kiến thức trong bài giảng giáo dục có chi phí sửa chữa rất lớn (ảnh hưởng đến niềm tin và hiểu biết của hàng nghìn học viên). AI đóng vai trò tìm kiếm và đề xuất nguồn/câu viết, con người luôn có quyền kiểm soát duyệt/loại nguồn trước khi xuất bản.
7. **Willing users dự kiến (≥2 người ngoài nhóm):**
   - Đào Xuân Anh (Học viên lớp 3A / Content Creator)
   - Trần Đức Mạnh (Học viên lớp 3A / Trợ giảng)
8. **Phân công nhóm:**
   - **Nguyễn Hồ Nam (2A202602788)** — Đội trưởng: Điều phối tiến độ, kiến trúc hệ thống Agent, nộp bài các mốc CP1–CP5.
   - **Nguyễn Văn Chiến (2A202602926)** — Product & Spec Lead: Khảo sát Mom Test, viết AI Spec, Canvas, phân tích JTBD.
   - **Nguyễn Cảnh Duy (2A202602815)** — Dev / Agent Engineer: Xây dựng Search Agent, thẩm định nguồn và module sinh kịch bản.
   - **Vũ Văn Hà (2A202602589)** — Eval & Prompt Engineer: Thiết kế Golden Set, prompt chống bịa trích dẫn, UI prototype.

---

## §1. User & Job
- **Job executor + workflow:** Người viết kịch bản trong Studio Team. Workflow hiện tại: Nhận chủ đề → Tìm kiếm Google/tài liệu → Đọc và ghi chép rời rạc → Viết bản nháp kịch bản → Gửi Giảng viên duyệt → Giảng viên đọc lại từ đầu để fact-check → Sửa qua lại nhiều vòng.
- **Core JTBD (không tên sản phẩm/AI):** Soạn thảo kịch bản bài giảng nói ngắn gọn, chính xác và có thể kiểm chứng nguồn gốc thông tin trong thời gian ngắn nhất.
- **Problem statement (KHÔNG chữ AI):** Người soạn nội dung mất nhiều ngày để tra cứu và viết kịch bản bài giảng, nhưng người duyệt không có cách nào đối chiếu nhanh từng câu nói với nguồn tham khảo gốc để đảm bảo tính đúng đắn trước khi ghi hình.
- **Evidence:**
  - Bằng chứng A (Khảo sát): Đang thực hiện với giảng viên/TA và học viên tạo nội dung trong khoá.
  - Bằng chứng B (Mining): Phân tích 8 chủ đề mẫu và kịch bản 40 câu trong `data/studio-pack/c3-scriptscout/`, xác định 100% các câu có số liệu cần có chứng cứ kèm theo.

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên bài toán | Người gặp | Tần suất | Mỗi lần tốn | Khả thi hackathon | Chọn? |
  |---|---|---|---|---|---|
  | 1. ScriptScout (Tìm nguồn & viết kịch bản gắn citation) | Studio team & Giảng viên (~15-20 người) | Hàng tuần / mỗi bài giảng | 8-12 tiếng viết + 2 tiếng duyệt fact-check | Cao (agent search + citation RAG) | **CHỌN** |
  | 2. StoryboardAI (Kế hoạch hình ảnh cho video) | Studio animator / scriptwriter | Mỗi bài giảng | 4-6 tiếng phác thảo hình | Trung bình (cần model sinh ảnh/layout) | Loại (khó kiểm soát style trong 48h) |
  | 3. QA Spoken-Script (Đo độ mượt văn nói tiếng Việt) | Biên tập viên kịch bản | Hàng tuần | 1-2 tiếng đọc soát lỗi | Cao | Loại (chưa giải quyết tận gốc khâu tìm tư liệu) |
- **Ứng viên ĐÃ LOẠI + vì sao:** Loại StoryboardAI vì phụ thuộc nhiều vào visual style consistency khó đo lường khách quan; loại Spoken-Script QA vì người viết vẫn tốn nhiều thời gian nhất ở khâu tra cứu thông tin ban đầu.
- **Ứng viên CHỌN + vì sao:** ScriptScout đánh thẳng vào nút thắt cổ chai lớn nhất: tốn thời gian nghiên cứu và nỗi sợ thông tin sai lệch/lỗi thời khi phát hành bài giảng AI.

## §3. Giải pháp tương tự đã nghiên cứu
- **Perplexity / Genspark:** Search & cite tốt, nhưng output dạng báo cáo nghiên cứu đọc bằng mắt, không phải kịch bản văn nói phân cảnh (spoken dialogue).
- **NotebookLM:** Nối nguồn rất chặt, nhưng chỉ nhận nguồn người dùng tải lên, không tự tìm và đánh giá nguồn mới trên Internet theo chủ đề.
- **Điểm khác biệt của ScriptScout:** Tự động tìm nguồn → chấm độ tin cậy → viết kịch bản văn nói có gắn từng câu vào span tài liệu → hỗ trợ loại nguồn và viết lại cục bộ.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một người viết kịch bản · cần 5 câu mở đầu cho 1 chủ đề AI · AI tìm tài liệu trên mạng, đánh giá độ tin cậy và viết 5 câu văn nói kèm link trích dẫn nguồn gốc chính xác · người duyệt loại 1 nguồn thì AI chỉ viết lại các câu phụ thuộc nguồn đó.
- **Non-goals (≥3 thứ KHÔNG build):**
  1. Không sinh video hoàn chỉnh hay voice TTS.
  2. Không tự động publish kịch bản mà không có sự phê duyệt của con người.
  3. Không thay thế toàn bộ kịch bản dài 40-50 phút (chỉ tập trung lát cắt micro-learning 5 câu mở đầu/phân cảnh quan trọng).
- **Mức prototype nhắm tới:** [x] Mock [x] Working — Phần mock: Bộ crawl web có thể dùng fixture/search API có sẵn; Phần thật: Lời gọi LLM đánh giá độ tin cậy nguồn, trích xuất span bằng chứng và sinh kịch bản văn nói gắn citation.
- **Automation:** Augment — Lý do: Cost-of-error trong giáo dục là cao; người duyệt luôn là chốt chặn cuối cùng.
- **§4b. Nguyên tắc HAX/PAIR dự kiến:**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ năng lực** | Màn hình nhập chủ đề thông báo rõ: Agent chỉ tìm tài liệu công khai và viết kịch bản 5 câu có căn cứ |
  | **G2 — Làm rõ mức độ tin cậy** | Mỗi nguồn tìm được đều có điểm tin cậy (High/Medium/Low) kèm lý do giải thích |
  | **G9 — Sửa đổi dễ dàng** | Người duyệt bấm nút "Bỏ nguồn" trực tiếp trên UI, hệ thống chỉ cập nhật các câu liên quan |
  | **G11 — Giải thích vì sao** | Bấm vào bất kỳ câu nào trong kịch bản sẽ highlight chính xác đoạn trích gốc chứng minh |

## §5. Kiểu lỗi — 4 lớp chỗ khó (Sẽ hoàn thiện ở CP2–CP4)
1. **Nguồn sự thật:** Web chứa thông tin sai lệch, hoặc AI bịa trích dẫn không có trong trang web.
2. **Mơ hồ / thiếu thông tin:** Chủ đề quá mới chưa có tài liệu tiếng Việt hoặc tài liệu mâu thuẫn số liệu.
3. **Ngoài phạm vi / thẩm quyền:** Prompt injection ẩn trong trang web cố tình ép AI sinh nội dung quảng cáo/sai lệch.
4. **Đặc thù domain:** Văn phong kịch bản bị mang tính báo cáo hàn lâm khó đọc thành lời, hoặc kiến thức AI bị cũ.

## §6. Bốn đường đi của trải nghiệm (Sẽ hoàn thiện ở CP2–CP4)
- Happy path: Nhập chủ đề → Ra 3 nguồn uy tín → Sinh 5 câu kịch bản chuẩn văn nói kèm link trích dẫn.
- Low-confidence: Nguồn ít hoặc mâu thuẫn → Cảnh báo người duyệt và yêu cầu xác nhận.
- Failure: Không tìm thấy nguồn đáng tin → Từ chối sinh kịch bản và đề xuất người dùng cung cấp link tài liệu.
- Correction: Người duyệt loại 1 nguồn → AI chỉ viết lại các câu dựa trên nguồn bị loại.

## §7. Kiểm thử (Golden set & Quality Bar - CP3–CP4)
- Sẽ xây dựng bộ test ≥20 ca thử thách bao gồm: Prompt injection web, tài liệu mâu thuẫn, chủ đề thiếu tài liệu tiếng Việt, và chủ đề kỹ thuật AI thay đổi nhanh.

## §8. Phân công & kế hoạch
- Xem bảng phân công chi tiết tại `README.md`.
- Willing users: Đào Xuân Anh, Trần Đức Mạnh.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 16/9 19:15 | Khởi tạo Spec & Canvas CP1 | Chốt bài toán Track C3 ScriptScout và phân công nhóm |
