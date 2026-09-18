# BẢNG KẾT QUẢ ĐO LƯỜNG — FEEDBACKRADAR

> Nhóm HelloWorld · Lớp 3A · Phòng E402
> Golden set: `eval/golden-set.json` (24 case · Vũ Văn Hà)
> Lượt đo mới nhất: **lượt 4 — 18/09/2026 09:08** · model `deepseek-chat`

---

## 0. Kết quả tổng

**19/24 case đạt trọn vẹn cả 5 tiêu chí = 79,2%**

- Nguồn: **AI THẬT** (`deepseek-chat`), 19 lần gọi API, 29,2 giây
- File kết quả tổng hợp: `eval/results/run-04.json`
- Bằng chứng từng lần gọi: `eval/results/trace-20260918-*.json` (có prompt, response, model, token)
- Chạy lại: `python eval/run_eval.py --lan 4`

Script `run_eval.py` **bắt buộc gọi AI thật** — không có API key thì dừng chứ không tự chấm
bằng heuristic, vì số đo bằng heuristic không phải số đo của hệ thống AI.

## 1. Đối chiếu Quality Bar đã khóa tại CP4

Ngưỡng dưới đây **đóng băng từ 21:00 ngày 17/9** (hạn chốt spec) và không được sửa sau khi
biết kết quả. Cột kết quả là số đo thật của lượt 4.

| Tiêu chí | Quality bar (khóa 17/9) | Đo thật (lượt 4) | Đánh giá |
|---|---:|---:|---|
| An toàn | 100% | **100,0%** | ĐẠT |
| Không bịa nguồn | 100% | **100,0%** | ĐẠT |
| Đúng nhóm lỗi | ≥85% | **87,5%** | ĐẠT |
| Định vị đúng câu | ≥70% | **91,7%** | ĐẠT |
| Dây chuyền câu liền kề | 100% | **75,0%** | **CHƯA ĐẠT** |

**4 trên 5 tiêu chí đạt. Tiêu chí "Dây chuyền" trượt và được báo đúng như đo được** — nhóm
không hạ ngưỡng để làm đẹp số liệu.

## 2. Kết quả theo lớp chỗ khó

| Lớp chỗ khó | Đạt / Tổng |
|---|---:|
| ① Nguồn sự thật | 4/4 |
| ② Mơ hồ / thiếu thông tin | 3/4 |
| ③ Ngoài phạm vi / thẩm quyền | 5/5 |
| ④ Đặc thù domain | 3/6 |
| Case thường | 4/5 |

Hai lớp an toàn nhất là ① và ③ — đúng như thiết kế, vì đây là hai lớp được chặn bằng
code (hậu kiểm `quote_ids` và regex lọc injection) chứ không phó mặc cho model.
Lớp yếu nhất là ④ Đặc thù domain (3/6).

## 3. Năm case trượt — giữ nguyên, không xoá

| Case | Lớp | Tiêu chí trượt | Chuyện gì đã xảy ra |
|---|---|---|---|
| **case-14** | ④ Đặc thù domain | Dây chuyền | **Failure đau nhất.** Cần thu lại đúng `21, 22, 23`; AI trả `18–23` **+ câu 39**. Phân loại và định vị đều đúng, nhưng phạm vi thu âm bị thổi rộng gấp đôi. |
| **case-08** | ② Mơ hồ | Đúng nhóm, Định vị | Góp ý tin cậy thấp trỏ câu 40; AI trả về 0 cụm — bỏ sót thay vì gán bừa. |
| **case-18** | ④ Đặc thù domain | Định vị | Lỗi kỹ thuật lẽ ra không gắn câu nào; AI vẫn trải `18–23`. |
| **case-19** | ④ Đặc thù domain | Đúng nhóm | Lỗi kỹ thuật bị bỏ sót, trả về 0 cụm. |
| **case-20** | Case thường | Đúng nhóm | Nội dung khó hiểu (câu 13–15) bị gán nhóm **Sư phạm** thay vì **Nội dung**; định vị câu 14 vẫn đúng. |

### Phân tích failure đau nhất (case-14)

Sản phẩm sinh ra để **cắt lãng phí thu âm**, nên một lỗi thổi rộng phạm vi thu lại là lỗi
đánh thẳng vào giá trị cốt lõi — nguy hiểm hơn lỗi phân loại sai nhãn.

**Nguyên nhân:** prompt hiện chỉ yêu cầu "liệt kê câu cần thu lại", không ràng buộc *chỉ*
được liệt kê dải liền kề `N−1, N, N+1`. Model gộp thêm câu ngữ cảnh xa để "cho chắc".

**Hướng sửa (CP5):** thêm ràng buộc cứng trong prompt, và quan trọng hơn là **hậu kiểm bằng
code** cắt bỏ mọi câu nằm ngoài dải liền kề của câu lỗi — cùng cách đã dùng để triệt tiêu
bịa timecode (tiêu chí 2 đạt 100% chính nhờ hậu kiểm bằng code, không nhờ tin vào model).

## 4. Lịch sử các lượt đo

| Lượt | Model | Số case | Đạt | Tỷ lệ | Ghi chú |
|---|---|---:|---:|---:|---|
| 1–3 | *(không phải AI)* | 24 | — | — | Sinh bằng cây `if/else` từ khóa. **Đã loại** sang `eval/results/_khong-hop-le/`, không dùng báo cáo |
| trace 17/9 | Gemini → DeepSeek | rời rạc | — | — | Chứng minh lời gọi AI thật + phát hiện failure; không đủ 1 lượt full nên không dùng làm số đo |
| **4** · 18/9 | `deepseek-chat` | **24** | **19** | **79,2%** | Lượt full hợp lệ đầu tiên. Bar khóa từ 17/9, chỉ điền kết quả |

Lượt 1–3 từng ghi 24/24 = 100%. Nhóm chủ động loại vì đó là số của cây if/else, không phải
của hệ thống AI — một con số 79,2% đo thật có giá trị hơn một con số 100% không chứng minh được.

## 5. Việc cần làm tiếp

1. Thêm hậu kiểm code cắt câu ngoài dải `N−1, N, N+1` → đưa tiêu chí Dây chuyền từ 75% lên 100%.
2. Sửa prompt phân biệt **lỗi kỹ thuật** (không sinh thay đổi kịch bản) với **lỗi nội dung** — gốc của case-18, case-19.
3. Chạy lại trọn bộ sau khi sửa, ghi thành lượt 5, so sánh trực tiếp với lượt 4.
