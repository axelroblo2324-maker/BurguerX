/* ==========================================================================
   Atelier Editorial — carrito
   Usa la Section Rendering API de Shopify. El checkout sigue siendo el
   checkout protegido nativo: aquí nunca se imita ni se reemplaza.
   ========================================================================== */

(function () {
  'use strict';

  const Theme = window.Theme || {};
  const routes = window.routes || {};
  const strings = window.themeStrings || {};

  /* ------------------------- Secciones a refrescar ------------------------ */

  function sectionsToRender() {
    const list = [];
    if (document.getElementById('shopify-section-cart-drawer')) list.push('cart-drawer');
    if (document.getElementById('shopify-section-main-cart')) list.push('main-cart');
    list.push('cart-icon-bubble');
    return list;
  }

  function parseSection(html) {
    return new DOMParser().parseFromString(html, 'text/html');
  }

  function replaceInner(targetSelector, sourceDoc, sourceSelector) {
    const target = document.querySelector(targetSelector);
    const source = sourceDoc.querySelector(sourceSelector || targetSelector);
    if (!target || !source) return;
    target.innerHTML = source.innerHTML;
  }

  function applySections(sections) {
    if (!sections) return;

    if (sections['cart-drawer']) {
      const doc = parseSection(sections['cart-drawer']);
      replaceInner('[data-cart-drawer-body]', doc);
      replaceInner('[data-cart-drawer-footer]', doc);
      const drawer = document.querySelector('cart-drawer');
      const nextDrawer = doc.querySelector('cart-drawer');
      if (drawer && nextDrawer) {
        drawer.setAttribute('data-cart-count', nextDrawer.getAttribute('data-cart-count') || '0');
        drawer.classList.toggle('is-empty', nextDrawer.classList.contains('is-empty'));
      }
    }

    if (sections['main-cart']) {
      const doc = parseSection(sections['main-cart']);
      replaceInner('#shopify-section-main-cart', doc);
    }

    if (sections['cart-icon-bubble']) {
      const doc = parseSection(sections['cart-icon-bubble']);
      const target = document.getElementById('cart-icon-bubble');
      const source = doc.getElementById('shopify-section-cart-icon-bubble');
      if (target && source) target.innerHTML = source.innerHTML.trim();
    }

    if (window.Theme && typeof window.Theme.initReveals === 'function') {
      window.Theme.initReveals(document);
    }

    document.dispatchEvent(new CustomEvent('cart:updated', { bubbles: true }));
  }

  Theme.applyCartSections = applySections;

  /* --------------------------- Carrito lateral ---------------------------- */

  const PanelBase = Theme.ThemePanel || HTMLElement;

  class CartDrawer extends PanelBase {
    connectedCallback() {
      if (super.connectedCallback) super.connectedCallback();
    }

    setLoading(state) {
      this.classList.toggle('is-loading', Boolean(state));
    }
  }

  if (!customElements.get('cart-drawer')) customElements.define('cart-drawer', CartDrawer);

  function getDrawer() {
    return document.querySelector('cart-drawer');
  }

  function openDrawer() {
    const drawer = getDrawer();
    if (drawer && typeof drawer.open === 'function') drawer.open();
  }

  Theme.openCartDrawer = openDrawer;

  /* --------------------------- Artículos del carrito ---------------------- */

  class CartItems extends HTMLElement {
    connectedCallback() {
      this.addEventListener('change', (event) => {
        const input = event.target.closest('[data-quantity-input]');
        if (!input) return;
        this.updateQuantity(input.dataset.index, input.value, input);
      });

      this.addEventListener('click', (event) => {
        const remove = event.target.closest('[data-cart-remove]');
        if (!remove) return;
        event.preventDefault();
        this.updateQuantity(remove.dataset.index, 0, remove);
      });
    }

    setBusy(state) {
      const drawer = this.closest('cart-drawer');
      if (drawer && typeof drawer.setLoading === 'function') drawer.setLoading(state);
      this.toggleAttribute('aria-busy', state);
    }

    showError(index, message) {
      const node = this.querySelector(`[data-cart-error="${index}"]`);
      if (node) node.textContent = message || '';
    }

    updateQuantity(index, quantity, source) {
      if (!index) return;
      this.setBusy(true);
      this.showError(index, '');

      const body = JSON.stringify({
        line: index,
        quantity: Number(quantity),
        sections: sectionsToRender().join(','),
        sections_url: window.location.pathname
      });

      fetch(routes.cartChange, Object.assign({}, Theme.fetchConfig(), { body }))
        .then((response) => response.json())
        .then((data) => {
          if (data.status) {
            this.showError(index, data.description || data.message || strings.cartError);
            this.setBusy(false);
            return;
          }
          applySections(data.sections);
          this.setBusy(false);
        })
        .catch(() => {
          this.showError(index, strings.cartError);
          this.setBusy(false);
        });

      void source;
    }
  }

  if (!customElements.get('cart-items')) customElements.define('cart-items', CartItems);

  /* ------------------------- Nota del pedido ------------------------------ */

  document.addEventListener('change', (event) => {
    const note = event.target.closest('[data-cart-note]');
    if (!note) return;
    fetch(routes.cartUpdate, Object.assign({}, Theme.fetchConfig(), {
      body: JSON.stringify({ note: note.value })
    }));
  });

  /* ------------------------ Formulario de producto ------------------------ */

  class ProductForm extends HTMLElement {
    connectedCallback() {
      this.form = this.querySelector('form');
      if (!this.form) return;
      this.submitButton = this.querySelector('[type="submit"]');
      this.errorNode = this.querySelector('[data-product-form-error]');
      this.form.addEventListener('submit', this.onSubmit.bind(this));
    }

    onSubmit(event) {
      if (this.getAttribute('data-cart-type') === 'page') return;
      event.preventDefault();
      if (!this.submitButton || this.submitButton.getAttribute('aria-disabled') === 'true') return;

      this.setLoading(true);
      if (this.errorNode) this.errorNode.textContent = '';

      const formData = new FormData(this.form);
      formData.append('sections', sectionsToRender().join(','));
      formData.append('sections_url', window.location.pathname);

      fetch(routes.cartAdd, {
        method: 'POST',
        headers: { Accept: 'application/javascript', 'X-Requested-With': 'XMLHttpRequest' },
        body: formData
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status) {
            if (this.errorNode) {
              this.errorNode.textContent = data.description || data.message || strings.cartError;
            }
            this.setLoading(false);
            return;
          }
          applySections(data.sections);
          this.setLoading(false);
          this.flashAdded();
          if (Theme.bumpCartIcon) Theme.bumpCartIcon();
          openDrawer();
        })
        .catch(() => {
          if (this.errorNode) this.errorNode.textContent = strings.cartError;
          this.setLoading(false);
        });
    }

    flashAdded() {
      if (!this.submitButton) return;
      const label = this.submitButton.querySelector('[data-add-label]');
      if (!label) return;
      const original = label.textContent;
      label.textContent = strings.added || original;
      window.setTimeout(() => {
        label.textContent = original;
      }, 1600);
    }

    setLoading(state) {
      if (!this.submitButton) return;
      this.submitButton.classList.toggle('is-loading', state);
      this.submitButton.toggleAttribute('aria-busy', state);
      const spinner = this.submitButton.querySelector('[data-add-spinner]');
      if (spinner) spinner.hidden = !state;
    }
  }

  if (!customElements.get('product-form')) customElements.define('product-form', ProductForm);

  /* ------------------------ Ventas adicionales ---------------------------- */

  document.addEventListener('click', (event) => {
    const button = event.target.closest('[data-upsell-add]');
    if (!button) return;
    event.preventDefault();
    const id = button.getAttribute('data-variant-id');
    if (!id) return;

    button.setAttribute('aria-busy', 'true');

    fetch(routes.cartAdd, Object.assign({}, Theme.fetchConfig(), {
      body: JSON.stringify({
        items: [{ id: Number(id), quantity: 1 }],
        sections: sectionsToRender().join(','),
        sections_url: window.location.pathname
      })
    }))
      .then((response) => response.json())
      .then((data) => {
        if (!data.status) {
          applySections(data.sections);
          if (Theme.bumpCartIcon) Theme.bumpCartIcon();
        }
        button.removeAttribute('aria-busy');
      })
      .catch(() => button.removeAttribute('aria-busy'));
  });
})();
