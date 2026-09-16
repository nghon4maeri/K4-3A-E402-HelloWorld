# Ba file này KHÔNG phải kết quả đo của AI — đã loại khỏi bài nộp

`run-01.json`, `run-02.json`, `run-03.json` trong thư mục này được sinh lúc
00:26–00:54 ngày 17/9 bởi **bản `run_eval.py` cũ**, bản đó chấm điểm bằng một
cây `if/else` từ khoá (`classify_text_heuristically`) và **không gọi AI lần nào**.

Bằng chứng:
- Cả ba file đều không có trường `nguon`, `model`, `so_lan_goi_ai`.
- Trace AI đầu tiên trong `eval/results/` là `trace-20260917-014724.json`,
  tức **sau** ba file này gần một tiếng. Trước thời điểm đó chưa có lời gọi AI nào.
- Bộ từ khoá của bản cũ còn khớp `"cross-attention"` và `"1:20"` — những thứ
  không hề có trong video d1.

Số 24/24 = 100% ở cả bốn tiêu chí là điểm của bộ từ khoá đó, không phải điểm
của hệ thống AI. Giữ lại đây để minh bạch quá trình, **không dùng cho bảng đo**.

Kết quả đo thật nằm ở `eval/results/run-0N.json` (có trường `nguon: "ai-that"`)
và các file `trace-*.json` kèm prompt/response/tokens của từng lần gọi.
