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


# --------------------------------------------------------------------------
# Validación. Horizon acepta un conjunto cerrado de clases de botón y, si el
# valor no coincide, no aplica ninguna: el botón queda como texto suelto. Ya
# pasó dos veces ("button-primary" en el hero, "link" en los "Ver todos"),
# así que el generador ahora lo revisa antes de escribir nada.
# --------------------------------------------------------------------------

STYLE_CLASSES = {"button", "button-secondary", "button-unstyled", "button-custom"}

# Lo que la gente escribe por costumbre -> lo que Horizon entiende.
STYLE_ALIAS = {"link": "button-unstyled", "button-primary": "button"}


# typography-style.liquid compone las variables así:
#
#   --line-height:   var(--line-height--{tipo}-{line_height})
#   --letter-spacing: var(--letter-spacing--{tipo}-{letter_spacing})
#
# El prefijo display-/heading-/body- lo pone el snippet según el tamaño, así
# que el ajuste sólo debe traer el sufijo. Un "display-tight" guardado
# produce var(--line-height--display-display-tight), que no existe, y el
# navegador se queda con el valor heredado.
ESCALA = {"tight", "normal", "loose"}
PREFIJOS = ("display-", "heading-", "body-")
ESCALA_ALIAS = {"wide": "loose", "narrow": "tight"}


def _escala(valor):
    """Deja sólo el sufijo válido de un line_height o letter_spacing."""
    if not isinstance(valor, str):
        return valor
    limpio = valor
    for prefijo in PREFIJOS:
        if limpio.startswith(prefijo):
            limpio = limpio[len(prefijo):]
            break
    limpio = ESCALA_ALIAS.get(limpio, limpio)
    return limpio if limpio in ESCALA else valor


def normalizar_estilos(nodo, ruta=""):
    """Corrige alias conocidos y revienta ante un valor que no existe."""
    for bid, bloque in (nodo or {}).items():
        settings = bloque.get("settings", {})

        sc = settings.get("style_class")
        if sc is not None:
            if sc in STYLE_ALIAS:
                settings["style_class"] = STYLE_ALIAS[sc]
            elif sc not in STYLE_CLASSES:
                raise SystemExit(
                    f"style_class desconocido en {ruta}/{bid}: {sc!r}. "
                    f"Válidos: {sorted(STYLE_CLASSES)}"
                )

        for clave in ("line_height", "letter_spacing"):
            if clave in settings:
                settings[clave] = _escala(settings[clave])

        # La variante en columna no acepta space-between; sólo la de fila.
        col = settings.get("horizontal_alignment_flex_direction_column")
        if col == "space-between":
            settings["horizontal_alignment_flex_direction_column"] = "flex-start"

        # product-title toma el título del producto; no tiene ajuste de texto.
        if bloque.get("type") == "product-title":
            settings.pop("text", None)

        normalizar_estilos(bloque.get("blocks"), f"{ruta}/{bid}")


