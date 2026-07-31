#!/usr/bin/env python3
"""Genera las plantillas mejoradas del tema LevelUP (Horizon).

Parte de las plantillas que ya están en el borrador (carpeta actual/) y les
aplica los cambios de conversión, en vez de reescribirlas desde cero. Así se
conservan los ajustes, los IDs y cualquier bloque de app que ya existiera.
"""

import json
import os

SRC = os.path.join(os.path.dirname(__file__), "actual")
OUT = os.path.join(os.path.dirname(__file__), "theme")

UMBRAL = "1,050"  # coincide con la tarifa real de envío gratis de la tienda


def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(relpath, data):
    path = os.path.join(OUT, relpath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    return path


# --------------------------------------------------------------------------
# Fábricas de bloques. Copian la forma exacta que Horizon ya guarda para que
# el importador de Shopify no descarte ajustes desconocidos.
# --------------------------------------------------------------------------

def txt(text, preset="rte", align="left", color="", size="1rem",
        font="var(--font-body--family)", case="none", spacing="normal",
        line_height="normal", width="fit-content", pt=0, pb=0):
    return {
        "type": "text",
        "settings": {
            "text": text, "width": width, "max_width": "normal",
            "alignment": align, "type_preset": preset, "font": font,
            "font_size": size, "line_height": line_height,
            "letter_spacing": spacing, "case": case, "wrap": "pretty",
            "text_color": color, "background": False,
            "background_color": "#00000026", "corner_radius": 0,
            "padding-block-start": pt, "padding-block-end": pb,
            "padding-inline-start": 0, "padding-inline-end": 0,
        },
        "blocks": {},
    }


def group(children, order, direction="column", gap=8, valign="center",
          halign="flex-start", vertical_on_mobile=True, width="fill", pt=0, pb=0):
    return {
        "type": "group",
        "settings": {
            "content_direction": direction,
            "vertical_on_mobile": vertical_on_mobile,
            "horizontal_alignment": halign, "vertical_alignment": valign,
            "align_baseline": False,
            "horizontal_alignment_flex_direction_column": halign,
            "vertical_alignment_flex_direction_column": valign,
            "gap": gap, "width": width, "custom_width": 100,
            "width_mobile": width, "custom_width_mobile": 100,
            "height": "fit", "custom_height": 100,
            "background_media": "none", "background_color": "",
            "video_position": "cover", "background_image_position": "cover",
            "toggle_overlay": False, "overlay_color": "#00000026",
            "overlay_style": "solid", "gradient_direction": "to top",
            "border": "none", "border_width": 1, "border_opacity": 100,
            "border_color": "", "border_radius": 0, "open_in_new_tab": False,
            "placeholder": "",
            "padding-block-start": pt, "padding-block-end": pb,
            "padding-inline-start": 0, "padding-inline-end": 0,
        },
        "blocks": children,
        "block_order": order,
    }


def icon(name, width=20):
    return {
        "type": "icon",
        "settings": {
            "icon": name, "width": width, "link": "",
            "open_in_new_tab": False, "icon_color": "",
        },
        "blocks": {},
    }


def trust_item(icon_name, label):
    """Columna de confianza: icono arriba, texto corto abajo."""
    return group(
        {"i": icon(icon_name), "t": txt(f"<p>{label}</p>", preset="custom",
                                        align="center", size="0.75rem",
                                        line_height="tight")},
        ["i", "t"], direction="column", gap=6,
        halign="center", valign="flex-start", vertical_on_mobile=False,
    )


def acc_row(heading, children, order, open_default=False, icon_name="none"):
    return {
        "type": "_accordion-row",
        "settings": {
            "heading": heading, "open_by_default": open_default,
            "icon": icon_name, "width": 20,
        },
        "blocks": children,
        "block_order": order,
    }


# ==========================================================================
# 1. PÁGINA DE PRODUCTO
# ==========================================================================

def build_product():
    d = load("product.json")
    details = d["sections"]["main"]["blocks"]["product-details"]
    b = details["blocks"]

    # Muestras de color visuales en lugar de botones de texto.
    b["variant_picker"]["settings"]["show_swatches"] = True

    # Disponibilidad real: Horizon sólo marca "quedan pocas" cuando el
    # inventario está por debajo del umbral, así que no inventa urgencia.
    b["inventory"] = {
        "type": "product-inventory",
        "settings": {
            "inventory_threshold": 10, "show_inventory_quantity": True,
            "text_color": "", "padding-block-start": 0,
            "padding-block-end": 0, "padding-inline-start": 0,
            "padding-inline-end": 0,
        },
        "blocks": {},
    }

    # Guía de tallas en modal. La duda de talla es la causa número uno de
    # carritos abandonados en ropa, y abrirla no saca al cliente de la página.
    guia = (
        "<p><strong>Cómo medirte</strong></p>"
        "<p>Usa una cinta métrica sobre ropa ligera, sin apretar.</p>"
        "<ul>"
        "<li><strong>Busto / pecho:</strong> en la parte más amplia, con los brazos relajados.</li>"
        "<li><strong>Cintura:</strong> en la parte más estrecha del torso.</li>"
        "<li><strong>Cadera:</strong> en la parte más amplia, de pie y con los pies juntos.</li>"
        "<li><strong>Entrepierna:</strong> del tiro interior al tobillo.</li>"
        "</ul>"
        "<p><strong>Cómo elegir</strong></p>"
        "<ul>"
        "<li>Nuestras prendas siguen el <strong>tallaje asiático</strong>, que corre "
        "más pequeño que el mexicano. Si dudas entre dos tallas, elige la mayor.</li>"
        "<li>Para prendas de corte holgado u <em>oversize</em>, tu talla habitual funciona bien.</li>"
        "<li>Para cortes entallados o <em>bodycon</em>, considera subir una talla.</li>"
        "<li>Varias fotos del producto incluyen la tabla de medidas específica de esa prenda.</li>"
        "</ul>"
        "<p>¿Sigues con dudas? Escríbenos antes de comprar y te ayudamos a elegir. "
        "Y si no queda, tienes 30 días para cambiarla.</p>"
    )
    b["size_guide"] = {
        "type": "popup-link",
        "settings": {
            "behavior": "default", "heading": "Guía de tallas",
            "type_preset": "paragraph", "padding-block-start": 0,
            "padding-block-end": 0, "padding-inline-start": 0,
            "padding-inline-end": 0,
        },
        "blocks": {"guia_txt": txt(guia, preset="rte", width="100%")},
        "block_order": ["guia_txt"],
    }

    # Fila de confianza justo debajo del botón de compra: es donde aparece la
    # duda de "¿y si no me queda / es seguro pagar aquí?".
    b["trust_row"] = group(
        {
            "t1": trust_item("truck", f"Envío gratis<br>desde ${UMBRAL}"),
            "t2": trust_item("return", "30 días para<br>cambios"),
            "t3": trust_item("lock", "Pago 100%<br>seguro"),
        },
        ["t1", "t2", "t3"],
        direction="row", gap=12, halign="space-between",
        valign="flex-start", vertical_on_mobile=False, pt=8, pb=8,
    )

    b["payment"] = {
        "type": "payment-icons",
        "settings": {
            "horizontal_alignment": "flex-start", "gap": 8,
            "padding-block-start": 0, "padding-block-end": 0,
            "padding-inline-start": 0, "padding-inline-end": 0,
        },
        "blocks": {},
    }

    # Los textos sueltos de envío y garantía pasan a un acordeón: la misma
    # información deja de empujar el botón de compra fuera de la pantalla.
    envios = (
        "<p><strong>Envío gratis</strong> en pedidos desde $" + UMBRAL + " MXN. "
        "Por debajo de ese monto, el envío estándar cuesta $150 MXN.</p>"
        "<p>Entrega estimada de <strong>1 a 7 días hábiles</strong> según tu "
        "ubicación. Enviamos a todo México.</p>"
        "<p>Recibirás tu número de guía por correo en cuanto salga tu pedido.</p>"
    )
    devoluciones = (
        "<p><strong>30 días para cambios y devoluciones.</strong> Si la prenda "
        "no te queda o no era lo que esperabas, escríbenos y lo resolvemos.</p>"
        "<p>La prenda debe estar sin uso y con sus etiquetas.</p>"
        "<p>Pago protegido con el checkout encriptado de Shopify. Nunca "
        "almacenamos los datos de tu tarjeta.</p>"
    )

    b["info_accordion"] = {
        "type": "accordion",
        "settings": {
            "icon": "plus", "dividers": True, "divider_color": "",
            "type_preset": "h6", "background_color": "", "text_color": "",
            "border": "none", "border_width": 1, "border_opacity": 100,
            "border_color": "", "border_radius": 0,
            "padding-block-start": 0, "padding-block-end": 0,
            "padding-inline-start": 0, "padding-inline-end": 0,
        },
        "blocks": {
            "row_desc": acc_row(
                "Descripción",
                {"d": txt("{{ closest.product.description }}", width="100%")},
                ["d"], open_default=True),
            "row_ship": acc_row(
                "Envíos y entregas",
                {"d": txt(envios, width="100%")}, ["d"], icon_name="truck"),
            "row_ret": acc_row(
                "Cambios, devoluciones y pago seguro",
                {"d": txt(devoluciones, width="100%")}, ["d"], icon_name="return"),
        },
        "block_order": ["row_desc", "row_ship", "row_ret"],
    }

    # Bloques que el acordeón reemplaza.
    for dead in ("prod_desc", "shipping_info", "guarantee_info", "divider3"):
        b.pop(dead, None)

    details["block_order"] = [
        "prod_header", "divider1", "variant_picker", "inventory",
        "size_guide", "buy_buttons", "trust_row", "payment",
        "divider2", "info_accordion",
    ]

    # Más recomendaciones = más oportunidades de segunda pieza (y de cruzar el
    # umbral de envío gratis).
    d["sections"]["related_products"]["settings"]["max_products"] = 8
    return d


# ==========================================================================
# 2. BARRA DE ANUNCIOS
# ==========================================================================

def build_header():
    d = load("header-group.json")
    ann = d["sections"]["header_announcements_9jGBFp"]
    base = dict(next(iter(ann["blocks"].values()))["settings"])

    def msg(text):
        s = dict(base)
        s["text"] = text
        return {"type": "_announcement", "settings": s, "blocks": {}}

    ann["blocks"] = {
        "ann_ship": msg(f"Envío <strong>GRATIS</strong> en pedidos desde ${UMBRAL} MXN"),
        "ann_ret": msg("30 días para cambios y devoluciones"),
        "ann_pay": msg("Pago seguro · Envíos a todo México"),
    }
    ann["block_order"] = ["ann_ship", "ann_ret", "ann_pay"]

    # El header apuntaba a 'main-menu' (Inicio / Catálogo / Contacto), que no
    # deja llegar a ninguna categoría. 'main-menu-1' tiene las cinco reales.
    d["sections"]["header_section"]["blocks"]["header-menu"]["settings"]["menu"] = "main-menu-1"
    return d


# ==========================================================================
# 3. CARRITO
# ==========================================================================

def build_cart():
    d = load("cart.json")
    pl = d["sections"]["product_list_NNFgcy"]
    hdr = pl["blocks"]["static-header"]["blocks"]
    hdr["product_list_text_fifeh4"]["settings"]["text"] = "<h3>Completa tu look</h3>"
    hdr["product_list_button_eibbma"]["settings"]["label"] = "Ver todo"
    # Sugerir del catálogo completo y en fila de 2 en celular: se ven más
    # piezas sin empujar el botón de pagar fuera de la pantalla.
    pl["settings"]["collection"] = "mas-vendidos"
    pl["settings"]["max_products"] = 4
    pl["settings"]["mobile_columns"] = "2"
    return d


# ==========================================================================
# 4. COLECCIÓN
# ==========================================================================

def build_collection():
    d = load("collection.json")
    d["sections"]["trust_strip"] = {
        "type": "media-with-content",
        "blocks": {
            "media": {
                "type": "_media-without-appearance", "name": "Media",
                "static": True,
                "settings": {
                    "media_type": "image", "link": "", "video_loop": True,
                    "video_autoplay": False, "image_position": "cover",
                    "video_position": "cover",
                },
                "blocks": {},
            },
            "content": {
                "type": "_content-without-appearance", "name": "Contenido",
                "static": True,
                "settings": {
                    "horizontal_alignment_flex_direction_column": "center",
                    "vertical_alignment_flex_direction_column": "center",
                    "gap": 16,
                },
                "blocks": {
                    "row": group(
                        {
                            "t1": trust_item("truck", f"Envío gratis desde ${UMBRAL}"),
                            "t2": trust_item("return", "30 días para cambios"),
                            "t3": trust_item("lock", "Pago 100% seguro"),
                        },
                        ["t1", "t2", "t3"], direction="row", gap=16,
                        halign="space-between", valign="flex-start",
                        vertical_on_mobile=False,
                    )
                },
                "block_order": ["row"],
            },
        },
        "name": "Garantías",
        "settings": {
            "media_position": "left", "media_width": "wide",
            "media_height": "auto", "section_width": "page-width",
            "extend_media": False, "background_color": "#f5f5f5",
            "padding-block-start": 24, "padding-block-end": 24,
        },
    }
    d["order"] = ["collection_hero", "trust_strip", "main"]
    return d


# ==========================================================================
# 5. FOOTER
# ==========================================================================

def build_footer():
    d = load("footer-group.json")
    # Los iconos van en la sección 'footer', no en 'footer-utilities': esa
    # última tiene max_blocks 3 y sólo admite copyright, políticas y redes.
    foot = d["sections"]["footer_m9NzUG"]
    foot["blocks"]["payment_icons"] = group(
        {
            "lbl": txt("<p>Pago 100% seguro</p>", preset="custom",
                       size="0.75rem", case="uppercase", spacing="wide"),
            "icons": {
                "type": "payment-icons",
                "settings": {
                    "horizontal_alignment": "flex-start", "gap": 8,
                    "padding-block-start": 0, "padding-block-end": 0,
                    "padding-inline-start": 0, "padding-inline-end": 0,
                },
                "blocks": {},
            },
        },
        ["lbl", "icons"], direction="column", gap=8,
    )
    order = foot.get("block_order") or list(foot["blocks"])
    if "payment_icons" not in order:
        order = list(order) + ["payment_icons"]
    foot["block_order"] = order
    return d


# ==========================================================================
# 6. PORTADA — banda de confianza alta y navegación por categoría
# ==========================================================================

def build_index():
    with open(os.path.join(os.path.dirname(__file__), "index.json"), encoding="utf-8") as fh:
        d = json.load(fh)

    d["sections"]["trust_band"] = {
        "type": "media-with-content",
        "blocks": {
            "media": {
                "type": "_media-without-appearance", "name": "Media",
                "static": True,
                "settings": {
                    "media_type": "image", "link": "", "video_loop": True,
                    "video_autoplay": False, "image_position": "cover",
                    "video_position": "cover",
                },
                "blocks": {},
            },
            "content": {
                "type": "_content-without-appearance", "name": "Contenido",
                "static": True,
                "settings": {
                    "horizontal_alignment_flex_direction_column": "center",
                    "vertical_alignment_flex_direction_column": "center",
                    "gap": 16,
                },
                "blocks": {
                    "row": group(
                        {
                            "t1": trust_item("truck", f"Envío gratis desde ${UMBRAL}"),
                            "t2": trust_item("return", "30 días para cambios"),
                            "t3": trust_item("lock", "Pago 100% seguro"),
                            "t4": trust_item("stopwatch", "Entrega en 1–7 días"),
                        },
                        ["t1", "t2", "t3", "t4"], direction="row", gap=16,
                        halign="space-between", valign="flex-start",
                        vertical_on_mobile=False,
                    )
                },
                "block_order": ["row"],
            },
        },
        "name": "Garantías",
        "settings": {
            "media_position": "left", "media_width": "wide",
            "media_height": "auto", "section_width": "page-width",
            "extend_media": False, "background_color": "#f5f5f5",
            "padding-block-start": 20, "padding-block-end": 20,
        },
    }

    # collection-list arma las tarjetas iterando el ajuste collection_list con
    # un bloque estático _collection-card; no lleva una tarjeta por colección.
    d["sections"]["categorias"] = {
        "type": "collection-list",
        "blocks": {
            "cat_header": group(
                {"t": txt("<h3>Compra por categoría</h3>", preset="h4")},
                ["t"], direction="column", gap=12,
            ),
            "static-collection-card": {
                "type": "_collection-card",
                "name": "Tarjeta de colección",
                "static": True,
                "settings": {
                    "placement": "on_image",
                    "horizontal_alignment": "flex-start",
                    "vertical_alignment": "flex-end",
                    "collection_card_gap": 8,
                    "border": "none", "border_width": 1,
                    "border_opacity": 100, "border_radius": 0,
                },
                "blocks": {
                    "collection-card-image": {
                        "type": "_collection-card-image",
                        "name": "Imagen", "static": True,
                        "settings": {
                            "image_ratio": "square", "toggle_overlay": True,
                            "overlay_color": "#00000040",
                            "overlay_style": "gradient",
                            "gradient_direction": "to top",
                            "border": "none", "border_width": 1,
                            "border_opacity": 100, "border_radius": 0,
                        },
                        "blocks": {},
                    },
                    "collection-title": {
                        "type": "collection-title",
                        "name": "Título",
                        "settings": {
                            "width": "fit-content", "max_width": "normal",
                            "alignment": "left", "type_preset": "h5",
                            "font": "var(--font-heading--family)",
                            "font_size": "", "line_height": "normal",
                            "letter_spacing": "normal", "case": "uppercase",
                            "wrap": "pretty", "background": False,
                            "background_color": "#00000026",
                            "corner_radius": 0, "text_color": "#FFFFFF",
                            "padding-block-start": 0, "padding-block-end": 0,
                            "padding-inline-start": 0, "padding-inline-end": 0,
                        },
                        "blocks": {},
                    },
                },
                "block_order": ["collection-title"],
            },
        },
        "block_order": ["cat_header"],
        "name": "Compra por categoría",
        "settings": {
            "collection_list": ["mujeres", "hombres", "accesorios"],
            "layout_type": "grid", "carousel_on_mobile": False,
            "columns": 3, "mobile_columns": "2",
            "columns_gap": 8, "rows_gap": 8,
            "icons_style": "arrow", "icons_shape": "none",
            "section_width": "page-width", "gap": 24,
            "background_color": "{{ settings.color_palette.background }}",
            "padding-block-start": 60, "padding-block-end": 60,
        },
    }

    # La banda de garantías sube justo debajo del hero: responde la objeción
    # de confianza antes de que el visitante decida irse.
    d["order"] = [
        "hero_main", "trust_band", "brand_marquee", "featured_products",
        "categorias", "col_mujeres", "col_hombres", "benefits_section",
        "statement_section", "col_accesorios", "mas_vendidos", "faq_section",
    ]
    return d


if __name__ == "__main__":
    builders = [
        ("templates/product.json", build_product),
        ("sections/header-group.json", build_header),
        ("templates/cart.json", build_cart),
        ("templates/collection.json", build_collection),
        ("sections/footer-group.json", build_footer),
        ("templates/index.json", build_index),
    ]
    for rel, fn in builders:
        path = save(rel, fn())
        print(f"{rel:34} {os.path.getsize(path):>7} bytes")
