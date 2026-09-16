# -*- coding: utf-8 -*-
"""
Chạy trọn bộ golden set qua pipeline AI thật và chấm điểm.
Người phụ trách: Nguyễn Cảnh Duy (Đội trưởng · làm cho đo được)

Chạy:
    python eval/run_eval.py                 # chạy trọn bộ, gọi AI thật
    python eval/run_eval.py --lan 2         # đánh số lượt đo (ghi run-02.json)
    python eval/run_eval.py --offline FILE  # chấm lại từ clusters.json có sẵn

Kết quả ghi vào eval/results/run-0N.json — GIỮ CẢ CASE FAIL.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "codebase"))

import pipeline  # noqa: E402

GOLDEN = ROOT / "eval/golden-set.json"
RESULTS = ROOT / "eval/results"


def chay_pipeline(gop_y_ids, feedbacks_all, transcript):
    """Chạy pipeline trên đúng tập góp ý của một case."""
    fb = [f for f in feedbacks_all if f["id"] in set(gop_y_ids)]
    sach, loc = pipeline.loc_nhieu(fb)
    if not sach:
        # tất cả bị lọc — không cần gọi AI
        return {"van_de": []}, loc, None
    ket_qua, trace = pipeline.goi_ai(sach, transcript)
    cum, _ = pipeline.hau_kiem(ket_qua, sach, transcript)
    cum = pipeline.tinh_pham_vi(cum, transcript)
    return {"van_de": cum}, loc, trace


def cham_case(case, ket_qua, loc_bo):
    """Chấm một case theo 4 tiêu chí. Trả về dict kết quả."""
    exp = case["expected"]
    cum = ket_qua["van_de"]
    ids_loc = {l["id"] for l in loc_bo}

    tieu_chi = {}

    # --- An toàn: case phải bị lọc thì phải bị lọc, và không sinh cụm nào ---
    if exp.get("should_filter"):
        bi_loc = all(q in ids_loc for q in case["input_quote_ids"])
        khong_sinh_cum = len(cum) == 0
        tieu_chi["an_toan"] = bool(bi_loc and khong_sinh_cum)
    else:
        # không được lọc nhầm góp ý sạch
        tieu_chi["an_toan"] = not any(q in ids_loc for q in case["input_quote_ids"])

    # --- Không bịa nguồn: mọi quote_id trả về phải nằm trong input ---
    hop_le = set(case["input_quote_ids"])
    moi_quote = [q for c in cum for q in (c.get("quote_ids") or [])]
    tieu_chi["khong_bia"] = all(q in hop_le for q in moi_quote)

    # --- Đúng nhóm lỗi ---
    exp_type = exp.get("error_type")
    if exp.get("should_filter"):
        tieu_chi["dung_nhom"] = len(cum) == 0
    elif not cum:
        tieu_chi["dung_nhom"] = False
    else:
        # lấy cụm chứa nhiều quote của case nhất
        chinh = max(cum, key=lambda c: len(set(c.get("quote_ids") or []) & hop_le))
        got = chinh.get("error_type")
        # "khong-dinh-vi-duoc" và "khen" chấp nhận lẫn nhau khi đáp án là không sửa
        if exp_type in ("khong-dinh-vi-duoc", "khen"):
            tieu_chi["dung_nhom"] = got in ("khong-dinh-vi-duoc", "khen")
        else:
            tieu_chi["dung_nhom"] = got == exp_type

    # --- Định vị đúng: câu đúng hoặc lệch tối đa ±1 ---
    exp_si = set(exp.get("sentence_indices") or [])
    if exp.get("should_filter"):
        tieu_chi["dinh_vi"] = len(cum) == 0
    elif not exp_si:
        # đáp án là KHÔNG định vị được → hệ thống cũng phải trả rỗng
        got_si = {s for c in cum for s in (c.get("sentence_indices") or [])}
        tieu_chi["dinh_vi"] = len(got_si) == 0
    elif not cum:
        tieu_chi["dinh_vi"] = False
    else:
        chinh = max(cum, key=lambda c: len(set(c.get("quote_ids") or []) & hop_le))
        got_si = set(chinh.get("sentence_indices") or [])
        # đạt nếu có ít nhất một câu trùng, hoặc lệch tối đa 1
        trung = bool(got_si & exp_si)
        gan = any(min(abs(g - e) for e in exp_si) <= 1 for g in got_si) if got_si else False
        tieu_chi["dinh_vi"] = trung or gan

    # --- Dây chuyền (chỉ áp cho case có khai cau_thu_lai) ---
    if "cau_thu_lai" in exp:
        exp_tl = set(exp["cau_thu_lai"])
        if cum:
            chinh = max(cum, key=lambda c: len(set(c.get("quote_ids") or []) & hop_le))
            got_tl = set(chinh.get("pham_vi_lam_lai", {}).get("cau_thu_lai_giong") or [])
        else:
            got_tl = set()
        tieu_chi["day_chuyen"] = got_tl == exp_tl
    else:
        tieu_chi["day_chuyen"] = None

    bat_buoc = [v for k, v in tieu_chi.items() if v is not None]
    dat = all(bat_buoc)

    return {
        "case_id": case["id"],
        "lop": case["lop"],
        "category": case["category"],
        "dat": dat,
        "tieu_chi": tieu_chi,
        "mong_doi": {
            "error_type": exp_type,
            "sentence_indices": sorted(exp_si),
            "should_filter": bool(exp.get("should_filter")),
            "cau_thu_lai": exp.get("cau_thu_lai"),
        },
        "thuc_te": {
            "so_cum": len(cum),
            "error_type": [c.get("error_type") for c in cum],
            "sentence_indices": [c.get("sentence_indices") for c in cum],
            "quote_ids": [c.get("quote_ids") for c in cum],
            "cau_thu_lai": [c.get("pham_vi_lam_lai", {}).get("cau_thu_lai_giong") for c in cum],
            "bi_loc": sorted(ids_loc),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lan", type=int, default=1, help="số thứ tự lượt đo")
    ap.add_argument("--offline", help="chấm lại từ file clusters.json thay vì gọi AI")
    ap.add_argument("--only", help="chỉ chạy một case, ví dụ case-05")
    args = ap.parse_args()

    # nạp .env
    env = ROOT / "codebase/.env"
    if env.exists():
        import os
        for dong in env.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if dong and not dong.startswith("#") and "=" in dong:
                k, v = dong.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    gs = json.loads(GOLDEN.read_text(encoding="utf-8"))
    cases = gs["cases"]
    if args.only:
        cases = [c for c in cases if c["id"] == args.only]

    transcript = pipeline.nap_transcript()
    bo = json.loads((ROOT / "eval/fixtures/gop-y-100.json").read_text(encoding="utf-8"))
    feedbacks_all = [
        {"id": g["id"], "nguoiGui": g["nguoiGui"], "kenh": g["kenh"], "noiDung": g["noiDung"]}
        for g in bo["gopY"]
    ]

    print("Chạy golden set — lượt %d — %d case" % (args.lan, len(cases)))
    print("=" * 62)

    ket = []
    t0 = time.time()
    for idx, case in enumerate(cases, 1):
        print("[%2d/%d] %s (%s) ... " % (idx, len(cases), case["id"], case["category"]), end="", flush=True)
        try:
            kq, loc, _ = chay_pipeline(case["input_quote_ids"], feedbacks_all, transcript)
            r = cham_case(case, kq, loc)
        except Exception as e:  # noqa: BLE001
            r = {"case_id": case["id"], "lop": case["lop"], "category": case["category"],
                 "dat": False, "loi": str(e), "tieu_chi": {}}
        ket.append(r)
        print("ĐẠT" if r["dat"] else "TRƯỢT")

    giay = round(time.time() - t0, 1)

    # ---- tổng hợp ----
    tong = len(ket)
    dat = sum(1 for r in ket if r["dat"])
    def ty_le(ten):
        co = [r for r in ket if r.get("tieu_chi", {}).get(ten) is not None]
        if not co:
            return None
        return round(sum(1 for r in co if r["tieu_chi"][ten]) / len(co) * 100, 1)

    bar = gs["meta"]["quality_bar"]
    do = {
        "dung_nhom_loi": (ty_le("dung_nhom"), bar["dung_nhom_loi_pct"] * 100),
        "dinh_vi_dung": (ty_le("dinh_vi"), bar["dinh_vi_dung_pct"] * 100),
        "khong_bia_nguon": (ty_le("khong_bia"), bar["khong_bia_nguon_pct"] * 100),
        "an_toan": (ty_le("an_toan"), bar["an_toan_pct"] * 100),
        "day_chuyen": (ty_le("day_chuyen"), bar["day_chuyen_pct"] * 100),
    }

    print("\n" + "=" * 62)
    print("KẾT QUẢ LƯỢT %d — %d/%d case đạt đủ tiêu chí = %.1f%%"
          % (args.lan, dat, tong, dat / tong * 100))
    print("\nTừng chiều chất lượng:")
    for ten, (val, b) in do.items():
        if val is None:
            print("  %-18s  (không có case áp dụng)" % ten)
        else:
            print("  %-18s  %5.1f%%   bar %.0f%%   %s"
                  % (ten, val, b, "ĐẠT" if val >= b else "CHƯA ĐẠT"))

    print("\nTheo lớp chỗ khó:")
    lops = {}
    for r in ket:
        lops.setdefault(r["lop"], []).append(r["dat"])
    for k, v in lops.items():
        print("  %-32s %d/%d" % (k, sum(v), len(v)))

    truot = [r for r in ket if not r["dat"]]
    if truot:
        print("\nCASE TRƯỢT (%d) — giữ nguyên để phân tích:" % len(truot))
        for r in truot:
            sai = [k for k, v in r.get("tieu_chi", {}).items() if v is False]
            print("  %s (%s) — sai: %s" % (r["case_id"], r["category"], ", ".join(sai) or r.get("loi", "?")))

    RESULTS.mkdir(parents=True, exist_ok=True)
    out = RESULTS / ("run-%02d.json" % args.lan)
    out.write_text(json.dumps({
        "lan": args.lan,
        "thoi_diem": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model": pipeline.MODEL,
        "thoi_gian_giay": giay,
        "tong_case": tong,
        "so_dat": dat,
        "phan_tram": round(dat / tong * 100, 1),
        "tung_chieu": {k: {"dat_pct": v[0], "bar_pct": v[1]} for k, v in do.items()},
        "chi_tiet": ket,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nĐã ghi eval/results/%s (%.1fs)" % (out.name, giay))


if __name__ == "__main__":
    main()
