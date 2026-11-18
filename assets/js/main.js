(function () {
  var b = document.querySelector('.burger'), n = document.getElementById('nav');
  if (b && n) b.addEventListener('click', function () {
    var o = n.classList.toggle('open'); b.setAttribute('aria-expanded', o);
  });
  [].forEach.call(document.querySelectorAll('.sub-t'), function (t) {
    t.addEventListener('click', function () {
      var li = t.parentNode, o = li.classList.toggle('open'); t.setAttribute('aria-expanded', o);
    });
  });
  var grid = document.getElementById('grid');
  if (grid) {
    var cards = [].slice.call(grid.children), f = 'all', q = '', c = document.getElementById('count');
    var run = function () {
      var k = 0;
      cards.forEach(function (x) {
        var ok = (f === 'all' || x.dataset.brand === f) && x.dataset.t.indexOf(q) > -1;
        x.hidden = !ok; if (ok) k++;
      });
      c.textContent = k + (k === 1 ? ' resultado' : ' resultados');
    };
    document.getElementById('filters').addEventListener('click', function (e) {
      var t = e.target.closest('.chip'); if (!t) return;
      [].forEach.call(this.children, function (x) { x.classList.remove('on'); });
      t.classList.add('on'); f = t.dataset.f; run();
    });
    document.getElementById('q').addEventListener('input', function () { q = this.value.trim().toLowerCase(); run(); });
    var porHash = function () {
      var m = { todos: 'all', amd: 'AMD', intel: 'Intel' }, v = m[location.hash.slice(1).toLowerCase()];
      if (!v) return;
      f = v;
      [].forEach.call(document.getElementById('filters').children, function (x) { x.classList.toggle('on', x.dataset.f === v); });
      run();
    };
    porHash(); window.addEventListener('hashchange', porHash);
  }
  document.addEventListener('click', function (e) {
    var i = e.target.closest('img[data-zoom]'); if (!i) return;
    var d = document.createElement('div'); d.className = 'lb'; d.innerHTML = '<img alt="">';
    d.firstChild.src = i.src; d.firstChild.alt = i.alt;
    var h = function (k) { if (k.key === 'Escape') { d.remove(); document.removeEventListener('keydown', h); } };
    d.onclick = function () { d.remove(); document.removeEventListener('keydown', h); };
    document.addEventListener('keydown', h); document.body.appendChild(d);
  });
})();
