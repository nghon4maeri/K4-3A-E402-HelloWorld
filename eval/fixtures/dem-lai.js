#!/usr/bin/env node
/**
 * Đếm lại mọi con số trong eval/evidence-log.md từ dữ liệu gốc.
 * Chạy:  node eval/fixtures/dem-lai.js
 *
 * Cần có gói data tại chỗ: data/studio-pack/c5-feedbackradar/
 * (gói này KHÔNG commit vào repo theo quy định bảo mật điều 3)
 */
const fs = require('fs');
const path = require('path');

const PACK = path.join(__dirname, '..', '..', 'data', 'studio-pack', 'c5-feedbackradar');
const FIXTURES = __dirname;

if (!fs.existsSync(PACK)) {
  console.error('Không tìm thấy ' + PACK);
  console.error('Đặt gói data của ban tổ chức vào đúng đường dẫn trên rồi chạy lại.');
  process.exit(1);
}

const ok = (dung) => (dung ? 'KHỚP' : '>>> LỆCH <<<');
let lech = 0;
const check = (nhan, thucTe, congBo) => {
  const dung = String(thucTe) === String(congBo);
  if (!dung) lech++;
  console.log(`  ${nhan}: đếm được ${thucTe} | evidence-log ghi ${congBo} → ${ok(dung)}`);
};

// ---------- Phần 1: góp ý ----------
const gy = JSON.parse(fs.readFileSync(path.join(PACK, 'vi-du', 'gop-y-mau.json'), 'utf8')).gopY;

console.log('=== 1. Góp ý mẫu ===');
check('Tổng góp ý JSON', gy.length, 18);

// 6 chỗ khó — phân loại theo đúng bảng trong README của gói
const CHO_KHO = {
  'Mơ hồ, không rõ chỗ nào': ['gy-001', 'gy-009'],
  'Hai nhóm nói ngược nhau': ['gy-005', 'gy-006'],
  'Một người gửi lặp lại': ['gy-002', 'gy-003', 'gy-018'],
  'Lệnh ẩn lừa AI': ['gy-011'],
  'Công kích cá nhân': ['gy-012'],
  'Lỗi kỹ thuật trộn nội dung': ['gy-008', 'gy-017'],
};

console.log('\n=== 2. Sáu chỗ khó (theo README của gói) ===');
let tongKho = 0;
for (const [ten, ids] of Object.entries(CHO_KHO)) {
  const thieu = ids.filter((id) => !gy.find((g) => g.id === id));
  if (thieu.length) { console.log(`  >>> ${ten}: thiếu ${thieu.join(', ')}`); lech++; }
  tongKho += ids.length;
  console.log(`  ${ten}: ${ids.length}/18 = ${((ids.length / 18) * 100).toFixed(1)}%`);
}
check('Cộng nhóm khó', tongKho, 11);
const thuoc = new Set(Object.values(CHO_KHO).flat());
const thuong = gy.filter((g) => !thuoc.has(g.id)).map((g) => g.id);
check('Góp ý thường', thuong.length, 7);
console.log(`     (${thuong.join(', ')})`);

console.log('\n=== 3. Kênh & người gửi ===');
const kenh = {};
gy.forEach((g) => (kenh[g.kenh] = (kenh[g.kenh] || 0) + 1));
check('bình luận', kenh['binh-luan'], 7);
check('khảo sát', kenh['khao-sat'], 6);
check('tin nhắn', kenh['tin-nhan'], 5);

const nguoi = {};
gy.forEach((g) => (nguoi[g.nguoiGui] = (nguoi[g.nguoiGui] || 0) + 1));
const ds = Object.keys(nguoi);
check('Người gửi duy nhất', ds.length, 16);
check('Học viên (hv-)', ds.filter((x) => x.startsWith('hv')).length, 14);
check('hv-011 gửi mấy lần', nguoi['hv-011'], 3);

// ---------- Khảo sát trong gói ----------
const csvPack = fs.readFileSync(path.join(PACK, 'vi-du', 'khao-sat-mau.csv'), 'utf8')
  .trim().split('\n').slice(1);
