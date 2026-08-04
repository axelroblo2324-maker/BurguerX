/* ==========================================================================
   Atelier Editorial — utilidades globales
   JavaScript nativo, sin dependencias. Cada pieza es un módulo independiente.
   ========================================================================== */

(function () {
  'use strict';

  const config = window.themeConfig || {};
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* ----------------------------- Utilidades ------------------------------ */

  const Theme = (window.Theme = window.Theme || {});

  Theme.debounce = function debounce(fn, wait) {
    let timer;
    return function debounced(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), wait);
    };
  };

  Theme.fetchConfig = function fetchConfig(type = 'json') {
    return {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: `application/${type}`
      }
    };
  };

  Theme.formatMoney = function formatMoney(cents, format) {
    const template = format || config.moneyFormat || '${{amount}}';
    const value = typeof cents === 'string' ? parseFloat(cents.replace('.', '')) : cents;

    function withDelimiters(number, precision = 2, thousands = ',', decimal = '.') {
      if (isNaN(number) || number === null) return '0';
      const fixed = (number / 100).toFixed(precision);
      const parts = fixed.split('.');
      const dollars = parts[0].replace(/(\d)(?=(\d\d\d)+(?!\d))/g, `$1${thousands}`);
      const cts = parts[1] ? decimal + parts[1] : '';
      return dollars + cts;
    }

    const placeholder = /\{\{\s*(\w+)\s*\}\}/;
    const match = template.match(placeholder);
    if (!match) return template;

    let formatted;
    switch (match[1]) {
      case 'amount_no_decimals':
        formatted = withDelimiters(value, 0);
        break;
      case 'amount_with_comma_separator':
        formatted = withDelimiters(value, 2, '.', ',');
        break;
      case 'amount_no_decimals_with_comma_separator':
        formatted = withDelimiters(value, 0, '.', ',');
        break;
      case 'amount_with_space_separator':
        formatted = withDelimiters(value, 2, ' ', ',');
        break;
      case 'amount_no_decimals_with_space_separator':
        formatted = withDelimiters(value, 0, ' ', ',');
        break;
      default:
        formatted = withDelimiters(value, 2);
    }

    return template.replace(placeholder, formatted);
  };

  Theme.bumpCartIcon = function bumpCartIcon() {
    if (prefersReducedMotion.matches) return;
    const icon = document.querySelector('[data-cart-icon]');
    if (!icon) return;
    icon.classList.remove('is-bumping');
    void icon.offsetWidth;
    icon.classList.add('is-bumping');
  };

  const FOCUSABLE =
    'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])';

  Theme.getFocusable = function getFocusable(container) {
    return Array.from(container.querySelectorAll(FOCUSABLE)).filter(
      (el) => el.offsetParent !== null || el === document.activeElement
    );
  };

  Theme.trapFocus = function trapFocus(container, event) {
    if (event.key !== 'Tab') return;
    const focusable = Theme.getFocusable(container);
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  /* ------------------------- Bloqueo de scroll --------------------------- */

  let scrollLocks = 0;
  let savedScrollY = 0;

  Theme.lockScroll = function lockScroll() {
    scrollLocks += 1;
    if (scrollLocks > 1) return;
    savedScrollY = window.scrollY;
    const scrollbar = window.innerWidth - document.documentElement.clientWidth;
    document.body.style.paddingRight = scrollbar > 0 ? `${scrollbar}px` : '';
    document.body.classList.add('overflow-hidden');
  };

  Theme.unlockScroll = function unlockScroll() {
    scrollLocks = Math.max(0, scrollLocks - 1);
    if (scrollLocks > 0) return;
    document.body.classList.remove('overflow-hidden');
    document.body.style.paddingRight = '';
    void savedScrollY;
  };

  /* ------------------------------ Scrim ---------------------------------- */

  const Scrim = {
    element: null,
    owners: new Set(),
    get node() {
      if (!this.element) this.element = document.querySelector('[data-scrim]');
      return this.element;
    },
    show(owner) {
      const node = this.node;
      if (!node) return;
      this.owners.add(owner);
      node.hidden = false;
      requestAnimationFrame(() => node.classList.add('is-active'));
      node.onclick = () => {
        this.owners.forEach((item) => {
          if (typeof item.close === 'function') item.close();
        });
      };
    },
    hide(owner) {
      const node = this.node;
      if (!node) return;
      this.owners.delete(owner);
      if (this.owners.size) return;
      node.classList.remove('is-active');
      const done = () => {
        if (!this.owners.size) node.hidden = true;
        node.removeEventListener('transitionend', done);
      };
      node.addEventListener('transitionend', done);
      setTimeout(done, 400);
    }
  };

  Theme.Scrim = Scrim;

  /* --------------------------- Panel deslizante --------------------------- */

  class ThemePanel extends HTMLElement {
    constructor() {
      super();
      this.onKeydown = this.onKeydown.bind(this);
      this.isOpen = false;
    }

    connectedCallback() {
      this.querySelectorAll('[data-panel-close]').forEach((button) => {
        button.addEventListener('click', () => this.close());
      });
    }

    open(trigger) {
      if (this.isOpen) return;
      this.isOpen = true;
      this.opener = trigger || document.activeElement;
      this.hidden = false;
      Theme.lockScroll();
      Scrim.show(this);
      requestAnimationFrame(() => {
        this.classList.add('is-open');
        this.setAttribute('aria-hidden', 'false');
        const focusTarget =
          this.querySelector('[data-panel-focus]') || Theme.getFocusable(this)[0];
        if (focusTarget) {
          window.setTimeout(() => focusTarget.focus({ preventScroll: true }), 60);
        }
      });
      document.addEventListener('keydown', this.onKeydown);
      this.dispatchEvent(new CustomEvent('panel:open', { bubbles: true }));
    }

    close() {
      if (!this.isOpen) return;
      this.isOpen = false;
      this.classList.remove('is-open');
      this.setAttribute('aria-hidden', 'true');
      Theme.unlockScroll();
      Scrim.hide(this);
      document.removeEventListener('keydown', this.onKeydown);
      if (this.opener && document.contains(this.opener)) {
        this.opener.focus({ preventScroll: true });
      }
      const finish = () => {
        if (!this.isOpen) this.hidden = true;
        this.removeEventListener('transitionend', finish);
      };
      this.addEventListener('transitionend', finish);
      window.setTimeout(finish, 450);
      this.dispatchEvent(new CustomEvent('panel:close', { bubbles: true }));
    }

    toggle(trigger) {
      if (this.isOpen) this.close();
      else this.open(trigger);
    }

    onKeydown(event) {
      if (event.key === 'Escape') {
        event.stopPropagation();
        this.close();
        return;
      }
      Theme.trapFocus(this, event);
    }
  }

  Theme.ThemePanel = ThemePanel;
  if (!customElements.get('theme-panel')) customElements.define('theme-panel', ThemePanel);

  /* ------------------------- Botones que abren paneles -------------------- */

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-panel-trigger]');
    if (!trigger) return;
    const target = document.getElementById(trigger.getAttribute('data-panel-trigger'));
    if (!target || typeof target.open !== 'function') return;
    event.preventDefault();
    target.toggle(trigger);
  });

  /* ---------------------------- Menú de celular --------------------------- */

  class MenuDrawer extends ThemePanel {}
  if (!customElements.get('menu-drawer')) customElements.define('menu-drawer', MenuDrawer);

  /* ------------------------------ Encabezado ------------------------------ */

  class HeaderController {
    constructor(wrapper) {
      this.wrapper = wrapper;
      this.allowTransparent = wrapper.hasAttribute('data-allow-transparent');
      this.hideOnScroll = wrapper.hasAttribute('data-hide-on-scroll');
      this.lastY = window.scrollY;
      this.threshold = 8;
      this.overlaySection = null;

      this.setHeight();
      this.setupTransparency();
      this.onScroll = this.onScroll.bind(this);
      window.addEventListener('scroll', this.onScroll, { passive: true });
      window.addEventListener('resize', Theme.debounce(() => {
        this.setHeight();
        this.measureOverlay();
      }, 150));

      if ('ResizeObserver' in window) {
        this.resizeObserver = new ResizeObserver(() => this.setHeight());
        this.resizeObserver.observe(this.wrapper);
      }

      this.onScroll();
    }

    setHeight() {
      const height = this.wrapper.offsetHeight;
      document.documentElement.style.setProperty('--header-height', `${height}px`);
    }

    setupTransparency() {
      if (!this.allowTransparent) return;
      const main = document.getElementById('MainContent');
      if (!main) return;
      const firstSection = main.querySelector(':scope > .shopify-section');
      if (!firstSection) return;
      const flag = firstSection.querySelector('[data-header-transparent="true"]');
      if (!flag) return;

      this.overlaySection = firstSection;
      this.wrapper.classList.add('header-wrapper--transparent');
      document.body.classList.add('header-is-overlay');

      const color = flag.getAttribute('data-header-color');
      if (color) {
        this.wrapper.style.setProperty('--transparent-header-color', color);
        if (color.toLowerCase() !== '#0a0a0a') this.wrapper.classList.add('has-light-logo');
      } else {
        this.wrapper.classList.add('has-light-logo');
      }
      this.measureOverlay();
    }

    measureOverlay() {
      if (!this.overlaySection) return;
      this.overlayEnd =
        this.overlaySection.offsetTop + this.overlaySection.offsetHeight - this.wrapper.offsetHeight;
    }

    onScroll() {
      const y = window.scrollY;

      if (this.overlaySection) {
        if (this.overlayEnd === undefined) this.measureOverlay();
        this.wrapper.classList.toggle('is-stuck', y > this.overlayEnd);
      } else {
        this.wrapper.classList.toggle('header-wrapper--bordered', y > this.threshold);
      }

      if (this.hideOnScroll) {
        const goingDown = y > this.lastY && y > this.wrapper.offsetHeight * 2;
        const anyPanelOpen = document.body.classList.contains('overflow-hidden');
        this.wrapper.classList.toggle('header-wrapper--hidden', goingDown && !anyPanelOpen);
      }

      this.lastY = y;
    }

    destroy() {
      window.removeEventListener('scroll', this.onScroll);
      if (this.resizeObserver) this.resizeObserver.disconnect();
    }
  }

  let headerController = null;

  function initHeader() {
    const wrapper = document.querySelector('[data-header-wrapper]');
    if (!wrapper) return;
    if (headerController) headerController.destroy();
    headerController = new HeaderController(wrapper);
  }

  /* ------------------------ Apariciones al desplazar ---------------------- */

  let revealObserver = null;

  const REVEAL_SELECTOR = '[data-reveal], [data-reveal-lines], [data-reveal-words]';

  // Parte un titular en palabras para que entren escalonadas. Sólo actúa sobre
  // elementos de puro texto: si el titular trae marcado propio se deja intacto
  // en lugar de reconstruirlo mal.
  function splitWords(el) {
    if (el.dataset.wordsSplit === 'true') return;
    if (el.children.length) return;
    const text = el.textContent.replace(/\s+/g, ' ').trim();
    if (!text) return;

    el.dataset.wordsSplit = 'true';
    const words = text.split(' ');
    const fragment = document.createDocumentFragment();

    words.forEach((word, index) => {
      const mask = document.createElement('span');
      mask.className = 'reveal-word';
      const inner = document.createElement('span');
      inner.textContent = word;
      inner.style.setProperty('--word-index', String(index));
      mask.appendChild(inner);
      fragment.appendChild(mask);
      if (index < words.length - 1) fragment.appendChild(document.createTextNode(' '));
    });

    el.textContent = '';
    el.appendChild(fragment);
  }

  function initReveals(root = document) {
    if (config.animations === false) {
      document.body.classList.add('animations-off');
      root.querySelectorAll(REVEAL_SELECTOR).forEach((el) => {
        el.classList.add('is-revealed');
      });
      return;
    }

    if (prefersReducedMotion.matches) {
      root.querySelectorAll(REVEAL_SELECTOR).forEach((el) => {
        el.classList.add('is-revealed');
      });
      return;
    }

    if (!('IntersectionObserver' in window)) {
      root.querySelectorAll(REVEAL_SELECTOR).forEach((el) => {
        el.classList.add('is-revealed');
      });
      return;
    }

    if (!revealObserver) {
      revealObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-revealed');
            revealObserver.unobserve(entry.target);
          });
        },
        { rootMargin: '0px 0px -8% 0px', threshold: 0.06 }
      );
    }

    root.querySelectorAll(REVEAL_SELECTOR).forEach((el) => {
      if (el.classList.contains('is-revealed')) return;
      if (el.hasAttribute('data-reveal-words')) splitWords(el);
      revealObserver.observe(el);
    });
  }

  Theme.initReveals = initReveals;

  /* -------------------------------- Parallax ------------------------------ */

  let parallaxItems = [];
  let parallaxTicking = false;
  let parallaxListening = false;

  function updateParallax() {
    parallaxTicking = false;
    const viewportHeight = window.innerHeight;
    parallaxItems.forEach((item) => {
      const rect = item.el.getBoundingClientRect();
      if (rect.bottom < -200 || rect.top > viewportHeight + 200) return;
      const progress = (rect.top + rect.height / 2 - viewportHeight / 2) / viewportHeight;
      const shift = -progress * item.strength;
      item.target.style.transform = `translate3d(0, ${shift.toFixed(2)}px, 0)`;
    });
  }

  function requestParallax() {
    if (parallaxTicking) return;
    parallaxTicking = true;
    requestAnimationFrame(updateParallax);
  }

  function initParallax(root = document) {
    // El parallax de secciones interiores se reserva a escritorio; el de la
    // portada (data-parallax-always) también corre en celular, donde es el
    // único movimiento ligado al scroll de esa pantalla.
    const allowed =
      config.parallax !== false && !prefersReducedMotion.matches;
    const isDesktop = window.matchMedia('(min-width: 990px)').matches;

    const nodes = Array.from(root.querySelectorAll('[data-parallax]'));

    nodes.forEach((el) => {
      const enabled = allowed && (isDesktop || el.hasAttribute('data-parallax-always'));
      if (enabled) return;
      const target = el.querySelector('[data-parallax-target]') || el.firstElementChild;
      if (target) target.style.transform = '';
    });

    if (!allowed) return;

    nodes.filter((el) => isDesktop || el.hasAttribute('data-parallax-always')).forEach((el) => {
      const target = el.querySelector('[data-parallax-target]') || el.firstElementChild;
      if (!target) return;
      if (parallaxItems.some((item) => item.el === el)) return;
      parallaxItems.push({
        el,
        target,
        strength: parseFloat(el.getAttribute('data-parallax')) || 40
      });
    });

    if (parallaxItems.length && !parallaxListening) {
      parallaxListening = true;
      window.addEventListener('scroll', requestParallax, { passive: true });
      window.addEventListener('resize', requestParallax);
    }

    requestParallax();
  }

  /* ------------------------ Logotipo gigante del pie ---------------------- */

  function fitWordmark(el) {
    const inner = el.querySelector('[data-wordmark-inner]');
    if (!inner) return;
    const available = el.clientWidth;
    if (!available) return;
    el.style.fontSize = '100px';
    const width = inner.scrollWidth;
    if (!width) return;
    const next = Math.floor((available / width) * 100);
    el.style.fontSize = `${next}px`;
  }

  function initWordmarks(root = document) {
    const nodes = root.querySelectorAll('[data-wordmark]');
    nodes.forEach((el) => {
      const run = () => fitWordmark(el);
      run();
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(run);
      if ('ResizeObserver' in window && !el.dataset.wordmarkObserved) {
        el.dataset.wordmarkObserved = 'true';
        const observer = new ResizeObserver(Theme.debounce(run, 120));
        observer.observe(el.parentElement || el);
      }
    });
  }

  /* --------------------------- Selector de cantidad ----------------------- */

  class QuantityInput extends HTMLElement {
    connectedCallback() {
      this.input = this.querySelector('input');
      if (!this.input) return;
      this.changeEvent = new Event('change', { bubbles: true });

      this.querySelectorAll('button').forEach((button) => {
        button.addEventListener('click', (event) => {
          event.preventDefault();
          const previous = this.input.value;
          if (button.name === 'plus') this.input.stepUp();
          else this.input.stepDown();
          if (previous !== this.input.value) this.input.dispatchEvent(this.changeEvent);
        });
      });
    }
  }

  if (!customElements.get('quantity-input')) customElements.define('quantity-input', QuantityInput);

  /* -------------------------------- Modal --------------------------------- */

  class ThemeModal extends HTMLElement {
    constructor() {
      super();
      this.onKeydown = this.onKeydown.bind(this);
    }

    connectedCallback() {
      this.querySelectorAll('[data-modal-close]').forEach((button) => {
        button.addEventListener('click', () => this.close());
      });
      const overlay = this.querySelector('.modal__overlay');
      if (overlay) overlay.addEventListener('click', () => this.close());
    }

    open(trigger) {
      this.opener = trigger;
      this.hidden = false;
      Theme.lockScroll();
      requestAnimationFrame(() => {
        this.classList.add('is-open');
        const focusTarget = Theme.getFocusable(this)[0];
        if (focusTarget) focusTarget.focus({ preventScroll: true });
      });
      document.addEventListener('keydown', this.onKeydown);
    }

    close() {
      this.classList.remove('is-open');
      Theme.unlockScroll();
      document.removeEventListener('keydown', this.onKeydown);
      if (this.opener && document.contains(this.opener)) this.opener.focus({ preventScroll: true });
      window.setTimeout(() => {
        if (!this.classList.contains('is-open')) this.hidden = true;
      }, 350);
    }

    onKeydown(event) {
      if (event.key === 'Escape') {
        event.stopPropagation();
        this.close();
        return;
      }
      Theme.trapFocus(this, event);
    }
  }

  if (!customElements.get('theme-modal')) customElements.define('theme-modal', ThemeModal);

  document.addEventListener('click', (event) => {
    const trigger = event.target.closest('[data-modal-trigger]');
    if (!trigger) return;
    const modal = document.getElementById(trigger.getAttribute('data-modal-trigger'));
    if (!modal || typeof modal.open !== 'function') return;
    event.preventDefault();
    modal.open(trigger);
  });

  /* ---------------------------- Anuncio rotativo -------------------------- */

  class AnnouncementBar extends HTMLElement {
    connectedCallback() {
      this.items = Array.from(this.querySelectorAll('[data-announcement-item]'));
      if (this.items.length < 2) return;
      this.index = 0;
      this.interval = parseInt(this.getAttribute('data-interval'), 10) || 5000;

      const prev = this.querySelector('[data-announcement-prev]');
      const next = this.querySelector('[data-announcement-next]');
      if (prev) prev.addEventListener('click', () => this.go(this.index - 1, true));
      if (next) next.addEventListener('click', () => this.go(this.index + 1, true));

      this.addEventListener('mouseenter', () => this.stop());
      this.addEventListener('mouseleave', () => this.start());
      this.addEventListener('focusin', () => this.stop());
      this.addEventListener('focusout', () => this.start());

      this.start();
    }

    disconnectedCallback() {
      this.stop();
    }

    go(next, manual) {
      const total = this.items.length;
      const index = (next + total) % total;
      this.items[this.index].classList.remove('is-active');
      this.items[index].classList.add('is-active');
      this.index = index;
      if (manual) {
        this.stop();
        this.start();
      }
    }

    start() {
      if (prefersReducedMotion.matches) return;
      this.stop();
      this.timer = window.setInterval(() => this.go(this.index + 1), this.interval);
    }

    stop() {
      if (this.timer) window.clearInterval(this.timer);
      this.timer = null;
    }
  }

  if (!customElements.get('announcement-bar')) {
    customElements.define('announcement-bar', AnnouncementBar);
  }

  /* --------------------------- Búsqueda predictiva ------------------------ */

  class SearchPanel extends ThemePanel {
    connectedCallback() {
      super.connectedCallback();
      this.input = this.querySelector('[data-search-input]');
      this.results = this.querySelector('[data-search-results]');
      this.resetButton = this.querySelector('[data-search-reset]');
      this.enabled = this.hasAttribute('data-predictive');
      this.abortController = null;

      if (this.input && this.enabled) {
        this.input.addEventListener(
          'input',
          Theme.debounce(() => this.search(), 260)
        );
      }

      if (this.resetButton) {
        this.resetButton.addEventListener('click', () => {
          if (!this.input) return;
          this.input.value = '';
          this.input.focus();
          this.clear();
        });
      }
    }

    clear() {
      if (this.results) this.results.innerHTML = '';
    }

    search() {
      if (!this.input || !this.results) return;
      const term = this.input.value.trim();
      if (term.length < 2) {
        this.clear();
        return;
      }

      if (this.abortController) this.abortController.abort();
      this.abortController = new AbortController();

      const types = this.getAttribute('data-search-types') || 'product';
      const params = new URLSearchParams({
        q: term,
        'resources[type]': types,
        'resources[limit]': '6',
        'resources[options][unavailable_products]': 'last',
        section_id: 'predictive-search'
      });

      fetch(`${window.routes.predictiveSearch}?${params.toString()}`, {
        signal: this.abortController.signal
      })
        .then((response) => (response.ok ? response.text() : Promise.reject(response.status)))
        .then((text) => {
          const parsed = new DOMParser().parseFromString(text, 'text/html');
          const markup = parsed.querySelector('#shopify-section-predictive-search');
          this.results.innerHTML = markup ? markup.innerHTML : '';
          Theme.initReveals(this.results);
        })
        .catch((error) => {
          if (error && error.name === 'AbortError') return;
          this.clear();
        });
    }
  }

  if (!customElements.get('search-panel')) customElements.define('search-panel', SearchPanel);

  /* ------------------------- Revelar más resultados ----------------------- */

  class ShowMore extends HTMLElement {
    connectedCallback() {
      this.button = this.querySelector('[data-show-more-button]');
      this.list = this.querySelector('[data-show-more-list]');
      if (!this.button || !this.list) return;

      this.step = parseInt(this.getAttribute('data-initial'), 10) || 4;

      this.button.addEventListener('click', () => {
        const hidden = Array.from(this.list.querySelectorAll('[hidden]'));
        hidden.slice(0, this.step).forEach((item, index) => {
          item.hidden = false;
          item.classList.remove('is-hidden-item');
          const card = item.querySelector('[data-reveal]');
          if (card) card.style.setProperty('--reveal-delay', `${index * 45}ms`);
        });
        initReveals(this.list);
        if (!this.list.querySelector('[hidden]')) {
          this.button.closest('.editorial-footer')?.remove();
        }
      });
    }
  }

  if (!customElements.get('show-more')) customElements.define('show-more', ShowMore);

  /* ------------------------ Acordeones con movimiento --------------------- */

  function animateDetails(details, content, closing) {
    if (details.dataset.animating === 'true') return;
    details.dataset.animating = 'true';

    if (!closing) details.setAttribute('open', '');

    // Algunos paneles (los filtros) traen su propio max-height con scroll
    // interno; se respeta ese límite para no saltar de golpe al terminar.
    const computedMax = parseFloat(getComputedStyle(content).maxHeight);
    const cap = Number.isFinite(computedMax) ? computedMax : Infinity;
    const targetHeight = Math.min(content.scrollHeight, cap);

    const startHeight = closing ? targetHeight : 0;
    const endHeight = closing ? 0 : targetHeight;

    content.style.overflow = 'hidden';
    content.style.maxHeight = `${startHeight}px`;

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        content.style.transition = 'max-height var(--duration-base) var(--ease-out)';
        content.style.maxHeight = `${endHeight}px`;
      });
    });

    const onEnd = (event) => {
      if (event.target !== content || event.propertyName !== 'max-height') return;
      content.removeEventListener('transitionend', onEnd);
      content.style.transition = '';
      content.style.maxHeight = '';
      content.style.overflow = '';
      if (closing) details.removeAttribute('open');
      details.dataset.animating = 'false';
    };
    content.addEventListener('transitionend', onEnd);
  }

  document.addEventListener('click', (event) => {
    const summary = event.target.closest('summary');
    if (!summary) return;
    const details = summary.parentElement;
    if (!details || details.tagName !== 'DETAILS') return;
    const content = summary.nextElementSibling;
    if (!content || prefersReducedMotion.matches) return;

    event.preventDefault();
    animateDetails(details, content, details.hasAttribute('open'));
  });

  /* --------------------------- Enlaces con confirmación ------------------- */

  function initExternalLinks(root = document) {
    root.querySelectorAll('a[target="_blank"]').forEach((link) => {
      if (link.getAttribute('rel')) return;
      link.setAttribute('rel', 'noopener noreferrer');
    });
  }

  /* -------------------------------- Arranque ------------------------------ */

  function init(root = document) {
    initReveals(root);
    initParallax(root);
    initWordmarks(root);
    initExternalLinks(root);
    if (config.animations !== false && !prefersReducedMotion.matches) {
      document.body.classList.add('animations-zoom');
    }
  }

  Theme.init = init;

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      initHeader();
      init();
    });
  } else {
    initHeader();
    init();
  }

  /* ------------------------- Editor de temas de Shopify ------------------- */

  document.addEventListener('shopify:section:load', (event) => {
    initHeader();
    init(event.target);
  });

  document.addEventListener('shopify:section:reorder', () => {
    initHeader();
  });

  document.addEventListener('shopify:section:unload', () => {
    parallaxItems = parallaxItems.filter((item) => document.contains(item.el));
  });
})();
