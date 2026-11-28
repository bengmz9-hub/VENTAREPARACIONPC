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
  // Móvil: tocar el propio texto de una opción con desplegable lo abre (no navega); la página principal queda dentro del desplegable
  // («Ver todos los servicios», «Todos los equipos»). En escritorio el enlace navega y el submenú sale al pasar el ratón.
  var movil = window.matchMedia('(max-width: 960px)');
  [].forEach.call(document.querySelectorAll('.has-sub > a'), function (a) {
    a.addEventListener('click', function (e) {
      if (!movil.matches) return;
      var t = a.parentNode.querySelector('.sub-t'); if (!t) return;
      e.preventDefault(); e.stopPropagation(); t.click();
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
      c.textContent = k + (k === 1 ? ' resultado' : ' resultados') +
        (orden && orden.value ? (orden.value === 'asc' ? ' · de menor a mayor precio' : ' · de mayor a menor precio') : '');
    };
    document.getElementById('filters').addEventListener('click', function (e) {
      var t = e.target.closest('.chip'); if (!t) return;
      [].forEach.call(this.children, function (x) { x.classList.remove('on'); });
      t.classList.add('on'); f = t.dataset.f; run();
    });
    document.getElementById('q').addEventListener('input', function () { q = this.value.trim().toLowerCase(); run(); });
    // Orden por precio (data-price); "Orden habitual" recupera el orden del HTML. El filtro sigue funcionando porque se mueven los mismos nodos.
    var orden = document.getElementById('orden');
    if (orden) orden.addEventListener('change', function () {
      var v = this.value, lista = cards.slice();
      if (v) lista.sort(function (a, b) { return (a.dataset.price - b.dataset.price) * (v === 'asc' ? 1 : -1); });
      lista.forEach(function (x) { grid.appendChild(x); });
      run();   // el contador (aria-live) anuncia también el orden
    });
    var sortrow = document.getElementById('sortrow');
    if (sortrow) sortrow.hidden = false;   // sin JS el selector no haría nada: solo se muestra si funciona
    // El navegador puede recordar la búsqueda y el orden al recargar: se aplican para que lista y contador cuadren.
    var qi = document.getElementById('q');
    if (qi && qi.value) { q = qi.value.trim().toLowerCase(); run(); }
    if (orden && orden.value) orden.dispatchEvent(new Event('change'));
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

// Barra flotante inferior (solo móvil; mismo comportamiento que la landing de verstats): aparece tras 380 px de scroll,
// se esconde al bajar y reaparece al subir. Lleva Llamar, Pedir cita y una flecha ↑ que vuelve al inicio.
(function () {
  var bar = document.getElementById('m-bar'), up = document.getElementById('m-up');
  if (!bar) return;
  var last = window.scrollY, raf = false;
  if (up) up.addEventListener('click', function () {
    var quiet = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    window.scrollTo({ top: 0, behavior: quiet ? 'auto' : 'smooth' });
  });
  var update = function () {
    var y = window.scrollY;
    if (y > 380) {
      bar.classList.add('visible');
      if (y - last > 10 && y > 500) bar.classList.add('away');
      else if (last - y > 10) bar.classList.remove('away');
    } else {
      bar.classList.remove('visible', 'away');
    }
    last = y; raf = false;
  };
  window.addEventListener('scroll', function () { if (!raf) { raf = true; requestAnimationFrame(update); } }, { passive: true });
  update();
})();

// Menú superior: al bajar más de 24 px pasa de transparente a píldora de cristal (is-scrolled), en todas las páginas.
// En la portada lo hace también home.js; aquí cubre las páginas interiores (el CSS de escritorio está en style.css, sección 8).
(function () {
  var top = document.querySelector('.top');
  if (!top) return;
  var f = function () { top.classList.toggle('is-scrolled', window.scrollY > 24); };
  window.addEventListener('scroll', f, { passive: true });
  f();
})();

// Reseñas: la cuadrícula estática se convierte en dos filas en movimiento (la 2.ª, en sentido contrario y con reseñas distintas a la 1.ª).
// Arrancan siempre solas, sin botones ni paneles. Sin JavaScript queda la cuadrícula estática.
// El HTML conserva cada reseña una sola vez; las únicas copias que se crean aquí son las del bucle de cada fila, con aria-hidden.
(function () {
  var m = document.querySelector('[data-marquee]');
  if (!m) return;
  var grid = m.querySelector('.rv-grid');
  var cards = grid ? [].slice.call(grid.children) : [];
  if (cards.length < 3) return;
  var el = function (c, a) { var d = document.createElement('div'); d.className = c; if (a) for (var k in a) d.setAttribute(k, a[k]); return d; };
  var fila = function (lista, rev, dur, ocultaTodo) {
    var r = el('rv-row' + (rev ? ' rv-rev' : '')), t = el('rv-track');
    t.style.setProperty('--d', dur);
    for (var i = 0; i < 2; i++) {
      var s = el('rv-set', (i || ocultaTodo) ? { 'aria-hidden': 'true' } : null);
      lista.forEach(function (c) { s.appendChild(c.cloneNode(true)); });
      t.appendChild(s);
    }
    r.appendChild(t); return r;
  };
  // Cada fila lleva reseñas distintas: la mitad de arriba y la mitad de abajo (nunca se repite una entre filas).
  var n = Math.ceil(cards.length / 2), arriba = cards.slice(0, n), abajo = cards.slice(n);
  m.classList.add('is-live');
  m.replaceChildren(fila(arriba, false, arriba.length * 11 + 's', false), fila(abajo, true, abajo.length * 11 + 's', false));
  window.dispatchEvent(new Event('rv-montado'));
})();

// Reseñas: las tarjetas tienen altura limitada; si el texto no cabe, se difumina por abajo (clase is-cut). El texto completo sigue en el HTML.
(function () {
  if (!document.querySelector('.rv-card')) return;
  var f = function () { [].forEach.call(document.querySelectorAll('.rv-card blockquote'), function (e) { e.classList.toggle('is-cut', e.scrollHeight > e.clientHeight + 1); }); };
  f();
  window.addEventListener('load', f);
  window.addEventListener('resize', f);
  window.addEventListener('rv-montado', f);
})();
