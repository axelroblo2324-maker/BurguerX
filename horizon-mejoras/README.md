# LevelUP — mejoras al tema Horizon

Respaldo de los archivos que se subieron al tema **borrador** "LevelUP FINAL —
mejorado" (`gid://shopify/OnlineStoreTheme/187613413671`). El tema activo no se
tocó en ningún momento.

## Carpetas

| Carpeta | Qué es |
|---|---|
| `actual/` | Estado de las plantillas **antes** de estos cambios. Es la base desde la que trabaja el generador, no lo borres. |
| `theme/` | Lo que quedó subido al borrador. Refleja 1:1 los archivos del tema. |
| `build.py` | Genera `theme/` a partir de `actual/`. Idempotente: se puede volver a correr. Ojo: **no** regenera los archivos parcheados a mano (`snippets/`, `templates/404.json`, `list-collections.json`, `page.contact.json`); esos se editaron sobre la copia del tema. |
| `index.json` | Portada base que usa `build.py` (paso previo, con los productos ya conectados). |
| `settings_data.json` | Ajustes de tipografía ya aplicados al borrador. |
| `politicas-borrador.md` | Borradores de envíos, devoluciones y términos. **No publicados**: llevan datos por verificar y son un compromiso legal que decide el dueño. |

```bash
python3 build.py     # regenera theme/ desde actual/
python3 validar.py   # contrasta lo generado contra los esquemas del tema
```

`validar.py` existe porque Shopify **no avisa** cuando un ajuste trae un valor
que su esquema no acepta: simplemente no lo aplica. Así se colaron un botón
del hero sin estilo y tres `letter_spacing` que nunca llegaron al CSS, y los
tres sólo se vieron abriendo la tienda en un teléfono. El script compara cada
valor contra `schemas/`, extraídos del propio tema. Córrelo después de cada
`build.py`.

## El umbral de envío gratis

La tienda tiene una tarifa real de **envío gratis a partir de $1,050 MXN**
(por debajo, el estándar cuesta $150). Ese número aparece en seis lugares:

1. `theme/snippets/levelup-free-shipping.liquid` — el cálculo de la barra.
   Sale de `settings.levelup_free_shipping_threshold` y, si esa configuración
   no existe, cae al valor `1050` escrito en el `assign` de arriba del archivo.
2. Barra de anuncios (`sections/header-group.json`).
3. Fila de garantías de la página de producto (`templates/product.json`).
4. Acordeón "Envíos y entregas" (`templates/product.json`).
5. Banda de garantías de la portada (`templates/index.json`).
6. Banda de garantías de colección (`templates/collection.json`).

Del 2 al 6 son bloques de texto normales: se editan desde el editor visual de
Shopify. El 1 es código y hay que cambiarlo en el archivo.

**Si cambias la tarifa de envío en Shopify, actualiza los seis.** Si no, la
barra promete un envío gratis que el checkout no va a dar.

## Cambios fuera del tema

Estos no viven en archivos del tema, así que `build.py` no los reproduce. Se
hicieron por la API de Shopify y quedan registrados aquí:

- **Publicación de las colecciones.** Las cinco (`nueva-coleccion`, `mujeres`,
  `hombres`, `accesorios`, `mas-vendidos`) existían con sus productos dentro
  pero **no estaban publicadas en ningún canal de venta**
  (`resourcePublicationsCount: 0`). En Liquid una colección sin publicar
  resuelve a nulo, así que Horizon caía a los productos de ejemplo: toda la
  portada salía con "Nombre del producto — $19.99" y playeras de relleno, y
  los cinco enlaces del menú de categorías daban 404.

  Ya están publicadas en Tienda online y Shop. Los 22 productos nunca
  tuvieron este problema: estaban ACTIVE y en cuatro canales.

  Si vuelves a ver placeholders en la tienda, esto es lo primero que hay que
  revisar — no es el tema, es la publicación del recurso.

- **Imágenes de colección** para las cinco colecciones, tomadas de un producto
  representativo de cada una. Antes estaban vacías.
- **Menú `main-menu-1`** reescrito a las cinco categorías reales (Nuevos
  Ingresos, Mujeres, Hombres, Accesorios, Más Vendidos). Estaba huérfano; el
  header del borrador ahora apunta a él. `main-menu` no se tocó, así que el
  tema activo conserva su navegación.
