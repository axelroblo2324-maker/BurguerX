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

```bash
python3 build.py     # regenera theme/ desde actual/
```

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

Viven en `theme/assets/levelup-motion.css` y `.js`. La sección "Animaciones
LevelUP" del pie sólo los carga, así que se pueden apagar desde el editor sin
tocar código. Todo va dentro de `prefers-reduced-motion: no-preference`: quien
pida menos movimiento ve la página estática y completa, nunca con contenido
oculto esperando una animación que no va a correr.

| Efecto | Dónde |
|---|---|
| Texto revelado palabra por palabra tras una máscara | `h1`, `h2`, `h3` fuera de header, pie y diálogos |
| Entrada con desplazamiento y zoom, en cascada | Tarjetas de producto y de colección |
| Parallax | Imagen del hero y tarjetas de categoría |
| Secciones apiladas | La frase de marca se fija y Accesorios sube encima |

El logotipo gigante del cierre es un bloque `jumbo-text` en su propia sección
del pie (`brand_wordmark`), colocada debajo de los enlaces legales. Ese bloque
escala el texto hasta llenar el ancho y trae su propia animación de Horizon
(`text_effect: "reveal"`), independiente de `levelup-motion`. El texto se
edita desde el editor; es literal, no acepta `{{ shop.name }}` porque el
ajuste es un textarea y no evalúa Liquid.

**Cuidado con el apilado.** Se hace con selectores de ID en el CSS
(`#shopify-section-statement_section` y `#shopify-section-col_accesorios`).
Esos IDs salen de las claves de sección en `templates/index.json`. Si borras
o recreas alguna de esas dos secciones desde el editor, Shopify le asigna un
ID nuevo y el apilado deja de aplicarse en silencio — no rompe nada, sólo
deja de verse. Habría que actualizar el CSS con los IDs nuevos.

Dos detalles del texto: los títulos que llevan marcado dentro (un enlace, un
`<strong>`) se saltan a propósito, porque reescribir su contenido lo
destruiría; y los de más de 40 palabras también, porque el escalonado se
volvería absurdo.

## Qué falta verificar

La revisión visual en 390×844, 768×1024 y 1440×900 no se pudo hacer: el dominio
`levelupmx.myshopify.com` está bloqueado por la política de red del entorno
donde se generaron estos archivos.
