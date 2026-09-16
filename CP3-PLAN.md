# PLAN CP3 — FeedbackRadar · Nhóm HelloWorld · 3A · E402

> Hạn nộp CP3: 16:00 · 17/9 — Video thao tác 30s + Số đo (thử-bao-nhiêu-đúng-bao-nhiêu) + cập nhật `spec.md` §4 "phần nào mock".

---

## 1. CP3 phải nộp 3 thứ

| # | Nộp | Chuẩn "đạt" |
|---|---|---|
| 1 | Video 30 giây quay màn hình = bấm thật qua luồng, AI trả kết quả thật (≥1 lời gọi AI chạy thật — Luật chung điều 1) | Không cần dựng/không lồng tiếng |
| 2 | Số đo — bảng "thử N case, đúng M, đúng theo tiêu chí gì" + phân tích case sai | Số thật, số xấu vẫn đủ điểm |
| 3 | `spec.md` §4 + §7 cập nhật: khâu nào AI thật, khâu nào mock | Ghi rõ ranh giới |

---

## 2. Lời gọi AI chạy thật — đặt vào QUYẾT ĐỊNH TRUNG TÂM

Quyết định trung tâm của sản phẩm = gom cụm + phân loại lỗi + định vị câu bị lỗi. Đó là chỗ bắt buộc AI thật.

### Pipeline (đầu-ra JSON, không để AI bịa giây)

```
feedback.json (30 dòng, có ID gy-xxx)
transcript.json (40 câu ↔ câu index)
timecode.json  (câu index ↔ phút/giây)   ← BẢNG CỨNG, KHÔNG cho AI sinh giây
bảng chi phí (ký tự thu lại giọng + số cảnh dựng lại — BTC không cấp đơn giá tiền)
        │
        ▼
[1] LỌC NHIỄU (heuristic cứng, KHÔNG AI):
     - regex prompt injection / công kích cá nhân → bỏ + ghi log an toàn
        │
        ▼
[2] AI CALL (Gemini free tier) — ONE call, output JSON thuần:
     mỗi cụm: { cụm_id, loại_lỗi, số_người, quote_id[], câu_index[], đề_xuất_sửa }
        │  (prompt buộc: mọi quote_id phải nằm trong danh sách đầu vào — chống bịa)
        ▼
[3] MAP câu_index → timecode bằng bảng cứng (không đúng giây gì)
[4] TÍNH PHẠM VI: Σ ký tự câu phải thu lại + Σ số cảnh dựng lại — phép cộng, không AI
        │
        ▼
clusters.json  →  UI (index.html) hiển thị + Accept/Reject
```

Nguyên tắc "không để AI bịa": AI chỉ được chọn `câu_index` từ danh sách cho sẵn và `quote_id` từ danh sách cho sẵn. Giây/chi phí do code tính. → 100% quote trỏ về gốc (quality bar §7 đã cam kết).

### Files sẽ tạo

| File | Loại | Ghi chú |
|---|---|---|
| `codebase/pipeline.py` | Mới · AI thật | Chạy toàn bộ quy trình trên, in ra `clusters.json` |
| `codebase/config_prompt.py` | Mới | Prompt system + template request cho Gemini |
| `codebase/data/sample-feedback.json` | Mới | Input thật từ fixture C5 (tối thiểu 20 dòng, có ID) |
| `codebase/data/transcript-timecode.json` | Mới | 40 câu + timecode — từ fixture |
| `codebase/.env.example` | Mới | Chứa `GEMINI_API_KEY=` rỗng — key thật NẰM NGOÀI repo |
| `codebase/run_local.py` | Mới | `python -m http.server` để mở UI — tránh lỗi CORS khi mở file:// |
| `eval/golden-set.json` | Mới | Bộ câu thử ≥20 case (Hà) |
| `eval/run_eval.py` | Mới | Chạy golden set → bảng % tự động (Nam) |
| `eval/results/*.json` | Mới | Kết quả từng lượt đo (giữ cả case fail) |

> Input có thể dùng data giả tự sinh từ fixture — được phép theo Luật 4. KHÔNG commit data pack thật vào repo.

---

## 3. Cách đo — số đo thật cho CP3

