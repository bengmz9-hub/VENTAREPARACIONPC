/* Portada VRPC · navbar al hacer scroll, cortina de la Pantalla 2, montaje y resaltado de la Pantalla 3 */
(function () {
      var topBar = document.querySelector('.top');
      var s2 = document.getElementById('pantalla-2');
      var cue = document.getElementById('scrollCue');
      if (!s2) return;

      /* Seguidor radial especular 2D en tarjetas Liquid Glass (0° 3D tilt) */
      [].forEach.call(document.querySelectorAll('[data-glass]'), function (card) {
        card.addEventListener('pointermove', function (e) {
          var r = card.getBoundingClientRect();
          card.style.setProperty('--mouse-x', (e.clientX - r.left).toFixed(1) + 'px');
          card.style.setProperty('--mouse-y', (e.clientY - r.top).toFixed(1) + 'px');
        }, { passive: true });
      });

      var desktop = window.matchMedia('(min-width: 961px)');
      var curtains = [].slice.call(s2.querySelectorAll('[data-reveal="curtain"]'));
      var cards = [].slice.call(s2.querySelectorAll('[data-reveal="left"]'));

      function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
      function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

      function setStatic() {
        document.documentElement.classList.remove('js-scroll');
        document.documentElement.setAttribute('data-motion', 'off');
        cards.forEach(function (el) {
          ['--p-o','--p-x','--p-y','--p-s'].forEach(function (k) { el.style.removeProperty(k); });
        });
        curtains.forEach(function (el) {
          ['--c-o','--c-x','--c-clip'].forEach(function (k) { el.style.removeProperty(k); });
        });
      }

      /* SEO: hasta el primer scroll real todo el texto está visible (Google no hace scroll) */
      var userScrolled = false;
      var rafId = 0;
      function update() {
        rafId = 0;
        var vh = window.innerHeight || 1;
        var scrollY = window.scrollY || window.pageYOffset;
        var maxScroll = Math.max(1, document.documentElement.scrollHeight - vh);

        if (topBar) topBar.classList.toggle('is-scrolled', scrollY > 24);
        if (cue) cue.classList.toggle('is-hidden', scrollY > 36);

        if (!desktop.matches || !userScrolled) {
          setStatic();
          return;
        }

        /* Fase de lectura de layout (evita layout thrashing al mezclar lecturas y escrituras) */
        var s2Rect = s2.getBoundingClientRect();
        var s2Top = s2Rect.top;
        var s2Bottom = s2Rect.bottom + scrollY;
        var limitScroll = Math.min(maxScroll, Math.max(0, s2Bottom - vh));
        var curtainTops = curtains.map(function (el) { return el.getBoundingClientRect().top; });

        /* Fase de escritura en estilos */
        document.documentElement.setAttribute('data-motion', 'on');
        document.documentElement.classList.add('js-scroll');

        /* 1) Cortina por elemento basada en su posición real dentro del viewport:
              entra cerrada al 100% por abajo y se abre visiblemente frente al usuario al subir */
        curtains.forEach(function (el, idx) {
          var rectTop = curtainTops[idx];
          var absTop = rectTop + scrollY;
          var topAtBottom = absTop - limitScroll;   /* posición de la línea en pantalla en ese límite */
          /* termina 36px de scroll antes del límite, y nunca más arriba del 42% de la ventana */
          var finishY = Math.min(vh, Math.max(vh * 0.42, topAtBottom + 36));
          var startY = Math.min(vh * 1.02, finishY + vh * 0.34);
          var raw = (startY - rectTop) / Math.max(40, startY - finishY);
          var t = clamp(raw, 0, 1);
          var e = easeOutCubic(t);

          var clipRight = (1 - e) * 100;
          var shiftX = -(1 - e) * 32;
          el.style.setProperty('--c-o', (0.05 + e * 0.95).toFixed(3));
          el.style.setProperty('--c-x', shiftX.toFixed(1) + 'px');
          el.style.setProperty('--c-clip', clipRight.toFixed(1) + '%');
        });

        /* 2) Tarjetas Liquid Glass a la izquierda: aparecen progresivamente al entrar Pantalla 2 */
        var panelProg = clamp((vh * 0.92 - s2Top) / (vh * 0.82), 0, 1);
        cards.forEach(function (el) {
          var idx = parseInt(el.dataset.order || '0', 10);
          var st = idx * 0.14;
          var en = Math.min(1, st + 0.56);
          var t = clamp((panelProg - st) / Math.max(0.01, en - st), 0, 1);
          var e = easeOutCubic(t);
          el.style.setProperty('--p-o', e.toFixed(3));
          el.style.setProperty('--p-x', ((1 - e) * 44).toFixed(1) + 'px');
          el.style.setProperty('--p-y', ((1 - e) * 16).toFixed(1) + 'px');
          el.style.setProperty('--p-s', (0.96 + e * 0.04).toFixed(4));
        });
      }

      function onScroll(e) {
        if (e && e.type === 'scroll') userScrolled = true;
        if (!rafId) rafId = window.requestAnimationFrame(update);
      }

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      if (desktop.addEventListener) desktop.addEventListener('change', onScroll);
      update();
    })();

