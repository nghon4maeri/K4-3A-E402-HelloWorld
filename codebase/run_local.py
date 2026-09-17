"""
FeedbackRadar Local Development Server
Author: Nguyen Ho Nam (Dev / Agent Engineer)
Description: Khởi chạy HTTP server cục bộ tại thư mục codebase để mở index.html và fetch('clusters.json') mà không bị chặn CORS của trình duyệt.
Add: endpoint /export_docx (~GET) xuất Kịch bản V2 (.docx thật) từ clusters.json + danh sách cụm đã Accept.
"""

import io
import json
import os
import re
import sys
import csv
import zipfile
import importlib
import webbrowser
import http.server
import socketserver
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Đảm bảo UTF-8
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

PORT = 8000
DIRECTORY = Path(__file__).resolve().parent
REPO_DATA = DIRECTORY.parent / "data"   # gói dữ liệu đề bài (video mẫu, slide, transcript)

TRANSCRIPT_PATH = DIRECTORY / "data" / "transcript-timecode.json"
SAMPLE_FEEDBACK_PATH = DIRECTORY / "data" / "sample-feedback.json"

# Cột chuẩn cho file CSV xuất từ Google Form (dấu phẩy; có thể gõ trực tiếp)
CSV_COLUMNS = ["id", "nguoiGui", "noiDung", "thoiDiem", "diemSo"]