const idsCsv = csvPack.map((l) => l.split(',')[0]);
const chiCsv = idsCsv.filter((id) => !gy.find((g) => g.id === id));
console.log('\n=== 4. Khảo sát trong gói ===');
check('Dòng khảo sát', csvPack.length, 10);
check('Chỉ có ở CSV', chiCsv.length, 4);
console.log(`     (${chiCsv.join(', ')})`);
check('Tổng góp ý duy nhất toàn gói', new Set([...gy.map((g) => g.id), ...idsCsv]).size, 22);

// ---------- Chi phí ----------
console.log('\n=== 5. Chi phí làm lại ===');
const rows = fs.readFileSync(path.join(PACK, 'video-mau', 'cau-timecode-d1.csv'), 'utf8')
  .trim().split('\n').slice(1)
  .map((l) => {
    const m = l.match(/^(\d+),([^,]+),([^,]+),([^,]+),(\d+),"(.*)"$/);
    return m ? { cau: +m[1], batDau: m[2], ketThuc: m[4], loi: m[6] } : null;
  })
  .filter(Boolean);

const coLoi = rows.filter((r) => r.loi !== '(dừng 5 giây)');
const tongKyTu = coLoi.reduce((s, r) => s + r.loi.length, 0);
check('Tổng số câu', rows.length, 40);
check('Câu có lời đọc', coLoi.length, 39);
check('Tổng ký tự', tongKyTu, 3637);
check('TB ký tự/câu', Math.round(tongKyTu / coLoi.length), 93);

// dây chuyền: sửa câu N kéo theo N-1 và N+1
const dayChuyen = (ds) => {
  const s = new Set();
  ds.forEach((c) => [c - 1, c, c + 1].forEach((x) => { if (x >= 1 && x <= 40) s.add(x); }));
  return [...s].sort((a, b) => a - b);
};
const kyTu = (ds) => ds.reduce((s, c) => {
  const r = rows.find((x) => x.cau === c);
  return s + (r && r.loi !== '(dừng 5 giây)' ? r.loi.length : 0);
}, 0);

const c22 = dayChuyen([22]);
check('Sửa câu 22 → thu lại câu', c22.join('-'), '21-22-23');
check('  ký tự phải thu lại', kyTu(c22), 269);
const pct = (kyTu(c22) / tongKyTu) * 100;
check('  % công thu giọng', pct.toFixed(1), '7.4');
check('  % tiết kiệm', (100 - pct).toFixed(1), '92.6');

// ---------- Phần 2: khảo sát mô phỏng ----------
console.log('\n=== 6. Khảo sát mô phỏng của nhóm ===');
const splitCsv = (l) => {
  const out = []; let cur = '', inq = false;
  for (const ch of l) {
    if (ch === '"') { inq = !inq; continue; }
    if (ch === ',' && !inq) { out.push(cur); cur = ''; } else cur += ch;
  }
  out.push(cur); return out;
};
const ks = fs.readFileSync(path.join(FIXTURES, 'khao-sat-mo-phong.csv'), 'utf8')
  .trim().split('\n').slice(1).map(splitCsv);

check('Số người', ks.length, 20);
const vaiTro = [...new Set(ks.map((r) => r[2]))];
check('Vai trò duy nhất', vaiTro.join('|'), 'Học viên');
const q1 = ks.filter((r) => r[5] === 'Có').length;
const q3 = ks.filter((r) => r[7] === 'Không').length;
const q2 = ks.filter((r) => /Bỏ qua|tra ngoài|search ngoài|Hỏi bạn|Hỏi trợ giảng/i.test(r[6])).length;
const tyLe = (n) => `${n}/20 = ${((n / ks.length) * 100).toFixed(0)}%`;
check('Q1 từng gặp lỗi', tyLe(q1), '18/20 = 90%');
check('Q3 không ghi timestamp', tyLe(q3), '18/20 = 90%');
check('Q2 không gửi góp ý', tyLe(q2), '11/20 = 55%');

console.log('\n' + '='.repeat(52));
console.log(lech === 0
  ? 'TẤT CẢ KHỚP — mọi con số trong evidence-log.md kiểm lại được.'
  : `CÓ ${lech} CHỖ LỆCH — sửa evidence-log.md cho khớp dữ liệu.`);
process.exit(lech === 0 ? 0 : 1);