(function () {
      /* Ventiladores de 120 mm dibujados por código (marco, aspas curvas, anillo ARGB) */
      var NS = 'http://www.w3.org/2000/svg';
      function el(tag, attrs, parent) { var e = document.createElementNS(NS, tag); for (var k in attrs) e.setAttribute(k, attrs[k]); parent.appendChild(e); return e; }
      [].forEach.call(document.querySelectorAll('#fans .fan'), function (g) {
        var cx = +g.dataset.cx, cy = +g.dataset.cy, r = +g.dataset.r, s = r / 50;
        el('rect', { x: cx - r, y: cy - r, width: r * 2, height: r * 2, rx: r * .22, fill: '#0c1018', stroke: '#2a3141', 'stroke-width': 2 }, g);
        el('circle', { 'class': 'glow argbc', cx: cx, cy: cy, r: r * .86, fill: 'none', stroke: 'currentColor', 'stroke-width': 12, filter: 'url(#fGlow)' }, g);
        el('circle', { 'class': 'argbc', cx: cx, cy: cy, r: r * .86, fill: '#06080c', stroke: 'currentColor', 'stroke-width': 3.5 }, g);
        var blades = el('g', { 'class': 'fan-blade' }, g);
        for (var i = 0; i < 9; i++) {
          el('path', { d: 'M0 -9 C 14 -44, 40 -40, 42 -14 C 30 -18, 16 -16, 0 -9 Z', fill: '#1d2330', stroke: '#3a4458', 'stroke-width': .8,
            transform: 'translate(' + cx + ' ' + cy + ') rotate(' + (i * 40) + ') scale(' + s + ')' }, blades);
        }
        el('circle', { cx: cx, cy: cy, r: r * .2, fill: '#141922', stroke: '#3a4458' }, g);
        el('circle', { 'class': 'argbc', cx: cx, cy: cy, r: r * .08, fill: 'currentColor' }, g);
        [[-1, -1], [1, -1], [-1, 1], [1, 1]].forEach(function (c) { el('circle', { cx: cx + c[0] * r * .8, cy: cy + c[1] * r * .8, r: 2.4, fill: '#3a4255' }, g); });
      });

      var sec = document.getElementById('pantalla-3');
      var rig = document.getElementById('rig');
      var pct = document.getElementById('rigPct');
      var parts = [].slice.call(sec.querySelectorAll('.part'));
      var items = [].slice.call(document.querySelectorAll('#steps3 li'));
      var N = items.length;
      var DURATION = 1500; /* ms: montaje completo a velocidad constante */
      var raf = 0, played = false;

      function clamp(v, a, b) { return v < a ? a : v > b ? b : v; }
      function ease(t) { return 1 - Math.pow(1 - t, 3); }

      /* Estado "montado": lo que ve Google y cualquiera antes de que empiece la animación */
      function assembled() {
        document.documentElement.classList.remove('js-anim');
        parts.forEach(function (p) { ['--o','--x','--y','--r','--s'].forEach(function (k) { p.style.removeProperty(k); }); });
        items.forEach(function (li) { li.classList.remove('act', 'done'); });
        rig.classList.add('on');
        if (pct) pct.textContent = '';
      }

      function render(prog) {
        document.documentElement.classList.add('js-anim');
        var seg = 0.9 / N; /* el 10 % final es para encender el PC */
        parts.forEach(function (p) {
          var i = +p.dataset.step;
          var t = ease(clamp((prog - i * seg) / seg, 0, 1));
          var f = p.dataset.from.split(',');
          p.style.setProperty('--o', (t < .02 ? 0 : .25 + t * .75).toFixed(3));
          p.style.setProperty('--x', ((1 - t) * f[0]).toFixed(1) + 'px');
          p.style.setProperty('--y', ((1 - t) * f[1]).toFixed(1) + 'px');
          p.style.setProperty('--r', ((1 - t) * (i % 2 ? 8 : -8)).toFixed(2) + 'deg');
          p.style.setProperty('--s', (.9 + t * .1).toFixed(3));
        });
        var act = Math.min(N - 1, Math.floor(prog / seg));
        items.forEach(function (li, i) {
          li.classList.toggle('act', i === act && prog < .9);
          li.classList.toggle('done', i < act || prog >= .9);
        });
        rig.classList.toggle('on', prog >= .9);
        if (pct) pct.textContent = Math.round(prog * 100) + '%';
      }

      function play() {
        cancelAnimationFrame(raf);
        played = true;
        var t0 = performance.now();
        render(0);
        (function tick(now) {
          var prog = clamp((now - t0) / DURATION, 0, 1);
          render(prog);
          if (prog < 1) raf = requestAnimationFrame(tick);
          else setTimeout(function () { if (pct) pct.textContent = ''; }, 900);
        })(t0);
      }

      /* Arranca sola cuando la sección se ve; sin depender del scroll */
      if ('IntersectionObserver' in window) {
        new IntersectionObserver(function (entries, obs) {
          entries.forEach(function (e) {
            if (e.isIntersecting && !played) { play(); obs.disconnect(); }
          });
        }, { threshold: .35 }).observe(rig);
      }
      var again = document.getElementById('again');
      if (again) again.addEventListener('click', play);
      assembled();
    })();

