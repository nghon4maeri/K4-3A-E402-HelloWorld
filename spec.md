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
   - *Mining gói dữ liệu ban tổ chức (`data/studio-pack/c5-feedbackradar/`):* 18 góp ý mẫu (`gy-001`→`gy-018`) có **11/18 = 61,1% thuộc các nhóm khó**: mơ hồ không định vị được (`gy-001` "Đoạn giữa hơi nhanh, em không kịp ghi"), hai người nói ngược nhau về cùng câu 35 (`gy-005` chê khoảng dừng ngắn ↔ `gy-006` chê dài), một người hỏi lại 3 lần (`hv-011`: `gy-002`, `gy-003`, `gy-018`), lệnh ẩn (`gy-011`), công kích cá nhân (`gy-012`), lỗi kỹ thuật lẫn nội dung (`gy-008`, `gy-017`). Theo `bang-chi-phi-lam-lai.md`, sửa lời câu N buộc thu lại cả câu N−1 và N+1 — sửa đúng 1 câu chỉ tốn **269/3 637 ký tự (7,4%)**, tiết kiệm **92,6%** công thu giọng so với làm lại cả video. (Nhóm đã đếm lại toàn bộ: `node eval/fixtures/dem-lai.js`.)
   - *Khảo sát người học lớp 3A:* **chưa thực hiện tại thời điểm CP1**. Bảng hỏi đã chốt và bộ dữ liệu mô phỏng để chạy thử đặt tại `eval/fixtures/khao-sat-mo-phong.csv`; khảo sát thật sẽ thay số trước CP4.
5. **Lát cắt MỘT CÂU:**
   > **Một biên tập viên video · có một tập góp ý của người học về một video bài giảng · AI gom thành các vấn đề có quote gốc dẫn ngược được, định vị đúng câu & phút và đề xuất cách sửa ít tốn nhất kèm phạm vi phải làm lại (số ký tự thu lại giọng, số cảnh dựng lại) · biên tập viên Accept/Reject từng đề xuất rồi xuất kịch bản V2.**
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
| **Ô 2: Nỗi đau cốt lõi** | **Pain có bằng chứng (KHÔNG chữ AI)** | **Nỗi đau 1 câu:** Đội sản xuất bài giảng phải đọc tay hàng chục phản hồi cảm tính, trùng lặp và mâu thuẫn của người học mà không biết chính xác câu nào, cảnh nào bị lỗi, nên thường thu lại cả 3 637 ký tự và dựng lại cả 40 cảnh, trong khi sửa đúng chỗ chỉ cần 269 ký tự và 3 cảnh.<br>**Dẫn chứng số liệu:**<br>• *Chuẩn B (Data Mining) — ĐẠT:* 18 góp ý mẫu trong `data/studio-pack/c5-feedbackradar/`: 11,1% mơ hồ không định vị được (`gy-001`, `gy-009`), 11,1% lỗi kỹ thuật lẫn nội dung (`gy-008`, `gy-017`), 11,1% hai người nói ngược nhau (`gy-005` ↔ `gy-006`), 16,7% một người gửi lặp (`hv-011`), 11,1% nhiễu cần lọc (`gy-011` lệnh ẩn, `gy-012` công kích) — tổng 61,1% thuộc nhóm khó. Sửa đúng 1 câu tốn 269/3 637 ký tự = 7,4%, tiết kiệm 92,6% (`bang-chi-phi-lam-lai.md`).<br>• *Chuẩn A (Khảo sát) — **CHƯA ĐẠT**:* số liệu hiện có là **bộ mô phỏng** n=20 (`eval/fixtures/khao-sat-mo-phong.csv`), chưa hỏi người thật. Khảo sát thật hoàn thành trước CP4. |
| **Ô 3: Lát cắt giải pháp** | **Đúng chuẩn MỘT CÂU** | **[Biên tập viên video]** cần **[rà soát 30 phản hồi của người học về một video bài giảng]** được **[AI gom nhóm vấn đề, định vị chính xác câu/mốc thời gian và đề xuất kế hoạch sửa tối thiểu]** giúp **[biên tập viên duyệt (accept/reject) từng đề xuất và xuất bản kịch bản sửa gọn nhất mà không phải làm lại cả video]**. |
| **Ô 4: Cam kết triển khai** | **Automation, Phân công & Willing Users** | **Mức tự động hoá:** Augment (AI phân tích gom cụm và đề xuất, con người giữ quyền duyệt để đảm bảo chất lượng sư phạm).<br>**Phân công:**<br>• Nguyễn Cảnh Duy (2A202602815) - Lead: Luồng gom cụm & pipeline.<br>• Nguyễn Văn Chiến (2A202602926) - Product: Spec, khảo sát Mom Test, evidence log.<br>• Nguyễn Hồ Nam (2A202602788) - Dev: Agent phân loại lỗi & map timestamp.<br>• Vũ Văn Hà (2A202602589) - Eval: Golden set, prompt cost & UI prototype.<br>**Willing Users (≥2 người ngoài nhóm):** Đào Xuân Anh (HV lớp 3A), Trần Đức Mạnh (HV lớp 3A). |

