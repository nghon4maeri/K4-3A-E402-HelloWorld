# AI SPEC — FeedbackRadar (Chuyển góp ý học viên thành bản sửa video tối thiểu) · Nhóm HelloWorld · Lớp 3A · Phòng E402

Hướng: [x] Track C — Lesson Studio (C5 · FeedbackRadar)  
Loại: [x] Tính năng mới

---

## 📌 CANVAS CP1 (Nộp lúc 19:30 · 16/9)

### Canvas 7 dòng (Theo Guide §1.5)
1. **Hướng:** Track C — Lesson Studio (Đề C5: FeedbackRadar — Agent biến góp ý của người học thành bản sửa video).
2. **Job executor:** Biên tập viên video / Đội sản xuất bài giảng VLearn (Studio team) & Giảng viên phụ trách môn học.
3. **Pain cụ thể (1 câu):** Đội sản xuất video sau mỗi khoá học nhận hàng chục phản hồi rời rạc, mơ hồ hoặc trái chiều từ học viên (trộn lẫn lỗi nội dung và lỗi kỹ thuật) nhưng phải đọc tay toàn bộ, không định vị được phản hồi ứng với câu nào/phút nào của video, dẫn đến việc phải làm lại gần như cả video dù chỉ vài câu có vấn đề (tốn kém chi phí thu âm lại giọng và dựng lại cảnh).
4. **1-2 Bằng chứng đầu tiên:**
   - *Mining dữ liệu mẫu (`data/studio-pack/c5-feedbackradar/`):* Bộ dữ liệu mẫu 18 góp ý (`gy-001` đến `gy-018`) cho thấy: góp ý mơ hồ ("đoạn giữa hơi nhanh"), mâu thuẫn ("giải thích chậm buồn ngủ" vs "nói nhanh quá"), lẫn lộn kỹ thuật và nội dung; bảng chi phí `bang-chi-phi-lam-lai.md` xác nhận thu lại lời tốn 50k/câu và dựng lại cảnh tốn 150k/cảnh — sửa tràn lan tốn gấp 5–10 lần so với sửa đúng điểm.
   - *Khảo sát nhanh người học trong lớp 3A:* ~80% học viên khi học video gặp chỗ khó hiểu hoặc lỗi phụ đề thường bỏ qua hoặc chỉ comment chung chung "phần này khó hiểu" mà không ghi timestamp, khiến đội sản xuất không biết chính xác cần sửa ở đâu.
5. **Lát cắt MỘT CÂU:**
   > **Một biên tập viên video · có 30 góp ý của người học về một video bài giảng · AI gom nhóm thành các cụm vấn đề có bằng chứng quote gốc, định vị đúng câu/mốc thời gian và đề xuất kế hoạch sửa tối thiểu (thu lại lời / dựng lại hình) · biên tập viên duyệt (accept/reject) từng đề xuất sửa.**
6. **Automation dự kiến & Lý do:**
   - **Augment (AI gom nhóm & đề xuất điểm sửa tối thiểu, Người duyệt quyết định)**.
   - *Lý do theo cost-of-error:* Làm lại video tốn tiền và công sức (thu âm voice talent, dựng animation). AI không được tự ý sửa kịch bản hay tự chốt kế hoạch dựng lại; biên tập viên/giảng viên phải là người quyết định cuối cùng dựa trên các bằng chứng quote học viên mà AI tập hợp.
7. **Willing users dự kiến (≥2 người ngoài nhóm):**
   - Đào Xuân Anh (Học viên lớp 3A / Content Creator)
   - Trần Đức Mạnh (Học viên lớp 3A / Trợ giảng)
8. **Phân công nhóm:**
   - **Nguyễn Hồ Nam (2A202602788)** — Đội trưởng: Điều phối tiến độ, kiến trúc luồng hệ thống Feedback Clustered Pipeline, nộp form các mốc CP1–CP5.
   - **Nguyễn Văn Chiến (2A202602926)** — Product & Spec Lead: Khảo sát Mom Test người học & TA, thu thập log góp ý thật, viết AI Spec và Canvas.
   - **Nguyễn Cảnh Duy (2A202602815)** — Dev / Agent Engineer: Xây dựng Agent gom cụm feedback, phân loại lỗi (Nội dung/Hình ảnh/Kỹ thuật) và map timestamp câu/cảnh.
   - **Vũ Văn Hà (2A202602589)** — Eval & Prompt Engineer: Thiết kế Golden Set (18+ feedback bẫy), prompt tính toán chi phí sửa tối thiểu, UI prototype bảng duyệt.