/* Pantalla 3 · resaltar la pieza del paso bajo el ratón */
    (function () {
      var rig = document.getElementById('rig');
      var items = [].slice.call(document.querySelectorAll('#steps3 li'));
      if (!rig || !items.length) return;
      var parts = [].slice.call(rig.querySelectorAll('.part'));
      function on(i) {
        rig.classList.add('focus');
        parts.forEach(function (p) { p.classList.toggle('hl', +p.dataset.step === i); });
        items.forEach(function (li, k) { li.classList.toggle('hov', k === i); });
      }
      function off() {
        rig.classList.remove('focus');
        parts.forEach(function (p) { p.classList.remove('hl'); });
        items.forEach(function (li) { li.classList.remove('hov'); });
      }
      items.forEach(function (li, i) {
        li.addEventListener('mouseenter', function () { on(i); });
        li.addEventListener('focus', function () { on(i); });
        li.addEventListener('mouseleave', off);
        li.addEventListener('blur', off);
      });
    })();

    /* Pantalla 3 (solo escritorio): centra la caja del montaje con el texto «título → botones».
       La fila del texto incluye arriba la línea pequeña «PC GAMING A MEDIDA»; la caja se baja la mitad de la distancia
       entre el inicio de la fila y el título, de modo que su centro coincide con el centro del texto. */
    (function () {
      var rig = document.querySelector('.s3 .rig'), title = document.getElementById('s3-title'), row = document.querySelector('.s3-top');
      if (!rig || !title || !row) return;
      var desktop = window.matchMedia('(min-width: 961px)');
      function fit() {
        if (!desktop.matches) { rig.style.removeProperty('--rig-dy'); return; }
        var dy = (title.getBoundingClientRect().top - row.getBoundingClientRect().top) / 2;
        rig.style.setProperty('--rig-dy', Math.max(0, Math.round(dy)) + 'px');
      }
      fit();
      window.addEventListener('resize', fit, { passive: true });
      window.addEventListener('load', fit);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    })();
