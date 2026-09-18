# Kịch bản quay video 30 giây — CP3

Người phụ trách: Nguyễn Văn Chiến (viết) · Nguyễn Cảnh Duy (quay & nộp)

> **Mục tiêu CP3:** giám khảo tick được ô "**lời gọi AI thật, không hardcode**".
> Nên video phải thấy **terminal chạy AI** rồi mới tới UI — chỉ quay UI không chứng minh được gì.

---

## Chuẩn bị trước khi bấm quay (làm hết, rồi mới quay)

1. Điền key: copy `codebase/.env.example` → `codebase/.env`, chọn `AI_PROVIDER=gemini` cho demo cá nhân và dán `GEMINI_API_KEY` (hoặc chọn `AI_PROVIDER=deepseek` rồi dán `DEEPSEEK_API_KEY` khi demo cùng đội)
2. Chạy thử một lần cho chắc: `python codebase/pipeline.py --require-ai`
3. **Xoá `codebase/clusters.json`** đi — để lúc quay sinh lại từ đầu, mới là thật
4. Mở sẵn 2 cửa sổ cạnh nhau:
   - Trái: terminal, đã `cd` vào thư mục repo
   - Phải: trình duyệt ở `http://localhost:8000/index.html` (chạy `python codebase/run_local.py` trước)
5. Phóng to chữ terminal (Ctrl + +) để giám khảo đọc được trên video

---

## Kịch bản 30 giây

| Giây | Thao tác | Thấy gì trên màn hình |
|---|---|---|
| 0–3 | Terminal đang mở sẵn, gõ lệnh | `python codebase/pipeline.py --require-ai` |
| 3–8 | Enter, để chạy | `[1/5] Lọc nhiễu — 27 sạch \| 3 bị lọc` rồi liệt kê mã bị lọc |
| 8–14 | AI chạy thật | `[Bước 3/5]` → `model=<model đang chọn> · thời gian · tokens` |
| 14–18 | Hậu kiểm + kết quả | `[3/5] Hậu kiểm chống bịa` → danh sách vấn đề, mỗi cái kèm số người + số ký tự |
| 18–22 | Chuyển sang trình duyệt, F5 | Banner xanh: **"Đang dùng kết quả AI THẬT — đọc từ clusters.json"** |
| 22–27 | Bấm vào một vấn đề | Mở ra thấy mã `gy-xxx` gốc, câu kịch bản, mốc thời gian |
| 27–30 | Bấm Accept một đề xuất | Ô "Phải làm lại" nhảy số ký tự · số cảnh |

**Câu chốt nếu có lồng tiếng** (không bắt buộc):
> "AI gom cụm và định vị câu — timecode tra bảng cứng, chi phí do code cộng, nên AI không bịa được."

---

## Cách quay trên Windows

**Cách 1 — Game Bar (có sẵn, không cài gì):**
- `Win + G` → bấm nút ghi hình, hoặc `Win + Alt + R` để quay ngay
- Dừng: `Win + Alt + R` lần nữa
- File nằm ở `C:\Users\<tên>\Videos\Captures\`
- *Hạn chế:* không quay được toàn màn hình, chỉ quay một cửa sổ. Nếu cần thấy cả terminal lẫn trình duyệt thì dùng cách 2.

**Cách 2 — OBS Studio (miễn phí, quay cả màn hình):**
- Tải ở obsproject.com → Sources → **Display Capture** → Start Recording
- Dừng rồi lấy file ở `C:\Users\<tên>\Videos\`

**Cách 3 — điện thoại quay màn hình máy tính:** vẫn được chấp nhận, miễn đọc được chữ.

---

## Sau khi quay

1. Xem lại: có thấy rõ dòng `model=` và `tokens` không? Không thấy thì quay lại.
2. Cắt cho đúng ~30 giây nếu lỡ dài (không bắt buộc dựng đẹp).
3. Đặt tên `cp3-demo-30s.mp4`, để trong `codebase/video/`.
4. **Nếu file nặng > 25 MB:** đừng commit vào repo. Upload Google Drive, để link vào `codebase/video/README.md`, mở quyền "ai có link cũng xem được".
5. Trước khi push: `git status` xem có `.env` không. Có là dừng lại ngay.

---

## Phòng khi hỏng

| Hỏng gì | Làm gì |
|---|---|
| Hết quota / lỗi 429 | Đổi model Gemini trong `.env`, hoặc chuyển `AI_PROVIDER=deepseek` và điền `DEEPSEEK_API_KEY` |
| AI trả JSON lỗi | Pipeline tự thử lại 3 lần; vẫn lỗi thì chạy lại lệnh |
| Không kịp quay | Quay riêng terminal 15 giây cũng được — miễn thấy `model=` và kết quả |
| Mạng chậm lúc demo live | Đã có `clusters.json` sinh sẵn, UI vẫn hiện kết quả AI thật |
