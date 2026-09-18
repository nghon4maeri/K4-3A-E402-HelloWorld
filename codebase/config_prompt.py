"""
Config & Prompt Template for FeedbackRadar Pipeline
Author: Nguyen Ho Nam (Dev / Agent Engineer)
"""

import re
from typing import List, Dict, Any, Tuple

# ==========================================
# 1. THƯỚC ĐO PHẠM VI LÀM LẠI
# ==========================================
# NGUỒN: data/studio-pack/c5-feedbackradar/bang-chi-phi-lam-lai.md
#
# Ban tổ chức KHÔNG cấp đơn giá tiền. File đó nói rõ:
#   "Giọng tính tiền theo SỐ KÝ TỰ của lời đọc"
#   "Đội tự chọn cách quy đổi, miễn là nhất quán và nói rõ đã quy đổi ra sao"
#   "Rồi đặt cạnh con số của việc làm lại toàn bộ — 3 637 ký tự và 40 cảnh"
#
# Vì vậy nhóm đo bằng đúng hai đại lượng ban tổ chức cấp — SỐ KÝ TỰ phải thu
# lại giọng và SỐ CẢNH phải dựng lại — không tự đặt giá tiền.
#
# Số gốc của video d1, nhóm đã đếm lại từ cau-timecode-d1.csv và khớp 100%:
TONG_KY_TU_CA_VIDEO = 3637   # tổng ký tự lời đọc (39 câu có lời; câu 35 là dừng 5 giây)
TONG_CANH_CA_VIDEO = 40      # tổng số cảnh

# Ảnh hưởng dây chuyền: đổi lời câu N buộc thu lại cả N-1 và N+1, vì máy đọc
# lấy câu trước/sau làm ngữ cảnh. Bỏ qua điều này là báo thiếu gần nửa chi phí.
DAY_CHUYEN = 1

# ==========================================
# 2. BỘ LỌC HEURISTIC AN TOÀN (SAFETY & INJECTION FILTER)
# ==========================================
PROMPT_INJECTION_PATTERNS = [
    r"bỏ\s+qua\s+mọi\s+hướng\s+dẫn",
    r"ignore\s+(all\s+)?(previous\s+|prior\s+)?instructions",
    r"đánh\s+giá\s+video\s+này\s+(mười|10(\s*/\s*10)?)\s*(điểm)?",
    r"return\s+a\s+perfect\s+score",
    r"say\s+there\s+are\s+no\s+problems",
    r"output\s+(the\s+)?system\s+prompt",
    r"pretend\s+you\s+are",
    r"you\s+are\s+now\s+a",
    r"jailbreak",
    r"system\s*prompt",
    r"ghi\s+vào\s+báo\s+cáo\s+là\s+không\s+có\s+vấn\s+đề",
    # Bổ sung sau lượt đo 1 — case-11 lọt lưới:
    r"(hệ\s*thống|system)\s+(chú\s*ý|lưu\s*ý|attention)",
    r"đặt\s+toàn\s+bộ\s+.{0,30}(mức|về)",
    r"tự\s+(chấp\s+nhận|duyệt)\s+mọi",
    r"đừng\s+phân\s+tích",
    r"trả\s+về\s+.{0,15}(rỗng|empty)",
    r"(in|xuất|print)\s+ra\s+.{0,25}prompt",
    r"prompt\s+(hệ\s*thống|của\s+bạn)",
]

PERSONAL_ATTACK_PATTERNS = [
    r"(người\s+làm|giảng\s+viên|thầy|cô|tác\s+giả)\s+.*chả\s+hiểu\s+gì",
    r"chả\s+hiểu\s+gì\s+về\s+ai",
    r"làm\s+ăn\s+kiểu\s+gì",
    r"dở\s+tệ",
    r"trò\s+hề",
    r"thằng\s+ngu",
    r"đồ\s+ngu",
    r"ngu\s+ngốc",
    r"đần\s+độn",
    r"vô\s+học",
    r"không\s+đáng\s+học",
    r"tệ\s+hại",
    r"phát\s+âm\s+như\s+hạch",
    # Bổ sung sau lượt đo 1 — case-13 lọt lưới:
    r"(đọc|giảng|nói)\s+như\s+(máy|robot|cái\s+máy)",
    r"chán\s+không\s+chịu\s+được",
    r"lười\s+biếng",
    r"làm\s+cho\s+có",
    r"(là\s+)?biết\s+(ngay\s+)?không\s+có\s+chuyên\s+môn",
]

