#!/usr/bin/env node
/**
 * Kiểm tra golden-set.json có bám dữ liệu thật không.
 * Chạy: node eval/fixtures/kiem-golden.js
 *
 * Bắt các lỗi: quote_id không tồn tại, câu ngoài 1-40, input không khớp
 * nguyên văn góp ý gốc, thiếu phủ 4 lớp chỗ khó.
 */
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..', '..');

const bo = JSON.parse(fs.readFileSync(path.join(ROOT, 'eval/fixtures/gop-y-100.json'), 'utf8'));
const gs = JSON.parse(fs.readFileSync(path.join(ROOT, 'eval/golden-set.json'), 'utf8'));

const gopY = new Map(bo.gopY.map((g) => [g.id, g]));
const vanDe = new Set(bo.vanDe.map((v) => v.id));

let loi = 0;
const bao = (m) => { console.log('  >>> ' + m); loi++; };

console.log('=== 1. Bộ góp ý nguồn ===');
console.log('  Tổng góp ý: ' + bo.gopY.length);
console.log('  Số vấn đề thật: ' + bo.vanDe.length);
const nguoi = new Set(bo.gopY.map((g) => g.nguoiGui));
console.log('  Người gửi duy nhất: ' + nguoi.size);
if (bo.gopY.length < 100) bao('Bộ góp ý dưới 100 — đề C5 yêu cầu khoảng một trăm');

console.log('\n=== 2. Từng case trong golden set ===');
gs.cases.forEach((c) => {
  const ids = c.input_quote_ids || [];
  if (!ids.length) bao(c.id + ': không có input_quote_ids');
  ids.forEach((id) => {
    if (!gopY.has(id)) bao(c.id + ': quote_id "' + id + '" không có trong bộ 100');
  });
  const si = c.expected.sentence_indices || [];
  si.forEach((n) => {
    if (n < 1 || n > 40) bao(c.id + ': câu ' + n + ' nằm ngoài 1-40');
  });
  if (c.expected.van_de && !vanDe.has(c.expected.van_de)) {
    bao(c.id + ': van_de "' + c.expected.van_de + '" không có trong danh sách vấn đề');
  }
  // input_text phải khớp nguyên văn góp ý gốc (khi chỉ có 1 quote)
  if (ids.length === 1 && c.input_text) {
    const goc = gopY.get(ids[0]);
    if (goc && goc.noiDung !== c.input_text) {
      bao(c.id + ': input_text KHÔNG khớp nguyên văn ' + ids[0]);
    }
  }
  // đáp án của case phải khớp đáp án của góp ý gốc
  if (ids.length === 1) {
    const goc = gopY.get(ids[0]);
    if (goc) {
      if (!!c.expected.should_filter !== !!goc.dapAn.locBo) {
        bao(c.id + ': should_filter lệch với đáp án gốc của ' + ids[0]);
      }
      if (c.expected.van_de !== goc.dapAn.vanDe) {
        bao(c.id + ': van_de lệch — golden "' + c.expected.van_de + '" vs gốc "' + goc.dapAn.vanDe + '"');
      }
    }
  }
});
if (!loi) console.log('  ✔ mọi case đều trỏ về góp ý có thật, câu hợp lệ, đáp án khớp nguồn');

console.log('\n=== 3. Phủ 4 lớp chỗ khó ===');
const lop = {};
gs.cases.forEach((c) => { lop[c.lop] = (lop[c.lop] || 0) + 1; });
Object.entries(lop).forEach(([k, v]) => {
  const du = k === 'Case thường' ? v >= 1 : v >= 2;
  console.log('  ' + k + ': ' + v + ' case ' + (du ? '✔' : '>>> CẦN ≥2'));
  if (!du) loi++;
});
console.log('  Tổng: ' + gs.cases.length + ' case ' + (gs.cases.length >= 20 ? '✔ (bar ≥20)' : '>>> CẦN ≥20'));
if (gs.cases.length < 20) loi++;

console.log('\n=== 4. Quality bar đã khai ===');
Object.entries(gs.meta.quality_bar).forEach(([k, v]) => {
  console.log('  ' + k + ': ' + (v * 100).toFixed(0) + '%');
});

console.log('\n' + '='.repeat(52));
console.log(loi === 0
  ? 'GOLDEN SET HỢP LỆ — mọi case bám dữ liệu thật.'
  : 'CÓ ' + loi + ' VẤN ĐỀ — sửa trước khi chạy đo.');
process.exit(loi === 0 ? 0 : 1);