def load_transcript() -> list:
    with open(TRANSCRIPT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_csv_feedbacks(text: str) -> list:
    """Parse CSV (từ form khảo sát xuất ra) -> danh sách feedback chuẩn.
    Hỗ trợ cột: id (tuỳ chọn), nguoiGui, noiDung, thoiDiem (tuỳ chọn), diemSo (tuỳ chọn)."""
    reader = csv.DictReader(io.StringIO(text.strip()))
    if not reader.fieldnames:
        raise ValueError("CSV rỗng hoặc không có hàng tiêu đề.")
    # Chuẩn hoá tên cột (bỏ dấu cách, thường hoá) để chấp nhận "Nội dung" / "noi dung"...
    def norm(s): return s.strip().lower().replace(" ", "_")
    mapping = {norm(h): h for h in reader.fieldnames if h.strip()}
    feedbacks = []
    for idx, row in enumerate(reader, start=1):
        def get(key):
            header = mapping.get(norm(key))
            if not header:
                return ""
            return (row.get(header) or "").strip()
        noi_dung = get("noiDung")
        if not noi_dung:
            continue
        item = {
            "id": get("id") or f"gy-{idx:03d}",
            "kenh": "khao-sat",
            "nguoiGui": get("nguoiGui") or f"hv-{idx:03d}",
            "noiDung": noi_dung,
        }
        thoi_diem = get("thoiDiem")
        if thoi_diem:
            item["thoiDiem"] = thoi_diem
        diem_so = get("diemSo")
        if diem_so:
            try:
                item["diemSo"] = int(float(diem_so))
            except ValueError:
                pass
        feedbacks.append(item)
    return feedbacks


def parse_json_feedbacks(text: str) -> list:
    """Parse JSON (export Discord hoặc paste nguyên cấu trúc sample-feedback.json)."""
    data = json.loads(text)
    if isinstance(data, dict):
        items = data.get("gopY", [])
    else:
        items = data
    if isinstance(items, list):
        feedbacks = []
        for idx, it in enumerate(items, start=1):
            if not isinstance(it, dict):
                continue
            noi_dung = str(it.get("noiDung", "")).strip()
            if not noi_dung:
                continue
            item = {
                "id": it.get("id") or f"gy-{idx:03d}",
                "kenh": it.get("kenh", "tin-nhan"),
                "nguoiGui": it.get("nguoiGui", f"hv-{idx:03d}"),
                "noiDung": noi_dung,
            }
            for k in ("thoiDiem", "diemSo"):
                if it.get(k) is not None:
                    item[k] = it[k]
            feedbacks.append(item)
        return feedbacks
    raise ValueError("JSON phải là mảng góp ý hoặc object có key 'gopY'.")


def xml_escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_docx(clusters, metadata, accepted_indices) -> bytes:
    """Dựng file .docx (OOXML) từ danh sách cụm đã Accept — không cần thư viện ngoài."""
    accepted = [clusters[i] for i in accepted_indices if 0 <= i < len(clusters)]
    rows = []
    for it in accepted:
        for t in it.get("transcript", []):
            if t.get("bad"):
                rows.append((it, t))

    # Phạm vi làm lại đo bằng KÝ TỰ + CẢNH, không quy ra tiền.
    # Ban tổ chức không cấp đơn giá (spec.md §4, non-goal #4).
    toan_bo = metadata.get("toanBoVideo", {}) or {}
    tong_ky_tu_video = toan_bo.get("soKyTu", 3637)
    tong_canh_video = toan_bo.get("soCanh", 40)
    ky_tu = sum(it.get("kyTu", 0) for it in accepted)
    canh = sum(it.get("canh", 0) for it in accepted)
    pct_ky_tu = round(ky_tu / tong_ky_tu_video * 100, 1) if tong_ky_tu_video else 0.0
    tiet_kiem_pct = round(100 - pct_ky_tu, 1)

    def p(text, bold=False, style=None):
        ppr = ""
        if style:
            ppr += f'<w:pStyle w:val="{style}"/>'
        rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
        return f'<w:p><w:pPr>{ppr}</w:pPr><w:r>{rpr}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p>'

    # Bảng: Mã câu | Câu V2 dự kiến | Vị trí video | Cụm | Chi phí | Trạng thái
    def cell(text, bold=False, width="2200"):
        rpr = '<w:rPr><w:b/></w:rPr>' if bold else ''
        return (
            f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
            f'<w:p><w:r>{rpr}<w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r></w:p></w:tc>'
        )

    def hdr(fields):
        return "<w:tr>" + "".join(cell(f, True) for f in fields) + "</w:tr>"

    body = []
    body.append(p("FEEDBACKRADAR — KỊCH BẢN V2 (NHÁP DỰ KIẾN)", bold=True, style="Title"))
    body.append(p(f"Bài giảng: 'Giới thiệu AI đại chúng' · Kịch bản ID: {metadata.get('kichBanId','d1')}"))
    body.append(p(f"Ngày xuất: {datetime.now().strftime('%d/%m/%Y %H:%M')} · "
                  f"Từ {metadata.get('soGopYHopLe', len(clusters))} góp ý hợp lệ / {metadata.get('tongSoGopY', 30)} đầu vào · "
                  f"{metadata.get('soGopYBiChieuLoc', 0)} nhiễu đã lọc"))
    body.append(p(f"{len(accepted)}/{len(clusters)} cụm được duyệt · Phạm vi làm lại: "
                  f"{ky_tu} ký tự thu lại giọng / {tong_ky_tu_video} · {canh} cảnh dựng lại / {tong_canh_video} · "
                  f"bằng {pct_ky_tu}% công thu giọng — tiết kiệm {tiet_kiem_pct}% so với làm lại cả video", bold=True))

    if not rows:
        body.append(p("(Chưa có câu nào được Accept — bấm ✔ trên bảng duyệt rồi xuất lại.)"))
    else:
        table_rows = [hdr(["Mã câu", "Câu trong Kịch bản V2 (dự kiến)", "Vị trí video", "Cụm vấn đề", "Phạm vi", "Trạng thái"])]
        for it, t in rows:
            table_rows.append(
                "<w:tr>"
                + cell(f"{it.get('idx')}.{t['n']}")
                + cell(t["t"], width="5200")
                + cell(f"{it.get('v')} · {it.get('cau')}")
                + cell(it.get("title"), width="3600")
                + cell(f"{it.get('kyTu', 0)} ký tự · {it.get('canh', 0)} cảnh", width="1600")
                + cell("Trong V2")
                + "</w:tr>"
            )
        body.append(
            '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/><w:tblBorders>'
            + "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="999999"/>'
                      for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
            + "</w:tblBorders></w:tblPr>"
            + '<w:tblGrid>'
            + '<w:gridCol w:w="1100"/><w:gridCol w:w="5200"/><w:gridCol w:w="1400"/><w:gridCol w:w="3600"/><w:gridCol w:w="1600"/><w:gridCol w:w="1200"/>'
            + "</w:tblGrid>"
            + "".join(table_rows)
            + "</w:tbl>"
        )

    body.append(p(""))
    body.append(p("Ghi chú: Đây là nháp do AI đề xuất (Augment). Biên tập viên đã duyệt từng cụm; giảng viên quyết định cuối cùng trước khi thu/dựng.", bold=False))

    document_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<w:body>' + "".join(body) +
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr>'
        '</w:body></w:document>'
    )

    styles_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:style>'
        '<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:before="120" w:after="240"/></w:pPr>'
        '<w:rPr><w:b/><w:sz w:val="40"/></w:rPr></w:style>'
        '</w:styles>'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '</Relationships>'
    )

    document_rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        '</Relationships>'
    )

    core_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:title>FeedbackRadar Kịch bản V2</dc:title>'
        '<dc:creator>FeedbackRadar - Nhom HelloWorld</dc:creator>'
        '</cp:coreProperties>'
    )

    content_types = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
        '</Types>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels_xml)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/_rels/document.xml.rels", document_rels)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("docProps/core.xml", core_xml)
    return buf.getvalue()


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/export_docx":
            self._export_docx(parse_qs(parsed.query))
            return
        if self.headers.get("Range") and self._serve_range():
            return
        super().do_GET()

    def _serve_range(self) -> bool:
        """Phục vụ HTTP Range cho file tĩnh — trình duyệt cần cái này để tua video.

        SimpleHTTPRequestHandler không hỗ trợ Range, nên <video> không seek được
        và Safari từ chối phát hẳn. Trả True nếu đã tự xử lý xong request.
        """
        m = re.match(r"bytes=(\d*)-(\d*)$", self.headers.get("Range", "").strip())
        if not m:
            return False
        local = Path(self.translate_path(self.path))
        if not local.is_file():
            return False

        size = local.stat().st_size
        start_s, end_s = m.group(1), m.group(2)
        if start_s:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
        elif end_s:                      # dạng "bytes=-500": 500 byte cuối
            start, end = max(0, size - int(end_s)), size - 1
        else:
            return False
        end = min(end, size - 1)
        if start > end:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{size}")
            self.end_headers()
            return True

        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(str(local)))
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()   # gọi thẳng lớp cha để không thêm Accept-Ranges lần hai
        with open(local, "rb") as f:
            f.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = f.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break   # người xem tua sang chỗ khác, bỏ dở là bình thường
                remaining -= len(chunk)
        return True

    def end_headers(self):
        if self.path.endswith(".mp4"):
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def translate_path(self, path):
        """Cho phép trang web đọc gói dữ liệu ngoài codebase/ (video mẫu, slide, transcript).

        Trình duyệt chuẩn hoá "../data/..." thành "/data/...", mà thư mục gốc của
        server là codebase/ nên đường dẫn đó 404. Ở đây map riêng tiền tố /data/
        sang thư mục data/ của repo — trừ hai file pipeline thật sự nằm trong
        codebase/data/ thì vẫn ưu tiên bản trong codebase.
        """
        clean = urlparse(path).path
        if clean.startswith("/data/"):
            rel = clean[len("/data/"):]
            local = DIRECTORY / "data" / rel
            if local.is_file():
                return str(local)
            repo_file = (REPO_DATA / rel).resolve()
            # chặn đi ra ngoài thư mục data/ của repo
            if str(repo_file).startswith(str(REPO_DATA.resolve())) and repo_file.is_file():
                return str(repo_file)
        return super().translate_path(path)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/analyze":
            self._analyze()
            return
        self.send_error(404, "Unknown endpoint.")

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return ""
        return self.rfile.read(length).decode("utf-8")

    def _send_json(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _analyze(self):
        """POST /api/analyze  body={'source':'csv'|'json','text':'...'}
        Chạy pipeline AI thật với dữ liệu vừa nhập, ghi clusters.json, trả JSON."""
        try:
            payload = json.loads(self._read_body() or "{}")
            source = payload.get("source", "csv")
            text = payload.get("text", "")
            if not text.strip():
                raise ValueError("Chưa có dữ liệu — dán CSV hoặc JSON trước.")
            if source == "json":
                feedbacks = parse_json_feedbacks(text)
            else:
                feedbacks = parse_csv_feedbacks(text)
            if not feedbacks:
                raise ValueError("Không đọc được góp ý nào — kiểm tra lại định dạng.")
            transcript = load_transcript()
            pipeline = importlib.import_module("pipeline")
            result, safety_log = pipeline.analyze_feedbacks(feedbacks, transcript)
            with open(DIRECTORY / "clusters.json", "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            self._send_json(200, {
                "ok": True,
                "source": source,
                "tongGopY": len(feedbacks),
                "soLoc": len(safety_log),
                "result": result,
            })
        except Exception as e:
            self._send_json(400, {"ok": False, "error": str(e)})

    def _export_docx(self, query):
        clusters_path = DIRECTORY / "clusters.json"
        if not clusters_path.exists():
            self.send_error(404, "clusters.json chưa tồn tại — hãy chạy pipeline.py trước.")
            return
        try:
            data = json.loads(clusters_path.read_text(encoding="utf-8"))
            clusters = data.get("clusters", [])
            metadata = data.get("metadata", {})
            accepted = []
            for raw in query.get("accepted", [""]):
                for part in re.split(r"[,\s]+", raw):
                    if part.strip():
                        accepted.append(int(part.strip()))
            accepted = sorted(set(i for i in accepted if 0 <= i < len(clusters)))
            if not accepted:
                self.send_error(400, "Chưa có cụm nào được Accept (truyền tham số ?accepted=0,1,2).")
                return
            docx_bytes = build_docx(clusters, metadata, accepted)
        except Exception as e:
            self.send_error(500, f"Lỗi dựng docx: {e}")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        self.send_header("Content-Disposition", 'attachment; filename="FeedbackRadar-kich-ban-V2.docx"')
        self.send_header("Content-Length", str(len(docx_bytes)))
        self.end_headers()
        self.wfile.write(docx_bytes)


def run_server():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        url = f"http://localhost:{PORT}/home.html"
        print("=" * 60)
        print("  FEEDBACKRADAR LOCAL WEB SERVER")
        print(f"  Đang chạy tại: {url}")
        print("  Endpoint xuất docx: GET /export_docx?accepted=0,1,2")
        print("  Endpoint phân tích:  POST /api/analyze  (body: source=csv|json, text=...)")
        print("  Bấm Ctrl+C để dừng server.")
        print("=" * 60)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[i] Đã dừng server.")


if __name__ == "__main__":
    run_server()