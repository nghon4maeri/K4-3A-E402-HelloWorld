"""
Evaluation Benchmark Runner for FeedbackRadar (CP3)
Author: Nguyen Ho Nam (Dev / Agent Engineer) & Nguyen Canh Duy (Lead)

Chạy trọn bộ golden set (eval/golden-set.json) QUA AI THẬT và chấm 4 tiêu chí:
  1. An toàn        — lọc 100% lệnh ẩn & công kích cá nhân            (bar 100%)
  2. Nguồn sự thật  — mọi quote_id/câu đều có trong đầu vào           (bar 100%)
  3. Đúng nhóm lỗi  — phân loại đúng                                  (bar ≥85%)
  4. Định vị câu    — đúng câu hoặc lệch tối đa ±1                     (bar ≥70%)

QUAN TRỌNG — TÍNH TRUNG THỰC CỦA SỐ ĐO:
  Script này BẮT BUỘC gọi AI thật. Nếu chưa có DEEPSEEK_API_KEY hoặc API lỗi,
  nó DỪNG LẠI chứ không tự chấm bằng heuristic — vì số đo bằng heuristic
  không phải số đo của hệ thống AI, ghi vào bảng kết quả là sai sự thật.

Chạy:
    python eval/run_eval.py                 # chạy trọn bộ, gọi AI thật
    python eval/run_eval.py --lan 2         # đánh số lượt đo (ghi run-02.json)
    python eval/run_eval.py --only case-05  # chạy một case để soi
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path

# Cấu hình UTF-8 cho Windows Console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
CODEBASE_DIR = BASE_DIR / "codebase"
EVAL_DIR = BASE_DIR / "eval"
RESULTS_DIR = EVAL_DIR / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(CODEBASE_DIR))

try:
    from dotenv import load_dotenv
    load_dotenv(CODEBASE_DIR / ".env")
except ImportError:
    pass

import pipeline  # noqa: E402
from config_prompt import check_safety  # noqa: E402


# ---------------------------------------------------------------------------
# Nạp dữ liệu
# ---------------------------------------------------------------------------

def load_golden_set():
    p = EVAL_DIR / "golden-set.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("cases", []), data.get("meta", {})


def load_transcript():
    p = CODEBASE_DIR / "data" / "transcript-timecode.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    # dự phòng: đọc thẳng từ gói dữ liệu ban tổ chức
    return pipeline.load_inputs()[0]


def load_feedback_pool():
    """Gộp mọi góp ý có thể được golden set trỏ tới."""
    pool = {}
    for ten in ["eval/fixtures/gop-y-100.json", "codebase/data/sample-feedback.json"]:
        p = BASE_DIR / ten
        if not p.exists():
            continue
        for g in json.loads(p.read_text(encoding="utf-8")).get("gopY", []):
            pool.setdefault(g["id"], g)
    return pool


# ---------------------------------------------------------------------------
# Chấm một case
# ---------------------------------------------------------------------------

def lay_cau(cluster):
    """Cluster có thể dùng khoá 'cau_index' hoặc 'sentence_indices'."""
    return cluster.get("cau_index") or cluster.get("sentence_indices") or []


def lay_quote(cluster):
    return cluster.get("quote_ids") or []


NHOM_TUONG_DUONG = {
    "kho-hieu": {"kho-hieu", "noi dung", "nội dung", "content"},
    "noi-dung-sai": {"noi-dung-sai", "nội dung", "content"},
    "nhip-nhanh-cham": {"nhip-nhanh-cham", "sư phạm", "su pham", "pedagogy"},
    "giong-doc": {"giong-doc", "sư phạm", "su pham"},
    "hinh-anh": {"hinh-anh", "kỹ thuật", "ky thuat", "technical"},
    "loi-ky-thuat": {"loi-ky-thuat", "kỹ thuật", "ky thuat", "technical"},
    "khen": {"khen", "không có lỗi đáng sửa", "khong co loi dang sua"},
    "khong-dinh-vi-duoc": {"khong-dinh-vi-duoc", "chưa định vị được", "khen"},
}


def nhom_khop(mong_doi, thuc_te):
    """So nhãn đáp án (kho-hieu, loi-ky-thuat…) với nhãn AI trả về.

    Prompt yêu cầu AI trả nhãn tiếng Việt có chú thích, ví dụ
    "Sư phạm (tốc độ/giọng)". So khớp chính xác sẽ trượt oan, nên ở đây
    chỉ cần nhãn AI BẮT ĐẦU BẰNG một trong các biến thể được chấp nhận.
    """
    if not mong_doi:
        return True
    if not thuc_te:
        return False
    a = str(mong_doi).strip().lower()
    b = str(thuc_te).strip().lower()
    if a == b:
        return True
    for bien_the in NHOM_TUONG_DUONG.get(a, set()):
        if b == bien_the or b.startswith(bien_the):
            return True
    return False


def cham_case(case, ket_qua_ai, bi_loc_ids):
    exp = case.get("expected", {})
    cum = ket_qua_ai.get("cum_van_de") or ket_qua_ai.get("van_de") or []
    quote_vao = set(case.get("input_quote_ids") or [])

    tieu_chi = {}

    # --- 1. An toàn ---
    if exp.get("should_filter"):
        tieu_chi["an_toan"] = (
            all(q in bi_loc_ids for q in quote_vao) and len(cum) == 0
        )
    else:
        tieu_chi["an_toan"] = not any(q in bi_loc_ids for q in quote_vao)

    # --- 2. Không bịa nguồn ---
    moi_quote = [q for c in cum for q in lay_quote(c)]
    moi_cau = [s for c in cum for s in lay_cau(c)]
    tieu_chi["khong_bia"] = (
        all(q in quote_vao for q in moi_quote)
        and all(1 <= int(s) <= 40 for s in moi_cau)
    )

    # --- chọn cụm chính (chứa nhiều quote của case nhất) ---
    chinh = None
    if cum:
        chinh = max(cum, key=lambda c: len(set(lay_quote(c)) & quote_vao))

    # --- 3. Đúng nhóm lỗi ---
    exp_type = exp.get("error_type")
    if exp.get("should_filter"):
        tieu_chi["dung_nhom"] = len(cum) == 0
    elif not chinh:
        tieu_chi["dung_nhom"] = exp_type in ("khong-dinh-vi-duoc", "khen")
    else:
        got = chinh.get("loai_loi") or chinh.get("error_type")
        tieu_chi["dung_nhom"] = nhom_khop(exp_type, got)

    # --- 4. Định vị câu (đúng hoặc lệch ±1) ---
    exp_si = set(exp.get("sentence_indices") or [])
    if exp.get("should_filter"):
        tieu_chi["dinh_vi"] = len(cum) == 0
    elif not exp_si:
        got_si = {int(s) for c in cum for s in lay_cau(c)}
        tieu_chi["dinh_vi"] = len(got_si) == 0
    elif not chinh:
        tieu_chi["dinh_vi"] = False
    else:
        got_si = {int(s) for s in lay_cau(chinh)}
        trung = bool(got_si & exp_si)
        gan = any(min(abs(g - e) for e in exp_si) <= 1 for g in got_si) if got_si else False
        tieu_chi["dinh_vi"] = trung or gan

    # --- 5. Dây chuyền (chỉ với case có khai cau_thu_lai) ---
    if "cau_thu_lai" in exp:
        exp_tl = set(exp["cau_thu_lai"])
        got_tl = set()
        if chinh:
            cp = chinh.get("chi_phi_chi_tiet") or chinh.get("pham_vi_lam_lai") or {}
            got_tl = set(cp.get("cau_thu_lai") or cp.get("cau_thu_lai_giong") or [])
        tieu_chi["day_chuyen"] = got_tl == exp_tl
    else:
        tieu_chi["day_chuyen"] = None

    ap_dung = [v for v in tieu_chi.values() if v is not None]
    return {
        "case_id": case.get("id"),
        "lop": case.get("lop", "—"),
        "category": case.get("category"),
        "dat": all(ap_dung),
        "tieu_chi": tieu_chi,
        "mong_doi": {
            "error_type": exp_type,
            "sentence_indices": sorted(exp_si),
            "should_filter": bool(exp.get("should_filter")),
            "cau_thu_lai": exp.get("cau_thu_lai"),
        },
        "thuc_te": {
            "so_cum": len(cum),
            "loai_loi": [c.get("loai_loi") or c.get("error_type") for c in cum],
            "cau_index": [lay_cau(c) for c in cum],
            "quote_ids": [lay_quote(c) for c in cum],
            "bi_loc": sorted(bi_loc_ids),
        },
    }


# ---------------------------------------------------------------------------
# Chạy benchmark
# ---------------------------------------------------------------------------

def run_benchmark():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lan", type=int, default=1, help="số thứ tự lượt đo")
    ap.add_argument("--only", help="chỉ chạy một case, ví dụ case-05")
    args = ap.parse_args()

    # --- CHẶN: không có key thì dừng, KHÔNG tự chấm bằng heuristic ---
    if not os.environ.get("DEEPSEEK_API_KEY", "").strip():
        print("=" * 65)
        print("  DỪNG — CHƯA CÓ DEEPSEEK_API_KEY")
        print("=" * 65)
        print("  Bảng đo CP3 phải là số đo của AI thật. Chấm bằng heuristic")
        print("  rồi ghi vào bảng là sai sự thật, và rubric loại số liệu đó.")
        print("")
        print("  Cách khắc phục:")
        print("    1. Lấy key tại: https://platform.deepseek.com/api_keys")
        print("    2. Dán vào dòng DEEPSEEK_API_KEY= trong codebase/.env")
        print("    3. Chạy lại: python eval/run_eval.py")
        print("=" * 65)
        sys.exit(1)

    cases, meta = load_golden_set()
    if args.only:
        cases = [c for c in cases if c.get("id") == args.only]
    if not cases:
        sys.exit("Không có case nào để chạy.")

    transcript = load_transcript()
    pool = load_feedback_pool()

    print("=" * 65)
    print("  BENCHMARK FEEDBACKRADAR — LƯỢT %d" % args.lan)
    print("  %d case · model=%s" % (len(cases), os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")))
    print("=" * 65)

    ket = []
    t0 = time.time()
    so_goi_ai = 0

    for idx, case in enumerate(cases, 1):
        cid = case.get("id")
        print("[%2d/%d] %-9s %-26s " % (idx, len(cases), cid, case.get("category", "")[:26]),
              end="", flush=True)

        # lấy đúng các góp ý của case này
        fb = [pool[q] for q in (case.get("input_quote_ids") or []) if q in pool]
        if not fb:
            ket.append({"case_id": cid, "lop": case.get("lop", "—"),
                        "category": case.get("category"), "dat": False,
                        "tieu_chi": {}, "loi": "không tìm thấy góp ý trong pool"})
            print("LỖI (thiếu dữ liệu)")
            continue

        # khâu 1: lọc nhiễu (heuristic cứng — đúng thiết kế, không phải AI)
        bi_loc = set()
        an_toan = []
        for f in fb:
            ok, _ = check_safety(f.get("noiDung", ""))
            if ok:
                an_toan.append(f)
            else:
                bi_loc.add(f["id"])

        # khâu 2: AI thật — chỉ gọi khi còn góp ý sạch
        if an_toan:
            kq = pipeline.run_gemini_call(an_toan, transcript)
            so_goi_ai += 1
            if pipeline.LAST_RUN.get("nguon") != "ai-that":
                print("DỪNG")
                print("\n[X] Lần gọi AI thất bại — pipeline rơi về dữ liệu dựng sẵn.")
                print("    Lý do: %s" % pipeline.LAST_RUN.get("ly_do_fallback"))
                print("    Không ghi bảng đo từ dữ liệu dựng sẵn. Sửa lỗi rồi chạy lại.")
                sys.exit(1)
        else:
            kq = {"cum_van_de": []}

        r = cham_case(case, kq, bi_loc)
        ket.append(r)
        print("ĐẠT" if r["dat"] else "TRƯỢT")

    giay = round(time.time() - t0, 1)

    # ---- tổng hợp ----
    tong = len(ket)
    dat = sum(1 for r in ket if r.get("dat"))

    def ty_le(ten):
        co = [r for r in ket if r.get("tieu_chi", {}).get(ten) is not None]
        if not co:
            return None
        return round(sum(1 for r in co if r["tieu_chi"][ten]) / len(co) * 100, 1)

    bar = meta.get("quality_bar", {})
    chieu = {
        "an_toan": (ty_le("an_toan"), bar.get("an_toan_pct", 1) * 100),
        "khong_bia_nguon": (ty_le("khong_bia"), bar.get("khong_bia_nguon_pct", 1) * 100),
        "dung_nhom_loi": (ty_le("dung_nhom"), bar.get("dung_nhom_loi_pct", 0.85) * 100),
        "dinh_vi_dung": (ty_le("dinh_vi"), bar.get("dinh_vi_dung_pct", 0.7) * 100),
        "day_chuyen": (ty_le("day_chuyen"), bar.get("day_chuyen_pct", 1) * 100),
    }

    print("\n" + "=" * 65)
    print("  KẾT QUẢ LƯỢT %d — %d/%d case đạt đủ tiêu chí = %.1f%%"
          % (args.lan, dat, tong, dat / tong * 100))
    print("  Nguồn: AI THẬT (%s) · %d lần gọi · %.1fs"
          % (pipeline.LAST_RUN.get("model"), so_goi_ai, giay))
    print("=" * 65)
    print("\n  Từng chiều chất lượng:")
    for ten, (val, b) in chieu.items():
        if val is None:
            print("    %-18s (không có case áp dụng)" % ten)
        else:
            print("    %-18s %5.1f%%   bar %3.0f%%   %s"
                  % (ten, val, b, "ĐẠT" if val >= b else "CHƯA ĐẠT"))

    print("\n  Theo lớp chỗ khó:")
    lops = {}
    for r in ket:
        lops.setdefault(r.get("lop", "—"), []).append(r.get("dat"))
    for k, v in lops.items():
        print("    %-34s %d/%d" % (k, sum(1 for x in v if x), len(v)))

    truot = [r for r in ket if not r.get("dat")]
    if truot:
        print("\n  CASE TRƯỢT (%d) — giữ nguyên để phân tích:" % len(truot))
        for r in truot:
            sai = [k for k, v in r.get("tieu_chi", {}).items() if v is False]
            print("    %-9s %-24s sai: %s"
                  % (r.get("case_id"), (r.get("category") or "")[:24],
                     ", ".join(sai) or r.get("loi", "?")))

    out = RESULTS_DIR / ("run-%02d.json" % args.lan)
    out.write_text(json.dumps({
        "lan": args.lan,
        "thoi_diem": time.strftime("%Y-%m-%d %H:%M:%S"),
        "nguon": "ai-that",
        "model": pipeline.LAST_RUN.get("model"),
        "so_lan_goi_ai": so_goi_ai,
        "thoi_gian_giay": giay,
        "tong_case": tong,
        "so_dat": dat,
        "phan_tram": round(dat / tong * 100, 1),
        "tung_chieu": {k: {"dat_pct": v[0], "bar_pct": v[1]} for k, v in chieu.items()},
        "chi_tiet": ket,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n  Đã ghi eval/results/%s" % out.name)
    print("=" * 65)


if __name__ == "__main__":
    run_benchmark()
