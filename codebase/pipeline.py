# -*- coding: utf-8 -*-
"""
FeedbackRadar — pipeline gom cụm góp ý bằng AI thật.
Người phụ trách: Nguyễn Hồ Nam (Dev · Agent Engineer)

Luồng 5 khâu:
  [1] Lọc nhiễu          — heuristic cứng, KHÔNG dùng AI
  [2] Gọi AI             — gom cụm + phân loại + định vị câu  <<< QUYẾT ĐỊNH TRUNG TÂM
  [3] Kiểm hậu kiểm      — vứt mọi quote_id / câu mà AI bịa ra
  [4] Map câu → timecode — tra bảng cứng, AI không được sinh giây
  [5] Tính phạm vi làm lại — phép cộng, có tính ảnh hưởng dây chuyền

Chạy:
    python codebase/pipeline.py
    python codebase/pipeline.py --input eval/fixtures/gop-y-100.json --limit 30
    python codebase/pipeline.py --dry-run     # không gọi API, xem prompt sẽ gửi
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

# Console Windows mặc định cp1252, không in được tiếng Việt — ép UTF-8.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config_prompt import SYSTEM_PROMPT, build_user_prompt  # noqa: E402

# Đường dẫn mặc định
TIMECODE_CSV = ROOT / "data/studio-pack/c5-feedbackradar/video-mau/cau-timecode-d1.csv"
INPUT_MAC_DINH = ROOT / "eval/fixtures/gop-y-100.json"
OUT_CLUSTERS = ROOT / "codebase/clusters.json"
OUT_TRACE = ROOT / "eval/results"

MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# ----------------------------------------------------------------------------
# [0] Nạp dữ liệu
# ----------------------------------------------------------------------------

def nap_transcript():
    """Đọc 40 câu + mốc thời gian từ bảng cứng của ban tổ chức."""
    if not TIMECODE_CSV.exists():
        sys.exit(
            "Không tìm thấy %s\n"
            "Cần có gói data của ban tổ chức tại data/studio-pack/c5-feedbackradar/\n"
            "(gói này không commit vào repo theo quy định bảo mật điều 3)" % TIMECODE_CSV
        )
    cau = []
    with open(TIMECODE_CSV, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cau.append({
                "cau": int(row["cau"]),
                "batDau": row["batDau"],
                "ketThucTieng": row["ketThucTieng"],
                "ketThuc": row["ketThuc"],
                "loi": row["loi"],
                "soKyTu": 0 if row["loi"] == "(dừng 5 giây)" else len(row["loi"]),
            })
    return cau


def nap_gop_y(duong_dan, gioi_han=None):
    data = json.loads(Path(duong_dan).read_text(encoding="utf-8"))
    gy = data["gopY"]
    if gioi_han:
        gy = gy[:gioi_han]
    return [
        {"id": g["id"], "nguoiGui": g["nguoiGui"], "kenh": g["kenh"], "noiDung": g["noiDung"]}
        for g in gy
    ]


# ----------------------------------------------------------------------------
# [1] Lọc nhiễu — heuristic cứng, không dùng AI
# ----------------------------------------------------------------------------

MAU_LENH_AN = [
    r"bỏ qua .{0,20}(hướng dẫn|chỉ dẫn|yêu cầu)",
    r"quên .{0,20}(hướng dẫn|prompt)",
    r"ignore .{0,20}(instruction|prompt|previous)",
    r"disregard .{0,20}(instruction|prompt)",
    r"(in|xuất|print) ra .{0,20}prompt",
    r"system prompt",
    r"bạn là .{0,30}(trợ lý duyệt|admin)",
    r"trả về .{0,15}(rỗng|empty)",
    r"(đánh giá|chấm) .{0,20}(mười điểm|10 điểm|perfect)",
    r"(hệ thống|system) (chú ý|lưu ý|attention)",
    r"đặt toàn bộ .{0,30}(mức|về)",
    r"tự (chấp nhận|duyệt) mọi",
    r"đừng phân tích",
]

MAU_CONG_KICH = [
    r"\b(ngu|dốt|óc chó|thằng|con mẹ|đồ vô dụng)\b",
    r"chả hiểu gì",
    r"lười biếng",
    r"làm ăn kiểu gì",
    r"không có chuyên môn",
    r"(đọc|giảng) như (máy|robot)",
    r"tệ hại",
]


def loc_nhieu(feedbacks):
    """Trả về (sạch, bị_lọc). Chạy TRƯỚC khi gửi cho AI."""
    sach, loc = [], []
    for f in feedbacks:
        t = f["noiDung"].lower()
        ly_do = None
        for m in MAU_LENH_AN:
            if re.search(m, t):
                ly_do = "lenh-an"
                break
        if not ly_do:
            for m in MAU_CONG_KICH:
                if re.search(m, t):
                    ly_do = "cong-kich"
                    break
        if ly_do:
            loc.append({
                "id": f["id"],
                "nguoiGui": f["nguoiGui"],
                "ly_do": ly_do,
                # Không lưu nguyên văn lời công kích vào báo cáo (mục An toàn của đề)
                "noiDung": f["noiDung"] if ly_do == "lenh-an" else "(đã ẩn — lời công kích cá nhân)",
            })
        else:
            sach.append(f)
    return sach, loc


# ----------------------------------------------------------------------------
# [2] Gọi AI — quyết định trung tâm
# ----------------------------------------------------------------------------

def goi_ai(feedbacks, transcript, thu_lai=3):
    """Gọi OpenAI, trả về (ket_qua_json, trace)."""
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("Chưa cài SDK. Chạy:  pip install openai python-dotenv")

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        sys.exit(
            "Chưa có OPENAI_API_KEY.\n"
            "  1. Copy codebase/.env.example thành codebase/.env\n"
            "  2. Điền key vào dòng OPENAI_API_KEY=\n"
            "  (.env đã nằm trong .gitignore, sẽ không bị commit)"
        )

    client = OpenAI(api_key=api_key)
    user_prompt = build_user_prompt(feedbacks, transcript)

    loi_cuoi = None
    for lan in range(1, thu_lai + 1):
        try:
            t0 = time.time()
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,
                response_format={"type": "json_object"},
            )
            giay = round(time.time() - t0, 2)
            raw = resp.choices[0].message.content
            trace = {
                "model": MODEL,
                "thoi_gian_giay": giay,
                "so_gop_y_gui": len(feedbacks),
                "tokens": {
                    "prompt": resp.usage.prompt_tokens,
                    "completion": resp.usage.completion_tokens,
                    "tong": resp.usage.total_tokens,
                },
                "system_prompt": SYSTEM_PROMPT,
                "user_prompt": user_prompt,
                "raw_response": raw,
            }
            return json.loads(raw), trace
        except Exception as e:  # noqa: BLE001
            loi_cuoi = e
            cho = 2 ** lan
            print("  ! Lần %d lỗi: %s — thử lại sau %ds" % (lan, e, cho))
            time.sleep(cho)
    sys.exit("Gọi AI thất bại sau %d lần: %s" % (thu_lai, loi_cuoi))


# ----------------------------------------------------------------------------
# [3] Hậu kiểm — vứt mọi thứ AI bịa
# ----------------------------------------------------------------------------

def hau_kiem(ket_qua, feedbacks, transcript):
    """Bỏ quote_id và sentence_index không có trong đầu vào. Trả về (cụm, vi_phạm)."""
    id_hop_le = {f["id"] for f in feedbacks}
    nguoi_cua = {f["id"]: f["nguoiGui"] for f in feedbacks}
    cau_hop_le = {c["cau"] for c in transcript}

    cum, vi_pham = [], []
    for c in ket_qua.get("van_de", []):
        qid = c.get("quote_ids") or []
        bia_q = [q for q in qid if q not in id_hop_le]
        sach_q = [q for q in qid if q in id_hop_le]

        si = c.get("sentence_indices") or []
        bia_s = [s for s in si if s not in cau_hop_le]
        sach_s = [s for s in si if s in cau_hop_le]

        if bia_q:
            vi_pham.append({"cluster_id": c.get("cluster_id"), "loai": "quote_id bịa", "gia_tri": bia_q})
        if bia_s:
            vi_pham.append({"cluster_id": c.get("cluster_id"), "loai": "sentence_index bịa", "gia_tri": bia_s})

        if not sach_q:
            continue  # cụm không còn quote thật nào -> vứt

        # Đếm lại số người độc lập bằng code, không tin số AI trả về
        nguoi = sorted({nguoi_cua[q] for q in sach_q})
        c["quote_ids"] = sach_q
        c["sentence_indices"] = sach_s
        c["nguoi_gui"] = nguoi
        c["so_nguoi_doc_lap"] = len(nguoi)
        c["muc_tin_cay"] = "cao" if len(nguoi) >= 2 else "thap"
        cum.append(c)

    return cum, vi_pham


# ----------------------------------------------------------------------------
# [4] Map câu → timecode (bảng cứng)
# [5] Tính phạm vi làm lại (phép cộng, có dây chuyền)
# ----------------------------------------------------------------------------

def day_chuyen(cau_doi_loi, tong_cau=40):
    """Đổi lời câu N ⇒ phải thu lại N-1, N, N+1 (bang-chi-phi-lam-lai.md)."""
    s = set()
    for c in cau_doi_loi:
        for x in (c - 1, c, c + 1):
            if 1 <= x <= tong_cau:
                s.add(x)
    return sorted(s)


LOAI_DOI_LOI = {"kho-hieu", "noi-dung-sai", "giong-doc", "nhip-nhanh-cham"}


def tinh_pham_vi(cum, transcript):
    ky_tu_cua = {c["cau"]: c["soKyTu"] for c in transcript}
    moc_cua = {c["cau"]: (c["batDau"], c["ketThuc"]) for c in transcript}
    tong_ky_tu = sum(c["soKyTu"] for c in transcript)

    for c in cum:
        si = c.get("sentence_indices") or []
        # [4] tra bảng cứng — AI không sinh giây
        c["timecode"] = [
            {"cau": n, "batDau": moc_cua[n][0], "ketThuc": moc_cua[n][1]} for n in si
        ]

        # [5] phạm vi làm lại
        et = c.get("error_type")
        if c.get("should_filter") or et in ("khen", "khong-dinh-vi-duoc", "nhieu-loc-bo"):
            thu_lai, canh = [], []
        elif et == "loi-ky-thuat":
            thu_lai, canh = [], []          # kỹ thuật: không đổi kịch bản
        elif et == "hinh-anh":
            thu_lai, canh = [], si          # đổi hình: giữ giọng, dựng lại cảnh
        elif c.get("tranh_chap"):
            thu_lai, canh = [], []          # tranh chấp: không sửa
        elif et in LOAI_DOI_LOI and si:
            thu_lai = day_chuyen(si)
            canh = thu_lai
        else:
            thu_lai, canh = [], si

        so_ky_tu = sum(ky_tu_cua.get(n, 0) for n in thu_lai)
        c["pham_vi_lam_lai"] = {
            "cau_thu_lai_giong": thu_lai,
            "canh_dung_lai": canh,
            "so_ky_tu": so_ky_tu,
            "so_canh": len(canh),
            "phan_tram_cong_thu": round(so_ky_tu / tong_ky_tu * 100, 1) if tong_ky_tu else 0,
        }
    return cum


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="FeedbackRadar pipeline")
    ap.add_argument("--input", default=str(INPUT_MAC_DINH))
    ap.add_argument("--limit", type=int, default=30, help="số góp ý gửi cho AI (mặc định 30)")
    ap.add_argument("--out", default=str(OUT_CLUSTERS))
    ap.add_argument("--dry-run", action="store_true", help="không gọi API, chỉ in prompt")
    args = ap.parse_args()

    # nạp .env nếu có
    env = Path(__file__).resolve().parent / ".env"
    if env.exists():
        for dong in env.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if dong and not dong.startswith("#") and "=" in dong:
                k, v = dong.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    print("FeedbackRadar — pipeline gom cụm góp ý")
    print("=" * 52)

    transcript = nap_transcript()
    feedbacks = nap_gop_y(args.input, args.limit)
    print("Nạp %d câu kịch bản, %d góp ý" % (len(transcript), len(feedbacks)))

    # [1]
    sach, loc = loc_nhieu(feedbacks)
    print("\n[1/5] Lọc nhiễu (heuristic, không AI)")
    print("      %d góp ý sạch | %d bị lọc" % (len(sach), len(loc)))
    for l in loc:
        print("      - %s (%s)" % (l["id"], l["ly_do"]))

    if args.dry_run:
        print("\n--- DRY RUN: prompt sẽ gửi ---")
        print(build_user_prompt(sach, transcript)[:1500] + "\n...")
        return

    # [2]
    print("\n[2/5] Gọi AI — gom cụm + phân loại + định vị câu")
    ket_qua, trace = goi_ai(sach, transcript)
    print("      model=%s | %.2fs | %d tokens"
          % (trace["model"], trace["thoi_gian_giay"], trace["tokens"]["tong"]))

    # [3]
    cum, vi_pham = hau_kiem(ket_qua, sach, transcript)
    print("\n[3/5] Hậu kiểm chống bịa")
    print("      %d cụm hợp lệ | %d vi phạm bị vứt" % (len(cum), len(vi_pham)))
    for v in vi_pham:
        print("      ! %s: %s %s" % (v["cluster_id"], v["loai"], v["gia_tri"]))

    # [4][5]
    cum = tinh_pham_vi(cum, transcript)
    print("\n[4/5] Map câu → timecode bằng bảng cứng ✓")
    print("[5/5] Tính phạm vi làm lại (có ảnh hưởng dây chuyền) ✓")

    out = {
        "_ghiChu": "Sinh bởi codebase/pipeline.py — khâu gom cụm/phân loại/định vị do AI thật quyết định; timecode tra bảng cứng, chi phí do code cộng.",
        "model": trace["model"],
        "input": {
            "file": str(Path(args.input).relative_to(ROOT)) if str(args.input).startswith(str(ROOT)) else args.input,
            "so_gop_y": len(feedbacks),
            "so_cau": len(transcript),
        },
        "loc_bo": loc,
        "vi_pham_bia_nguon": vi_pham,
        "van_de": cum,
    }
    Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    OUT_TRACE.mkdir(parents=True, exist_ok=True)
    ten = "trace-%s.json" % time.strftime("%Y%m%d-%H%M%S")
    (OUT_TRACE / ten).write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 52)
    print("Đã ghi %s" % Path(args.out).name)
    print("Trace AI: eval/results/%s" % ten)
    print("\nKẾT QUẢ — %d vấn đề:" % len(cum))
    for c in cum:
        pv = c["pham_vi_lam_lai"]
        print("  [%s] %s" % (c.get("error_type"), (c.get("summary") or "")[:60]))
        print("       %d người · câu %s · %d ký tự · %d cảnh"
              % (c.get("so_nguoi_doc_lap", 0), c.get("sentence_indices") or "-",
                 pv["so_ky_tu"], pv["so_canh"]))


if __name__ == "__main__":
    main()
