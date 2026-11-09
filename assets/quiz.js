// assets/quiz.js — reusable instant-feedback quiz widget.
// Author markup like:
//   <div class="quiz" data-quiz>
//     <div class="q">
//       <p class="q-text">Question?</p>
//       <button class="opt" data-ok>correct answer</button>
//       <button class="opt">distractor</button>
//       <div class="explain">Why the answer is what it is.</div>
//     </div>
//   </div>
// Options are shuffled on load, so authored order never hints at the answer.
(function () {
  "use strict";
  document.querySelectorAll("[data-quiz] .q").forEach(function (q) {
    var opts = Array.prototype.slice.call(q.querySelectorAll(".opt"));
    for (var i = opts.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = opts[i]; opts[i] = opts[j]; opts[j] = tmp;
    }
    opts.forEach(function (o) {
      q.insertBefore(o, q.querySelector(".explain"));
      o.addEventListener("click", function () {
        if (q.classList.contains("answered")) return;
        q.classList.add("answered");
        var right = o.hasAttribute("data-ok");
        o.classList.add(right ? "correct" : "wrong");
        if (!right) {
          var ok = q.querySelector(".opt[data-ok]");
          if (ok) ok.classList.add("correct");
        }
      });
    });
  });
})();
