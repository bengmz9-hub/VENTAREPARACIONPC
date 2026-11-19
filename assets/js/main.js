(function () {
  // Menú móvil: cajón lateral con fondo oscurecido (cierra con ✕, fondo, Escape o al elegir enlace)
  var b = document.querySelector('.burger'), n = document.getElementById('nav'), ov = document.getElementById('nav-ov');
  var cerrarSubs = function (salvo) {
    [].forEach.call(document.querySelectorAll('.has-sub.open'), function (h) {
      if (h === salvo) return;
      h.classList.remove('open');
      var t = h.querySelector('.sub-t'); if (t) t.setAttribute('aria-expanded', false);
    });
  };
  var menu = function (o) {
    n.classList.toggle('open', o); if (ov) ov.classList.toggle('open', o);
    b.setAttribute('aria-expanded', o); b.setAttribute('aria-label', o ? 'Cerrar menú' : 'Abrir menú');
    if (!o) cerrarSubs();
  };
  if (b && n) {
    b.addEventListener('click', function () { menu(!n.classList.contains('open')); });
    if (ov) ov.addEventListener('click', function () { menu(false); });
    n.addEventListener('click', function (e) { if (e.target.closest('a')) menu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && n.classList.contains('open')) { menu(false); b.focus(); }
    });
  }
  [].forEach.call(document.querySelectorAll('.sub-t'), function (t) {
    t.addEventListener('click', function () {
      var li = t.parentNode, o = li.classList.toggle('open'); t.setAttribute('aria-expanded', o);
      if (o) cerrarSubs(li);
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