---

### Canvas 4 ô (Theo chuẩn hướng dẫn 01-challenge-brief.md)

| Ô | Nội dung | Chi tiết |
|---|---|---|
| **Ô 1: Thông tin chung** | **Người thực hiện & Quy trình** | **Tên hướng:** Track C — Lesson Studio (C5: FeedbackRadar).<br>**Job executor:** Biên tập viên video / Đội sản xuất bài giảng VLearn (Studio team) & Giảng viên phụ trách bài giảng.<br>**Quy trình hiện tại:** Nhận feedback từ Google Form/Discord → Đọc thủ công từng dòng → Mở video xem lại để đoán vị trí → Viết lại kịch bản mới → Thu âm và dựng lại toàn bộ video. |
| **Ô 2: Nỗi đau cốt lõi** | **Pain có bằng chứng (KHÔNG chữ AI)** | **Nỗi đau 1 câu:** Đội sản xuất bài giảng mất 8–16 giờ rà soát hàng chục phản hồi cảm tính, mâu thuẫn của người học mà không biết chính xác câu nào, cảnh nào bị lỗi, dẫn đến việc phải quay dựng lại toàn bộ video với chi phí cao thay vì sửa cục bộ.<br>**Dẫn chứng số liệu:**<br>• *Chuẩn B (Data Mining):* Khai phá 18 feedback trong `data/studio-pack/c5-feedbackradar/` cho thấy: 22.2% feedback mơ hồ không có timestamp (`gy-001`), 16.7% lẫn lộn lỗi kỹ thuật vào nội dung (`gy-008`), 11.1% mâu thuẫn trực tiếp (`gy-005` vs `gy-006`), và việc thu âm lại cả bài tốn gấp 10 lần so với sửa cục bộ (theo `bang-chi-phi-lam-lai.md`).<br>• *Chuẩn A (Khảo sát):* Khảo sát 20 học viên lớp 3A: 90% (18/20) từng gặp đoạn video khó hiểu/lỗi; 85% (17/20) không nhớ timestamp khi gửi góp ý khiến đội sản xuất không thể định vị (chi tiết xem tại `eval/evidence-log.md`). |
| **Ô 3: Lát cắt giải pháp** | **Đúng chuẩn MỘT CÂU** | **[Biên tập viên video]** cần **[rà soát 30 phản hồi của người học về một video bài giảng]** được **[AI gom nhóm vấn đề, định vị chính xác câu/mốc thời gian và đề xuất kế hoạch sửa tối thiểu]** giúp **[biên tập viên duyệt (accept/reject) từng đề xuất và xuất bản kịch bản sửa gọn nhất mà không phải làm lại cả video]**. |
| **Ô 4: Cam kết triển khai** | **Automation, Phân công & Willing Users** | **Mức tự động hoá:** Augment (AI phân tích gom cụm và đề xuất, con người giữ quyền duyệt để đảm bảo chất lượng sư phạm).<br>**Phân công:**<br>• Nguyễn Hồ Nam (2A202602788) - Lead: Luồng gom cụm & pipeline.<br>• Nguyễn Văn Chiến (2A202602926) - Product: Spec, khảo sát Mom Test, evidence log.<br>• Nguyễn Cảnh Duy (2A202602815) - Dev: Agent phân loại lỗi & map timestamp.<br>• Vũ Văn Hà (2A202602589) - Eval: Golden set, prompt cost & UI prototype.<br>**Willing Users (≥2 người ngoài nhóm):** Đào Xuân Anh (HV lớp 3A), Trần Đức Mạnh (HV lớp 3A). |

---

