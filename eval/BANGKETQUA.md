# BẢNG KẾT QUẢ ĐO LƯỜNG CP3 — FEEDBACKRADAR

> Nhóm HelloWorld · Lớp 3A · Phòng E402
> Golden set: `eval/golden-set.json` (24 case · Vũ Văn Hà)
> Cập nhật: 01:55 · 17/09/2026

---

## 0. Trạng thái trung thực của bảng này

**Lượt đo trọn bộ 24 case CHƯA hoàn thành.** Lý do: hạn mức miễn phí của Gemini
là **20 request/ngày/model**, bộ đo gọi AI một lần cho mỗi case nên chạy tới
case thứ 19 thì hết quota (lỗi 429 `RESOURCE_EXHAUSTED`).

Bộ đo **cố ý dừng lại** thay vì chấm nốt bằng heuristic, và **không ghi file
kết quả** cho lượt dở dang — nên trong `eval/results/` không có số nào bịa.

> **Ba file `run-01/02/03.json` từng có trong repo đã bị loại** sang
> `eval/results/_khong-hop-le/`. Chúng do bản `run_eval.py` cũ sinh ra, bản đó
> chấm bằng cây `if/else` từ khoá và **không gọi AI lần nào** — xem README
> trong thư mục đó. Bảng "24/24 = 100% cả 4 tiêu chí" trước đây là điểm của
> bộ từ khoá, không phải điểm của hệ thống AI.

---

## 1. Những gì ĐÃ chứng minh được (có bằng chứng trong repo)

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| AI chạy thật ở quyết định trung tâm | **Có** — 18 lời gọi thành công | 18 file `eval/results/trace-*.json`, mỗi file có prompt, response nguyên văn, model, số token |
| Model | `gemini-3.6-flash` | trường `model` trong mỗi trace |
| Pipeline end-to-end | Chạy trọn 5 khâu, sinh `clusters.json` | `python codebase/pipeline.py --require-ai` |
| Gom cụm trên 30 góp ý | 8 vấn đề (đáp án có 8 vấn đề thật) | `codebase/clusters.json` |
| Phạm vi làm lại | 481 ký tự · 25 cảnh = **13,2%** công thu giọng, tiết kiệm **86,8%** | so với 3 637 ký tự / 40 cảnh của cả video |
| Lọc nhiễu (heuristic, không AI) | **100% recall, 100% precision** trên 100 góp ý | `eval/fixtures/gop-y-100.json` có đáp án `locBo` cho từng góp ý |

## 2. Những gì CHƯA đo được

| Tiêu chí | Bar | Trạng thái |
|---|---|---|
| An toàn | 100% | chưa có số trọn bộ |
| Không bịa nguồn | 100% | chưa có số trọn bộ |
| Đúng nhóm lỗi | ≥85% | chưa có số trọn bộ |
| Định vị đúng câu (±1) | ≥70% | chưa có số trọn bộ |
| Dây chuyền câu liền kề | 100% | chưa có số trọn bộ |

Trong 18 case chạy được trước khi hết quota có **cả case ĐẠT và case TRƯỢT** —
nghĩa là bộ đo phân biệt được, không phải lúc nào cũng cho qua. Nhưng số lẻ của
một lượt dở dang không đủ để kết luận, nên **không ghi vào bảng**.

---

## 3. Cách chạy trọn bộ để có số thật

Hạn mức free tier là 20 request/ngày/model. Ba cách:

| Cách | Lệnh / thao tác | Ghi chú |
|---|---|---|
| **A. Đợi reset quota** | chạy lại sau 24h | `python eval/run_eval.py --lan 1` |
| **B. Đổi model khác** | sửa `GEMINI_MODEL=gemini-3.5-flash-lite` trong `codebase/.env` | mỗi model có quota riêng → chạy được thêm 20 case |
| **C. Chia hai ngày** | `--only case-01` … từng case | chậm, chỉ nên dùng khi cần soi một case |

Chạy xong, file `eval/results/run-0N.json` sẽ có trường `nguon: "ai-that"`,
`model`, `so_lan_goi_ai` — đó là dấu hiệu phân biệt số đo thật với số bịa.

---

## 4. Nhịp lặp bắt buộc (Guide §4.1)

```
chạy trọn bộ → bảng % → chọn MỘT failure đau nhất → sửa → chạy lại trọn bộ
```

Mỗi lượt giữ file riêng trong `eval/results/`, **giữ nguyên cả case trượt**.

| Lượt | Thử | Đạt | % | Failure đau nhất | Đổi gì từ lượt trước |
|---|---|---|---|---|---|
| — | — | — | — | *chưa có lượt nào hoàn thành* | — |

---

## 5. Quan sát định tính từ 18 lời gọi AI (chưa phải số đo)

Đây là nhận xét đọc được từ `clusters.json` và các trace, ghi lại để định
hướng sửa prompt — **không phải kết quả đo**:

1. **AI gom cụm quá rộng.** Một cụm trả về "Câu 20–39" trong khi đáp án là câu
   20–23. Định vị rộng làm phạm vi làm lại bị thổi lên.
2. **Nhầm lỗi kỹ thuật sang đổi hình.** Cụm "nhạc nền quá to" đáng lẽ không
   sinh thay đổi kịch bản nào, nhưng AI gán `loai_sua` có "dựng" → cộng nhầm
   6 cảnh.
3. **Điểm tốt:** không thấy AI bịa `quote_id` hay số câu ngoài 1–40 trong các
   lần chạy đã quan sát; hậu kiểm bằng code không phải vứt cụm nào.

Khi chạy được trọn bộ, failure đau nhất nhiều khả năng là **(1) định vị quá
rộng** — sửa bằng cách siết prompt: chỉ trả về những câu thật sự khớp nội dung
góp ý, không mở rộng sang câu lân cận.
