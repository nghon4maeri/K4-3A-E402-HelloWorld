# CP1 Canvas — FeedbackRadar (C5)

> Agent biến góp ý của người học thành bản kế hoạch sửa video

| Mục | Nội dung |
|---|---|
| **Hướng** | C — Lesson Studio (FeedbackRadar) |
| **Job executor** | Đội sản xuất video bài giảng (biên tập + giảng viên/trợ giảng) sau mỗi đợt học phải đọc và xử lý góp ý về video |
| **Pain 1 câu** | Góp ý từ nhiều kênh, mơ hồ / trùng / mâu thuẫn; đội đọc tay rồi thường làm lại gần cả video dù chỉ vài câu có vấn đề — mà quy trình thu giọng rồi dựng hình khớp theo câu khiến mỗi lần sửa rất tốn thời gian và tiền |
| **Evidence ban đầu** | Mining trong `data/`: video mẫu d1.mp4 (4'11"), kịch bản 40 câu, bảng câu↔timecode, ~100 góp ý mô phỏng tự tạo kèm đáp án. Không dùng dữ liệu người học thật; ẩn danh trước khi đưa vào AI |
| **Lát cắt 1 câu** | Nhập góp ý nhiều kênh + transcript có timecode → hệ thống quyết định `VẤN ĐỀ / MƠ HỒ / NHIỄU`; gom góp ý cùng chuyện thành 1 vấn đề, định vị đúng câu & phút, xếp ưu tiên, đề xuất cách sửa ít tốn nhất kèm danh sách thu/dựng lại; mỗi vấn đề dẫn ngược về góp ý gốc |
| **Automation** | Conditional: AI tự gom + đề xuất khi ≥N góp ý độc lập cùng chỉ một chỗ; đánh dấu để người duyệt xử lý khi mơ hồ hoặc hai nhóm nói ngược nhau; từ chối/lọc khi gặp lệnh ẩn, công kích cá nhân, hoặc yêu cầu ngoài phạm vi. AI chỉ đề xuất — người duyệt quyết mọi thay đổi |
| **Willing users dự kiến** | Mời 5 người ngoài nhóm test: biên tập nội dung khóa học online · giảng viên/gia sư tự làm khóa · phụ trách L&D doanh nghiệp · trợ giảng thu thập góp ý · nhà sáng tạo video giáo dục |
| **Phân công** | Trưởng nhóm: spec + prototype · TV2: dữ liệu + đáp án (~100 góp ý) · TV3: gom nhóm & định vị (AI call) · TV4: eval / tự chấm · TV5: giao diện duyệt + demo |
