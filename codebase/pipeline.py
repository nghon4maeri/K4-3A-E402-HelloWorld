"""
FeedbackRadar AI Pipeline
Author: Nguyen Ho Nam (Dev / Agent Engineer - Batch 04 · Room E402)
Features:
  1. Heuristic Safety Screening (Regex Prompt Injection & Personal Attack Filter)
    2. DeepSeek AI Call (Structured JSON Output via OpenAI-compatible SDK)
  3. Anti-Hallucination Guardrails (Quote verification & Static Sentence Index)
  4. Static Timecode Mapping (Hard-coded lookup from fixture, strictly no AI-hallucinated timestamps)
  5. Minimal Rework Cost Calculation (Chain effect on adjacent sentences)
  6. Output Export for Web UI (clusters.json & safety_log.json)
"""

import os
import sys
import json
import math
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Đảm bảo in tiếng Việt Unicode mượt mà trên Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Load prompt configuration & rules
from config_prompt import (
    SYSTEM_PROMPT,
    TONG_KY_TU_CA_VIDEO,
    TONG_CANH_CA_VIDEO,
    DAY_CHUYEN,
    filter_feedbacks,
    build_user_prompt
)

BASE_DIR = Path(__file__).resolve().parent

# Load the project-local environment file regardless of the terminal cwd.
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

DATA_DIR = BASE_DIR / "data"

TRANSCRIPT_PATH = DATA_DIR / "transcript-timecode.json"
SAMPLE_FEEDBACK_PATH = DATA_DIR / "sample-feedback.json"
CLUSTERS_OUTPUT_PATH = BASE_DIR / "clusters.json"
SAFETY_LOG_PATH = BASE_DIR / "safety_log.json"


def load_inputs():
    """Tải kịch bản 40 câu có timecode và danh sách 30 góp ý đầu vào"""
    if not TRANSCRIPT_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {TRANSCRIPT_PATH}")
    if not SAMPLE_FEEDBACK_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {SAMPLE_FEEDBACK_PATH}")
        
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        transcript = json.load(f)
        
    with open(SAMPLE_FEEDBACK_PATH, "r", encoding="utf-8") as f:
        fb_data = json.load(f)
        feedbacks = fb_data.get("gopY", [])
        
    return transcript, feedbacks


# Ghi lại nguồn của kết quả lần chạy gần nhất — để clusters.json và UI
# nói đúng sự thật là kết quả do AI sinh hay do dữ liệu dựng sẵn.
LAST_RUN = {"nguon": None, "model": None, "so_giay": None, "tokens": None,
            "chi_phi_usd": None, "ly_do_fallback": None}
PROCESS_BUDGET_USED_USD = 0.0


def estimate_request_cost(user_content: str, max_output_tokens: int) -> float:
    """Ước tính bảo thủ chi phí request để không vượt ngân sách process."""
    input_tokens = math.ceil((len(SYSTEM_PROMPT) + len(user_content)) / 4)
    input_price = float(os.environ.get("DEEPSEEK_INPUT_PRICE_USD_PER_MILLION", "0.28"))
    output_price = float(os.environ.get("DEEPSEEK_OUTPUT_PRICE_USD_PER_MILLION", "0.42"))
    return (input_tokens * input_price + max_output_tokens * output_price) / 1_000_000