- **Menú `footer`** ampliado de sólo "Buscar" a Sobre Nosotros, Contacto,
  Envíos, Preguntas Frecuentes y Buscar. ⚠️ Este menú **sí lo usa el tema
  activo**, así que el cambio ya se ve en la tienda publicada. Es aditivo (no
  se quitó nada), pero conviene saberlo.

## Animaciones

Viven en `theme/assets/levelup-motion.css` y `.js`, y **se cargan sólo en la
plantilla de producto**. La sección "Animaciones LevelUP" del pie envuelve la
carga así:

```liquid
{%- if template.name == 'product' -%}
  ...
{%- endif -%}
```

Para llevarlas a otra página se añade su plantilla a esa condición, desde el
editor. La portada quedó deliberadamente quieta.

| Efecto | Dónde |
|---|---|
| Texto revelado palabra por palabra tras una máscara | `h1`, `h2`, `h3` fuera de header, pie y diálogos |
| Recorrido de la galería | Cada foto se atenúa y desplaza según su distancia al centro de la pantalla |
| Entrada con desplazamiento y zoom | Tarjetas de recomendados |
| Tres columnas en escritorio | Datos a la izquierda, prenda al centro, aire a la derecha |
| Parallax dentro de la foto | `.media-gallery__grid .product-media__image` |
| Galería en vertical en celular | Se invierte el carrusel que Horizon impone en móvil |

Ese último es el que hace visible todo lo demás. Horizon **renderiza la
galería dos veces** —un carrusel y una rejilla— y decide por CSS cuál se ve:
carrusel en celular, rejilla en escritorio. Con carrusel no hay nada que
recorrer, se desliza de lado, así que ninguna animación de scroll aparecía en
teléfono. El tema oculta la rejilla con `:where()`, que no suma especificidad,
así que basta nombrar la clase directamente para invertirlo.

Las animaciones apuntan sólo a `.media-gallery__grid > .product-media-container`
y no a `.product-media-container` a secas: si no, se animarían también las
copias del carrusel, que están ocultas.

**Barra de compra adelantada en celular.** Con la galería en vertical, el
botón de compra real queda debajo de todas las fotos: en el Pantalón Sastre
son 16, y se puede recorrer medio producto sin ver nunca el precio. Horizon
ya trae una barra fija con foto, título, variante, precio y botón, pero la
muestra sólo cuando el botón real sale de pantalla, que aquí es demasiado
tarde. El JS la adelanta con `.lu-bar-on`: aparece al pasar la primera foto
y se retira al llegar al bloque de datos, para no duplicar un botón que ya
está a la vista. Sólo por debajo de 750px.

**Las tres columnas son CSS sobre la rejilla de Horizon.** El tema sólo
ofrece media-izquierda o media-derecha; el CSS reescribe
`grid-template-columns` a `1fr 2fr 0.8fr` y coloca los datos en la columna 1
y la galería en la 2, dejando la 3 vacía. El selector repite la forma del
tema y le antepone `.product-information` para ganar por especificidad sin
depender del orden de carga. Sólo a partir de 1000px.

Lo que **no** se pudo replicar de la referencia: ahí el botón de comprar va
en una tercera columna, separado de los datos. En Horizon el título, el
precio, la talla y el botón viven todos dentro de `.product-details`, que es
un único hijo de la rejilla; separarlos exigiría partir ese contenedor y eso
rompe el `sticky` de la columna, que es justo lo que hace que la info
acompañe a las fotos. El botón se queda con los datos, a la izquierda.

La primera foto de la galería se salta a propósito: es la imagen que carga
con prioridad alta y marca el LCP, y arrancarla en opacidad cero retrasaría
lo que el visitante percibe como "ya cargó".

Todo va dentro de `prefers-reduced-motion: no-preference`, incluidos los
estados iniciales, así que quien pida menos movimiento ve la página completa
y estática en vez de contenido oculto esperando una animación que no corre.

El logotipo gigante del cierre es aparte: es un bloque `jumbo-text` en su
propia sección del pie (`brand_wordmark`), con la animación `reveal` que trae
Horizon. Esa sí se ve en todas las páginas, porque el pie es común.

## Qué falta verificar

La revisión visual en 390×844, 768×1024 y 1440×900 no se pudo hacer: el dominio
`levelupmx.myshopify.com` está bloqueado por la política de red del entorno
donde se generaron estos archivos.