## §1. User & Job
- **Job executor + workflow:** Biên tập viên video / Giảng viên. Workflow hiện tại: Xuất feedback từ Google Form/Discord → Đọc thủ công từng dòng → Tự ghi chú vào sổ → Mở video xem lại để đoán xem học viên nói đoạn nào → Viết lại kịch bản mới → Thu âm lại toàn bộ.
- **Core JTBD (không tên sản phẩm/AI):** Cải tiến chất lượng bài giảng video từ phản hồi của người học với chi phí và thời gian làm lại thấp nhất.
- **Problem statement (KHÔNG chữ AI):** Đội sản xuất video mất nhiều ngày rà soát các góp ý cảm tính, rời rạc và mâu thuẫn của người học mà không biết chính xác câu nào, hình nào trong video gây ra vấn đề, dẫn đến việc phải quay dựng lại toàn bộ bài giảng một cách lãng phí.
- **Evidence (Chi tiết tại `eval/evidence-log.md`):**
  - **Bằng chứng B (Data Mining):** Phân tích tập 18 feedback trong `data/studio-pack/c5-feedbackradar/vi-du/gop-y-mau.json`: 22.2% mơ hồ (`gy-001`), 16.7% lẫn kỹ thuật (`gy-008`), 11.1% mâu thuẫn (`gy-005` vs `gy-006`), 16.7% trùng lặp (`gy-002`, `gy-003`, `gy-018` cùng của `hv-011`). Chi phí sửa theo `bang-chi-phi-lam-lai.md` tiết kiệm 93% công thu âm nếu sửa đúng câu liền kề (269 ký tự vs 3.637 ký tự).
  - **Bằng chứng A (Khảo sát n = 20 học viên lớp 3A):** 90% (18/20) gặp video khó hiểu; 70% (14/20) bỏ qua không phản hồi vì nghĩ khó được sửa; 85% (17/20) thừa nhận không ghi mốc thời gian khi góp ý.

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên bài toán | Người gặp | Tần suất | Mỗi lần tốn | Khả thi hackathon | Chọn? |
  |---|---|---|---|---|---|
  | 1. FeedbackRadar (Gom feedback → Bản sửa tối thiểu) | Studio video editor & Giảng viên (~10-15 người) | Sau mỗi bài giảng/khóa học | 8-16 tiếng đọc soát + chi phí thu/dựng lại (hàng triệu VNĐ/video) | Rất cao (đã có sẵn video mẫu 4 phút, kịch bản 40 câu & 18 feedback) | **CHỌN** |
  | 2. ScriptScout (Tìm tài liệu & viết kịch bản từ đầu) | Scriptwriter | Khi mở môn mới | 2-3 ngày | Cao | Loại (C5 có data fixture video sẵn và user ngay trong lớp) |
  | 3. StoryboardAI (Lên kế hoạch hình ảnh) | Animator | Khi kịch bản đã chốt | 4-6 tiếng | Trung bình | Loại (khó đánh giá style nhất quán) |
- **Ứng viên ĐÃ LOẠI + vì sao:** Loại C3 và C4 vì C5 có sẵn toàn bộ hệ sinh thái dữ liệu hoàn chỉnh (`data/studio-pack/c5-feedbackradar/` có cả video mp4, kịch bản câu ↔ timestamp, bảng chi phí sửa), và người dùng thực tế chính là bạn học cùng lớp (dễ thu thập bằng chứng kiểm chứng nhất).
- **Ứng viên CHỌN + vì sao:** FeedbackRadar giải quyết đúng bài toán chi phí thật: giảm lãng phí tài nguyên dựng lại video và biến phản hồi vô hình của người học thành hành động sửa cụ thể.

## §3. Giải pháp tương tự đã nghiên cứu
- **YouTube Creator Analytics / Timed Comments:** Cho phép xem comment theo mốc thời gian nhưng chỉ dừng ở hiển thị rời rạc, không gom cụm vấn đề và không chỉ ra câu kịch bản cần sửa.
- **ChatGPT / Claude (Prompt thủ công):** Đưa feedback vào tóm tắt được ý chung nhưng không ánh xạ được vào timestamp của video và không tính toán được phạm vi chi phí sửa tối thiểu.
- **Điểm khác biệt của FeedbackRadar:** Tích hợp trực tiếp Kịch bản ↔ Timestamp ↔ Feedback; tự động tính phạm vi sửa tối thiểu (chỉ câu X, cảnh Y) kèm trích dẫn quote làm chứng cứ.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một biên tập viên video · có 30 góp ý của người học về một video bài giảng · AI gom nhóm thành các cụm vấn đề có bằng chứng quote gốc, định vị đúng câu/mốc thời gian và đề xuất kế hoạch sửa tối thiểu (thu lại lời / dựng lại hình) · biên tập viên duyệt (accept/reject) từng đề xuất sửa.
- **Non-goals (≥3 thứ KHÔNG build):**
  1. Không tự động render/dựng video mới bằng AI.
  2. Không tự động publish kịch bản sửa mà chưa có sự đồng ý của biên tập viên.
  3. Không xử lý các góp ý công kích cá nhân (sẽ được bộ lọc lọc bỏ).