def run_deepseek_call(safe_feedbacks: List[Dict[str, Any]], transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Gọi DeepSeek API để gom cụm và định vị câu — ĐÂY LÀ QUYẾT ĐỊNH TRUNG TÂM.

    Nếu không có key hoặc API lỗi, trả về bộ dữ liệu DỰNG SẴN để luồng không gãy
    khi test offline. Bộ dựng sẵn KHÔNG phải kết quả AI — mọi đầu ra đều được
    đánh dấu nguon="fallback-dung-san" để không ai nhầm.
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    model_name = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat").strip()
    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").strip()
    max_budget_usd = float(os.environ.get("DEEPSEEK_MAX_BUDGET_USD", "0.5"))
    max_output_tokens = int(os.environ.get("DEEPSEEK_MAX_OUTPUT_TOKENS", "2048"))
    request_timeout = float(os.environ.get("DEEPSEEK_REQUEST_TIMEOUT_SECONDS", "45"))

    if not api_key:
        LAST_RUN.update(nguon="fallback-dung-san", model=None,
                        ly_do_fallback="Chưa điền DEEPSEEK_API_KEY trong codebase/.env")
        canh_bao_fallback("Chưa điền DEEPSEEK_API_KEY trong codebase/.env")
        return run_fallback_engine(safe_feedbacks, transcript)

    print(f"[*] Khởi tạo kết nối DeepSeek với model: {model_name}...")
    user_content = build_user_prompt(safe_feedbacks, transcript)
    estimated_cost = estimate_request_cost(user_content, max_output_tokens)

    loi_cuoi = None
    for lan in range(1, 4):
        global PROCESS_BUDGET_USED_USD
        if PROCESS_BUDGET_USED_USD + estimated_cost > max_budget_usd:
            loi_cuoi = (f"Ngân sách process {max_budget_usd:.2f} USD không đủ cho "
                        f"request tiếp theo (ước tính {estimated_cost:.4f} USD)")
            break
        PROCESS_BUDGET_USED_USD += estimated_cost
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url,
                            timeout=request_timeout, max_retries=0)

            t0 = time.time()
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=max_output_tokens,
            )
            so_giay = round(time.time() - t0, 2)

            raw_text = (response.choices[0].message.content or "").strip()
            # Loại bỏ markdown fence nếu model có bọc lại
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            result = json.loads(raw_text.strip())

            tokens = None
            try:
                um = response.usage
                tokens = {
                    "prompt": um.prompt_tokens,
                    "completion": um.completion_tokens,
                    "tong": um.total_tokens,
                }
            except Exception:
                pass

            LAST_RUN.update(nguon="ai-that", model=model_name, so_giay=so_giay,
                            tokens=tokens, chi_phi_usd=round(estimated_cost, 6),
                            ly_do_fallback=None)

            print(f"[✓] Gọi DeepSeek THÀNH CÔNG — model={model_name} · {so_giay}s"
                f" · ước tính ${estimated_cost:.4f}"
                  + (f" · {tokens['tong']} tokens" if tokens else ""))

            # Lưu trace để chứng minh AI chạy thật (bằng chứng cho CP3)
            luu_trace(model_name, so_giay, tokens, user_content, raw_text, len(safe_feedbacks))
            return result

        except Exception as e:
            loi_cuoi = e
            if lan < 3:
                cho = 2 ** lan
                print(f"[!] Lần {lan} lỗi: {e}")
                print(f"    Thử lại sau {cho}s...")
                time.sleep(cho)

    LAST_RUN.update(nguon="fallback-dung-san", model=None, chi_phi_usd=None,
                    ly_do_fallback=f"Gọi DeepSeek lỗi sau 3 lần: {loi_cuoi}")
    canh_bao_fallback(f"Gọi DeepSeek lỗi sau 3 lần: {loi_cuoi}")
    return run_fallback_engine(safe_feedbacks, transcript)


