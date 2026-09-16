# FeedbackRadar — Sơ đồ luồng hoạt động

> **CP2 deliverable: Mock bấm được** — mở `index.html` trong thư mục này (trình duyệt, không cần server)
>
> **Mức prototype hiện tại: MOCK.** Toàn bộ kết quả là dữ liệu tĩnh dựng tay từ gói
> `data/studio-pack/c5-feedbackradar/` — **chưa có lời gọi AI nào**. Mọi mã `gy-xxx`, câu kịch bản và
> mốc thời gian đều lấy nguyên văn từ gói; kiểm lại bằng `node eval/fixtures/dem-lai.js`.

---

## Luồng chính — 4 bước

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  NHẬP DỮ LIỆU — 22 góp ý duy nhất                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐                        │
│  │ Bảng khảo sát│ │ Bình luận    │ │ Tin nhắn     │                        │
│  │ 10 dòng      │ │ 7 góp ý      │ │ 5 góp ý      │                        │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘                        │
│         └────────────────┼────────────────┘                                 │
│                          ▼                                                  │
│  + Kịch bản d1: 40 câu (39 câu có lời) · 3 637 ký tự · bảng câu↔timecode   │
│  Nguồn: gop-y-mau.json (18) + khao-sat-mau.csv (4 mã chỉ có ở đây)         │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT XỬ LÝ (5 khâu) — Mock ở CP2, chạy AI thật từ CP3                    │
│                                                                             │
│  (1) Khử PII & lọc nhiễu                                                   │
│       └─► Loại gy-011 (cài lệnh ẩn) · gy-012 (công kích cá nhân)          │
│           → log an toàn, KHÔNG sinh đề xuất sửa nào                        │
│           → gy-012 không trích nguyên văn vào báo cáo                      │
│                                                                             │
│  (2) Phân loại theo 6 nhóm của đề                                          │
│       └─► nội dung sai · khó hiểu · nhịp nhanh chậm ·                      │
│           giọng đọc · hình ảnh · lỗi kỹ thuật                              │
│                                                                             │
│  (3) Gom cụm theo nghĩa — ĐẾM THEO NGƯỜI, không theo số góp ý             │
│       └─► hv-011 gửi gy-002 + gy-003 + gy-018 cùng một ý → tính 1 người    │
│           ≥2 người độc lập  → tin cậy cao                                  │
│           1 người           → tin cậy thấp + cảnh báo                      │
│           số phiếu 1–1 ngược nhau → tranh chấp, KHÔNG đề xuất sửa          │
│                                                                             │
│  (4) Định vị câu & phút                                                    │
│       └─► khớp ngữ nghĩa với 40 câu trong cau-timecode-d1.csv              │
│           "cùng một ứng dụng nối được nhiều mô hình" → câu 22 · 02:14.6    │
│                                                                             │
│  (5) Tính phạm vi làm lại — đơn vị: KÝ TỰ + CẢNH (không quy ra tiền)      │
│       └─► đổi lời câu N ⇒ thu lại cả N−1, N, N+1 (ảnh hưởng dây chuyền)   │
│           đổi hình / chữ trên màn hình ⇒ 0 ký tự, chỉ dựng lại cảnh        │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRẢ KẾT QUẢ — 22 góp ý → 4 vấn đề + 1 rổ "chưa định vị được"             │
│                                                                             │
│  Mỗi vấn đề hiện:                                                          │
│    · Tiêu đề + loại lỗi + pill mức tin cậy                                 │
│    · Số NGƯỜI độc lập phản ánh (không phải số góp ý)                       │
│    · Quote gốc kèm mã gy-xxx và mã người gửi                               │
│    · Vị trí: câu số mấy + mốc thời gian thật                               │
│    · Kịch bản gốc, đánh dấu câu đổi lời vs câu liền kề phải thu lại        │
│    · Phạm vi làm lại: N ký tự · M cảnh                                     │
│    · Nút [✔ Accept] [✘ Reject]                                             │
│                                                                             │
│  Rổ "chưa định vị được": gy-001 (mơ hồ) · gy-009 (khen chung) ·           │
│  gy-008 + gy-017 (lỗi kỹ thuật, chuyển bộ phận khác)                       │
│  KHÔNG gán bừa vào bất kỳ câu nào (Spec §5 lớp ①②)                        │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BIÊN TẬP VIÊN DUYỆT & XUẤT KỊCH BẢN V2                                    │
│                                                                             │
│  Bảng duyệt: Accept / Reject từng đề xuất                                  │
│    ├── Khung video đồng bộ timecode (mock — chưa nhúng d1.mp4)             │
│    └── Chỉ câu được Accept mới vào Kịch bản V2                             │
│                                                                             │
│  Phạm vi làm lại = tổng các đề xuất đã accept, đối chiếu 3 637 ký tự/40 cảnh│
│                                                                             │
│  XUẤT: kịch bản V2 theo mau-kich-ban.md → gửi giảng viên duyệt cuối        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Bốn vấn đề trong bản mock — và vì sao chọn đúng bốn cái này