def load(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as fh:
        return json.load(fh)


def save(relpath, data):
    for sid, seccion in data.get("sections", {}).items():
        normalizar_estilos(seccion.get("blocks"), sid)
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


def plain_section(name, blocks, order, bg="", pt=48, pb=48, halign="center", gap=24):
    """Sección genérica de Horizon.

    Se usa en lugar de 'media-with-content' porque esa sección siempre exige
    una imagen: si no se le da una, pinta un placeholder gigante de playera.
    'section' acepta bloques @theme sin media.
    """
    return {
        "type": "section",
        "blocks": blocks,
        "block_order": order,
        "name": name,
        "settings": {
            "content_direction": "column", "vertical_on_mobile": True,
            "horizontal_alignment": halign, "vertical_alignment": "center",
            "align_baseline": False,
            "horizontal_alignment_flex_direction_column": halign,
            "vertical_alignment_flex_direction_column": "center",
            "gap": gap, "section_width": "page-width",
            "section_height_custom": 50,
            "background_media": "none", "background_color": bg,
            "video_position": "cover", "background_image_position": "cover",
            "border": "none", "border_width": 1, "border_opacity": 100,
            "border_color": "", "border_radius": 0,
            "toggle_overlay": False, "overlay_color": "#00000026",
            "overlay_style": "solid", "gradient_direction": "to top",
            "padding-block-start": pt, "padding-block-end": pb,
        },
    }


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

    # Galería: una sola columna vertical, como la referencia. Estaba en
    # rejilla de dos columnas, que parte la secuencia de la prenda.
    g = d["sections"]["main"]["blocks"]["media-gallery"]["settings"]
    g["media_columns"] = "one"
    g["large_first_image"] = False        # sólo aplica con dos columnas
    # "portrait" no es un valor del esquema: la proporción vertical es
    # "1/1.25". Con el valor inválido no se aplicaba ninguna proporción.
    g["aspect_ratio"] = "1/1.25"
    # Igual con "none", que no está entre los iconos de carrusel.
    g["icons_style"] = "arrow"
    # Separación amplia: con constrain_to_viewport cada prenda ocupa casi
    # toda la altura, y este hueco hace que se vea una sola a la vez.
    g["image_gap"] = 64

    # ---------------------------------------------------------------- datos
    # La columna de datos deja de ser una lista vertical y pasa a repartirse
    # en dos: nombre, precio y ficha a la izquierda; talla, existencias,
    # compra y guía a la derecha. El reparto lo hace levelup-motion.css a
    # partir de las clases de cada bloque; aquí sólo se ordenan para que en
    # celular, donde todo se apila, la secuencia siga siendo la correcta.
    ds = details["settings"]
    ds["gap"] = 20
    ds["padding-block-start"] = 8
    ds["padding-block-end"] = 40
    ds["sticky_details_desktop"] = True

    # Nombre y precio: etiqueta pequeña en mayúsculas, centrada en su
    # columna. El titular de la página es la prenda, no el texto.
    cab = b["prod_header"]
    cab["settings"]["gap"] = 10
    cab["settings"]["horizontal_alignment"] = "center"
    cab["settings"]["horizontal_alignment_flex_direction_column"] = "center"
    cab["blocks"]["prod_title"]["settings"].update({
        "type_preset": "custom",
        "font": "var(--font-heading--family)",
        "font_size": "0.875rem",
        "case": "uppercase",
        "letter_spacing": "loose",
        "line_height": "normal",
        "alignment": "center",
        "width": "100%",
        "max_width": "none",
        "wrap": "balance",
    })
    cab["blocks"]["prod_price"]["settings"].update({
        "type_preset": "custom",
        "font": "var(--font-body--family)",
        "font_size": "0.875rem",
        "case": "none",
        "letter_spacing": "normal",
        "line_height": "normal",
        "alignment": "center",
        "width": "100%",
    })

    # Talla en texto suelto, sin recuadros. Horizon no tiene un ajuste para
    # "sin caja", pero sí colores personalizados: con fondo y borde
    # transparentes el botón se queda en su etiqueta. El gris de la no
    # seleccionada y el subrayado de la elegida hacen el resto.
    b["variant_picker"]["settings"].update({
        "show_swatches": True,
        "alignment": "center",
        "variant_style_class": "custom",
        "custom_variant_background": "rgba(0,0,0,0)",
        "custom_variant_text": "#8A8A8A",
        "custom_variant_border": "rgba(0,0,0,0)",
        "selected_variant_style_class": "custom",
        "custom_selected_variant_background": "rgba(0,0,0,0)",
        "custom_selected_variant_text": "{{ settings.color_palette.foreground }}",
        "custom_selected_variant_border": "rgba(0,0,0,0)",
    })

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
        "Nuestro tallaje es asiático, así que vale la pena revisarlo dos veces.</p>"
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

    # La referencia deja el buy box con lo mínimo: nombre, precio, talla y
    # botón. Las garantías y los iconos de pago se quitan de aquí; siguen en
    # portada, colección y pie, donde no compiten con la decisión de compra.
    _trust_row_sin_usar = group(
        {
            "t1": trust_item("truck", f"Envío gratis<br>desde ${UMBRAL}"),
            "t2": trust_item("map_pin", "Envíos a todo<br>México"),
            "t3": trust_item("lock", "Pago 100%<br>seguro"),
        },
        ["t1", "t2", "t3"],
        direction="row", gap=12, halign="space-between",
        valign="flex-start", vertical_on_mobile=False, pt=8, pb=8,
    )

    _payment_sin_usar = {
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
        "<p>Enviamos a todo México y también al extranjero.</p>"
        "<p>Los tiempos de entrega varían según la pieza y tu ubicación. Te "
        "avisamos por correo en cuanto tu pedido salga.</p>"
        "<p><strong>¿La necesitas para una fecha concreta?</strong> Escríbenos "
        "antes de comprar y te confirmamos si llega a tiempo.</p>"
    )
    devoluciones = (
        "<p>El pago se procesa en el <strong>checkout encriptado de Shopify</strong>. "
        "Nunca almacenamos los datos de tu tarjeta.</p>"
        "<p>Si tu pedido llega <strong>dañado, incompleto o distinto</strong> a lo que "
        "pediste, escríbenos con fotos dentro de las 48 horas siguientes y lo "
        "resolvemos.</p>"
    )

    # La ficha va en una caja con borde fino, como en la referencia: es lo
    # que separa el detalle técnico del nombre y el precio sin necesidad de
    # divisores sueltos por toda la columna.
    b["info_accordion"] = {
        "type": "accordion",
        "settings": {
            "icon": "plus", "dividers": True, "divider_color": "",
            "type_preset": "h6", "background_color": "", "text_color": "",
            "border": "solid", "border_width": 1, "border_opacity": 100,
            "border_color": "{{ settings.color_palette.color2 }}",
            "border_radius": 0,
            "padding-block-start": 4, "padding-block-end": 4,
            "padding-inline-start": 20, "padding-inline-end": 20,
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
                "Pago seguro y garantía",
                {"d": txt(devoluciones, width="100%")}, ["d"], icon_name="lock"),
        },
        "block_order": ["row_desc", "row_ship", "row_ret"],
    }

    # Bloques que el acordeón reemplaza, y los tres divisores: con el
    # contenido repartido en dos columnas ya no separan nada, sólo cruzan la
    # página de lado a lado por encima de la prenda.
    for dead in ("prod_desc", "shipping_info", "guarantee_info",
                 "divider1", "divider2", "divider3"):
        b.pop(dead, None)

    # Este orden es el que se ve en celular, donde las dos columnas se
    # apilan: nombre, precio, talla, existencias, botón, guía y ficha. En
    # escritorio el CSS los reparte por clase, así que el orden no manda.
    details["block_order"] = [
        "prod_header", "variant_picker", "inventory",
        "buy_buttons", "size_guide", "info_accordion",
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
        "ann_ret": msg("Envíos a todo México y al extranjero"),
        "ann_pay": msg("Pago seguro con el checkout de Shopify"),
    }
    ann["block_order"] = ["ann_ship", "ann_ret", "ann_pay"]

    # La barra era una franja negra sobre el encabezado y era lo primero que
    # pesaba al abrir la tienda. La referencia no tiene ninguna. Se conserva
    # —el envío gratis es el mejor argumento que hay antes de entrar— pero
    # pasa a fondo de página con una línea fina debajo: sigue leyéndose y
    # deja de partir la parte de arriba en dos bloques.
    ann["settings"].update({
        "background_color": "{{ settings.color_palette.background }}",
        "divider_width": 1,
        "divider_color": "{{ settings.color_palette.color2 }}",
        "padding-block-start": 9,
        "padding-block-end": 9,
    })

    # El header apuntaba a 'main-menu' (Inicio / Catálogo / Contacto), que no
    # deja llegar a ninguna categoría. 'main-menu-1' tiene las cinco reales.
    d["sections"]["header_section"]["blocks"]["header-menu"]["settings"]["menu"] = "main-menu-1"

    # Con el header transparente sobre el hero, Horizon usa por defecto el
    # color de texto de la página (negro) y el logo y los iconos quedaban
    # ilegibles sobre una foto oscura.
    d["sections"]["header_section"]["settings"]["text_color_transparent_home"] = "#FFFFFF"
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
    d["sections"]["trust_strip"] = plain_section(
        "Garantías",
        {"row": group(
            {
                "t1": trust_item("truck", f"Envío gratis desde ${UMBRAL}"),
                "t2": trust_item("map_pin", "Envíos a todo México"),
                "t3": trust_item("lock", "Pago 100% seguro"),
            },
            ["t1", "t2", "t3"], direction="row", gap=16,
            halign="space-between", valign="flex-start",
            vertical_on_mobile=False,
        )},
        ["row"], bg="#EFEAE2", pt=20, pb=20, gap=0,
    )
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

    # Las animaciones vivían como CSS y JS incrustados en un ajuste de texto:
    # imposibles de leer y de mantener. Pasan a assets/ y esta sección sólo
    # los carga. Sigue siendo una sección del editor, así que se puede
    # desactivar sin tocar código.
    # Las animaciones se cargan sólo en la plantilla de producto. Para
    # llevarlas a otra página basta con añadirla a esta condición.
    #
    # levelup-fondos.css va fuera de la condición: las tarjetas de producto
    # están en todas las páginas, así que el fondo de estudio de las fotos hay
    # que borrarlo en todas.
    #
    # levelup-fondos.css es una sola regla: mix-blend-mode: darken. Aquí no
    # hace falta nada más que cargarlo.
    #
    # Llevó encima un filtro SVG con una curva que empujaba a blanco puro todo
    # lo que pasara de 229, para borrar también fondos grises. Se quitó: los
    # fondos grises no existían —medidos sin filtro dan (255,253,255)— y la
    # curva se comía las prendas blancas, hasta el 95% de la Chaqueta Margot.
    # El razonamiento y los números están en la cabecera del CSS.
    #
    # Al no haber filtro tampoco hay que inyectar el <svg> en la página, que
    # era la parte frágil: si el CSS se cargaba sin el SVG, un navegador podía
    # dejar de pintar la imagen entera.
    # levelup-tallas.css también va fuera de la condición: el selector de talla
    # sale en la ficha, pero también en el diálogo de compra rápida, y ese se
    # abre desde las tarjetas de cualquier página.
    d["sections"]["levelup_animations"]["settings"]["custom_liquid"] = (
        "{{ 'levelup-fondos.css' | asset_url | stylesheet_tag }}\n"
        "{{ 'levelup-tallas.css' | asset_url | stylesheet_tag }}\n"
        "{{ 'levelup-premium.css' | asset_url | stylesheet_tag }}\n"
        "{%- if template.name == 'product' -%}\n"
        "  {{ 'levelup-motion.css' | asset_url | stylesheet_tag }}\n"
        "  <script src=\"{{ 'levelup-motion.js' | asset_url }}\" defer></script>\n"
        "{%- endif -%}"
    )
    d["sections"]["levelup_animations"]["name"] = "Animaciones LevelUP"

    # Logotipo gigante al cierre de la página. jumbo-text escala el texto
    # hasta llenar el ancho del contenedor y trae su propia animación:
    # text_effect "reveal" sube cada línea desde abajo tras una máscara.
    #
    # Va en su propia sección para quedar por debajo de los enlaces legales,
    # que es donde lo pone la referencia. Con un solo bloque, footer.liquid
    # colapsa la rejilla a una columna y lo centra.
    d["sections"]["brand_wordmark"] = {
        "type": "footer",
        "blocks": {
            "wordmark": {
                "type": "jumbo-text",
                "name": "Nombre de la marca",
                "settings": {
                    "text": "LevelUP",
                    "font": "heading",
                    "alignment": "center",
                    "line_height": "0.8",
                    "letter_spacing": "-0.03em",
                    "case": "none",
                    "text_effect": "reveal",
                    "animation_repeat": False,
                    "text_color": "",
                },
                "blocks": {},
            }
        },
        "block_order": ["wordmark"],
        "name": "Nombre de la marca",
        "settings": {
            "section_width": "page-width",
            "gap": 0,
            "background_color": "{{ settings.color_palette.background }}",
            "padding-block-start": 24,
            "padding-block-end": 8,
        },
    }

    d["order"] = ["footer_m9NzUG", "footer_utilities_jLGE8U",
                  "brand_wordmark", "levelup_animations"]
    return d


