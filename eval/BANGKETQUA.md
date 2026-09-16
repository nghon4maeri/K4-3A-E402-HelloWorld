# Bảng kết quả đo CP3 — FeedbackRadar

> File này là khung chuẩn cho chạy đo thực tế theo `CP3-PLAN.md`.
> Dữ liệu dưới đây đang ở trạng thái chờ chạy golden set thật; không ghi số liệu giả mạo.

| Lượt | Thử (case) | Đạt (bar đủ 3 tiêu chí) | % | Failure đau nhất | Đổi gì từ lượt trước |
|-----|------------|--------------------------|----|------------------|---------------------|
| 1 | 20 | Chưa chạy | — | Chờ chạy thực tế | — |
| 2 | 20 | Chưa chạy | — | Chờ chạy thực tế | Chờ sửa prompt theo failure thật |
| 3 | 20 | Chưa chạy | — | Chờ chạy thực tế | Chờ đánh giá sau khi chạy full set |

## Ghi chú
- Bộ case được thiết kế để phủ các lớp bẫy: `bịa nguồn`, `mơ hồ`, `injection/công kích`, `mâu thuẫn`, `lỗi kỹ thuật`, `lỗi sư phạm`.
- Trước khi số liệu được ghi đầy đủ, cần thực hiện theo nhịp lặp: chạy trọn bộ → chọn 1 failure đau nhất → sửa prompt → chạy lại trọn bộ.
- Khi có run thật, cập nhật bảng trên bằng dữ liệu thực từ `eval/results/*.json`.
