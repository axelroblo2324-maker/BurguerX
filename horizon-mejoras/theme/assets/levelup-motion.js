/* ==========================================================================
   LevelUP — sistema de movimiento

   Sin dependencias. Si el visitante pide menos movimiento, el script no
   hace absolutamente nada: no parte títulos, no observa nada y no engancha
   el scroll.
   ========================================================================== */

(function () {
  'use strict';

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  if (window.__levelupMotion) return;
  window.__levelupMotion = true;

  /* ---------------------------------------------------------------- común */

  var observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('lu-in');
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -8% 0px', threshold: 0.05 }
  );

  // El encabezado, el pie y los diálogos no se animan: son navegación, no
  // contenido, y animarlos al abrir un panel se siente lento.
  function esContenido(el) {
    return !el.closest('header, footer, nav, dialog, .header, .footer, [role="dialog"]');
  }

  /* ------------------------------------------- 1. revelado de texto */

  var TITULOS = 'h1, h2, h3';
  var MAX_PALABRAS = 40;

  function partirTitulo(el) {
    if (el.dataset.luSplit) return;
    // Con marcado dentro (enlaces, <strong>) reescribir el contenido lo
    // destruiría, así que esos títulos se dejan como están.
    if (el.children.length) return;

    var texto = el.textContent.trim();
    if (!texto) return;

    var palabras = texto.split(/\s+/);
    if (palabras.length > MAX_PALABRAS) return;

    var fragmento = document.createDocumentFragment();
    palabras.forEach(function (palabra, i) {
      var mascara = document.createElement('span');
      mascara.className = 'lu-word';

      var interior = document.createElement('span');
      interior.textContent = palabra;
      interior.style.setProperty('--lu-d', Math.min(i * 45, 400) + 'ms');

      mascara.appendChild(interior);
      fragmento.appendChild(mascara);
      if (i < palabras.length - 1) {
        fragmento.appendChild(document.createTextNode(' '));
      }
    });

    el.textContent = '';
    el.appendChild(fragmento);
    el.classList.add('lu-split');
    el.dataset.luSplit = '1';
    observer.observe(el);
  }

  /* --------------------------------------------- 2. entrada de tarjetas */

  var TARJETAS = [
    'product-card',
    '.product-card',
    'collection-card',
    '.collection-card',
    '.resource-list__item'
  ].join(',');

  function prepararTarjeta(el, indice) {
    if (el.dataset.luRise) return;
    el.dataset.luRise = '1';
    el.classList.add('lu-rise');
    el.style.setProperty('--lu-d', (indice % 8) * 70 + 'ms');

    // Al terminar se quitan las clases: si el transform se quedara puesto,
    // pelearía con el zoom al pasar el cursor que ya trae el tema.
    el.addEventListener(
      'transitionend',
      function (e) {
        if (e.propertyName !== 'opacity') return;
        el.classList.remove('lu-rise', 'lu-in');
        el.style.removeProperty('--lu-d');
      },
      { once: true }
    );

    observer.observe(el);
  }

  /* ------------------------------------------------------- 3. parallax */

  // Sólo el hero y las tarjetas de categoría. Aplicarlo a cada foto de
  // producto satura la vista y compite con la animación de entrada.
  var PARALLAX = [
    '#shopify-section-hero_main img',
    '#shopify-section-categorias img'
  ].join(',');

  var capas = [];
  var enCola = false;

  function recogerCapas(raiz) {
    (raiz || document).querySelectorAll(PARALLAX).forEach(function (img) {
      if (img.dataset.luPar) return;
      var caja = img.parentElement;
      if (!caja) return;
      img.dataset.luPar = '1';
      caja.classList.add('lu-par');
      img.classList.add('lu-par-img');
      capas.push(img);
    });
  }

  /* ----------------------------------------------- 4. desvanecido del hero */

  // El hero queda fijo por CSS y la página sube encima. Para que no se lea
  // el título del hero a través del hueco mientras eso pasa, su contenido
  // se desvanece y sube al mismo ritmo del scroll.
  var heroContenido = null;

  function prepararHero() {
    if (heroContenido) return;
    var hero = document.getElementById('shopify-section-hero_main');
    if (!hero) return;
    heroContenido =
      hero.querySelector('.hero__content-wrapper') ||
      hero.querySelector('.hero__content');
    if (heroContenido) heroContenido.classList.add('lu-hero-content');
  }

  function pintarHero() {
    if (!heroContenido) return;
    var hero = document.getElementById('shopify-section-hero_main');
    if (!hero) return;

    var caja = hero.getBoundingClientRect();
    // Termina de desvanecerse a media altura del hero: pasado ese punto ya
    // está tapado por la sección siguiente y seguir animando no se ve.
    var recorrido = caja.height * 0.5;
    var avance = recorrido > 0 ? -caja.top / recorrido : 0;
    avance = Math.min(1, Math.max(0, avance));

    heroContenido.style.opacity = String(1 - avance);
    heroContenido.style.transform =
      'translate3d(0, ' + (-avance * 48).toFixed(1) + 'px, 0)';
  }

  function pintarParallax() {
    enCola = false;
    var alto = window.innerHeight;

    capas.forEach(function (img) {
      var caja = img.getBoundingClientRect();
      if (caja.bottom < 0 || caja.top > alto) return;

      // -1 cuando la imagen está saliendo por arriba, 1 cuando va entrando
      // por abajo, 0 justo al centro de la pantalla.
      var centro = caja.top + caja.height / 2;
      var desfase = (centro - alto / 2) / alto;
      img.style.setProperty('--lu-py', (desfase * -16).toFixed(1) + 'px');
    });

    pintarHero();
  }

  function alHacerScroll() {
    if (enCola) return;
    enCola = true;
    requestAnimationFrame(pintarParallax);
  }

  /* ------------------------------------------------------------ arranque */

  function iniciar(raiz) {
    var ambito = raiz && raiz.querySelectorAll ? raiz : document;

    Array.prototype.forEach.call(ambito.querySelectorAll(TITULOS), function (el) {
      if (esContenido(el)) partirTitulo(el);
    });

    Array.prototype.forEach.call(ambito.querySelectorAll(TARJETAS), function (el, i) {
      if (esContenido(el)) prepararTarjeta(el, i);
    });

    recogerCapas(ambito === document ? null : ambito);
    prepararHero();
    pintarParallax();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      iniciar();
    });
  } else {
    iniciar();
  }

  window.addEventListener('scroll', alHacerScroll, { passive: true });
  window.addEventListener('resize', alHacerScroll, { passive: true });
  window.addEventListener('pageshow', function () {
    iniciar();
  });

  // El editor de temas vuelve a montar secciones sueltas sin recargar.
  document.addEventListener('shopify:section:load', function (e) {
    iniciar(e.target);
  });
})();