# ==========================================================================
# 6. PORTADA — banda de confianza alta y navegación por categoría
# ==========================================================================

def build_index():
    with open(os.path.join(os.path.dirname(__file__), "index.json"), encoding="utf-8") as fh:
        d = json.load(fh)

    # "button-primary" no es una clase válida en Horizon (button /
    # button-secondary / button-unstyled / button-custom). Al no serlo, el
    # botón caía a texto sin fondo: gris oscuro sobre una foto oscura.
    boton = d["sections"]["hero_main"]["blocks"]["btn_primary"]["settings"]
    boton["style_class"] = "button-custom"
    boton["custom_button_background"] = "#FFFFFF"
    boton["custom_button_text"] = "#0A0A0A"
    boton["custom_button_border"] = "#FFFFFF"

    d["sections"]["trust_band"] = plain_section(
        "Garantías",
        {"row": group(
            {
                "t1": trust_item("truck", f"Envío gratis desde ${UMBRAL}"),
                "t2": trust_item("map_pin", "Envíos a todo México"),
                "t3": trust_item("lock", "Pago 100% seguro"),
                "t4": trust_item("ruler", "Guía de tallas incluida"),
            },
            ["t1", "t2", "t3", "t4"], direction="row", gap=16,
            halign="space-between", valign="flex-start",
            vertical_on_mobile=False,
        )},
        ["row"], bg="#EFEAE2", pt=20, pb=20, gap=0,
    )

    # Beneficios, frase de marca y FAQ también usaban media-with-content sin
    # imagen. Se conserva su contenido y se sube un nivel al quitar la media.
    for sid, pad in (("benefits_section", 56), ("statement_section", 96),
                     ("faq_section", 56)):
        vieja = d["sections"][sid]
        contenido = vieja["blocks"]["content"]
        d["sections"][sid] = plain_section(
            vieja.get("name", sid), contenido["blocks"],
            contenido["block_order"],
            bg=vieja["settings"].get("background_color", ""),
            pt=pad, pb=pad,
        )

    # Los textos de estas dos secciones prometían cosas que la tienda no
    # puede sostener: plazos de entrega concretos, devoluciones por
    # arrepentimiento y un control de calidad pieza por pieza que no existe
    # cuando el catálogo se surte por un proveedor. Se reescriben con lo que
    # sí es verificable.
    beneficios = (
        "<p><strong>Envío gratis desde $" + UMBRAL + "</strong><br>"
        "Por debajo de ese monto el estándar cuesta $150.</p>"
        "<p><strong>Envíos a todo México</strong><br>"
        "Y también al extranjero.</p>"
        "<p><strong>Pago 100% seguro</strong><br>"
        "Checkout encriptado de Shopify.</p>"
        "<p><strong>Guía de tallas en cada prenda</strong><br>"
        "Nuestro tallaje es asiático; te explicamos cómo elegir.</p>"
    )
    faq = (
        "<p><strong>¿Cuánto tarda el envío?</strong><br>"
        "Depende de la pieza y de tu ubicación. Te avisamos en cuanto tu "
        "pedido salga. Si la necesitas para una fecha concreta, escríbenos "
        "antes de comprar y te confirmamos si llega a tiempo.</p>"
        "<p><strong>¿Qué pasa si llega dañado o no es lo que pedí?</strong><br>"
        "Escríbenos con fotos dentro de las 48 horas siguientes y lo "
        "resolvemos.</p>"
        "<p><strong>¿Cómo sé qué talla pedir?</strong><br>"
        "Cada prenda tiene su guía de tallas. Nuestro tallaje es asiático y "
        "corre más pequeño: si dudas entre dos, elige la mayor.</p>"
        "<p><strong>¿Los pagos son seguros?</strong><br>"
        "Sí, el pago se procesa en el checkout encriptado de Shopify.</p>"
        "<p><strong>¿Tienen tienda física?</strong><br>"
        "Por ahora somos 100% en línea.</p>"
    )
    d["sections"]["benefits_section"]["blocks"]["ben_b"]["settings"]["text"] = beneficios
    d["sections"]["faq_section"]["blocks"]["faq_b"]["settings"]["text"] = faq

    # Dos grises fríos que quedaron de antes del blanco cálido. El de la frase
    # de marca iba escrito a mano (#FAFAFA, el fondo viejo); ahora lee la
    # paleta, así que si el fondo vuelve a cambiar no hay que tocarlo.
    d["sections"]["benefits_section"]["settings"]["background_color"] = "#EFEAE2"
    d["sections"]["statement_section"]["blocks"]["st_t"]["settings"]["text_color"] = (
        "{{ settings.color_palette.background }}"
    )

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