Đơn vị thử: cặp đầu vào = từng case trong golden set (mỗi case = 1 văn cảnh có feedback → kỳ vọng cụm/câu đúng).

Chấm một case ĐẠT khi cả 3 tiêu chí (so với đáp án fixture):

| Tiêu chí | Đổi thành "đo được" | Bar |
|---|---|---|
| Đúng nhóm lỗi | Loại lỗi gán đúng (Nội dung / Sư phạm / Kỹ thuật) | ≥85% case |
| Định vị chính xác | Câu đúng hoặc ±1 câu so với đáp án | ≥70% case |
| Không bịa nguồn | Mọi quote_id tồn tại trong input + PII đã khử | 100% case |
| An toàn | Feedback injection/công kích bị lọc, không vào cụm | 100% case |

Nhịp lặp (bắt buộc theo Guide §4.1): `chạy trọn bộ → bảng % → chọn MỘT failure đau nhất → sửa → chạy lại trọn bộ`. Mỗi lượt giữ file riêng trong `eval/results/`.

Bảng kết quả cuối (điền vào `eval/BANGKETQUA.md`):

```
Lượt | Thử (case) | Đạt (bar đủ 3 tiêu chí) | % | Failure đau nhất | Đổi gì từ lượt trước
-----|------------|--------------------------|----|------------------|---------------------
1    | 20         | ?                        | ?% | ?              | —
2    | 20         | ?                        | ?% | ?              | sửa prompt ...
3    | 20         | ?                        | ?% | ?              | ...
```

---

## 4. Chia việc — 4 người, mỗi người 1 mảnh giải thích được (vibe-coding rule)

| Người | Vai | Mục tiêu CP3 | Deliverable cụ thể | Người nộp/demo |
|---|---|---|---|---|
| Nguyễn Cảnh Duy | Đội trưởng · AI Lead | Điều phối + làm đo được | `eval/run_eval.py` (chạy trọn bộ golden set), `eval/BANGKETQUA.md`, quay & cắt video 30s, nộp form CP3 trước 16:00 | Video 30s |
| Nguyễn Hồ Nam | Dev · Agent Engineer | Viết pipeline AI thật | `pipeline.py` + `config_prompt.py`: lọc nhiễu heuristic, call Gemini, parse JSON, map timecode, tính chi phí; đảm bảo không commit key | Video 30s (bấm chạy) |
| Nguyễn Văn Chiến | Product · Spec Lead | Chuẩn bị input + UI nối AI | `data/sample-feedback.json` + `transcript-timecode.json` từ fixture; sửa `index.html` đọc `clusters.json` đường chuẩn thật; cập nhật `spec.md` §4 (khâu nào mock/thật); `demo-script.md` 30s | Demo script |
| Vũ Văn Hà | Eval · Prompt Engineer | Bộ câu thử có bẫy + prompt | `eval/golden-set.json` (≥20 case, phủ 4 lớp chỗ khó: bịa nguồn · mơ hồ · injection/công kích · mâu thuẫn); prompt v1 làm AI bám quote/câu_index; chấm độc lập 5 case | Bảng số đo |

Nguyên tắc: mỗi người phải trả lời được 1 câu hỏi giám khảo. Ví dụ: "Vì sao timestamp chính xác?" → Chiến/Nam trả lời bằng bảng cứng · "Vì sao không bịa quote?" → Hà trả lời bằng cấu trúc prompt + golden set · "Số đo bằng cách nào?" → Duy trả lời bằng `run_eval.py`.

---

## 5. Lịch — từ 20:00 16/9 đến 16:00 17/9 (≈20 giờ)

### Tối 16/9 (20:00–23:30) — chuẩn bị
- [ ] Tất cả: xác nhận máy nào có `data/studio-pack/c5-feedbackradar/` (fixture) → chép về máy
- [ ] Chiến: móc `transcript-timecode` + 20 feedback mẫu từ fixture → `sample-feedback.json` (chuẩn bị data, load lên repo)
- [ ] Hà: viết `golden-set.json` ≥20 case phủ 4 lớp bẫy, kèm đáp án fixture
- [ ] Nam: cài Gemini SDK + key riêng (ngoài repo), viết prompt v1 + pipeline khung đọc JSON
- [ ] Duy: chốt bar (như §3) vào `spec.md` §7 ngay đêm nay — trước khi biết kết quả

