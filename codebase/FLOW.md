# FeedbackRadar — Sơ đồ luồng hoạt động

> **CP2 deliverable: Mock bấm được** — mở `index.html` trong thư mục này (trình duyệt, không cần server)

---

## Luồng chính — 4 bước

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  NHẬP DỮ LIỆU                                                             │
│  ┌────────────────┐  ┌────────────────┐                                     │
│  │ Google Form    │  │ Discord #gop-y │                                     │
│  │ 22 góp ý       │  │ 8 tin nhắn     │                                     │
│  └───────┬────────┘  └───────┬────────┘                                     │
│          └──────┬─────────────┘                                             │
│                 ▼                                                           │
│  Kịch bản 40 câu có timecode + Bảng chi phí sửa                           │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AGENT AI XỬ LÝ (5 khâu) — Mock ở CP2, chạy thật từ CP3                 │
│                                                                             │
│  (1) Khử PII & lọc nhiễu                                                  │
│       └─► Lọc bỏ: công kích cá nhân, prompt injection (2 tin)             │
│           → Ghi vào log an toàn, KHÔNG đưa vào cụm                        │
│                                                                             │
│  (2) Phân loại lỗi                                                         │
│       └─► 3 nhóm: Nội dung | Sư phạm (tốc độ/giọng) | Kỹ thuật           │
│                                                                             │
│  (3) Gom cụm theo nghĩa (semantic clustering)                             │
│       └─► ≥2 người độc lập cùng chỉ 1 chỗ → cụm "chắc chắn"              │
│           1 người → cụm "tin cậy thấp" + cảnh báo                         │
│                                                                             │
│  (4) Định vị timestamp                                                    │
│       └─► Đối chiếu nghĩa → trỏ về CÂU & PHÚT trong transcript          │
│                                                                             │
│  (5) Ước chi phí sửa tối thiểu                                            │
│       └─► Đơn giá: thu lại lời 50k/câu · dựng lại cảnh 150k/cảnh        │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  TRẢ KẾT QUẢ — 30 góp ý → 4 cụm vấn đề                                   │
│                                                                             │
│  Mỗi cụm hiện:                                                            │
│    · Tiêu đề + loại lỗi (pill màu)                                         │
│    · Số người học phản ánh                                                 │
│    · Bằng chứng quote gốc (≥2 quote/trỏ về ID gy-xxx)                    │
│    · Vị trí: câu + phút + timecode trên video                              │
│    · Đề xuất sửa + chi phí ước tính                                        │
│    · Nút [✔ Accept] [✘ Reject]                                            │
│                                                                             │
│  Góp ý mơ hồ / không định vị được → rổ riêng "góp ý chung chung"         │
│  KHÔNG gán bừa vào bất kỳ câu nào (tránh hallucination — Spec §5 lớp ①②) │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  BIÊN TẬP VIÊN DUYỆT & XUẤT KỊCH BẢN V2                                  │
│                                                                             │
│  Bảng duyệt: решить Accept hay Reject cho từng đề xuất sửa                 │
│    ├── Video player đồng bộ timecode — xem đoạn lỗi tại đúng vị trí      │
│    └── Chỉ những câu được Accept → vào Kịch bản V2                        │
│                                                                             │
│  Chi phí sửa = tổng các đề xuất accepted                                   │
│  Tiết kiệm so với làm lại toàn bộ video                                   │
│                                                                             │
│  XUẤT:                                                                     │
│    · Nháp kịch bản V2 (.docx)                                              │
│    · Gửi giảng viên duyệt lần cuối (Luồng Augment: người quyết)           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Phân quyền theo mức Augment (Spec §4)

| AI làm | Người quyết định |
|---|---|
| Khử PII, gom cụm, định vị timestamp, ước chi phí | — |
| **Gợi ý** cách sửa tối thiểu cho mỗi cụm | Biên tập viên **Accept / Reject** |
| Chỉ xuất khi được chấp nhận | Biên tập viên chốt & gửi giảng viên |

---

## 4 đường đi trải nghiệm (Spec §6)

```
Happy path        : 30 feedback → 4 cụm chuẩn →_ACCEPT tất cả → Kịch bản V2 (430k)
Low-confidence    : "video chán quá" → rổ chung chung → KHÔNG gán bừa
Failure path      : prompt injection / công kích → LỌC BỎ → log an toàn
Correction path   : Reject câu X → giữ nguyên gốc, cập nhật lại chi phí
```

---

## Files trong codebase/

| File | Nội dung |
|---|---|
| `index.html` | Mock bấm được — mở bằng trình duyệt, không cần server |
| `FLOW.md` | Sơ đồ luồng này |
