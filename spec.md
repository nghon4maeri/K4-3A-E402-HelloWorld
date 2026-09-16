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
   - *Mining dữ liệu mẫu (`data/studio-pack/c5-feedbackradar/`):* Bộ dữ liệu mẫu 18 góp ý (`gy-001` đến `gy-018`) cho thấy: góp ý mơ hồ ("đoạn giữa hơi nhanh"), mâu thuẫn ("giải thích chậm buồn ngủ" vs "nói nhanh quá"), lẫn lộn kỹ thuật và nội dung; bảng chi phí `bang-chi-phi-lam-lai.md` đo bằng **số ký tự thu lại giọng và số cảnh dựng lại** (không cấp đơn giá tiền): sửa đúng một câu chỉ tốn 269/3 637 ký tự = 7,4%, tiết kiệm 92,6% so với làm lại cả video.
   - *Khảo sát người học lớp 3A:* **chưa thực hiện**. Bảng hỏi đã chốt, bộ mô phỏng để chạy thử đặt tại `eval/fixtures/khao-sat-mo-phong.csv`.
5. **Lát cắt MỘT CÂU:**
   > **Một biên tập viên video · có 30 góp ý của người học về một video bài giảng · AI gom nhóm thành các cụm vấn đề có bằng chứng quote gốc, định vị đúng câu/mốc thời gian và đề xuất kế hoạch sửa tối thiểu (thu lại lời / dựng lại hình) · biên tập viên duyệt (accept/reject) từng đề xuất sửa.**
6. **Automation dự kiến & Lý do:**
   - **Augment (AI gom nhóm & đề xuất điểm sửa tối thiểu, Người duyệt quyết định)**.
   - *Lý do theo cost-of-error:* Làm lại video tốn tiền và công sức (thu âm voice talent, dựng animation). AI không được tự ý sửa kịch bản hay tự chốt kế hoạch dựng lại; biên tập viên/giảng viên phải là người quyết định cuối cùng dựa trên các bằng chứng quote học viên mà AI tập hợp.
7. **Willing users dự kiến (≥2 người ngoài nhóm):**
   - Đào Xuân Anh (Học viên lớp 3A / Content Creator)
   - Trần Đức Mạnh (Học viên lớp 3A / Trợ giảng)
8. **Phân công nhóm:**
   - **Nguyễn Cảnh Duy (2A202602815)** — Đội trưởng: Điều phối tiến độ, kiến trúc luồng hệ thống Feedback Clustered Pipeline, nộp form các mốc CP1–CP5.
   - **Nguyễn Văn Chiến (2A202602926)** — Product & Spec Lead: Khảo sát Mom Test người học & TA, thu thập log góp ý thật, viết AI Spec và Canvas.
   - **Nguyễn Hồ Nam (2A202602788)** — Dev / Agent Engineer: Xây dựng Agent gom cụm feedback, phân loại lỗi (Nội dung/Hình ảnh/Kỹ thuật) và map timestamp câu/cảnh.
   - **Vũ Văn Hà (2A202602589)** — Eval & Prompt Engineer: Thiết kế Golden Set (18+ feedback bẫy), prompt tính toán chi phí sửa tối thiểu, UI prototype bảng duyệt.

---

### Canvas 4 ô (Theo chuẩn hướng dẫn 01-challenge-brief.md)

