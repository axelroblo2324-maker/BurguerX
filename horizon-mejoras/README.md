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
| `recorte-de-fondos.md` | Cómo se borra el fondo blanco de las fotos de producto: lo que ya hace el tema y cómo recortarlas de verdad. |
| `quitar-fondos.py` | Recorta el fondo de las fotos de **todos** los productos y las reemplaza en Shopify. Se corre **en tu máquina**, no aquí: `cdn.shopify.com` está bloqueado por la política de red de este entorno. |

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

- **Paleta en blanco cálido.** El fondo pasó de `#FAFAFA` (un gris frío) a
  `#F7F4EF`, y el color de bordes de `#E0E0E0` a `#E2DCD2`. Es el crema de la
  referencia y lo que pedía el encargo original ("blanco + negro + blanco
  cálido"). Vive en `theme/config/settings_data.json`, así que afecta a toda
  la tienda; las dos bandas de garantías que tenían fondo gris se movieron a
  `#EFEAE2` para no desentonar.

## La página de producto

Es la única página que se rediseñó a fondo, porque es donde se decide la
compra. `theme/assets/levelup-motion.css` tiene dos mitades y la separación
es deliberada:

- **Composición** — la forma de la página. Va **fuera** de
  `prefers-reduced-motion`, para que quien pida menos movimiento vea la misma
  página, sólo que quieta, y no una distinta.
- **Movimiento** — lo que se mueve al recorrer. Va dentro, estados iniciales
  incluidos, así que nadie se queda mirando contenido oculto esperando una
  animación que no va a correr.

### Las tres columnas

| Columna | Qué lleva |
|---|---|
| Izquierda | Nombre de la prenda, precio y la ficha en acordeón |
| Centro | La prenda sola: sin tarjeta, sin borde, sin sombra |
| Derecha | Talla, existencias, botón de compra y guía de tallas |

Horizon **no puede hacer esto por ajustes**. Su rejilla de producto tiene
exactamente dos celdas —galería y datos— y todo lo que se ve a izquierda y
derecha vive dentro de la misma celda de datos. El intento anterior se quedó
en dos columnas por eso mismo.

La salida no fue partir esa celda, sino extenderla: la celda de datos ocupa
las tres columnas de la rejilla, comparte fila con la galería (las dos con
`grid-row: 1` explícito, si no el colocado automático empujaría la prenda a
una segunda fila) y reparte su propio contenido entre la columna 1 y la 3. La
2 queda vacía y por debajo se ve la prenda. Como las dos celdas se
superponen, la de datos lleva `pointer-events: none` y son sus hijos los que
lo recuperan; así el centro sigue recibiendo los clics del zoom.

Lo importante de hacerlo así: la columna de datos **sigue siendo un único
hijo de la rejilla**, que es justo lo que hace funcionar su `position:
sticky`. La información acompaña a las fotos mientras pasan. Partirla en dos
elementos lo habría roto.

El reparto va **por clase, no por posición** (`.accordion` a la izquierda,
`.variant-picker` y `.buy-buttons-block` a la derecha). Reordenar los bloques
desde el editor no descoloca nada. La última fila de la rejilla interior es
`1fr` a propósito: absorbe el sobrante cuando la ficha de la izquierda es más
alta que la pila de la derecha, en vez de repartirlo entre la talla, el botón
y la guía y separarlos.

Sólo a partir de 1000px. Por debajo, las dos columnas se apilan en el orden
del `block_order`: nombre, precio, talla, existencias, botón, guía y ficha.

### Otros cambios de la ficha

- **El nombre dejó de ser un titular.** Pasó de `h3` en Archivo Black a una
  etiqueta de 14px en mayúsculas y muy espaciada. El peso visual lo lleva la
  foto, como en la referencia.
- **La talla dejó de ser una fila de botones con caja.** Horizon no tiene un
  ajuste de "sin recuadro", pero sí colores personalizados: con fondo y borde
  transparentes el botón se queda en su etiqueta. La no seleccionada va en
  gris y la elegida en negro con un subrayado fino.
- **Los tres divisores se quitaron.** Con el contenido repartido en dos
  columnas ya no separaban nada: cruzaban la página de lado a lado por encima
  de la prenda.
- **La ficha va en una caja con borde fino**, que es lo que separa el detalle
  técnico sin necesidad de divisores sueltos.
- **El selector de cantidad se oculta** en la ficha (la referencia no lo
  tiene y en ropa casi nadie compra dos de la misma talla). Se oculta, no se
  borra: sigue en el DOM, así que el formulario manda la cantidad de siempre
  y **en el carrito se puede cambiar exactamente igual que antes**.
- **La barra de anuncios dejó de ser una franja negra.** Pasó a fondo de
  página con una línea fina debajo. El mensaje de envío gratis sigue ahí —es
  el mejor argumento que hay antes de entrar— pero deja de partir la parte de
  arriba en dos bloques.

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
| Parallax dentro de la foto | `.media-gallery__grid .product-media__image` |

Y, fuera de `prefers-reduced-motion` porque son composición y no movimiento:

| Composición | Dónde |
|---|---|
| Tres columnas en escritorio | Datos a la izquierda, prenda al centro, compra a la derecha |
| Galería en vertical en celular | Se invierte el carrusel que Horizon impone en móvil |

Aparte va `theme/assets/levelup-fondos.css`, que **se carga en todas las
páginas** —lo demás es sólo producto— porque borra el fondo blanco de las
fotos y las tarjetas de producto están en todas partes. Está explicado en
`recorte-de-fondos.md`.

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

Las tres columnas están explicadas arriba, en "La página de producto". El
selector repite la forma del tema y le antepone `.product-information` para
ganar por especificidad sin depender del orden de carga; hace falta porque a
partir de 1200px Horizon impone su propio `grid-template-columns: 2fr 1fr`.

La primera foto de la galería se salta a propósito: es la imagen que carga
con prioridad alta y marca el LCP, y arrancarla en opacidad cero retrasaría
lo que el visitante percibe como "ya cargó".

Todo va dentro de `prefers-reduced-motion: no-preference`, incluidos los
estados iniciales, así que quien pida menos movimiento ve la página completa
y estática en vez de contenido oculto esperando una animación que no corre.

El logotipo gigante del cierre es aparte: es un bloque `jumbo-text` en su
propia sección del pie (`brand_wordmark`), con la animación `reveal` que trae
Horizon. Esa sí se ve en todas las páginas, porque el pie es común.

## Qué se verificó y qué no

**Sí:** que lo que hay en `theme/` es byte por byte lo que hay en el borrador.
Después de cada subida se compara el md5 local con el `checksumMd5` que
devuelve Shopify. Y `validar.py` da 0 problemas contra los esquemas de
`schemas/`, que ahora incluyen los seis bloques que toca la ficha de producto.

**No:** cómo se ve. La revisión visual en 390×844, 768×1024 y 1440×900 sigue
sin poder hacerse: el dominio `levelupmx.myshopify.com` está bloqueado por la
política de red del entorno donde se generaron estos archivos. Que un ajuste
sea válido y que el archivo llegue completo no demuestra que la página se vea
bien — eso hay que mirarlo en la vista previa.

Las tres columnas son lo que más conviene mirar, en escritorio ancho: que la
prenda quede centrada, que el botón de compra caiga a la derecha a la altura
del precio, y que el zoom de la foto siga respondiendo al clic en el centro.