def check_safety(text: str) -> Tuple[bool, str]:
    """
    Kiểm tra xem nội dung góp ý có vi phạm an toàn không:
    - Trả về (True, "") nếu an toàn
    - Trả về (False, lý do) nếu vi phạm (prompt injection / công kích cá nhân)
    """
    text_lower = text.lower()
    for pat in PROMPT_INJECTION_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return False, "Prompt Injection detected"
            
    for pat in PERSONAL_ATTACK_PATTERNS:
        if re.search(pat, text_lower, re.IGNORECASE):
            return False, "Personal attack / toxic content detected"
            
    return True, ""

def filter_feedbacks(feedbacks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Tách feedback thành 2 danh sách:
    - safe_list: Các góp ý hợp lệ đưa vào AI Pipeline
    - safety_log: Các góp ý bị chặn lại kèm lý do
    """
    safe_list = []
    safety_log = []
    for item in feedbacks:
        is_safe, reason = check_safety(item.get("noiDung", ""))
        if is_safe:
            safe_list.append(item)
        else:
            safety_log.append({
                "id": item.get("id"),
                "nguoiGui": item.get("nguoiGui"),
                "noiDung": item.get("noiDung"),
                "lyDo": reason
            })
    return safe_list, safety_log

# ==========================================
# 3. SYSTEM PROMPT & JSON SCHEMA
# ==========================================
SYSTEM_PROMPT = """Bạn là Chuyên gia Phân tích Góp ý & Tối ưu Sản xuất Bài giảng (FeedbackRadar Agent).
Nhiệm vụ của bạn là nhận danh sách các góp ý của người học về một video bài giảng, đối chiếu với danh sách câu trong kịch bản (kèm câu index 1..40), sau đó:
1. GOM CỤM (Clustering) các góp ý cùng chỉ về một vấn đề cụ thể.
2. PHÂN LOẠI LỖI thành 3 nhóm chính:
   - "Nội dung" (giải thích mơ hồ, sai khái niệm, nhồi nhét ví dụ, thiếu câu chốt...)
   - "Sư phạm (tốc độ/giọng)" (nói quá nhanh, nhịp dừng tranh cãi, ví dụ xa rời thực tế...)
   - "Kỹ thuật" (nhạc nền to át tiếng giảng, slide chữ quá nhỏ trên mobile, phụ đề lệch nhịp...)
     QUY TẮC ƯU TIÊN PHÂN LOẠI:
     - Chỉ nói "nhanh/chậm" hoặc "đoạn giữa" mà không có câu, từ khóa nội dung
         hoặc mốc đủ rõ thì coi là góp ý mơ hồ: đưa vào `gop_y_chung_chung`, không
         tự gán Sư phạm và không tự chọn một dải câu.
     - "Khó hiểu", "nghe nhiều lần", "nhồi nhiều ví dụ", "thiếu giải thích"
         là Nội dung, trừ khi quote nói rõ tốc độ/nhịp đọc là nguyên nhân.
     - "Phụ đề lệch/chạy nhanh hơn giọng" luôn là Kỹ thuật và phải tạo cụm với
         `cau_index: []`, không được im lặng bỏ qua quote.
3. ĐỊNH VỊ CÂU (Sentence Index): Xác định chính xác danh sách câu_index (từ 1 đến 40) bị ảnh hưởng trực tiếp bởi vấn đề.
   CHÚ Ý QUAN TRỌNG:
   - KHÔNG ĐƯỢC BỊA GIÂY HAY TIMECODE! Bạn CHỈ ĐƯỢC CHỌN các số nguyên trong khoảng 1 đến 40 đại diện cho `cau_index`.
    - Chỉ chọn câu thực sự bị ảnh hưởng trực tiếp, không mở rộng thành một dải câu lân cận chỉ vì chúng nằm gần nhau.
    - Với lỗi kỹ thuật thuần túy như nhạc nền, âm lượng, phụ đề lệch nhịp hoặc lỗi phát video: dùng `cau_index: []`, `loai_sua: "sửa phụ đề"` hoặc ghi chú chuyển kỹ thuật; không đề xuất thu lại lời hay dựng lại cảnh nếu quote không yêu cầu.
    - Với slide/chữ/hình ảnh, chỉ chọn các câu nói trong đúng cảnh bị ảnh hưởng; không mặc định chọn toàn bộ đoạn.
    - Mỗi cụm có quote_ids, cau_index, cau_trong_tam, loai_sua và de_xuat_sua; không được bỏ trống các trường này. Nếu không định vị được, đưa quote vào `gop_y_chung_chung` thay vì tạo cụm thiếu dữ liệu.
   - Mọi `quote_id` trong kết quả BẮT BUỘC phải nằm trong danh sách ID đầu vào (ví dụ: "gy-002", "gy-003"...). TUYỆT ĐỐI KHÔNG tự sáng tác ra quote_id!
   - Đếm đúng số người học độc lập (`so_nguoi`): Nếu cùng một người gửi nhiều góp ý cho cùng vấn đề, chỉ tính là 1 người.
    - Nếu vấn đề yêu cầu đổi lời câu N, phải ghi rõ phạm vi thu lại theo dây chuyền trong `chi_phi_chi_tiet.cau_thu_lai`: gồm đúng các câu hợp lệ trong {N-1, N, N+1}; không được để trống.
    - Nếu không đổi lời, `chi_phi_chi_tiet.cau_thu_lai` phải là `[]`.
4. ĐỀ XUẤT SỬA TỐI THIỂU (`de_xuat_sua`):
   - Đưa ra giải pháp sửa nhỏ gọn nhất có thể để không phải làm lại cả video.
   - Gán `loai_sua`: một trong các giá trị ["thu lời", "dựng hình", "thu lời + dựng", "sửa phụ đề"].
   - Gán màu UI gợi ý `ui_color`: ["violet", "blue", "green", "red"].

OUTPUT PHẢI LÀ JSON THUẦN TÚY (Pure JSON, không bọc ```json ``` hay bất kỳ văn bản giải thích nào ngoài JSON), tuân thủ định dạng sau:
{
  "cum_van_de": [
    {
      "cum_id": "cum-01",
      "tieu_de": "Tên ngắn gọn mô tả vấn đề",
      "loai_loi": "Nội dung" | "Sư phạm (tốc độ/giọng)" | "Kỹ thuật",
      "ui_color": "violet" | "blue" | "green" | "red",
      "so_nguoi": 3,
      "quote_ids": ["gy-002", "gy-003", "gy-018"],
      "cau_index": [20, 21, 22, 23],
      "cau_trong_tam": 22,
      "loai_sua": "thu lời + dựng" | "thu lời" | "dựng hình" | "sửa phụ đề",
      "de_xuat_sua": "Mô tả giải pháp sửa tối thiểu",
            "ghi_chu": "Giải thích thêm (ví dụ: mâu thuẫn 50-50, hoặc gộp từ 1 người gửi nhiều lần)",
            "chi_phi_chi_tiet": {
                "cau_thu_lai": [21, 22, 23],
                "so_ky_tu": 0,
                "so_canh": 0
            }
    }
  ],
  "gop_y_chung_chung": [
    {
      "quote_id": "gy-001",
      "noi_dung": "...",
      "ly_do_khong_dinh_vi": "Không đủ thông tin để chỉ ra câu/cảnh cụ thể"
    }
  ]
}
"""

def build_user_prompt(feedbacks: List[Dict[str, Any]], transcript: List[Dict[str, Any]]) -> str:
    """Tạo prompt đưa cho DeepSeek gồm danh sách feedback an toàn và danh sách câu kịch bản"""
    fb_text = "\n".join([
        f"- ID: {item.get('id')} | Người gửi: {item.get('nguoiGui')} | Kênh: {item.get('kenh')} | Nội dung: \"{item.get('noiDung')}\""
        for item in feedbacks
    ])
    
    script_text = "\n".join([
        f"Câu {item.get('cau')}: \"{item.get('loi')}\""
        for item in transcript
    ])
    
    return f"""DƯỚI ĐÂY LÀ DANH SÁCH 40 CÂU TRONG KỊCH BẢN VIDEO BÀI GIẢNG:
{script_text}

---
DƯỚI ĐÂY LÀ DANH SÁCH CÁC GÓP Ý ĐẦU VÀO ĐÃ QUA BỘ LỌC AN TOÀN:
{fb_text}

Hãy phân tích, gom cụm, phân loại lỗi và định vị câu theo đúng các nguyên tắc và định dạng JSON đã yêu cầu.
"""