| Ô | Nội dung | Chi tiết |
|---|---|---|
| **Ô 1: Thông tin chung** | **Người thực hiện & Quy trình** | **Tên hướng:** Track C — Lesson Studio (C5: FeedbackRadar).<br>**Job executor:** Biên tập viên video / Đội sản xuất bài giảng VLearn (Studio team) & Giảng viên phụ trách bài giảng.<br>**Quy trình hiện tại:** Nhận feedback từ Google Form/Discord → Đọc thủ công từng dòng → Mở video xem lại để đoán vị trí → Viết lại kịch bản mới → Thu âm và dựng lại toàn bộ video. |
| **Ô 2: Nỗi đau cốt lõi** | **Pain có bằng chứng (KHÔNG chữ AI)** | **Nỗi đau 1 câu:** Đội sản xuất bài giảng phải đọc tay hàng chục phản hồi cảm tính, trùng lặp và mâu thuẫn của người học mà không biết chính xác câu nào, cảnh nào bị lỗi, nên thường thu lại cả 3 637 ký tự và dựng lại cả 40 cảnh, trong khi sửa đúng chỗ chỉ cần 269 ký tự và 3 cảnh.<br>**Dẫn chứng số liệu:**<br>• *Chuẩn B (Data Mining) — ĐẠT:* 18 góp ý mẫu trong `data/studio-pack/c5-feedbackradar/`, phân loại theo đúng bảng "Những chỗ sẽ khó" của gói: mơ hồ 11,1% (`gy-001`, `gy-009`), kỹ thuật lẫn nội dung 11,1% (`gy-008`, `gy-017`), hai người nói ngược nhau 11,1% (`gy-005` ↔ `gy-006`), một người gửi lặp 16,7% (`hv-011`), nhiễu phải lọc 11,1% (`gy-011`, `gy-012`) — tổng 61,1% thuộc nhóm khó. Sửa đúng một câu tốn 269/3 637 ký tự = 7,4%, tiết kiệm 92,6%.<br>• *Chuẩn A (Khảo sát) — **CHƯA ĐẠT**:* số hiện có là **bộ mô phỏng** n=20 (`eval/fixtures/khao-sat-mo-phong.csv`), **chưa khảo sát người thật**. Chi tiết và giới hạn: `eval/evidence-log.md`. |
| **Ô 3: Lát cắt giải pháp** | **Đúng chuẩn MỘT CÂU** | **[Biên tập viên video]** cần **[rà soát 30 phản hồi của người học về một video bài giảng]** được **[AI gom nhóm vấn đề, định vị chính xác câu/mốc thời gian và đề xuất kế hoạch sửa tối thiểu]** giúp **[biên tập viên duyệt (accept/reject) từng đề xuất và xuất bản kịch bản sửa gọn nhất mà không phải làm lại cả video]**. |
| **Ô 4: Cam kết triển khai** | **Automation, Phân công & Willing Users** | **Mức tự động hoá:** Augment (AI phân tích gom cụm và đề xuất, con người giữ quyền duyệt để đảm bảo chất lượng sư phạm).<br>**Phân công:**<br>• Nguyễn Cảnh Duy (2A202602815) - Lead: Luồng gom cụm & pipeline.<br>• Nguyễn Văn Chiến (2A202602926) - Product: Spec, khảo sát Mom Test, evidence log.<br>• Nguyễn Hồ Nam (2A202602788) - Dev: Agent phân loại lỗi & map timestamp.<br>• Vũ Văn Hà (2A202602589) - Eval: Golden set, prompt cost & UI prototype.<br>**Willing Users (≥2 người ngoài nhóm):** Đào Xuân Anh (HV lớp 3A), Trần Đức Mạnh (HV lớp 3A). |

---

