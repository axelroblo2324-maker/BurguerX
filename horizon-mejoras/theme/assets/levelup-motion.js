/* ==========================================================================
   LevelUP — sistema de movimiento (página de producto)

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

  /* ---------------------------------------------- 1. revelado de texto */

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

  /* --------------------------------- 2. entrada de fotos y de tarjetas */

  // Cada foto de la galería entra al aparecer, que es el movimiento que
  // define esta página: la columna de datos queda fija y las prendas van
  // pasando. Las tarjetas de recomendados usan la misma entrada.
  // Sólo la rejilla: Horizon también renderiza un carrusel con las mismas
  // fotos y la clase .product-media-container, oculto según el ancho. Si se
  // animaran ambos se estarían animando duplicados invisibles.
  var GALERIA = '.media-gallery__grid > .product-media-container';
  var ENTRADA = [
    GALERIA,
    'product-card',
    '.product-card',
    '.resource-list__item'
  ].join(',');

  function esPrimeraFoto(el) {
    var padre = el.parentElement;
    return (
      padre &&
      padre.classList.contains('media-gallery__grid') &&
      el === padre.firstElementChild
    );
  }

  function prepararEntrada(el, indice) {
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

  var PARALLAX = '.media-gallery__grid .product-media__image';

  var capas = [];
  var enCola = false;

  function recogerCapas(raiz) {
    (raiz || document).querySelectorAll(PARALLAX).forEach(function (img) {
      if (img.dataset.luPar) return;
      var caja = img.closest('.product-media') || img.parentElement;
      if (!caja) return;
      img.dataset.luPar = '1';
      caja.classList.add('lu-media');
      capas.push(img);
    });
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
      img.style.setProperty('--lu-py', (desfase * -18).toFixed(1) + 'px');
    });
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

    Array.prototype.forEach.call(ambito.querySelectorAll(ENTRADA), function (el, i) {
      if (!esContenido(el)) return;
      // La primera foto es la que carga con prioridad alta y marca el LCP.
      // Arrancarla en opacidad cero retrasaría lo que el visitante percibe
      // como "la página ya cargó".
      if (esPrimeraFoto(el)) return;
      // Las fotos se recorren de una en una, así que escalonarlas sólo
      // añade retraso; el escalonado es para las tarjetas, que entran en
      // grupo.
      prepararEntrada(el, el.matches(GALERIA) ? 0 : i);
    });

    recogerCapas(ambito === document ? null : ambito);
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