- **Mức prototype nhắm tới:** [x] Mock [x] Working — Mock: Trình phát video mockup đồng bộ timestamp; Working: Lời gọi AI thật ở khâu khử PII, gom nhóm ngữ nghĩa, phân loại lỗi và sinh bản sửa kịch bản tối thiểu.
- **Automation:** Augment — Lý do: Sửa video kéo theo chi phí tiền bạc và công sức của cả ekip sản xuất; AI chỉ đóng vai trò phân tích radar & trợ lý đề xuất, con người giữ quyền quyết định.
- **§4b. Nguyên tắc HAX/PAIR áp dụng:**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ năng lực** | Giao diện nêu rõ: Hệ thống phân tích feedback để chỉ ra vị trí câu/cảnh cần sửa và ước tính chi phí |
  | **G2 — Làm rõ mức độ tin cậy** | Mỗi vấn đề gom được đều hiện số lượng người phản hồi (ví dụ: "Được phản ánh bởi 5 học viên") kèm quote chứng cứ |
  | **G9 — Sửa đổi dễ dàng** | Biên tập viên có nút Accept / Reject cho từng đề xuất sửa câu kịch bản |
  | **G11 — Giải thích vì sao** | Bấm vào một vấn đề sẽ nhảy tới đúng giây trong video và hiển thị nguyên văn các câu feedback gốc |

## §5. Kiểu lỗi — 4 lớp chỗ khó (Theo Taxonomy của đề C5)
1. **Nguồn sự thật:** AI tự bịa ra vấn đề mà không có bất kỳ học viên nào phản ánh (hallucination). Khắc phục: Bắt buộc mỗi vấn đề phải gắn ID quote gốc.
2. **Mơ hồ / thiếu thông tin:** Góp ý kiểu "đoạn giữa khó hiểu" không rõ phút nào. Khắc phục: AI đối chiếu ngữ nghĩa với transcript để khoanh vùng khả dĩ và cảnh báo mức độ tin cậy thấp.
3. **Ngoài phạm vi / thẩm quyền:** Góp ý cài prompt injection hoặc công kích cá nhân giảng viên. Khắc phục: Lớp tiền xử lý lọc PII và vô hiệu hoá lệnh điều khiển.
4. **Đặc thù domain:** Hai nhóm người học nói ngược nhau (người chê nhanh, người khen vừa). Khắc phục: Tách thành 2 luồng quan điểm độc lập để biên tập viên tự cân nhắc đối tượng khán giả mục tiêu.

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Nạp 30 feedback → AI phân loại, gom thành 4 cụm vấn đề có timestamp chuẩn → Đề xuất sửa 2 câu → Biên tập viên bấm Accept → Xuất bản kịch bản V2.
- **Low-confidence path:** Feedback mơ hồ ("video chán quá") → AI xếp vào mục "Góp ý chung chung, không xác định vị trí", không gán bừa vào kịch bản.
- **Failure path:** Feedback chứa nội dung độc hại / prompt injection → Hệ thống lọc bỏ và ghi nhận vào log an toàn.
- **Correction path:** Biên tập viên reject đề xuất sửa câu 14 → Hệ thống giữ nguyên kịch bản gốc của câu 14 và cập nhật lại bảng chi phí dự toán.

## §7. Kiểm thử (Golden Set & Quality Bar)
- Xây dựng Golden Set ≥20 mẫu feedback thử nghiệm dựa trên 18 mẫu chuẩn trong `data/studio-pack/c5-feedbackradar/` + feedback thu thập thật từ lớp 3A.
- Quality bar: ≥85% vấn đề được gom đúng nhóm lỗi; 100% vấn đề đều có trích dẫn quote gốc; 0% vi phạm rò rỉ PII.

## §8. Phân công & Kế hoạch
- Xem phân công chi tiết tại `README.md`.
- Willing users: Đào Xuân Anh, Trần Đức Mạnh.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 16/9 18:50 | Đổi đề tài sang Track C5 FeedbackRadar | Tận dụng bộ dữ liệu fixture video mẫu có sẵn, bám sát nỗi đau chi phí sửa video và khảo sát trực tiếp học viên trong lớp |