| # | Vấn đề | Góp ý gốc | Vị trí | Phạm vi làm lại | Minh hoạ điều gì |
|---|---|---|---|---|---|
| 1 | Lẫn mô hình ngôn ngữ lớn ↔ ứng dụng trò chuyện | `gy-002`, `gy-003`, `gy-018` (đều `hv-011`), `gy-022` | câu 20–23 · 02:14 | **269 ký tự · 3 cảnh** (thu lại câu 21, 22, 23) | Đếm theo người: 4 góp ý nhưng chỉ **2 người** · ảnh hưởng dây chuyền |
| 2 | Định nghĩa "AI tạo sinh" nhồi 3 ví dụ vào 1 câu | `gy-007` (trợ giảng `tg-02`) | câu 14 · 01:20 | **284 ký tự · 3 cảnh** (thu lại câu 13, 14, 15) | Chỉ 1 người nhắc → **tin cậy thấp**, không thổi thành vấn đề chung |
| 3 | Chữ trên màn hình đoạn ba thẻ quá nhỏ | `gy-010` | câu 24–26 · 02:26 | **0 ký tự · 3 cảnh** | Đổi hình **không phải** đổi lời → giữ giọng đã thu, rẻ hơn hẳn |
| 4 | Khoảng dừng 5 giây | `gy-005` ↔ `gy-006` | câu 35 · 03:32 | **không sửa** | Hai người nói ngược nhau, phiếu 1–1 → **không đủ cơ sở để đổi** |

Con số 269 ký tự ở vấn đề 1 khớp chính xác với ví dụ `vi-du/ket-qua-mau.json` mà ban tổ chức tính sẵn.

---

## Phân quyền theo mức Augment (Spec §4)

| AI làm | Người quyết định |
|---|---|
| Khử PII, gom cụm, đếm người độc lập, định vị câu/phút, tính phạm vi làm lại | — |
| **Gợi ý** cách sửa tối thiểu cho mỗi vấn đề | Biên tập viên **Accept / Reject** |
| Chỉ xuất kịch bản V2 khi được chấp nhận | Biên tập viên chốt & gửi giảng viên |

---

## 4 đường đi trải nghiệm (Spec §6)

```
Happy path      : 22 góp ý → 4 vấn đề có bằng chứng → Accept → Kịch bản V2
                  (accept vấn đề 1 → 269/3 637 ký tự = 7,4%, tiết kiệm 92,6%)
Low-confidence  : gy-001 "đoạn giữa hơi nhanh" → rổ chưa định vị được, KHÔNG gán bừa
                  gy-007 chỉ 1 người nhắc → gắn nhãn tin cậy thấp, vẫn để người duyệt xem
Failure path    : gy-011 cài lệnh ẩn · gy-012 công kích → LỌC BỎ trước khi phân tích
Correction path : Reject một đề xuất → giữ nguyên câu gốc, trừ lại ký tự & cảnh tương ứng
Tranh chấp      : gy-005 ↔ gy-006 phiếu 1–1 → ghi nhận cả hai, KHÔNG đề xuất sửa
```

---

## Files trong codebase/

| File | Nội dung |
|---|---|
| `index.html` | Mock bấm được — mở bằng trình duyệt, không cần server |
| `FLOW.md` | Sơ đồ luồng này |

## Còn thiếu để lên mức Working (trước CP3 — 16:00 17/9)

- [ ] Lời gọi AI thật ở khâu (3) gom cụm và (4) định vị câu, log/trace lưu trong `eval/`
- [ ] Nhúng `video-mau/d1.mp4` thật thay khung video mock
- [ ] Đọc góp ý từ file JSON/CSV thay vì mảng `ISSUES` tĩnh
- [ ] Bộ ~100 góp ý tự sinh + đáp án (yêu cầu "Đội tự lo" trong README của gói)
