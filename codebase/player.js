/* ============================================================
   FeedbackRadar — Player dùng chung
   Dùng bởi:  home.html  (trang học bài, xem toàn video)
              index.html (màn Duyệt & Xuất, nhảy tới câu lỗi)

   Một chỗ sửa, hai nơi đổi. Player tự đọc transcript-timecode.json
   nên câu đang đọc và mốc giây luôn khớp dữ liệu thật, không hard-code.
   ============================================================ */
(function (global) {
  'use strict';

  var VIDEO_SRC = '../data/studio-pack/c5-feedbackradar/video-mau/d1.mp4';
  var TRANSCRIPT_URL = 'data/transcript-timecode.json';

  var transcriptCache = null;

  /* "02:14.6" hoặc "02:14" -> 134.6 */
  function toSec(s) {
    var p = String(s || '0:0').split(':');
    if (p.length < 2) return 0;
    return (parseInt(p[0], 10) || 0) * 60 + (parseFloat(p[1]) || 0);
  }

  /* 134.6 -> "02:14" */
  function toClock(sec) {
    sec = Math.max(0, Math.floor(sec || 0));
    var m = Math.floor(sec / 60), s = sec % 60;
    return (m < 10 ? '0' : '') + m + ':' + (s < 10 ? '0' : '') + s;
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function loadTranscript() {
    if (transcriptCache) return Promise.resolve(transcriptCache);
    return fetch(TRANSCRIPT_URL, { cache: 'no-store' })
      .then(function (r) { return r.ok ? r.json() : []; })
      .then(function (d) {
        transcriptCache = Array.isArray(d) ? d : [];
        global.FRPlayer.__lines = transcriptCache;   // cho phép đọc đồng bộ sau khi đã nạp
        return transcriptCache;
      })
      .catch(function () {
        transcriptCache = [];
        global.FRPlayer.__lines = transcriptCache;
        return transcriptCache;
      });
  }

  /* ----------------------------------------------------------
     create(mount, opts)
       mount : phần tử DOM để gắn player vào
       opts  : {
         startAt    : số giây bắt đầu (mặc định 0)
         marks      : [{sec, label, kind}] — chấm trên thanh seek
         showTranscript : true/false — có hiện bảng transcript cuộn theo không
         onTime     : callback(giây, câu đang đọc)
         compact    : true = bản gọn cho index.html
       }
     Trả về đối tượng điều khiển: { seekTo, seekToSentence, el, video, destroy }
     ---------------------------------------------------------- */
  function create(mount, opts) {
    opts = opts || {};
    var marks = opts.marks || [];
    var duration = 0;
    var lines = [];
    var curSentence = null;

    mount.innerHTML =
      '<div class="frp' + (opts.compact ? ' frp-compact' : '') + '">' +
        '<div class="frp-stage">' +
          '<video class="frp-video" preload="metadata" playsinline ' +
                 'src="' + VIDEO_SRC + '"></video>' +
          '<div class="frp-fallback" hidden>' +
            'Không nạp được <code>d1.mp4</code>.<br>' +
            'Mở trang qua <code>python run_local.py</code> để phát được video.' +
          '</div>' +
        '</div>' +
        '<div class="frp-controls">' +
          '<button class="frp-btn frp-play" type="button" aria-label="Phát / tạm dừng">▶</button>' +
          '<button class="frp-btn frp-back" type="button" aria-label="Lùi 5 giây">↺5</button>' +
          '<span class="frp-time tnum">00:00 / 00:00</span>' +
          '<div class="frp-bar" role="slider" tabindex="0" aria-label="Thanh thời gian">' +
            '<div class="frp-fill"></div>' +
            '<div class="frp-marks"></div>' +
          '</div>' +
          '<button class="frp-btn frp-full" type="button" aria-label="Toàn màn hình">⛶</button>' +
        '</div>' +
        '<div class="frp-caption"></div>' +
        (opts.showTranscript ? '<div class="frp-transcript"></div>' : '') +
      '</div>';

    var root     = mount.querySelector('.frp');
    var video    = mount.querySelector('.frp-video');
    var fallback = mount.querySelector('.frp-fallback');
    var playBtn  = mount.querySelector('.frp-play');
    var backBtn  = mount.querySelector('.frp-back');
    var fullBtn  = mount.querySelector('.frp-full');
    var timeEl   = mount.querySelector('.frp-time');
    var bar      = mount.querySelector('.frp-bar');
    var fill     = mount.querySelector('.frp-fill');
    var marksEl  = mount.querySelector('.frp-marks');
    var capEl    = mount.querySelector('.frp-caption');
    var trEl     = mount.querySelector('.frp-transcript');

    video.addEventListener('error', function () {
      video.hidden = true;
      fallback.hidden = false;
    });

    video.addEventListener('loadedmetadata', function () {
      duration = video.duration || 0;
      paintMarks();
      paintTime();
    });

    /* --- transcript --- */
    loadTranscript().then(function (d) {
      lines = d;
      if (trEl) {
        trEl.innerHTML = lines.map(function (l) {
          return '<div class="frp-line" data-cau="' + l.cau + '" data-sec="' + toSec(l.batDau) + '">' +
                   '<span class="frp-no tnum">' + l.cau + '</span>' +
                   '<span class="frp-tx">' + esc(l.loi) + '</span>' +
                   '<span class="frp-at tnum">' + toClock(toSec(l.batDau)) + '</span>' +
                 '</div>';
        }).join('');
        trEl.addEventListener('click', function (e) {
          var row = e.target.closest('.frp-line');
          if (row) seekTo(parseFloat(row.dataset.sec));
        });
      }
      if (opts.startAt) seekTo(opts.startAt);
      paintTime();
    });

    function sentenceAt(sec) {
      for (var i = lines.length - 1; i >= 0; i--) {
        if (sec >= toSec(lines[i].batDau)) return lines[i];
      }
      return lines[0] || null;
    }

    function paintMarks() {
      if (!duration || !marks.length) { marksEl.innerHTML = ''; return; }
      marksEl.innerHTML = marks.map(function (m) {
        var pct = Math.max(0, Math.min(100, m.sec / duration * 100));
        return '<i class="frp-mark' + (m.kind ? ' ' + m.kind : '') + '" ' +
               'style="left:' + pct + '%" title="' + esc(m.label || '') + '" ' +
               'data-sec="' + m.sec + '"></i>';
      }).join('');
    }

    marksEl.addEventListener('click', function (e) {
      var m = e.target.closest('.frp-mark');
      if (m) { e.stopPropagation(); seekTo(parseFloat(m.dataset.sec)); }
    });

    function paintTime() {
      var cur = video.currentTime || 0;
      var pct = duration ? (cur / duration * 100) : 0;
      fill.style.width = pct + '%';
      timeEl.textContent = toClock(cur) + ' / ' + toClock(duration);
      bar.setAttribute('aria-valuetext', toClock(cur));

      var s = sentenceAt(cur);
      if (s && s !== curSentence) {
        curSentence = s;
        capEl.innerHTML = '<span class="frp-cap-no">Câu ' + s.cau + '</span> ' + esc(s.loi);
        if (trEl) {
          var prev = trEl.querySelector('.frp-line.on');
          if (prev) prev.classList.remove('on');
          var now = trEl.querySelector('.frp-line[data-cau="' + s.cau + '"]');
          if (now) {
            now.classList.add('on');
            now.scrollIntoView({ block: 'nearest' });
          }
        }
        if (opts.onTime) opts.onTime(cur, s);
      }
    }

    video.addEventListener('timeupdate', paintTime);
    video.addEventListener('play',  function () { playBtn.textContent = '❚❚'; });
    video.addEventListener('pause', function () { playBtn.textContent = '▶'; });

    playBtn.addEventListener('click', function () {
      if (video.paused) { var p = video.play(); if (p && p.catch) p.catch(function(){}); }
      else video.pause();
    });
    backBtn.addEventListener('click', function () { seekTo((video.currentTime || 0) - 5); });
    fullBtn.addEventListener('click', function () {
      if (video.requestFullscreen) video.requestFullscreen();
      else if (video.webkitEnterFullscreen) video.webkitEnterFullscreen();
    });

    function barSeek(e) {
      if (!duration) return;
      var r = bar.getBoundingClientRect();
      seekTo((e.clientX - r.left) / r.width * duration);
    }
    bar.addEventListener('click', barSeek);
    bar.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft')  { e.preventDefault(); seekTo((video.currentTime || 0) - 5); }
      if (e.key === 'ArrowRight') { e.preventDefault(); seekTo((video.currentTime || 0) + 5); }
    });

    function seekTo(sec) {
      if (isNaN(sec)) return;
      try { video.currentTime = Math.max(0, sec); } catch (e) {}
      paintTime();
    }

    /* Nhảy tới câu số N theo bảng timecode — dùng ở index.html */
    function seekToSentence(n) {
      return loadTranscript().then(function (d) {
        var hit = d.find(function (l) { return l.cau === Number(n); });
        if (hit) seekTo(toSec(hit.batDau));
        return hit;
      });
    }

    function setMarks(list) { marks = list || []; paintMarks(); }

    return {
      el: root, video: video,
      seekTo: seekTo, seekToSentence: seekToSentence, setMarks: setMarks,
      destroy: function () { try { video.pause(); } catch (e) {} mount.innerHTML = ''; }
    };
  }

  global.FRPlayer = {
    create: create,
    loadTranscript: loadTranscript,
    toSec: toSec,
    toClock: toClock,
    VIDEO_SRC: VIDEO_SRC,
    __lines: []          // transcript đã nạp, đọc đồng bộ được sau loadTranscript()
  };
})(window);
