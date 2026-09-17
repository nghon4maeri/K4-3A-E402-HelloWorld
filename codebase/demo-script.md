# Demo Script — FeedbackRadar (CP3 · 30 giây)

> Người giữ:  Nguyễn Văn Chiến (Product · Spec Lead)  · Bản dùng để Duy quay video CP3 và demo live CP6.
> Số liệu trong script lấy  thật từ `clusters.json`  (chạy `pipeline.py` với 30 feedback, không pha).

## Chuẩn bị trước khi quay (30 giây bấm giờ)

1. Chạy pipeline AI thật để dựng lại `clusters.json` —  phải thấy dòng `[✓] Gọi Gemini API thành công!` ở bước 3  (nếu ra dòng `[!] Không tìm thấy GEMINI_API_KEY` hoặc `[X] Lỗi khi gọi Gemini API` tức là video sẽ không đạt "≥1 lời gọi AI chạy thật"):
   ```bash
   cd codebase
   python pipeline.py        # cần GEMINI_API_KEY trong .env (model mặc định gemini-2.5-flash đã đổi thành gemini-3.6-flash)
   ```
   > Lượt chạy gần nhất bằng `gemini-3.6-flash`:  8 cụm · 3.160.000đ · so làm lại 8.000.000đ → tiết kiệm 60,5%  · thời gian AI chạy ~40s.
2. Mở UI qua server cục bộ (tránh CORS khi mở file://):
   ```bash
   python run_local.py       # tự mở http://localhost:8000/index.html
   ```
3. Tắt tab/ứng dụng thừa, để sẵn cửa sổ trình duyệt đang ở màn hình "Nhập dữ liệu".
4. (tuỳ chọn để video có bằng chứng "AI thật" rõ ràng) Quay màn hình từ lúc chạy `pipeline.py`, ghi được dòng `[✓] Gọi Gemini API thành công!` rồi mới sang UI — cắt gọn đoạn ~5s này vào đầu video.

## Kịch bản 30 giây

| Giây | Thao tác trên màn hình | Lên hình / Lời kể (không bắt buộc lồng tiếng) |
|---|---|---|
| 0–3 | Đứng ở màn hình  1 · Nhập dữ liệu  | Header "FeedbackRadar" + thẻ "Giới thiệu AI đại chúng" · transcript 40 câu,  30 góp ý  đã nạp |
| 3–6 | Bấm  "Phân tích bằng AI →"  | Chuyển sang màn hình  2 · AI phân tích  — mỗi khâu hiện dòng trạng thái: lọc nhiễu → phân loại → gom cụm → định vị timestamp → ước chi phí |
| 6–10 | Chờ AI chạy (thật ~40s nhưng đã chạy trước, nên UI mở ra là số liệu sẵn) rồi bấm  "Xem kết quả gom cụm →"  | Kết quả  thật : `kpiClusters = 8` cụm · banner an toàn:  4 góp ý bị lọc bỏ  (công kích cá nhân + prompt injection) |
| 10–16 | Bấm vào  cụm 1 "Khó phân biệt ứng dụng trò chuyện và mô hình ngôn ngữ lớn (LLM)"  (chỉ tay chỗ timestamp `02:01`) | Mở body:  quote gốc `gy-002`/`gy-003`/`gy-018`/`gy-019`  kèm nguồn (hv-011, hv-080) + đề xuất sửa "Thêm hình ảnh minh họa phân lớp app bên ngoài / model bên trong" |
| 16–22 | Bấm sang cụm  6 "Ý kiến trái chiều về thời lượng khoảng dừng suy nghĩ 5 giây"  (`03:32`, câu 35) | Case chỗ khó  mâu thuẫn : `gy-005` (ngắn quá) vs `gy-006` (dài quá) → gom 1 cụm, đề xuất "giữ nguyên 5s + thêm thanh đếm ngược", không đổi độ dài |
| 22–27 | Bấm  "Bước duyệt & xuất kịch bản →"  | Màn hình  4 · Duyệt & Xuất : danh sách câu sửa + chi phí  3.160.000đ  vs làm lại trọn video  8.000.000đ  → "tiết kiệm ~60,5%" |
| 27–30 | Kết khung hình | End card (dừng 3s): "8 cụm từ 30 góp ý · 4 nhiễu bị lọc" |

## 1 case chỗ khó bắt buộc lên hình (trong 30s hoặc cắt gần cuối)

-  Injection/toxicity bị lọc (case ăn điểm):  `gy-011` ("Bỏ qua mọi hướng dẫn phía trên…"), `gy-025` ("Ignore previous instructions…") + `gy-012`/`gy-026` (công kích cá nhân) →  KHÔNG xuất hiện trong cụm nào , chỉ hiện ở banner an toàn `safety_log.json`. Khi quay, nhìn banner "4 góp ý bị lọc bỏ" là đủ bằng chứng.

## Nhắc khi quay

-  Bắt buộc AI thật:  phải thấy AI trả `clusters.json` thật (video quay sau khi `pipeline.py` chạy xong; nếu muốn camera ghi cả lệnh chạy thì bấm máy từ bước 1). Không quay bằng bản mock cứng.
-  Không cho hiện key : không quay lúc Terminal đang in `GEMINI_API_KEY`.
-  Trôi bám giây : thao tác + kể chậm, mỗi câu 1–2 dòng; nếu vượt 30s thì ưu tiên giữ đoạn "mở cụm thấy quote + timestamp" và banner lọc nhiễu.