---

## §1. User & Job
- **Job executor + workflow:** Biên tập viên video / Giảng viên. Workflow hiện tại: Xuất feedback từ Google Form/Discord → Đọc thủ công từng dòng → Tự ghi chú vào sổ → Mở video xem lại để đoán xem học viên nói đoạn nào → Viết lại kịch bản mới → Thu âm lại toàn bộ.
- **Core JTBD (không tên sản phẩm/AI):** Cải tiến chất lượng bài giảng video từ phản hồi của người học với chi phí và thời gian làm lại thấp nhất.
- **Problem statement (KHÔNG chữ AI):** Đội sản xuất video mất nhiều ngày rà soát các góp ý cảm tính, rời rạc và mâu thuẫn của người học mà không biết chính xác câu nào, hình nào trong video gây ra vấn đề, dẫn đến việc phải quay dựng lại toàn bộ bài giảng một cách lãng phí.
- **Evidence (Chi tiết + phương pháp đếm tại `eval/evidence-log.md`; đếm lại bằng `node eval/fixtures/dem-lai.js`):**
  - **Bằng chứng B (Data Mining) — ĐẠT.** Nguồn: `data/studio-pack/c5-feedbackradar/vi-du/gop-y-mau.json` (18 góp ý) + `vi-du/khao-sat-mau.csv` (4 góp ý chỉ có ở CSV) = **22 góp ý duy nhất**. Phân loại theo đúng bảng "Những chỗ sẽ khó" của gói: mơ hồ 2 (11,1%), nói ngược nhau 2 (11,1%), một người gửi lặp 3 (16,7%), lệnh ẩn 1 (5,6%), công kích 1 (5,6%), kỹ thuật lẫn nội dung 2 (11,1%) — **cộng 11/18 = 61,1%**. 16 người gửi cho 18 góp ý, riêng `hv-011` gửi 3 lần → **phải đếm theo người, không theo số góp ý**.
  - **Chi phí (theo `bang-chi-phi-lam-lai.md`, nhóm đã đếm lại khớp 100%):** video d1 có 40 câu, 39 câu có lời, **3 637 ký tự**, TB 93 ký tự/câu. Sửa lời câu N kéo theo thu lại N−1 và N+1 → sửa câu 22 phải thu lại câu 21–23 = **269 ký tự = 7,4%**, tiết kiệm **92,6%**.
  - **Bằng chứng A (Khảo sát) — CHƯA ĐẠT.** Bộ mô phỏng n=20 (toàn bộ vai trò học viên) tại `eval/fixtures/khao-sat-mo-phong.csv`: Q1 90% từng gặp đoạn khó hiểu/lỗi, Q3 90% không ghi được timestamp, Q2 55% không gửi góp ý chính thức. **Đây là dữ liệu mô phỏng, chưa tính điểm R1** — khảo sát thật trước CP4.