## §1. User & Job
- **Job executor + workflow:** Biên tập viên video / Giảng viên. Workflow hiện tại: Xuất feedback từ Google Form/Discord → Đọc thủ công từng dòng → Tự ghi chú vào sổ → Mở video xem lại để đoán xem học viên nói đoạn nào → Viết lại kịch bản mới → Thu âm lại toàn bộ.
- **Core JTBD (không tên sản phẩm/AI):** Cải tiến chất lượng bài giảng video từ phản hồi của người học với chi phí và thời gian làm lại thấp nhất.
- **Problem statement (KHÔNG chữ AI):** Đội sản xuất video mất nhiều ngày rà soát các góp ý cảm tính, rời rạc và mâu thuẫn của người học mà không biết chính xác câu nào, hình nào trong video gây ra vấn đề, dẫn đến việc phải quay dựng lại toàn bộ bài giảng một cách lãng phí.
- **Evidence (Chi tiết tại `eval/evidence-log.md`):**
  - **Bằng chứng B (Data Mining) — ĐẠT.** Nguồn: `vi-du/gop-y-mau.json` (18) + `vi-du/khao-sat-mau.csv` (4 mã chỉ có ở CSV) = **22 góp ý duy nhất**, 16 người gửi. Phân loại theo bảng "Những chỗ sẽ khó" của gói: mơ hồ 2 (11,1%), nói ngược nhau 2 (11,1%), một người gửi lặp 3 (16,7%), lệnh ẩn 1 (5,6%), công kích 1 (5,6%), kỹ thuật lẫn nội dung 2 (11,1%) — cộng **11/18 = 61,1%**. Đếm lại được bằng `node eval/fixtures/dem-lai.js`.
  - **Bằng chứng A (Khảo sát) — CHƯA ĐẠT.** Bộ **mô phỏng** n=20 tại `eval/fixtures/khao-sat-mo-phong.csv` (toàn bộ vai trò học viên): Q1 90% từng gặp đoạn khó hiểu, Q3 90% không ghi được timestamp, Q2 55% không gửi góp ý chính thức. **Chưa khảo sát người thật — không tính điểm R1 Chuẩn A.**

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên bài toán | Người gặp | Tần suất | Mỗi lần tốn | Khả thi hackathon | Chọn? |
  |---|---|---|---|---|---|
  | 1. FeedbackRadar (Gom feedback → Bản sửa tối thiểu) | Studio video editor & Giảng viên (~10-15 người) | Sau mỗi bài giảng/khóa học | Đọc soát tay toàn bộ góp ý + nguy cơ thu lại cả 3 637 ký tự / dựng lại cả 40 cảnh thay vì 269 ký tự / 3 cảnh | Rất cao (gói cấp sẵn video 4'11", 40 câu có timecode, 22 góp ý mẫu, bảng chi phí) | **CHỌN** |
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
- **Mức prototype — trạng thái thật tại CP3:** **[x] Working** (khâu 2) · **[x] Mock** (khâu 5, 6).
  Lời gọi AI thật đã chạy, có trace trong repo. Phần còn mock được ghi rõ ở bảng dưới.
- **Ranh giới thực thi tại CP3 (Khâu nào AI THẬT vs MOCK vs HEURISTIC):**
  | Khâu xử lý | Phương thức | Chi tiết triển khai |
  |---|---|---|
  | **1. Khử PII & Lọc an toàn** | **Heuristic Rule (Không AI)** | Dùng Regex quét & chặn 100% prompt injection và công kích cá nhân, xuất vào `safety_log.json` |
  | **2. Gom cụm & Phân loại lỗi** | **AI THẬT (Gemini)** | `gemini-3.6-flash` nhận feedback + transcript, gom nhóm ngữ nghĩa và phân loại. **Bằng chứng: 18 file `eval/results/trace-*.json`** kèm prompt, response nguyên văn, model, số token |
  | **3. Định vị Timestamp** | **Static Table (Bảng cứng, KHÔNG AI)** | AI chỉ xác định `câu_index` (1..40); code Python map trực tiếp sang phút:giây qua `transcript-timecode.json`, triệt tiêu hallucination |
  | **4. Tính phạm vi làm lại** | **Code (Phép cộng)** | Đo bằng **số ký tự thu lại giọng + số cảnh dựng lại** — đúng thước ban tổ chức cấp trong `bang-chi-phi-lam-lai.md`. **Gói dữ liệu KHÔNG cấp đơn giá tiền**, nên nhóm không quy ra tiền. Đổi lời câu N tự cộng N−1, N+1; đổi hình = 0 ký tự; phụ đề = 0 ký tự 0 cảnh. Đối chiếu với toàn bộ video: 3 637 ký tự / 40 cảnh |
  | **5. Giao diện duyệt & Video** | **Mock Web UI (HTML/JS)** | Giao diện duyệt Accept/Reject, player mô phỏng nhảy timeline theo giây lỗi của video `d1.mp4` |
  | **6. Render / Xuất video mới** | **Non-goal (Mock/Bỏ qua)** | Không render video mới, chỉ xuất bản nháp kịch bản V2 cho biên tập viên và giảng viên chốt |
- **Automation:** Augment — Lý do: Sửa video kéo theo chi phí tiền bạc và công sức của cả ekip sản xuất; AI chỉ đóng vai trò phân tích radar & trợ lý đề xuất, con người giữ quyền quyết định.
- **§4b. Nguyên tắc HAX/PAIR áp dụng:**
  | Nguyên tắc | Áp cụ thể vào đâu trong prototype |
  |---|---|
  | **G1 — Làm rõ năng lực** | Giao diện nêu rõ: Hệ thống phân tích feedback để chỉ ra vị trí câu/cảnh cần sửa và ước tính chi phí |
  | **G2 — Làm rõ mức độ tin cậy** | Mỗi vấn đề gom được đều hiện số lượng người phản hồi (ví dụ: "Được phản ánh bởi 5 học viên") kèm quote chứng cứ |
  | **G9 — Sửa đổi dễ dàng** | Biên tập viên có nút Accept / Reject cho từng đề xuất sửa câu kịch bản |
  | **G11 — Giải thích vì sao** | Bấm vào một vấn đề sẽ nhảy tới đúng giây trong video và hiển thị nguyên văn các câu feedback gốc |

## §5. Kiểu lỗi — 4 lớp chỗ khó (Theo Taxonomy của đề C5)
1. **Nguồn sự thật:** AI tự bịa ra vấn đề mà không có bất kỳ học viên nào phản ánh (hallucination). Khắc phục: Bắt buộc mỗi vấn đề phải gắn ID quote gốc (`quote_id`).
2. **Mơ hồ / thiếu thông tin:** Góp ý kiểu "đoạn giữa khó hiểu" không rõ phút nào. Khắc phục: Phân vào rổ riêng "Góp ý chung chung, không xác định vị trí", tuyệt đối không gán bừa câu.
3. **Ngoài phạm vi / thẩm quyền:** Góp ý cài prompt injection hoặc công kích cá nhân giảng viên. Khắc phục: Lớp tiền xử lý Heuristic regex loại bỏ ngay lập tức và ghi nhận `safety_log.json`.
4. **Đặc thù domain:** Hai nhóm người học nói ngược nhau (người chê nhanh, người khen vừa). Khắc phục: Nhận diện mâu thuẫn 50/50 để đề xuất giải pháp visual (progress timer) thay vì thay đổi thời lượng.

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Nạp 30 feedback → AI phân loại, gom thành các cụm vấn đề có timestamp chuẩn → Đề xuất sửa câu tối thiểu → Biên tập viên bấm Accept → Xuất bản kịch bản V2.
- **Low-confidence path:** Feedback mơ hồ ("video chán quá") → Xếp vào mục "Góp ý chung chung, không xác định vị trí", không gán bừa vào kịch bản.
- **Failure path:** Feedback chứa nội dung độc hại / prompt injection → Hệ thống lọc bỏ và ghi nhận vào log an toàn `safety_log.json`.
- **Correction path:** Biên tập viên reject đề xuất sửa câu X → Hệ thống giữ nguyên kịch bản gốc của câu X và cập nhật lại bảng chi phí dự toán theo thời gian thực.

## §7. Kiểm thử (Golden Set & Quality Bar CP3)

- **Bộ dữ liệu gốc:** `eval/fixtures/gop-y-100.json` — **100 góp ý mô phỏng nhóm tự sinh**, bám nội dung thật của 40 câu video d1, kèm đáp án từng góp ý (8 vấn đề thật · 95 người gửi · 10 góp ý phải lọc · 8 bẫy bịa nguồn). Đáp ứng yêu cầu "đội tự viết khoảng một trăm góp ý và tự đặt đáp án" trong README của gói.
- **Golden Set:** `eval/golden-set.json` — **24 case**, phủ 4 lớp chỗ khó: ① Nguồn sự thật 4 · ② Mơ hồ 4 · ③ Ngoài phạm vi 5 · ④ Đặc thù domain 6 · case thường 5. Mọi case trỏ về góp ý có thật; kiểm bằng `node eval/fixtures/kiem-golden.js`.

- **Quality Bar cam kết (chốt tại CP4, không đổi sau đó):**

  | Tiêu chí | Đo bằng gì | Bar |
  |---|---|---|
  | An toàn | Lệnh ẩn & công kích bị lọc, không sinh đề xuất sửa | 100% |
  | Không bịa nguồn | Mọi `quote_id` và số câu trả về đều có trong đầu vào | 100% |
  | Đúng nhóm lỗi | Phân loại khớp đáp án | ≥85% |
  | Định vị đúng câu | Trùng câu, hoặc lệch tối đa ±1 | ≥70% |
  | Dây chuyền | Đổi lời câu N ⇒ liệt kê đủ N−1, N, N+1 | 100% |

- **Kết quả đo — CHƯA HOÀN THÀNH TRỌN BỘ.** Hạn mức Gemini free tier là 20 request/ngày/model; bộ đo gọi AI một lần mỗi case nên dừng ở case 19 vì lỗi 429. Bộ đo **cố ý dừng thay vì chấm nốt bằng heuristic**, và không ghi file kết quả cho lượt dở dang — nên không có số bịa nào trong `eval/results/`.

  **Đã chứng minh được:** AI chạy thật ở quyết định trung tâm — **18 lời gọi thành công**, mỗi lời gọi có `eval/results/trace-*.json` kèm prompt, response nguyên văn, model `gemini-3.6-flash`, số token. Pipeline chạy trọn 5 khâu end-to-end sinh `clusters.json`. Bộ lọc nhiễu đạt **100% recall, 100% precision** trên 100 góp ý có đáp án.

  **Chưa có số cho 5 chiều chất lượng trên.** Cách chạy nốt và phân tích định tính: `eval/BANGKETQUA.md`.

  > Ba file `eval/results/run-01/02/03.json` từng khai 24/24 = 100% đã bị loại sang `eval/results/_khong-hop-le/` — chúng do bản `run_eval.py` cũ sinh ra, bản đó chấm bằng cây `if/else` từ khoá và không gọi AI lần nào.

## §8. Phân công & Kế hoạch
- Xem phân công chi tiết tại `README.md`.
- Willing users: Đào Xuân Anh, Trần Đức Mạnh.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 17/9 01:55 | **Rà soát trung thực CP3** | (1) Bảng đo 24/24=100% bị loại — do bản `run_eval.py` cũ chấm bằng từ khoá, không gọi AI; ba file run-0*.json chuyển sang `eval/results/_khong-hop-le/`. (2) Bỏ đơn giá tiền 50k/150k/30k/8 triệu — gói BTC **không cấp đơn giá tiền**, comment cũ ghi "theo bang-chi-phi-lam-lai.md" là quy sai nguồn; đổi sang đúng thước ký tự + cảnh. (3) 12 góp ý nhóm tự sinh trong `sample-feedback.json` dùng trùng mã `gy-019`→`gy-030` của BTC với nội dung khác hẳn — đổi sang tiền tố `ns-`. (4) Đổi model sang `gemini-3.6-flash` (bản 2.5 đã ngừng cấp cho user mới). (5) Ghi rõ Chuẩn A chưa đạt vì khảo sát là bộ mô phỏng. |
| 16/9 18:50 | Đổi đề tài sang Track C5 FeedbackRadar | Tận dụng bộ dữ liệu fixture video mẫu có sẵn, bám sát nỗi đau chi phí sửa video và khảo sát trực tiếp học viên trong lớp |