def run_gemini_call(safe_feedbacks: List[Dict[str, Any]], transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Tên tương thích ngược cho evaluator và các script cũ."""
    return run_deepseek_call(safe_feedbacks, transcript)


def canh_bao_fallback(ly_do: str):
    """In cảnh báo to, không thể bỏ qua, khi kết quả KHÔNG phải do AI sinh."""
    print("")
    print("!" * 65)
    print("!!  CẢNH BÁO: KẾT QUẢ DƯỚI ĐÂY KHÔNG PHẢI DO AI SINH RA")
    print("!!")
    print(f"!!  Lý do: {ly_do}")
    print("!!")
    print("!!  Đang dùng bộ dữ liệu DỰNG SẴN trong run_fallback_engine().")
    print("!!  Chỉ để kiểm thử luồng khi offline.")
    print("!!  KHÔNG dùng lần chạy này để quay video CP3 hay ghi vào bảng đo.")
    print("!!")
    print("!!  Cách chạy AI thật:")
    print("!!    1. Lấy key tại: https://platform.deepseek.com/api_keys")
    print("!!    2. Dán vào dòng DEEPSEEK_API_KEY= trong codebase/.env")
    print("!!    3. Chạy lại lệnh này")
    print("!" * 65)
    print("")


def luu_trace(model_name, so_giay, tokens, user_content, raw_text, so_gop_y):
    """Ghi lại prompt + response thật để làm bằng chứng AI đã chạy."""
    try:
        thu_muc = BASE_DIR.parent / "eval" / "results"
        thu_muc.mkdir(parents=True, exist_ok=True)
        ten = "trace-%s.json" % time.strftime("%Y%m%d-%H%M%S")
        (thu_muc / ten).write_text(json.dumps({
            "nguon": "ai-that",
            "model": model_name,
            "thoi_diem": time.strftime("%Y-%m-%d %H:%M:%S"),
            "thoi_gian_giay": so_giay,
            "tokens": tokens,
            "so_gop_y_gui": so_gop_y,
            "system_prompt": SYSTEM_PROMPT,
            "user_prompt": user_content,
            "raw_response": raw_text,
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[✓] Đã lưu bằng chứng AI: eval/results/{ten}")
    except Exception as e:
        print(f"[!] Không lưu được trace: {e}")


def run_fallback_engine(safe_feedbacks: List[Dict[str, Any]], transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bộ suy luận ngữ nghĩa cục bộ dùng quy tắc đối chiếu từ khoá kịch bản,
    đáp ứng đúng chuẩn đầu ra của Gemini khi offline hoặc chưa nạp key.
    """
    clusters = [
        {
            "cum_id": "cum-01",
            "tieu_de": "Phân biệt app trò chuyện và mô hình ngôn ngữ lớn chưa rõ ràng",
            "loai_loi": "Nội dung",
            "ui_color": "blue",
            "so_nguoi": 3,
            "quote_ids": ["gy-002", "gy-003", "gy-018", "ns-001"],
            "cau_index": [20, 21, 22, 23],
            "cau_trong_tam": 22,
            "loai_sua": "thu lời + dựng",
            "de_xuat_sua": "Thu lại lời câu 22 (nói rõ ứng dụng là vỏ ngoài, model là lõi xử lý bên trong) + dựng lại hình ảnh 2 lớp lồng nhau.",
            "ghi_chu": "gy-002, gy-003, gy-018 từ cùng 1 học viên hv-011 (tính 1 người), cộng thêm hv-080 -> 2-3 người độc lập."
        },
        {
            "cum_id": "cum-02",
            "tieu_de": "Âm thanh phút thứ 2 bị nhạc nền át tiếng giảng viên",
            "loai_loi": "Kỹ thuật",
            "ui_color": "green",
            "so_nguoi": 2,
            "quote_ids": ["gy-008", "ns-004"],
            "cau_index": [20],
            "cau_trong_tam": 20,
            "loai_sua": "thu lời",
            "de_xuat_sua": "Cân bằng lại âm lượng (gain reduction nhạc nền -6dB tại mốc 02:00 hoặc thu lại âm câu 20 chuẩn -16 LUFS).",
            "ghi_chu": "Lỗi kỹ thuật thuần tuý về mix âm thanh, không phải lỗi kịch bản."
        },
        {
            "cum_id": "cum-03",
            "tieu_de": "Slide minh hoạ 3 thẻ ứng dụng chữ quá nhỏ trên thiết bị di động",
            "loai_loi": "Kỹ thuật",
            "ui_color": "violet",
            "so_nguoi": 2,
            "quote_ids": ["gy-010", "ns-003"],
            "cau_index": [24, 25, 26, 27, 28, 29],
            "cau_trong_tam": 24,
            "loai_sua": "dựng hình",
            "de_xuat_sua": "Phóng to font chữ trên 3 thẻ và căn chỉnh bố cục dạng thẻ dọc để hiển thị sắc nét trên màn hình điện thoại.",
            "ghi_chu": "Chỉ đổi thiết kế đồ hoạ cảnh, hoàn toàn không cần thu lại giọng đọc."
        },
        {
            "cum_id": "cum-04",
            "tieu_de": "Khoảng dừng suy nghĩ 5 giây gây ý kiến trái chiều (ngắn vs dài)",
            "loai_loi": "Sư phạm (tốc độ/giọng)",
            "ui_color": "red",
            "so_nguoi": 3,
            "quote_ids": ["gy-005", "gy-006", "ns-010"],
            "cau_index": [35],
            "cau_trong_tam": 35,
            "loai_sua": "dựng hình",
            "de_xuat_sua": "Thêm thanh đếm ngược tiến trình (progress timer 5s) và dòng nhắc 'Tạm dừng video nếu bạn cần thêm thời gian'.",
            "ghi_chu": "Mâu thuẫn sư phạm 50/50: 1 người bảo ngắn, 1 người bảo dài, 1 người bảo vừa. Không thay đổi độ dài, chỉ thêm visual cue."
        },
        {
            "cum_id": "cum-05",
            "tieu_de": "Câu chốt kết thúc video hơi đột ngột, thiếu câu dẫn nối",
            "loai_loi": "Nội dung",
            "ui_color": "blue",
            "so_nguoi": 2,
            "quote_ids": ["gy-016", "ns-006"],
            "cau_index": [40],
            "cau_trong_tam": 40,
            "loai_sua": "thu lời",
            "de_xuat_sua": "Thu lại câu 40 bổ sung lời chào kết và giới thiệu chủ đề tập tiếp theo.",
            "ghi_chu": "Được góp ý bởi giảng viên gv-01 và học viên hv-092."
        },
        {
            "cum_id": "cum-06",
            "tieu_de": "Phụ đề chạy nhanh hoặc lệch nhịp so với lời đọc của video",
            "loai_loi": "Kỹ thuật",
            "ui_color": "violet",
            "so_nguoi": 2,
            "quote_ids": ["gy-017", "ns-005"],
            "cau_index": [18, 19],
            "cau_trong_tam": 18,
            "loai_sua": "sửa phụ đề",
            "de_xuat_sua": "Chỉnh lại timestamp hiển thị phụ đề cho câu 18 và 19 khớp chính xác với âm thanh voiceover.",
            "ghi_chu": "Chỉ chỉnh lại file phụ đề SRT/VTT, không tốn chi phí quay dựng hay thu âm."
        },
        {
            "cum_id": "cum-07",
            "tieu_de": "Định nghĩa AI tạo sinh nhồi 3 ví dụ văn bản hình ảnh âm thanh trong cùng một câu",
            "loai_loi": "Nội dung",
            "ui_color": "blue",
            "so_nguoi": 2,
            "quote_ids": ["gy-007", "ns-002"],
            "cau_index": [14],
            "cau_trong_tam": 14,
            "loai_sua": "thu lời",
            "de_xuat_sua": "Tách câu 14 thành 2 câu ngắn: nêu định nghĩa trước, sau đó liệt kê từng ví dụ kèm minh họa trực quan.",
            "ghi_chu": "Trợ giảng tg-02 phản ánh sinh viên hay bị trôi mất ý ở câu này."
        },
        {
            "cum_id": "cum-08",
            "tieu_de": "Mô hình học máy bên trong bộ lọc thư rác cần làm rõ và thêm ví dụ",
            "loai_loi": "Nội dung",
            "ui_color": "blue",
            "so_nguoi": 2,
            "quote_ids": ["gy-015", "ns-011"],
            "cau_index": [10],
            "cau_trong_tam": 10,
            "loai_sua": "thu lời",
            "de_xuat_sua": "Thu lại câu 10 nhấn mạnh khái niệm 'mô hình' và bổ sung ví dụ minh họa trực quan.",
            "ghi_chu": "Học viên phản ánh phải nghe lại 3 lần mới hiểu."
        },
        {
            "cum_id": "cum-09",
            "tieu_de": "Điểm sáng bài giảng được người học đánh giá cao (Khuyến nghị giữ nguyên)",
            "loai_loi": "Nội dung",
            "ui_color": "green",
            "so_nguoi": 2,
            "quote_ids": ["gy-004", "gy-014"],
            "cau_index": [1, 2, 31],
            "cau_trong_tam": 1,
            "loai_sua": "giữ nguyên",
            "de_xuat_sua": "Giữ nguyên đoạn mở đầu (câu 1-2) và ví dụ chuyển đổi công việc (câu 31) vì người học hiểu rất sâu.",
            "ghi_chu": "Phản hồi tích cực, không phát sinh chi phí sửa."
        }
    ]
    
    unlocatable = [
        {
            "quote_id": "gy-001",
            "noi_dung": "Đoạn giữa hơi nhanh, em không kịp ghi.",
            "ly_do_khong_dinh_vi": "Góp ý chung chung, không có mốc thời gian hoặc từ khóa nhận diện câu"
        },
        {
            "quote_id": "gy-009",
            "noi_dung": "Video hay ạ.",
            "ly_do_khong_dinh_vi": "Khen ngợi chung chung, không có yêu cầu điều chỉnh kịch bản"
        },
        {
            "quote_id": "ns-009",
            "noi_dung": "Video nhìn chung rất trực quan và dễ hiểu, em cảm ơn thầy cô.",
            "ly_do_khong_dinh_vi": "Đánh giá tích cực tổng thể, không chỉ ra vị trí cần sửa"
        },
        {
            "quote_id": "ns-012",
            "noi_dung": "Đoạn giữa clip xem thấy mông lung quá chả hiểu gì.",
            "ly_do_khong_dinh_vi": "Cảm nhận chủ quan, không định vị được phân đoạn lỗi"
        }
    ]
    
    return {
        "cum_van_de": clusters,
        "gop_y_chung_chung": unlocatable
    }


def calculate_cluster_cost(cau_indices: List[int], loai_sua: str, transcript_map: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tính phạm vi phải làm lại cho một cụm vấn đề.

    ĐƠN VỊ: số ký tự phải thu lại giọng + số cảnh phải dựng lại.
    Ban tổ chức KHÔNG cấp đơn giá tiền (xem bang-chi-phi-lam-lai.md), nên ở đây
    không quy ra tiền — đo bằng đúng hai đại lượng mà đề cấp.

    Quy tắc:
    - Đổi lời  : thu lại câu N và cả N-1, N+1 (ảnh hưởng dây chuyền) + dựng lại
                 đúng những cảnh đó.
    - Đổi hình : 0 ký tự (giữ nguyên giọng đã thu), chỉ dựng lại cảnh.
    - Phụ đề   : 0 ký tự, 0 cảnh — chỉ chỉnh file phụ đề, không đụng kịch bản.
    - Giữ nguyên / lỗi kỹ thuật thuần: không phát sinh gì.
    """
    rong = {"so_ky_tu": 0, "so_canh": 0, "cau_thu_lai": [], "cau_dung_lai": [],
            "phan_tram_cong_thu": 0.0}

    if "giữ nguyên" in loai_sua:
        return rong

    cau_set = {int(c) for c in cau_indices if 1 <= int(c) <= TONG_CANH_CA_VIDEO}
    cau_thu_lai, cau_dung_lai = set(), set()

    is_voice = "thu lời" in loai_sua
    is_visual = "dựng" in loai_sua
    is_sub = "phụ đề" in loai_sua

    if is_sub:
        # Chỉnh timecode phụ đề: không thu lại giọng, không dựng lại cảnh.
        return rong

    if is_voice:
        for c in cau_set:
            for x in (c - DAY_CHUYEN, c, c + DAY_CHUYEN):
                if 1 <= x <= TONG_CANH_CA_VIDEO:
                    cau_thu_lai.add(x)
        cau_dung_lai.update(cau_thu_lai)  # thu lại lời kéo theo dựng lại cho khớp giọng
    elif is_visual:
        cau_dung_lai.update(cau_set)      # đổi hình: giữ giọng, chỉ dựng lại cảnh

    # Số ký tự lấy từ transcript thật, không ước lượng
    so_ky_tu = 0
    for c in cau_thu_lai:
        item = transcript_map.get(c) or {}
        loi = item.get("loi", "")
        so_ky_tu += 0 if loi.strip() == "(dừng 5 giây)" else len(loi)

    return {
        "so_ky_tu": so_ky_tu,
        "so_canh": len(cau_dung_lai),
        "cau_thu_lai": sorted(cau_thu_lai),
        "cau_dung_lai": sorted(cau_dung_lai),
        "phan_tram_cong_thu": round(so_ky_tu / TONG_KY_TU_CA_VIDEO * 100, 1),
    }


def build_final_clusters(ai_output: Dict[str, Any], feedbacks: List[Dict[str, Any]], transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Hậu xử lý kết hợp bảng timecode cứng và dữ liệu feedback:
    1. Kiểm tra 100% quote_id hợp lệ (chống bịa nguồn)
    2. Map câu_index sang mốc thời gian thực từ transcript-timecode.json
    3. Tính toán chi phí chính xác
    4. Định dạng chuẩn để UI index.html hiển thị trực tiếp
    """
    fb_map = {item["id"]: item for item in feedbacks}
    tr_map = {item["cau"]: item for item in transcript}
    
    raw_clusters = ai_output.get("cum_van_de", [])
    final_clusters = []
    
    for idx, c in enumerate(raw_clusters, start=1):
        # 1. Chống bịa quote_id: Chỉ giữ lại các ID có thật trong input
        raw_quotes = c.get("quote_ids", [])
        valid_quotes = [q for q in raw_quotes if q in fb_map]
        
        quote_objs = []
        for qid in valid_quotes:
            fb = fb_map[qid]
            quote_objs.append({
                "id": qid,
                "t": f'"{fb.get("noiDung")}"',
                "src": f'{qid} · {fb.get("kenh")} · {fb.get("nguoiGui")}'
            })
            
        # 2. Xử lý câu_index & Map bảng cứng Timecode
        raw_cau = c.get("cau_index", [])
        cau_list = sorted([int(x) for x in raw_cau if isinstance(x, (int, str)) and str(x).isdigit() and 1 <= int(x) <= 40])
        
        if cau_list:
            start_cau = cau_list[0]
            end_cau = cau_list[-1]
            start_time = tr_map.get(start_cau, {}).get("batDau", "00:00")
            # Định dạng mm:ss
            v_time = start_time.split(".")[0] if "." in start_time else start_time
            if len(cau_list) == 1:
                cau_str = f"Câu {start_cau}"
            else:
                cau_str = f"Câu {start_cau}–{end_cau}"
        else:
            v_time = "00:00"
            cau_str = "Chung chung"
            
        # 3. Trích xuất trích đoạn transcript kèm đánh dấu câu trọng tâm
        cau_trong_tam = c.get("cau_trong_tam", cau_list[0] if cau_list else 1)
        transcript_snippet = []
        for cn in cau_list:
            if cn in tr_map:
                transcript_snippet.append({
                    "n": cn,
                    "t": tr_map[cn]["loi"],
                    "bad": (cn == cau_trong_tam)
                })
                
        # 4. Tính phạm vi làm lại
        # Sửa sau lượt đo 1-2 (failure "day_chuyen"): dây chuyền phải tính trên
        # CÂU THẬT SỰ ĐỔI LỜI, không phải trên cả cụm. AI thường trả cau_index
        # rộng (cả đoạn liên quan) nhưng chỉ cau_trong_tam mới là câu cần sửa lời.
        # Tính trên cả cụm làm phạm vi bị thổi lên: 269 -> 563 ký tự ở case-14.
        # Chỉ thu hẹp khi ĐỔI LỜI. Đổi hình thì vẫn phải dựng lại cả cụm cảnh,
        # vì lỗi hình ảnh trải trên toàn đoạn (ví dụ chữ nhỏ ở cả 3 thẻ).
        loai_sua_c = c.get("loai_sua", "thu lời")
        if "thu lời" in loai_sua_c and cau_trong_tam and cau_trong_tam in cau_list:
            cau_tinh = [cau_trong_tam]
        else:
            cau_tinh = cau_list
        cost_info = calculate_cluster_cost(cau_tinh, loai_sua_c, tr_map)
        
        # 5. UI Item
        final_clusters.append({
            "idx": idx,
            "cum_id": c.get("cum_id", f"cum-{idx:02d}"),
            "color": c.get("ui_color", "blue"),
            "title": c.get("tieu_de", "Vấn đề cần xử lý"),
            "loai": c.get("loai_loi", "Nội dung"),
            "so": f"{c.get('so_nguoi', len(valid_quotes))} người học",
            "v": v_time,
            "cau": cau_str,
            "chat": f"{c.get('so_nguoi', len(valid_quotes))} học viên độc lập",
            "kyTu": cost_info["so_ky_tu"],
            "canh": cost_info["so_canh"],
            "phanTramCongThu": cost_info["phan_tram_cong_thu"],
            "type": c.get("loai_sua", "thu lời"),
            "quotes": quote_objs,
            "transcript": transcript_snippet,
            "fix": c.get("de_xuat_sua", ""),
            "cau_indices": cau_list,
            "thuLai": cost_info["cau_thu_lai"],
            "cau_thu_lai": cost_info["cau_thu_lai"],
            "cau_dung_lai": cost_info["cau_dung_lai"],
            "ghi_chu": c.get("ghi_chu", "")
        })
        
    return final_clusters


def run_pipeline():
    """Hàm chạy chính của toàn bộ Pipeline"""
    print("=" * 65)
    print("  FEEDBACKRADAR AI PIPELINE — NHÓM HELLOWORLD (E402 · BATCH 04)")
    print("  Dev / Agent Engineer: Nguyễn Hồ Nam")
    print("=" * 65)
    
    start_time = time.time()
    
    # Bước 1: Đọc dữ liệu đầu vào
    print("\n[Bước 1/5] Đang đọc transcript 40 câu và 30 góp ý mẫu...")
    transcript, all_feedbacks = load_inputs()
    print(f" -> Đã nạp {len(transcript)} câu kịch bản có timecode.")
    print(f" -> Đã nạp {len(all_feedbacks)} góp ý của người học.")
    
    # Bước 2: Lọc nhiễu Heuristic (Safety & Injection Screening)
    print("\n[Bước 2/5] Thực hiện tiền xử lý & kiểm tra an toàn Heuristic...")
    safe_feedbacks, safety_log = filter_feedbacks(all_feedbacks)
    print(f" -> Số góp ý an toàn đưa vào phân tích: {len(safe_feedbacks)}/{len(all_feedbacks)}")
    print(f" -> Số góp ý bị loại bỏ (Safety Filter): {len(safety_log)}")
    for bad in safety_log:
        print(f"    [Lọc] {bad['id']} ({bad['nguoiGui']}): {bad['lyDo']} -> \"{bad['noiDung'][:45]}...\"")
        
    # Lưu safety_log.json
    with open(SAFETY_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(safety_log, f, ensure_ascii=False, indent=2)
    print(f" -> Đã ghi log an toàn vào: {SAFETY_LOG_PATH.name}")

    # Bước 3: Gọi AI DeepSeek (hoặc Fallback Engine)
    print("\n[Bước 3/5] Kích hoạt Agent AI phân tích ngữ nghĩa, gom cụm và phân loại...")
    ai_raw_output = run_deepseek_call(safe_feedbacks, transcript)
    
    # Bước 4: Chống hallucination, map timecode cứng và tính chi phí
    print("\n[Bước 4/5] Áp dụng Guardrails, đối chiếu timecode cứng và tính chi phí tối thiểu...")
    final_clusters = build_final_clusters(ai_raw_output, all_feedbacks, transcript)
    
    # Tính tổng ngân sách
    # Tổng phạm vi làm lại — đo bằng ký tự thu lại giọng và số cảnh dựng lại,
    # đặt cạnh con số làm lại toàn bộ (3 637 ký tự / 40 cảnh) như đề yêu cầu.
    tong_ky_tu = sum(c["kyTu"] for c in final_clusters)
    tong_canh = sum(c["canh"] for c in final_clusters)
    phan_tram_cong_thu = round(tong_ky_tu / TONG_KY_TU_CA_VIDEO * 100, 1)
    tiet_kiem_pct = round(100 - phan_tram_cong_thu, 1)

    # Đóng gói xuất bản
    la_ai_that = LAST_RUN.get("nguon") == "ai-that"
    pipeline_result = {
        # Trường này nói rõ kết quả do đâu mà có — UI và người chấm đọc trường này.
        "nguon_ket_qua": {
            "loai": LAST_RUN.get("nguon") or "khong-xac-dinh",
            "la_ai_that": la_ai_that,
            "model": LAST_RUN.get("model"),
            "thoi_gian_goi_giay": LAST_RUN.get("so_giay"),
            "tokens": LAST_RUN.get("tokens"),
            "chi_phi_uoc_tinh_usd": LAST_RUN.get("chi_phi_usd"),
            "ly_do_fallback": LAST_RUN.get("ly_do_fallback"),
            "_ghiChu": (
                "Khâu gom cụm + phân loại + định vị câu do AI thật quyết định."
                if la_ai_that else
                "KHÔNG PHẢI KẾT QUẢ AI — dữ liệu dựng sẵn trong run_fallback_engine(), "
                "chỉ dùng để kiểm thử luồng khi offline."
            ),
        },
        "metadata": {
            "kichBanId": "d1",
            "tongSoGopY": len(all_feedbacks),
            "soGopYHopLe": len(safe_feedbacks),
            "soGopYBiChieuLoc": len(safety_log),
            "soCumPhatHien": len(final_clusters),
            "phamViLamLai": {
                "soKyTuThuLai": tong_ky_tu,
                "soCanhDungLai": tong_canh,
                "phanTramCongThu": phan_tram_cong_thu,
                "tietKiemPhanTram": tiet_kiem_pct,
                "_donVi": "ký tự thu lại giọng + số cảnh dựng lại — ban tổ chức không cấp đơn giá tiền",
            },
            "toanBoVideo": {"soKyTu": TONG_KY_TU_CA_VIDEO, "soCanh": TONG_CANH_CA_VIDEO},
            "thoiGianChayGiay": round(time.time() - start_time, 2)
        },
        "clusters": final_clusters,
        "gop_y_chung_chung": ai_raw_output.get("gop_y_chung_chung", [])
    }
    
    # Bước 5: Ghi file clusters.json
    print("\n[Bước 5/5] Xuất kết quả hoàn tất ra clusters.json...")
    with open(CLUSTERS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(pipeline_result, f, ensure_ascii=False, indent=2)
        
    print(f" -> Đã ghi thành công file: {CLUSTERS_OUTPUT_PATH.name}")
    print("\n" + "=" * 65)
    if la_ai_that:
        tk = LAST_RUN.get("tokens")
        print(f"  NGUỒN KẾT QUẢ: AI THẬT — model={LAST_RUN.get('model')}"
              f" · {LAST_RUN.get('so_giay')}s"
              + (f" · {tk['tong']} tokens" if tk else ""))
    else:
        print("  NGUỒN KẾT QUẢ: *** DỮ LIỆU DỰNG SẴN, KHÔNG PHẢI AI ***")
        print(f"  Lý do: {LAST_RUN.get('ly_do_fallback')}")
    print("=" * 65)
    print("  KẾT QUẢ PHÂN TÍCH TỔNG HỢP:")
    print(f"  • Số cụm vấn đề xác định: {len(final_clusters)}")
    for c in final_clusters:
        print(f"    [{c['idx']}] {c['title']} ({c['loai']}) - {c['cau']} [{c['v']}]"
              f" - {c['kyTu']} ký tự · {c['canh']} cảnh")
    print(f"  • Tổng phạm vi làm lại: {tong_ky_tu} ký tự · {tong_canh} cảnh")
    print(f"  • So với làm lại toàn bộ ({TONG_KY_TU_CA_VIDEO} ký tự / {TONG_CANH_CA_VIDEO} cảnh):"
          f" chỉ {phan_tram_cong_thu}% công thu giọng — tiết kiệm {tiet_kiem_pct}%")
    print("=" * 65)


if __name__ == "__main__":
    run_pipeline()

    # --require-ai: thoát với mã lỗi nếu lần chạy này KHÔNG dùng AI thật.
    # Dùng khi quay video CP3 hoặc chạy đo, để không vô tình lấy kết quả dựng sẵn.
    if "--require-ai" in sys.argv and LAST_RUN.get("nguon") != "ai-that":
        print("\n[X] --require-ai: lần chạy này KHÔNG gọi được AI thật. Dừng.")
        sys.exit(1)
