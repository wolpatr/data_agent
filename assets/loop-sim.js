// assets/loop-sim.js — one-widget simulator of the trading agent loop:
// OBSERVE (price) → DECIDE (EMA crossover) → EXECUTE (market order) → EVALUATE (log P&L).
// Markup: <div data-loop-sim></div>. No dependencies, plain canvas.
(function () {
  "use strict";

  function emaArr(values, n) {
    var k = 2 / (n + 1), out = [], e = null;
    for (var i = 0; i < values.length; i++) {
      e = i === 0 ? values[i] : values[i] * k + e * (1 - k);
      out.push(e);
    }
    return out;
  }

  function makeSim(host) {
    var PHASES = ["OBSERVE", "DECIDE", "EXECUTE", "EVALUATE"];
    var prices, drift, cash, qty, entry, tradeCount, wins, tickNo, playing;

    host.innerHTML =
      '<div class="sim-controls">' +
      '<label>Fast EMA <input data-fast type="number" min="2" max="30" value="5"></label>' +
      '<label>Slow EMA <input data-slow type="number" min="4" max="60" value="20"></label>' +
      '<button data-step>Advance 1 cycle</button>' +
      '<button data-play>Autoplay</button>' +
      '<button data-reset>Reset</button>' +
      "</div>" +
      '<div class="sim-stage"><div class="sim-phase" data-phase></div>' +
      '<canvas class="sim-canvas" data-canvas></canvas>' +
      '<div class="sim-stats" data-stats></div></div>' +
      '<div class="sim-log" data-log></div>';

    var el = {
      canvas: host.querySelector("[data-canvas]"),
      phase: host.querySelector("[data-phase]"),
      stats: host.querySelector("[data-stats]"),
      log: host.querySelector("[data-log]"),
      fast: host.querySelector("[data-fast]"),
      slow: host.querySelector("[data-slow]"),
    };

    function seed() {
      drift = 0.0004; cash = 10000; qty = 0; entry = 0;
      tradeCount = 0; wins = 0; tickNo = 0; playing = null;
      prices = [];
      var p = 60000;
      for (var i = 0; i < 40; i++) {
        p *= 1 + (Math.random() - 0.5) * 0.008;
        prices.push(p);
      }
      logElAdd("cycle 0  seed filled, agent starting…", "hold");
    }

    function logElAdd(text, cls) {
      var d = document.createElement("div");
      d.className = cls || "";
      d.textContent = text;
      el.log.insertBefore(d, el.log.firstChild);
    }

    function step() {
      tickNo++;
      if (Math.random() < 0.02) drift = (Math.random() - 0.5) * 0.0035; // regime shift
      var p = prices[prices.length - 1] * (1 + drift + (Math.random() - 0.5) * 0.012);
      prices.push(p);
      if (prices.length > 460) prices.shift();

      var fastLen = clamp(+el.fast.value || 5, 2, 30);
      var slowLen = clamp(+el.slow.value || 20, fastLen + 2, 60);
      el.slow.value = slowLen;
      var f = emaArr(prices, fastLen), s = emaArr(prices, slowLen);
      var fNow = f[f.length - 1], fPrev = f[f.length - 2];
      var sNow = s[s.length - 1], sPrev = s[s.length - 2];
      var crossUp = fPrev <= sPrev && fNow > sNow;
      var crossDown = fPrev >= sPrev && fNow < sNow;

      // DECIDE
      var action = (crossUp && qty === 0) ? "BUY" : (crossDown && qty > 0) ? "SELL" : "HOLD";

      // EXECUTE
      var exec = "";
      if (action === "BUY") {
        qty = cash / p; entry = p; cash = 0;
        exec = "bought " + qty.toFixed(4) + " BTC @ $" + fmt(p);
        logElAdd("cycle " + tickNo + "  BUY   " + exec + "  (EMA fast crossed above slow)", "buy");
      } else if (action === "SELL") {
        var pnl = (p - entry) / entry * 100;
        cash = qty * p; qty = 0;
        exec = "closed @ $" + fmt(p) + " (" + pnl.toFixed(2) + "%)";
        tradeCount++; if (pnl > 0) wins++;
        logElAdd("cycle " + tickNo + "  SELL  " + exec + "  (EMA fast crossed below slow)", "sell");
      } else {
        exec = "no order";
        logElAdd("cycle " + tickNo + "  HOLD  no signal / already positioned", "hold");
      }

      // EVALUATE
      var equity = cash + qty * p;
      el.phase.innerHTML =
        PHASES[0] + " <b>$" + fmt(p) + "</b> → " +
        PHASES[1] + ": <b>" + action + "</b> → " +
        PHASES[2] + ": " + exec + " → " +
        PHASES[3] + ": <b>equity $" + fmt(equity) + "</b>";
      el.stats.innerHTML =
        "cash <b>$" + fmt(cash) + "</b> · BTC <b>" + (qty ? qty.toFixed(4) : "0.0000") +
        "</b> · equity <b>$" + fmt(equity) + "</b> · trades <b>" + tradeCount +
        "</b> · win rate <b>" + (tradeCount ? Math.round(wins / tradeCount * 100) + "%" : "—") + "</b>";
      renderChart(f, s);
    }

    function clamp(v, lo, hi) { return Math.min(hi, Math.max(lo, v)); }
    function fmt(v) { return v.toLocaleString("en-US", { maximumFractionDigits: 0 }); }

    function renderChart(f, s) {
      var dpr = window.devicePixelRatio || 1;
      var w = el.canvas.clientWidth || el.canvas.parentElement.clientWidth || 600;
      var h = 260;
      el.canvas.width = w * dpr; el.canvas.height = h * dpr;
      var ctx = el.canvas.getContext("2d");
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, w, h);

      var N = Math.min(240, prices.length);
      var pf = prices.slice(-N), ff = f.slice(-N), sf = s.slice(-N);
      var lo = Math.min.apply(null, pf.concat(ff, sf));
      var hi = Math.max.apply(null, pf.concat(ff, sf));
      var pad = (hi - lo) * 0.06 || 1; lo -= pad; hi += pad;

      function X(i) { return (i / (N - 1)) * (w - 8) + 4; }
      function Y(v) { return h - 20 - ((v - lo) / (hi - lo)) * (h - 34) + 10; }

      ctx.strokeStyle = "#e5e0d5";
      ctx.beginPath(); ctx.moveTo(4, Y(lo)); ctx.lineTo(w - 4, Y(lo)); ctx.stroke();
      ctx.fillStyle = "#6b675e"; ctx.font = "11px monospace";
      ctx.fillText("$" + fmt(lo), 6, h - 28);

      function line(arr, color, width) {
        ctx.strokeStyle = color; ctx.lineWidth = width; ctx.beginPath();
        arr.forEach(function (v, i) { i ? ctx.lineTo(X(i), Y(v)) : ctx.moveTo(X(0), Y(v)); });
        ctx.stroke();
      }
      line(sf, "#2e7d43", 1.6);
      line(ff, "#1d7fc4", 1.6);
      line(pf, "#22211d", 2);

      ctx.fillStyle = "#6b675e"; ctx.font = "11px sans-serif";
      ctx.fillText("price", w - 70, 14);
      ctx.fillStyle = "#1d7fc4"; ctx.fillText("EMA fast", w - 70, 28);
      ctx.fillStyle = "#2e7d43"; ctx.fillText("EMA slow", w - 70, 42);
    }

    function reset() { stopPlay(); seed(); renderChart(emaArr(prices, +el.fast.value), emaArr(prices, +el.slow.value)); step(); logElAdd("cycle 0  reset", "hold"); }
    function stopPlay() { if (playing) { clearInterval(playing); playing = null; host.querySelector("[data-play]").textContent = "Autoplay"; } }

    host.querySelector("[data-step]").addEventListener("click", step);
    host.querySelector("[data-reset]").addEventListener("click", reset);
    host.querySelector("[data-play]").addEventListener("click", function () {
      if (playing) { stopPlay(); return; }
      this.textContent = "Pause";
      playing = setInterval(step, 700);
    });

    seed();
    renderChart(emaArr(prices, 5), emaArr(prices, 20));
    window.addEventListener("resize", function () { renderChart(emaArr(prices, 5), emaArr(prices, 20)); });
  }

  document.querySelectorAll("[data-loop-sim]").forEach(makeSim);
})();