## §2. Impact & quyết định chọn
- **Bảng impact ≥3 ứng viên:**
  | Ứng viên bài toán | Người gặp | Tần suất | Mỗi lần tốn | Khả thi hackathon | Chọn? |
  |---|---|---|---|---|---|
  | 1. FeedbackRadar (Gom feedback → Bản sửa tối thiểu) | Studio video editor & Giảng viên (~10-15 người) | Sau mỗi bài giảng/khóa học | Đọc soát tay toàn bộ góp ý + nguy cơ thu lại 3 637 ký tự / dựng lại 40 cảnh thay vì 269 ký tự / 3 cảnh | Rất cao (gói cấp sẵn video 4'11", kịch bản 40 câu có timecode, 22 góp ý mẫu, bảng chi phí) | **CHỌN** |
  | 2. ScriptScout (Tìm tài liệu & viết kịch bản từ đầu) | Scriptwriter | Khi mở môn mới | 2-3 ngày | Cao | Loại (C5 có data fixture video sẵn và user ngay trong lớp) |
  | 3. StoryboardAI (Lên kế hoạch hình ảnh) | Animator | Khi kịch bản đã chốt | 4-6 tiếng | Trung bình | Loại (khó đánh giá style nhất quán) |
- **Ứng viên ĐÃ LOẠI + vì sao (bằng số):** Loại C3 (ScriptScout) và C4 (StoryboardAI). Gói `c3-scriptscout/` cấp 7 file và `c4-storyboardai/` cấp 6 file, đều **không có bảng câu ↔ timecode và không có mô hình chi phí**; riêng `c5-feedbackradar/` cấp 11 file gồm video thật 4'11", 40 câu có timecode, 22 góp ý mẫu phủ đủ 6 chỗ khó, và `bang-chi-phi-lam-lai.md` — nghĩa là C5 là đề duy nhất **đo được kết quả bằng con số kiểm lại được** (ký tự thu lại / cảnh dựng lại) ngay trong thời gian hackathon.
- **Ứng viên CHỌN + vì sao:** FeedbackRadar giải quyết đúng bài toán chi phí thật: giảm lãng phí tài nguyên dựng lại video và biến phản hồi vô hình của người học thành hành động sửa cụ thể.

## §3. Giải pháp tương tự đã nghiên cứu
- **YouTube Creator Analytics / Timed Comments:** Cho phép xem comment theo mốc thời gian nhưng chỉ dừng ở hiển thị rời rạc, không gom cụm vấn đề và không chỉ ra câu kịch bản cần sửa.
- **ChatGPT / Claude (Prompt thủ công):** Đưa feedback vào tóm tắt được ý chung nhưng không ánh xạ được vào timestamp của video và không tính toán được phạm vi chi phí sửa tối thiểu.
- **Điểm khác biệt của FeedbackRadar:** Tích hợp trực tiếp Kịch bản ↔ Timestamp ↔ Feedback; tự động tính phạm vi sửa tối thiểu (chỉ câu X, cảnh Y) kèm trích dẫn quote làm chứng cứ.

## §4. Thiết kế
- **Lát cắt MỘT CÂU:** Một biên tập viên video · có một tập góp ý của người học về một video bài giảng · AI gom thành các vấn đề có quote gốc dẫn ngược được, định vị đúng câu & phút và đề xuất cách sửa ít tốn nhất kèm phạm vi phải làm lại (số ký tự thu lại giọng, số cảnh dựng lại) · biên tập viên Accept/Reject từng đề xuất rồi xuất kịch bản V2.
- **Non-goals (≥3 thứ KHÔNG build):**
  1. Không tự động render/dựng video mới bằng AI.
  2. Không tự động publish kịch bản sửa mà chưa có sự đồng ý của biên tập viên.
  3. Không xử lý các góp ý công kích cá nhân (sẽ được bộ lọc lọc bỏ).
- **Mức prototype — trạng thái thật tại thời điểm này:** **[x] Working** (một phần) · [x] Mock (phần còn lại).

  **Ranh giới rõ ràng — khâu nào AI thật, khâu nào không:**

  | # | Khâu | AI thật? | Ai làm | Bằng chứng |
  |---|---|---|---|---|
  | 1 | Lọc nhiễu (lệnh ẩn, công kích) | **KHÔNG** — heuristic regex cứng | `pipeline.py::loc_nhieu` | Cố ý không dùng AI: an toàn phải tất định, không phụ thuộc model |
  | 2 | **Gom cụm + phân loại + định vị câu** | **CÓ — đây là quyết định trung tâm** | `pipeline.py::goi_ai` + `config_prompt.py` | Trace đầy đủ prompt/response/tokens trong `eval/results/trace-*.json` |
  | 3 | Hậu kiểm chống bịa | **KHÔNG** — code đối chiếu tập hợp | `pipeline.py::hau_kiem` | Vứt mọi `quote_id`/câu AI bịa; đếm lại số người bằng code, không tin số AI trả |
  | 4 | Map câu → mốc thời gian | **KHÔNG** — tra bảng cứng | `pipeline.py::tinh_pham_vi` | `cau-timecode-d1.csv`; AI bị cấm sinh giây trong prompt |
  | 5 | Tính phạm vi làm lại | **KHÔNG** — phép cộng | `pipeline.py::day_chuyen` | Tự cộng câu N−1, N+1 theo `bang-chi-phi-lam-lai.md` |
  | 6 | Giao diện duyệt | **Mock một phần** | `index.html` | Đọc `clusters.json` thật khi có; khung video vẫn mockup, **chưa nhúng `d1.mp4`** |

  **Vẫn còn là mock:** khung phát video (hiển thị đúng timecode thật nhưng chưa phát file mp4); nút "Xuất kịch bản V2" và "Gửi giảng viên" mới chỉ hiện thông báo.

  **Vì sao đặt AI đúng ở khâu 2:** đó là chỗ duy nhất cần hiểu ngữ nghĩa tiếng Việt. Bốn khâu còn lại đều có đáp án tất định — để AI làm chỉ thêm rủi ro bịa mà không được gì.
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
4. **Đặc thù domain:** Sai ở đây làm đội sản xuất tốn tiền thật. Hai chỗ dễ sai nhất:
   - *Bỏ quên ảnh hưởng dây chuyền:* báo "sửa câu 22" mà quên câu 21 và 23 → **báo thiếu gần một nửa chi phí thu giọng** (`bang-chi-phi-lam-lai.md`). Khắc phục: mọi kế hoạch sửa lời đều tự cộng câu liền kề.
   - *Đếm góp ý thay vì đếm người:* `hv-011` gửi `gy-002`, `gy-003`, `gy-018` cùng một ý — đếm thành "3 người phản ánh" là sai. Khắc phục: gom theo `nguoiGui` trước khi tính số người, như `ket-qua-mau.json` làm (4 góp ý nhưng chỉ 2 người).
   - *Hai người nói ngược nhau* (`gy-005` ↔ `gy-006` về câu 35): số phiếu 1–1, không đủ cơ sở đổi. Khắc phục: ghi nhận cả hai phía, **không đề xuất sửa**, chờ thêm dữ liệu đợt sau.

## §6. Bốn đường đi của trải nghiệm
- **Happy path:** Nạp 30 feedback → AI phân loại, gom thành 4 cụm vấn đề có timestamp chuẩn → Đề xuất sửa 2 câu → Biên tập viên bấm Accept → Xuất bản kịch bản V2.
- **Low-confidence path:** Feedback mơ hồ ("video chán quá") → AI xếp vào mục "Góp ý chung chung, không xác định vị trí", không gán bừa vào kịch bản.
- **Failure path:** Feedback chứa nội dung độc hại / prompt injection → Hệ thống lọc bỏ và ghi nhận vào log an toàn.
- **Correction path:** Biên tập viên reject đề xuất sửa câu 14 → Hệ thống giữ nguyên kịch bản gốc của câu 14 và cập nhật lại bảng chi phí dự toán.

## §7. Kiểm thử (Golden Set & Quality Bar)

**Trạng thái: ĐÃ XÂY XONG.**

- **Bộ dữ liệu gốc:** `eval/fixtures/gop-y-100.json` — **100 góp ý mô phỏng nhóm tự sinh**, bám nội dung thật của 40 câu video d1, kèm **đáp án** cho từng góp ý (thuộc vấn đề nào, câu nào, có phải nhiễu không). Đáp ứng yêu cầu "đội tự viết khoảng một trăm góp ý và tự đặt đáp án" trong README của gói.
  - 8 vấn đề có thật · 95 người gửi · 60 góp ý định vị được · 10 góp ý phải lọc bỏ
  - Phủ đủ 6 chỗ khó của đề: mơ hồ (14) · tranh chấp 1–1 (8) · một người gửi lặp (8) · lệnh ẩn (6) · công kích (4) · kỹ thuật lẫn nội dung (10) · **bẫy bịa nguồn (8)** — nhắc nội dung không có trong video
- **Golden set:** `eval/golden-set.json` — **24 case**, mỗi case trỏ về góp ý có thật trong bộ 100.

| Lớp chỗ khó | Số case | Bar rubric |
|---|---|---|
| ① Nguồn sự thật (bịa nguồn) | 4 | ≥2 ✔ |
| ② Mơ hồ / thiếu thông tin | 4 | ≥2 ✔ |
| ③ Ngoài phạm vi / thẩm quyền | 5 | ≥2 ✔ |
| ④ Đặc thù domain | 6 | ≥2 ✔ |
| Case thường | 5 | — |

- **Kiểm chứng:** `node eval/fixtures/kiem-golden.js` — bắt lỗi quote_id không tồn tại, câu ngoài 1–40, input không khớp nguyên văn, đáp án lệch nguồn. Hiện báo **HỢP LỆ**.
- **Chấm tự động:** `python eval/run_eval.py` chạy trọn bộ qua pipeline AI thật, ghi kết quả (**giữ cả case trượt**) vào `eval/results/run-0N.json`.

**Quality bar (bằng số, chốt tại CP4 và giữ nguyên sau đó):**

| Chiều chất lượng | Định nghĩa kiểm chứng được | Bar |
|---|---|---|
| Định vị đúng câu | Câu hệ thống trỏ ra trùng câu trong đáp án, hoặc lệch tối đa ±1 câu | ≥80% |
| Gom cụm đúng | Tập góp ý của một vấn đề trùng đáp án ≥2/3 số góp ý, không nuốt góp ý của vấn đề khác | ≥75% |
| Dẫn về góp ý gốc | Mỗi vấn đề nêu ra đều liệt kê được ≥1 mã `gy-xxx` có thật trong đầu vào | 100% |
| Không thổi ý kiến 1 người thành vấn đề chung | Vấn đề chỉ do 1 người độc lập nhắc phải được gắn nhãn tin cậy thấp | 100% |
| Chặn nhiễu | `gy-011` (lệnh ẩn) và `gy-012` (công kích) không bao giờ sinh ra đề xuất sửa | 100% |
| Chi phí tính đủ dây chuyền | Kế hoạch sửa lời câu N luôn liệt kê N−1, N, N+1 | 100% |

## §8. Phân công & Kế hoạch
- Xem phân công chi tiết tại `README.md`.
- Willing users: Đào Xuân Anh, Trần Đức Mạnh.

## §9. Changelog
| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
| 16/9 18:50 | Đổi đề tài sang Track C5 FeedbackRadar | Tận dụng bộ dữ liệu fixture video mẫu có sẵn, bám sát nỗi đau chi phí sửa video và khảo sát trực tiếp học viên trong lớp |
| 17/9 | **Rà soát trung thực toàn bộ số liệu, đếm lại từ gói dữ liệu gốc** | Nhiều con số trong bản trước không khớp nguồn. Cụ thể đã sửa: (1) tỷ lệ các nhóm khó — bản cũ ghi 22,2% mơ hồ / 16,7% lẫn kỹ thuật, đếm lại theo bảng "Những chỗ sẽ khó" của gói là **11,1% / 11,1%**; (2) `gy-012` bản cũ xếp vào "mơ hồ", thực tế là **công kích cá nhân**; (3) mô hình chi phí — bản cũ ghi "50k/câu · 150k/cảnh", gói **không cấp đơn giá tiền**, đã đổi sang đúng thước **ký tự thu lại + cảnh dựng lại**; (4) tổng góp ý trong gói là **22** (18 JSON + 4 chỉ ở CSV), không phải 18; (5) mức prototype hạ từ `[x] Mock [x] Working` xuống **`[x] Mock`** vì chưa có lời gọi AI nào; (6) Chuẩn A đánh dấu **CHƯA ĐẠT** — số liệu khảo sát là bộ mô phỏng, chưa hỏi người thật. Thêm `eval/fixtures/dem-lai.js` để giám khảo đếm lại mọi con số. |
