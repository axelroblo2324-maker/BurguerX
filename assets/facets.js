/* ==========================================================================
   Atelier Editorial — filtros y ordenamiento nativos de Shopify
   Actualiza la rejilla sin recargar la página y mantiene el historial.
   ========================================================================== */

(function () {
  'use strict';

  const Theme = window.Theme || {};

  const TARGETS = [
    '[data-facets-results]',
    '[data-facets-count]',
    '[data-facets-form-desktop]',
    '[data-facets-form-mobile]',
    '[data-facets-active]'
  ];

  let delegated = false;

  class FacetFilters extends HTMLElement {
    connectedCallback() {
      if (delegated) return;
      delegated = true;

      const debouncedSubmit = Theme.debounce
        ? Theme.debounce(this.applyFrom.bind(this), 500)
        : this.applyFrom.bind(this);

      // Los formularios de escritorio y el panel de celular viven en distintos
      // puntos del DOM, por eso se delegan los eventos en el documento.
      document.addEventListener('change', (event) => {
        const form = event.target.closest('[data-facets-form-desktop], [data-facets-form-mobile]');
        if (!form) return;
        if (event.target.type === 'number') debouncedSubmit(form);
        else this.applyFrom(form);
      });

      document.addEventListener('input', (event) => {
        if (event.target.type !== 'number') return;
        const form = event.target.closest('[data-facets-form-desktop], [data-facets-form-mobile]');
        if (form) debouncedSubmit(form);
      });

      document.addEventListener('click', (event) => {
        const clear = event.target.closest('[data-facet-clear]');
        if (!clear) return;
        event.preventDefault();
        this.render(clear.getAttribute('href'));
      });

      window.addEventListener('popstate', () => {
        this.render(window.location.href, false);
      });
    }

    applyFrom(form) {
      const formData = new FormData(form);
      const params = new URLSearchParams();

      formData.forEach((value, key) => {
        if (value === '' || key === 'sections') return;
        params.append(key, value);
      });

      const url = `${window.location.pathname}?${params.toString()}`;
      this.render(url);
    }

    setLoading(state) {
      const results = document.querySelector('[data-facets-results]');
      if (results) results.classList.toggle('is-loading', state);
    }

    render(url, pushState = true) {
      if (!url) return;
      this.setLoading(true);

      fetch(url)
        .then((response) => (response.ok ? response.text() : Promise.reject(response.status)))
        .then((text) => {
          const doc = new DOMParser().parseFromString(text, 'text/html');

          TARGETS.forEach((selector) => {
            const source = doc.querySelector(selector);
            const target = document.querySelector(selector);
            if (!source || !target) return;
            target.innerHTML = source.innerHTML;
          });

          if (pushState) window.history.pushState({ url }, '', url);
          this.setLoading(false);

          if (Theme.initReveals) Theme.initReveals(document);

          const results = document.querySelector('[data-facets-results]');
          if (results && pushState) {
            const top = results.getBoundingClientRect().top + window.scrollY - 120;
            const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            window.scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' });
          }
        })
        .catch(() => {
          this.setLoading(false);
          window.location.href = url;
        });
    }
  }

  if (!customElements.get('facet-filters')) customElements.define('facet-filters', FacetFilters);

  /* ---------------------- Cargar más productos ---------------------------- */

  class LoadMore extends HTMLElement {
    connectedCallback() {
      this.button = this.querySelector('button');
      this.target = document.querySelector(this.getAttribute('data-target'));
      if (!this.button || !this.target) return;

      this.loading = false;
      this.button.addEventListener('click', () => this.load());

      // Carga infinita: se pide la página siguiente en cuanto el botón se
      // acerca a la ventana. El botón se queda por debajo — sirve de aviso
      // para lectores de pantalla y de plan B si falla el observador.
      if ('IntersectionObserver' in window) {
        this.observer = new IntersectionObserver(
          (entries) => {
            if (!entries[0].isIntersecting) return;
            this.load();
          },
          { rootMargin: '600px 0px' }
        );
        this.observer.observe(this);
      }
    }

    disconnectedCallback() {
      if (this.observer) this.observer.disconnect();
    }

    load() {
      const url = this.getAttribute('data-next-url');
      if (!url || this.loading) return;

      this.loading = true;
      this.button.setAttribute('aria-busy', 'true');

      fetch(url)
        .then((response) => (response.ok ? response.text() : Promise.reject(response.status)))
        .then((text) => {
          const doc = new DOMParser().parseFromString(text, 'text/html');
          const items = doc.querySelectorAll(`${this.getAttribute('data-target')} > *`);
          items.forEach((item) => this.target.appendChild(item));

          const nextLoader = doc.querySelector('load-more');
          const nextUrl = nextLoader && nextLoader.getAttribute('data-next-url');

          this.loading = false;
          this.button.removeAttribute('aria-busy');
          if (Theme.initReveals) Theme.initReveals(this.target);

          if (nextUrl) {
            this.setAttribute('data-next-url', nextUrl);
          } else {
            if (this.observer) this.observer.disconnect();
            this.remove();
          }
        })
        .catch(() => {
          this.loading = false;
          this.button.removeAttribute('aria-busy');
        });
    }
  }

  if (!customElements.get('load-more')) customElements.define('load-more', LoadMore);
})();