### Sáng 17/9 (LEC — 8:00–12:00) — lượt đo 1
- [ ] Nam: hoàn tất pipeline chạy được end-to-end → `clusters.json` (AI thật)
- [ ] Duy: chạy `run_eval.py` lượt 1 trọn 20 case → `eval/results/run-01.json`
- [ ] Chiến: nối `index.html` đọc `clusters.json`; mở qua `run_local.py`
- [ ] Hà: chấm 5 case độc lập (giao nhau với kết quả máy) để kiểm độ rõ định nghĩa; ghi failure đau nhất

### Trưa–chiều 17/9 (12:00–15:00) — lượt 2–3 + video
- [ ] Hà + Nam: sửa MỘT failure đau nhất (thường là prompt) → chạy lại trọn bộ (lượt 2, rồi lượt 3 nếu kịp)
- [ ] Duy: chốt bảng kết quả + 1 đoạn phân tích vì sao số chưa 100% (số thật)
- [ ] Chiến: `demo-script.md` — 30s gồm: mở trang → nhập 30 feedback → AI chạy (5s) → 4 cụm hiện → bấm 1 cụm thấy quote + timestamp → trong đó 1 case chỗ khó (injection bị lọc)
- [ ] Duy: quay màn hình 30s (OBS / Win+G), để trong `codebase/video/` (repo riêng hoặc ngoài)

### 15:00–16:00 — soát & nộp
- [ ] `spec.md` §4 + §7 cập nhật, `eval/BANGKETQUA.md` đầy đủ
- [ ] Push lên repo public; kiểm tra không có `.env`/key, không data pack
- [ ] Duy nộp form CP3 trước 16:00 (đội trưởng nộp thay cả nhóm)

---

## 6. Rủi ro & giảm thiểu

| Rủi ro | Xác suất | Hậu quả | Giảm thiểu |
|---|---|---|---|
| Không có fixture `data/studio-pack/c5-feedbackradar/` trên máy | TB | Mất input chuẩn | Fallback: tự sinh 20 feedback kèm đáp án tự đặt (Data giả hợp lệ) — làm tối nay luôn |
| Gemini trả lỗi 429 / timeout | Cao | Lượt đo trễ | Retry + backoff trong pipeline; nếu chết lâu → chạy thủ công Google AI Studio rồi paste JSON |
| LLM trả JSON lỗi format | TB | Crash pipeline | Prompt "chỉ trả JSON thuần"; try/except + fallback ép parse |
| Key lộ khi push | Thấp nhưng chí mạng | 0 điểm an toàn | Key chỉ trong `.env` (gitignore sẵn); chỉ commit `.env.example`; chạy `git grep GEMINI_API` trước push |
| Số đo xấu <70% | TB | Mất điểm tự tin | Số xấu vẫn đủ điểm nếu phân tích được vì sao — viết 3–5 dòng cho 1 failure đau nhất |
| Định nghĩa "đạt" mơ hồ khi chấm | TB | Số đo không kiểm chứng được | Thử "2 người chấm độc lập 5 case" sáng 17/9 — lệch >2/5 thì viết lại định nghĩa |

---

## 7. Checklist nộp cuối (16:00 17/9)

- [ ] `eval/golden-set.json` — ≥20 case, phủ 4 lớp, có đáp án
- [ ] `eval/results/run-0*.json` — ≥2 lượt, đủ cả case fail
- [ ] `eval/BANGKETQUA.md` — bảng thử/đúng + 1 failure phân tích
- [ ] `spec.md` §4 — liệt kê khâu AI thật (gom cụm/locate) vs khâu mock (UI, video player)
- [ ] `spec.md` §7 — quality bar chốt (không đổi sau khi thấy kết quả)
- [ ] Video 30s trong repo (hoặc link) — thấy AI chạy thật trả cụm
- [ ] Không `.env`, không key, không data pack trong repo public
- [ ] Nộp form CP3 trước 16:00