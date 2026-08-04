/* ==========================================================================
   Atelier Editorial — página de producto
   Selector de variantes, galería y botón de compra fijo en celular.
   ========================================================================== */

(function () {
  'use strict';

  const Theme = window.Theme || {};
  const strings = window.themeStrings || {};
  const config = window.themeConfig || {};

  const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const desktopQuery = window.matchMedia('(min-width: 990px)');

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  /* --------------------------- Selector de variantes ---------------------- */

  class VariantPicker extends HTMLElement {
    connectedCallback() {
      this.sectionId = this.getAttribute('data-section');
      this.productUrl = this.getAttribute('data-url');
      this.updateUrl = this.getAttribute('data-update-url') !== 'false';
      this.variants = this.getVariantData();
      this.abortController = null;
      this.addEventListener('change', this.onChange.bind(this));
    }

    getVariantData() {
      const script = this.querySelector('[data-variant-json]');
      if (!script) return [];
      try {
        return JSON.parse(script.textContent);
      } catch (error) {
        return [];
      }
    }

    get selectedOptions() {
      const fieldsets = Array.from(this.querySelectorAll('[data-option-index]'));
      return fieldsets
        .sort((a, b) => Number(a.dataset.optionIndex) - Number(b.dataset.optionIndex))
        .map((fieldset) => {
          const select = fieldset.querySelector('select');
          if (select) return select.value;
          const checked = fieldset.querySelector('input:checked');
          return checked ? checked.value : null;
        });
    }

    onChange() {
      const selected = this.selectedOptions;
      this.currentVariant = this.variants.find((variant) =>
        variant.options.every((option, index) => option === selected[index])
      );

      this.updateOptionLabels(selected);
      this.updateAvailability(selected);

      if (!this.currentVariant) {
        this.setUnavailable();
        return;
      }

      this.updateFormInput();
      this.updateHistory();
      this.updateMedia();
      this.renderSection();
    }

    updateOptionLabels(selected) {
      this.querySelectorAll('[data-option-selected]').forEach((node) => {
        const index = Number(node.getAttribute('data-option-selected'));
        node.textContent = selected[index] || '';
      });
    }

    updateAvailability(selected) {
      const groups = Array.from(this.querySelectorAll('[data-option-index]'));
      groups.forEach((group) => {
        const index = Number(group.dataset.optionIndex);
        group.querySelectorAll('input[type="radio"]').forEach((input) => {
          const candidate = selected.slice();
          candidate[index] = input.value;
          const match = this.variants.find((variant) =>
            variant.options.every((option, i) => {
              if (candidate[i] == null) return true;
              return option === candidate[i];
            })
          );
          const label = input.nextElementSibling;
          const available = Boolean(match && match.available);
          input.toggleAttribute('data-unavailable', !available);
          if (label) label.classList.toggle('is-unavailable', !available);
        });
      });
    }

    updateFormInput() {
      document
        .querySelectorAll(`[data-variant-input="${this.sectionId}"], [data-variant-input="global"]`)
        .forEach((input) => {
          input.value = this.currentVariant.id;
          input.dispatchEvent(new Event('change', { bubbles: true }));
        });
    }

    updateHistory() {
      if (!this.updateUrl || !this.currentVariant) return;
      const url = new URL(window.location.href);
      url.searchParams.set('variant', this.currentVariant.id);
      window.history.replaceState({}, '', url.toString());
    }

    updateMedia() {
      if (!this.currentVariant || !this.currentVariant.featured_media) return;
      const gallery = document.querySelector('product-gallery');
      if (gallery && typeof gallery.showMedia === 'function') {
        gallery.showMedia(this.currentVariant.featured_media.id);
      }
    }

    setUnavailable() {
      const button = document.querySelector(`[data-add-button="${this.sectionId}"]`);
      if (!button) return;
      const label = button.querySelector('[data-add-label]');
      button.setAttribute('aria-disabled', 'true');
      button.disabled = true;
      if (label) label.textContent = strings.unavailable || 'No disponible';
    }

    renderSection() {
      if (!this.sectionId || !this.currentVariant) return;
      if (this.abortController) this.abortController.abort();
      this.abortController = new AbortController();

      const url = `${this.productUrl}?variant=${this.currentVariant.id}&section_id=${this.sectionId}`;

      fetch(url, { signal: this.abortController.signal })
        .then((response) => (response.ok ? response.text() : Promise.reject(response.status)))
        .then((text) => {
          const doc = new DOMParser().parseFromString(text, 'text/html');
          this.swap(doc, `[data-price-block="${this.sectionId}"]`);
          this.swap(doc, `[data-inventory-block="${this.sectionId}"]`);
          this.swap(doc, `[data-sku-block="${this.sectionId}"]`);
          this.swapBuyButtons(doc);
        })
        .catch(() => {});
    }

    swap(doc, selector) {
      const source = doc.querySelector(selector);
      const target = document.querySelector(selector);
      if (!source || !target) return;
      target.innerHTML = source.innerHTML;
    }

    swapBuyButtons(doc) {
      const selector = `[data-buy-buttons="${this.sectionId}"]`;
      const source = doc.querySelector(selector);
      const target = document.querySelector(selector);
      if (!source || !target) return;

      const button = target.querySelector('[data-add-button]');
      const nextButton = source.querySelector('[data-add-button]');
      if (button && nextButton) {
        const label = button.querySelector('[data-add-label]');
        const nextLabel = nextButton.querySelector('[data-add-label]');
        if (label && nextLabel) label.textContent = nextLabel.textContent;
        button.disabled = nextButton.disabled;
        if (nextButton.getAttribute('aria-disabled') === 'true') {
          button.setAttribute('aria-disabled', 'true');
        } else {
          button.removeAttribute('aria-disabled');
        }
      }

      const sticky = document.querySelector('[data-sticky-buy-label]');
      const nextLabelText = nextButton && nextButton.querySelector('[data-add-label]');
      if (sticky && nextLabelText) sticky.textContent = nextLabelText.textContent;

      const stickyPrice = document.querySelector('[data-sticky-price]');
      const nextPrice = doc.querySelector(`[data-price-block="${this.sectionId}"]`);
      if (stickyPrice && nextPrice) stickyPrice.innerHTML = nextPrice.innerHTML;
    }
  }

  if (!customElements.get('variant-picker')) customElements.define('variant-picker', VariantPicker);

  /* ------------------------------- Galería -------------------------------- */

  class ProductGallery extends HTMLElement {
    connectedCallback() {
      this.items = Array.from(this.querySelectorAll('[data-media-id]'));
      this.viewport = this.querySelector('[data-gallery-viewport]') || this;
      this.dots = Array.from(this.querySelectorAll('[data-gallery-dot]'));
      this.isMobile = window.matchMedia('(max-width: 989px)');

      this.dots.forEach((dot, index) => {
        dot.addEventListener('click', () => this.scrollToIndex(index));
      });

      if (this.dots.length && 'IntersectionObserver' in window) {
        this.observer = new IntersectionObserver(
          (entries) => {
            entries.forEach((entry) => {
              if (!entry.isIntersecting) return;
              const index = this.items.indexOf(entry.target);
              this.setActiveDot(index);
            });
          },
          { root: this.viewport, threshold: 0.6 }
        );
        this.items.forEach((item) => this.observer.observe(item));
      }

      this.setupMotion();
    }

    disconnectedCallback() {
      if (this.observer) this.observer.disconnect();
      if (this.onMotionScroll) {
        window.removeEventListener('scroll', this.onMotionScroll);
        window.removeEventListener('resize', this.onMotionSync);
        if (reduceMotionQuery.removeEventListener) {
          reduceMotionQuery.removeEventListener('change', this.onMotionSync);
        }
      }
    }

    /* --------- Recorrido de las fotos ligado al scroll (escritorio) --------
       Cada foto entra subiendo, ganando opacidad y escalando de 0.96 a 1
       mientras la anterior se desvanece. Los valores se escriben en cada
       cuadro: no hay transición CSS que pelear, sólo transform y opacity.
       Nada de esto se aplica antes de que corra el JS, así que la primera
       foto —la imagen LCP— nunca queda escondida esperando. */

    get motionEnabled() {
      return (
        this.hasAttribute('data-gallery-motion') &&
        config.animations !== false &&
        desktopQuery.matches &&
        !reduceMotionQuery.matches
      );
    }

    setupMotion() {
      if (!this.hasAttribute('data-gallery-motion')) return;
      if (config.animations === false) return;

      this.motionTicking = false;
      this.onMotionScroll = () => this.requestMotion();
      this.onMotionSync = () => this.syncMotion();

      window.addEventListener('scroll', this.onMotionScroll, { passive: true });
      window.addEventListener('resize', this.onMotionSync);
      if (reduceMotionQuery.addEventListener) {
        reduceMotionQuery.addEventListener('change', this.onMotionSync);
      }

      this.syncMotion();
    }

    syncMotion() {
      if (this.motionEnabled) {
        this.classList.add('product-gallery--motion');
        this.requestMotion();
        return;
      }

      this.classList.remove('product-gallery--motion');
      this.items.forEach((item) => {
        item.style.opacity = '';
        item.style.transform = '';
        const image = item.querySelector('.product-gallery__image');
        if (image) image.style.transform = '';
      });
    }

    requestMotion() {
      if (this.motionTicking || !this.motionEnabled) return;
      this.motionTicking = true;
      requestAnimationFrame(() => this.updateMotion());
    }

    updateMotion() {
      this.motionTicking = false;
      if (!this.motionEnabled) return;

      const viewportHeight = window.innerHeight;

      this.items.forEach((item) => {
        const rect = item.getBoundingClientRect();
        // Fuera de este margen no se toca nada: al entrar en él la foto ya
        // lleva puesto su estado inicial, así que no hay salto.
        if (rect.bottom < -viewportHeight || rect.top > viewportHeight * 2) return;

        const enter = clamp((viewportHeight - rect.top) / (viewportHeight * 0.55), 0, 1);
        const exit = clamp(rect.bottom / (viewportHeight * 0.5), 0, 1);
        const presence = Math.min(enter, exit);

        const shift = (1 - enter) * 26;
        const scale = 0.96 + 0.04 * enter;

        item.style.opacity = (0.18 + 0.82 * presence).toFixed(3);
        item.style.transform = `translate3d(0, ${shift.toFixed(2)}px, 0) scale(${scale.toFixed(4)})`;

        const image = item.querySelector('.product-gallery__image');
        if (image) {
          // Parallax interior mínimo. El 1.03 de escala es el margen que hace
          // falta para que el desplazamiento no descubra el borde del marco.
          const center = (rect.top + rect.height / 2 - viewportHeight / 2) / viewportHeight;
          const inner = clamp(-center * 10, -10, 10);
          image.style.transform = `translate3d(0, ${inner.toFixed(2)}px, 0) scale(1.03)`;
        }
      });
    }

    setActiveDot(index) {
      this.dots.forEach((dot, i) => {
        dot.classList.toggle('is-active', i === index);
        dot.setAttribute('aria-current', i === index ? 'true' : 'false');
      });
    }

    scrollToIndex(index) {
      const item = this.items[index];
      if (!item) return;
      if (this.isMobile.matches) {
        this.viewport.scrollTo({
          left: item.offsetLeft,
          behavior: this.reduceMotion ? 'auto' : 'smooth'
        });
      } else {
        item.scrollIntoView({ behavior: this.reduceMotion ? 'auto' : 'smooth', block: 'center' });
      }
    }

    get reduceMotion() {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }

    showMedia(mediaId) {
      const index = this.items.findIndex((item) => item.dataset.mediaId === String(mediaId));
      if (index < 0) return;
      this.scrollToIndex(index);
      this.setActiveDot(index);
    }
  }

  if (!customElements.get('product-gallery')) {
    customElements.define('product-gallery', ProductGallery);
  }

  /* ------------------------ Botón de compra fijo -------------------------- */

  class StickyBuy extends HTMLElement {
    connectedCallback() {
      this.anchorSelector = this.getAttribute('data-anchor');
      const anchor = this.anchorSelector && document.querySelector(this.anchorSelector);
      if (!anchor || !('IntersectionObserver' in window)) {
        this.classList.add('is-visible');
        return;
      }

      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            this.classList.toggle('is-visible', !entry.isIntersecting && entry.boundingClientRect.top < 0);
          });
        },
        { threshold: 0 }
      );
      this.observer.observe(anchor);

      const button = this.querySelector('[data-sticky-buy-trigger]');
      if (button) {
        button.addEventListener('click', () => {
          const target = document.querySelector(this.anchorSelector);
          const submit = target && target.querySelector('[data-add-button]');
          if (submit) {
            submit.click();
          }
        });
      }
    }

    disconnectedCallback() {
      if (this.observer) this.observer.disconnect();
    }
  }

  if (!customElements.get('sticky-buy')) customElements.define('sticky-buy', StickyBuy);

  /* --------------------- Recomendaciones de producto ---------------------- */

  class ProductRecommendations extends HTMLElement {
    connectedCallback() {
      const url = this.getAttribute('data-url');
      if (!url) return;

      const load = () => {
        fetch(url)
          .then((response) => (response.ok ? response.text() : Promise.reject(response.status)))
          .then((text) => {
            const doc = new DOMParser().parseFromString(text, 'text/html');
            const source = doc.querySelector('product-recommendations');
            if (!source || !source.innerHTML.trim()) {
              this.closest('[data-recommendations-section]')?.remove();
              return;
            }
            this.innerHTML = source.innerHTML;
            if (Theme.initReveals) Theme.initReveals(this);
          })
          .catch(() => {});
      };

      if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver(
          (entries) => {
            if (!entries[0].isIntersecting) return;
            observer.disconnect();
            load();
          },
          { rootMargin: '400px' }
        );
        observer.observe(this);
      } else {
        load();
      }
    }
  }

  if (!customElements.get('product-recommendations')) {
    customElements.define('product-recommendations', ProductRecommendations);
  }
})();
