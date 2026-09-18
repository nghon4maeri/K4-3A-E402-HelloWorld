# Validation log — hướng thay thế bằng benchmark

> Ngày lập: 18/09/2026
> Sản phẩm: FeedbackRadar
> Trạng thái: **Không thực hiện khảo sát hoặc user testing thật trong CP5.**

## 1. Phạm vi và tính trung thực

Nhóm không có feedback log từ người ngoài nhóm nên **không khai báo đạt R6** và không tự tạo tên, quote hay hành vi của người dùng. File này dùng hướng thay thế được nêu trong `02-guide.md`: thay phần "User thật nói gì" bằng kết quả đo trên golden set, các failure cụ thể và quyết định cải tiến.

Đây là bằng chứng kiểm thử hệ thống, **không phải** bằng chứng phỏng vấn người dùng. Khảo sát định hướng n = 5 trong `eval/evidence-log.md` cũng không được dùng để thay cho user validation.

## 2. Bằng chứng thay thế

| Hạng mục | Kết quả | Nguồn kiểm tra |
|---|---:|---|
| Golden set | 24 case | [`eval/golden-set.json`](../eval/golden-set.json) |
| Lượt chạy hợp lệ | 1 lượt AI thật | [`eval/results/run-04.json`](../eval/results/run-04.json) |
| Case đạt đầy đủ 5 tiêu chí | 19/24 = 79,2% | [`eval/BANGKETQUA.md`](../eval/BANGKETQUA.md) |
| Quality bar đạt | 4/5 tiêu chí | [`eval/BANGKETQUA.md`](../eval/BANGKETQUA.md) |
| Quality bar chưa đạt | Dây chuyền: 75% < 100% | [`eval/BANGKETQUA.md`](../eval/BANGKETQUA.md) |

## 3. Failure log thay cho quote người dùng

Các dòng dưới đây là quan sát từ output AI và fixture, không phải lời nói nguyên văn của người dùng.

| Case | Quan sát được | Tác động | Quyết định tiếp theo |
|---|---|---|---|
| `case-14` | Cần thu lại câu 21–23 nhưng AI trả 18–23 và thêm câu 39. | Thổi rộng phạm vi thu âm, đánh trực tiếp vào giá trị tiết kiệm công sức. | Thêm hậu kiểm chỉ cho phép dải `N-1, N, N+1`. |
| `case-08` | Feedback mơ hồ bị bỏ sót, không gán bừa vào cụm. | Giảm recall nhưng an toàn hơn việc bịa vị trí. | Giữ nguyên nguyên tắc không định vị khi thiếu bằng chứng; bổ sung trạng thái cần người duyệt. |
| `case-18` | Lỗi kỹ thuật đáng ra không gắn câu nào nhưng output trải rộng 18–23. | Có thể tạo kế hoạch sửa nội dung không cần thiết. | Tách lỗi kỹ thuật khỏi phạm vi thu lại lời bằng hậu kiểm. |
| `case-19` | Lỗi kỹ thuật bị bỏ sót. | Người biên tập có thể không thấy vấn đề cần xử lý. | Bổ sung case lỗi kỹ thuật vào lượt chạy tiếp theo và sửa prompt phân loại. |
| `case-20` | Lỗi nội dung bị gán nhãn sư phạm, dù định vị câu 14 đúng. | Làm lệch người nhận và cách sửa đề xuất. | Làm rõ ranh giới `Nội dung` và `Sư phạm` trong prompt. |

## 4. Kết luận và backlog

- Chủ đề lặp nhiều nhất trong bằng chứng thay thế: **AI mở rộng phạm vi sửa vượt quá phần có bằng chứng**, đặc biệt với lỗi domain và lỗi kỹ thuật.
- Việc cần sửa trước demo: hậu kiểm dải câu liền kề và chặn lỗi kỹ thuật khỏi kế hoạch thu lại lời.
- Giữ nguyên: AI chỉ đề xuất, biên tập viên accept/reject; các case không đủ bằng chứng không bị gán bừa.
- Để dành sau: thực hiện user testing thật với ít nhất 2 người ngoài nhóm, ghi quote nguyên văn và quan sát hành vi theo script CS177; khi đó mới có thể bổ sung feedback log R6.

Chi tiết thay đổi và lý do được ghi trong [`spec.md`](../spec.md), §9 Changelog.
