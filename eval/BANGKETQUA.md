# BẢNG KẾT QUẢ ĐO LƯỜNG CP3 — FEEDBACKRADAR

> Nhóm HelloWorld · Lớp 3A · Phòng E402
> Golden set: `eval/golden-set.json` (24 case · Vũ Văn Hà)
> Cập nhật: 10:42 · 18/09/2026

---

## 0. Trạng thái trung thực của bảng này

**Lượt 3 đã hoàn thành đủ 24 case.** Có 19 request gọi Gemini thật; 5 case
injection/công kích được bộ lọc heuristic chặn trước nên không cần gọi model.
Kết quả là **22/24 case đạt = 91,7%**.

Bộ đo không chấm các case sạch bằng heuristic: các case đó đều có trace AI thật.
Các file kết quả hợp lệ là `eval/results/run-01.json`, `run-02.json` và
`run-03.json`.

> **Ba file kết quả cũ trong `eval/results/_khong-hop-le/` đã bị loại**. Chúng do
> bản `run_eval.py` cũ sinh ra, bản đó
> chấm bằng cây `if/else` từ khoá và **không gọi AI lần nào** — xem README
> trong thư mục đó. Bảng "24/24 = 100% cả 4 tiêu chí" trước đây là điểm của
> bộ từ khoá, không phải điểm của hệ thống AI.

---

## 1. Những gì ĐÃ chứng minh được (có bằng chứng trong repo)

| Việc | Kết quả | Bằng chứng |
|---|---|---|
| AI chạy thật ở quyết định trung tâm | **Có** — 19 lời gọi thành công ở lượt 3 | `eval/results/run-03.json` và các file `trace-*.json` |
| Model | `gemini-3.5-flash-lite` | trường `model` trong `run-03.json` và trace |
| Pipeline end-to-end | Chạy trọn 5 khâu, sinh `clusters.json` | `python codebase/pipeline.py --require-ai` |
| Gom cụm trên 30 góp ý | 8 vấn đề (đáp án có 8 vấn đề thật) | `codebase/clusters.json` |
| Phạm vi làm lại | 481 ký tự · 25 cảnh = **13,2%** công thu giọng, tiết kiệm **86,8%** | so với 3 637 ký tự / 40 cảnh của cả video |
| Lọc nhiễu (heuristic, không AI) | **100% recall, 100% precision** trên 100 góp ý | `eval/fixtures/gop-y-100.json` có đáp án `locBo` cho từng góp ý |

## 2. Kết quả theo quality bar

| Tiêu chí | Bar | Trạng thái |
|---|---|---|
| An toàn | 100% | 100% (24/24) |
| Không bịa nguồn | 100% | 100% (24/24) |
| Đúng nhóm lỗi | ≥85% | 91,7% (22/24) |
| Định vị đúng câu (±1) | ≥70% | 100% (24/24) |
| Dây chuyền câu liền kề | 100% | 100% |

Lượt 3 có cả case ĐẠT và case TRƯỢT; bộ đo phân biệt được kết quả và giữ nguyên
hai case trượt để phân tích. Cả 5 quality bar đều đạt trong lượt này.

---

## 3. Cách chạy trọn bộ để có số thật

Hạn mức free tier phụ thuộc model/tài khoản; lượt 1 đã dùng 19 request Gemini.
Các cách chạy lượt tiếp theo:

| Cách | Lệnh / thao tác | Ghi chú |
|---|---|---|
| **A. Đợi reset quota** | chạy lại sau khi quota reset | `python eval/run_eval.py --lan 3 --delay 5` |
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
| 1 | 24 | 19 | 79,2% | Dây chuyền thu lời 75%; lỗi kỹ thuật và định vị còn mở rộng | — |
| 2 | 24 | 20 | 83,3% | Đúng nhóm lỗi 83,3%, dưới bar 85%; case 05, 08, 19, 20 | Siết dây chuyền, lỗi kỹ thuật và phạm vi định vị |
| 3 | 24 | 22 | 91,7% | Còn 2 case trượt: case-08 và case-20 | Siết quy tắc phân loại mơ hồ và nội dung |

---

## 5. Phân tích failure của lượt 3

Đây là nhận xét đọc được từ `clusters.json` và các trace, ghi lại để định
hướng sửa prompt — **không phải kết quả đo**:

1. **case-08:** vẫn định vị đúng câu 40 nhưng phân loại là Sư phạm thay vì
   Nội dung.
2. **case-20:** vẫn phân loại lỗi nội dung/nhồi ví dụ thành Sư phạm.

Điểm cải thiện: case-05, case-19 đã đạt sau khi siết prompt; case-14 vẫn giữ
được dây chuyền 100%; định vị đạt 100% và phân loại tăng lên 91,7%.

Điểm tốt: không có quote_id ngoài input hoặc câu_index ngoài 1–40.

Sau lượt 3, cả 5 tiêu chí đều đạt quality bar. Không cần sửa prompt hoặc chạy
thêm lượt benchmark để kết luận CP3; giữ nguyên hai case trượt để báo cáo trung
thực và làm đầu vào cho CP5.
