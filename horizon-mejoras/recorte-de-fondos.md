# Quitar el fondo de las fotos de producto

## Antes que nada: esto vive en un borrador, no en tu tienda

El tema que ve el público es **"Copia de LevelUP FINAL — con animaciones"**
(`gid://shopify/OnlineStoreTheme/187200110887`), y **no tiene
`levelup-fondos.css`**. Se comprobó pidiéndole sus archivos a Shopify: el
asset no existe ahí.

O sea que en la tienda publicada **no hay ningún borrado de fondos**, ni el
de antes ni el de ahora. Todo esto está en el borrador **"LevelUP FINAL —
mejorado"** (`187613413671`), que sólo se ve por vista previa.

Si abres levelupmx.com y los fondos siguen igual, no es que el borrado no
funcione: es que esa página no lo lleva. Para que llegue al público hay que
**publicar el borrador** desde Tienda online → Temas → Acciones → Publicar.
Eso cambia la tienda entera de golpe, así que conviene mirarlo antes en la
vista previa. No lo publico yo: es una decisión tuya.

## Por qué

Las fotos vienen del proveedor sobre fondo blanco de estudio. Mientras la
tienda tuvo fondo casi blanco (`#FAFAFA`) no se notaba. Ahora que está en
blanco cálido (`#F7F4EF`) cada foto se lee como un rectángulo blanco pegado
sobre el crema.

El tema **no** tiene la culpa: se revisó y ni `.product-media` ni
`.card-gallery` pintan ningún fondo. El rectángulo está dentro del JPG.

Recortarlo aquí no se puede: `cdn.shopify.com` está bloqueado por la política
de red del entorno donde se produce este repositorio, así que no hay forma de
descargar las imágenes, procesarlas y volver a subirlas.

## Ya está borrado desde el tema (en el borrador)

`theme/assets/levelup-fondos.css` lo resuelve sin tocar ni una imagen, y a
estas alturas es **una sola línea**: `mix-blend-mode: darken`.

Darken se queda, canal por canal, con el valor más oscuro entre la foto y lo
que hay detrás. El fondo de estudio (255,253,255) pierde contra el crema
(247,244,239) en los tres canales, así que **desaparece exacto**. Cualquier
píxel más oscuro que el crema gana y queda intacto — y eso es casi toda la
prenda, sea denim, negro o blanco roto.

Se eligió darken y no multiply, que era la opción obvia: multiply oscurece
todo un 4-6% y le mete un velo cálido a la prenda entera.

### El rodeo que costó dos vueltas, por si sirve de aviso

Durante un tiempo esto llevaba encima una curva SVG que empujaba a blanco puro
todo lo que pasara de 229, para borrar también fondos grises. **Borraba las
prendas blancas junto con el fondo.** Midiendo una captura de la tienda, píxel
a píxel contra el color exacto de la página:

| Producto | Superficie idéntica al fondo de la página |
|---|---|
| Top Amelie (blanco) | **93.0%** |
| Chaqueta Margot (blanco) | **94.7%** |
| Vestido Noir (blanco) | 75.8% |
| Blazer Verona (crema) | 66.3% |
| Chaqueta Sahara (khaki) | 44.4% ← eso es su fondo, está bien |
| Jeans (denim) | 9.0% ← idem, perfecto |

No se veían pálidas: **no se veían**.

El primer intento de arreglo fue apagar la curva sólo en esos seis productos y
disimular el recuadro fundiéndole el borde. Funcionó a medias: las prendas
volvieron, pero cada una quedó dentro de una caja blanca.

Lo que faltaba era una medición que no había hecho: **el fondo real**, ya sin
filtro, en esas mismas fichas. Da **(255,253,255), plano, con el canal más
bajo en 252**. Blanco puro. Los fondos grises que la curva venía a resolver
**nunca existieron** — la queja original venía de la tienda publicada, que en
ese momento no tenía este CSS cargado en absoluto.

Con el fondo en 252-255 y darken borrando desde 247 hay cinco niveles de
margen. Simulando cada variante sobre los píxeles reales de las fichas:

| Tratamiento | Prenda borrada (Margot / Amelie) |
|---|---|
| **darken solo** | **0.0% / 0.0%** ← lo que hay ahora |
| rodilla en 245 | 0.3% / 0.2% |
| rodilla en 240 | 4.2% / 1.3% |
| rodilla en 235 | 25.5% / 27.5% |
| rodilla en 229 | 43.2% / 55.6% ← la curva que se quitó |

La curva no compraba nada y podía destruir un producto entero. Fuera, junto
con la lista de excepciones, la máscara de borde y el `<svg>` que había que
inyectar en cada página. El CSS pasó de 10 231 bytes a 5 185, y ya no hay
ninguna lista que mantener cuando cambien las fotos.

De paso desaparece un modo de fallo desagradable: si el CSS se cargaba sin su
`<svg>`, un navegador podía dejar de pintar la imagen entera.

### Si algún día vuelve a asomar un recuadro

Sería un producto cuyo fondo esté por debajo de 247. Antes de tocar el CSS,
mira si no sale más barato recortar esa foto. Si aun así hace falta, la
rodilla de la tabla se reintroduce con un filtro SVG — empieza por 245, que
casi no cuesta prenda.

### Lo que el tema no puede resolver

1. **Los bolsos Praga y Firenze**, fotografiados sobre fondo tostado. Ese
   color no es más claro que la página, así que darken no lo toca y el
   recuadro se ve entero. No es un fallo del filtro: es un fondo de color, y
   sólo el recorte lo quita.
2. **Fotos de modelo en la calle o en un interior**, donde el fondo es parte
   de la imagen. Ahí no hay nada que borrar, y darken las deja en paz porque
   casi todo es más oscuro que la página.

## Recortarlo de verdad, en todos los productos de una pasada

`quitar-fondos.py` hace el trabajo completo: baja cada foto, le recorta el
fondo y —si se lo pides— sube la recortada a Shopify y retira la original.

Hay que correrlo **en tu computadora**. Desde el entorno donde se genera este
repositorio no se puede: la política de red devuelve 403 en
`cdn.shopify.com`, así que las imágenes son inalcanzables desde ahí. Y
Shopify no expone su quitafondos por API — se comprobó contra el esquema:
no existen `imageRemoveBackground`, `fileRemoveBackground`,
`mediaRemoveBackground`, `productImageRemoveBackground`, ni un campo
`removeBackground` en `FileUpdateInput`.

### 1. El token

Admin de Shopify → **Configuración → Aplicaciones y canales de venta →
Desarrollar aplicaciones → Crear una aplicación**. Ponle el nombre que
quieras. En **Configurar ámbitos de Admin API** marca los cuatro:

- `read_products`
- `write_products`
- `read_files`
- `write_files`

Los dos de archivos hacen falta para borrar la foto vieja: se hace con
`fileDelete`, que pide `write_files`. Sin ellos el script sube el recorte
pero no puede retirar la original, y el producto acaba con las dos.

Guarda, **Instalar**, y copia el token de acceso: empieza con `shpat_`. Se
muestra una sola vez.

### 2. Correrlo

```bash
pip install pillow requests

export SHOPIFY_TIENDA=levelupmx.myshopify.com
export SHOPIFY_TOKEN=shpat_loquetehayadado

python3 quitar-fondos.py                       # prueba, no toca la tienda
python3 quitar-fondos.py --producto stretchy-loose-straight-pants
python3 quitar-fondos.py --aplicar             # sube y reemplaza
```

Sin `--aplicar` **no escribe nada en Shopify**. Descarga, recorta, deja los
archivos en `fondos/recortadas/` y escribe `fondos/informe.txt`. Ábrelos,
míralos, y sólo entonces vuelve a correrlo con `--aplicar`. Con `--aplicar`
pide que escribas `SI` antes de empezar.

### Qué cuida

- **Guarda las originales** en `fondos/originales/` antes de tocar nada.
- **No borra la original hasta que la nueva está lista.** Sube el recorte,
  espera a que Shopify termine de procesarlo (`status: READY`) y sólo
  entonces retira la vieja. Si algo falla a medio camino, el producto se
  queda con la foto que tenía, nunca sin ninguna.
- **Respeta el blanco de dentro de la prenda.** No borra todo lo que se
  parezca al fondo —eso se comería una suela, un logo o el hueco de un asa—
  sino sólo lo que además esté pegado al borde, rellenando desde las cuatro
  esquinas. Está probado con un caso a propósito: un aro oscuro con un hueco
  blanco en medio; el hueco se queda.
- **Se salta las fotos que no son de estudio.** Mide si el marco de la foto
  es liso y claro; una foto de modelo en la calle no pasa el filtro y se
  deja intacta, porque recortarle el fondo deja a la persona flotando.
  `--forzar` lo salta si quieres decidir tú.
- **Avisa cuando el resultado es sospechoso.** Si el recorte borró menos del
  2% o más del 92% de la imagen, no la sube: eso pasa con las prendas
  blancas sobre fondo blanco, donde no hay forma de distinguir una de otro.
  Van al informe para que las hagas a mano.
- **Aguanta el degradado** de un ciclorama y la sombra suave bajo la prenda
  (tolerancia de 32 sobre 255, ajustable con `--tolerancia`).

### Lo que no pude probar

La parte de imagen está probada con seis casos sintéticos —fondo blanco
puro, ciclorama con degradado, blanco encerrado, foto ruidosa, pared con
textura y prenda blanca sobre blanco— y los seis dan lo esperado.

Lo que **no** pude ejecutar es el camino contra Shopify: descargar, subir y
reemplazar. Las cuatro mutaciones están validadas contra el esquema real de
la tienda —`productUpdate`, `productReorderMedia`, `fileDelete` y
`stagedUploadsCreate`, todas ✅— pero nunca corrieron de verdad. Por eso el
modo de prueba es el que viene por omisión y por eso conviene empezar con
`--producto` en uno solo. Si algo revienta, mándame el error y lo arreglo.

El script usaba `productCreateMedia` y `productDeleteMedia`, que **siguen
funcionando pero están deprecadas**. Se cambiaron por lo que dice el propio
esquema: `productUpdate` para adjuntar y `fileDelete` para retirar. Como
`productUpdate` no devuelve cuál de los medios acaba de crear, el script pide
la lista entera y saca el nuevo por diferencia; si aparece más de uno, se
planta y no borra nada, para no dejar el producto peor de como estaba.

## A mano, desde el admin (para las que el programa deje fuera)

Shopify ya trae el quitafondos, gratis y sin instalar nada:

**Productos → abre el producto → clic en la imagen → Editar → Quitar fondo →
Guardar.**

Guarda una copia, así que si algo sale mal se puede volver a la original
desde la misma pantalla.

## Por dónde empezar

Son **20 productos y 128 imágenes** (consultado a la tienda el 1 de agosto de
2026; antes decía 22 y 147, pero se borraron Jeans Brooklyn y Jeans Runway y
cambiaron varias cuentas). Hacerlas todas es mucho, y la mayoría **no hace
falta**: sobre fondo blanco de estudio el tema ya lo borra exacto, y eso son
18 de los 20.

Lo que sí rinde:

1. **Los dos bolsos con fondo tostado: Praga y Firenze.** Son los únicos que
   el tema no puede resolver, porque su fondo no es más claro que la página.
   Con recortar sus dos portadas se acaba el asunto.
2. **Las 2 o 3 primeras de la ficha de esos dos**, que son las que se ven
   antes de que el visitante decida seguir bajando.
3. El resto, sólo si queda ánimo. No se va a notar.

Ya no hay ninguna lista de excepciones que mantener: al recortar una foto,
el CSS la respeta sola, porque lo transparente sigue transparente.

| Producto | Fotos | Portada |
|---|---|---|
| Blazer Cruzado Verona · Corte Sastre | 5 | JPG |
| Blusa París · Lunares con Olanes | 5 | PNG |
| Bolso Firenze · Estructurado de Mano | 11 | JPG |
| Bolso Praga · Tote Estampado XL | 10 | JPG |
| Bolso Seúl · Hombro Minimalista Blanco | 1 | PNG |
| Chaqueta Ivy · Denim Cropped | 6 | JPG |
| Chaqueta Margot · Lunares Retro | 6 | JPG |
| Chaqueta Sahara · Cropped Khaki | 3 | JPG |
| Gabardina Capri · Con Capucha | 6 | JPG |
| Hoodie Boston · Zipper Oversize | 11 | JPG |
| Jeans Flare 70 · Corte Retro Hombre | 5 | PNG |
| Jeans Graff · Estampado Urbano Hombre | 3 | JPG |
| Jeans Nashville · Bootcut Vintage Rasgado | 6 | JPG |
| Jeans Star · Wide-Leg Lavado Vintage | 6 | JPG |
| Pantalón Milán · Recto Stretch | 6 | PNG |
| Pantalón Osaka · Slim Stretch | 6 | PNG |
| Pantalón Sastre Esencial · 12 Colores | 16 | JPG |
| Pulsera Éterna · Zircón Engarzado Hombre | 2 | JPG |
| Top Amelie · Encaje Entallado | 4 | JPG |
| Vestido Noir · Bodycon Sin Mangas | 10 | JPG |

Las cinco portadas en PNG **pueden venir ya sin fondo** —no lo pude
comprobar, las imágenes no se descargan desde aquí—. Si es así, esas cinco no
hay que tocarlas: el CSS las respeta, porque lo transparente sigue
transparente.

## Cuáles NO recortar

- **Fotos con modelo en un escenario real** (calle, interior, exterior). Ahí
  el fondo es parte de la imagen; recortarlo deja a la persona flotando y se
  ve peor que dejarlo. Esas conviene dejarlas tal cual: se leen como foto
  editorial, no como recuadro.
- **Tablas de medidas y fotos de detalle con texto.** El quitafondos puede
  comerse partes del gráfico.
- **Fotos que ya vienen sin fondo** (el Bolso Seúl ya es PNG; puede que no
  necesite nada).

Mezclar recortadas y con escenario en la misma ficha funciona bien: la
recortada manda en la rejilla y las de escenario aportan contexto más abajo.

## Del lado del tema ya está listo

- El blanco de las fotos se funde con la página en la ficha y en todas las
  tarjetas de producto (`levelup-fondos.css`).
- Las fotos caen directamente sobre el fondo de la página, sin caja ni borde
  ni sombra: se comprobó que el tema no pinta ninguna.
- Las esquinas de la galería están en 0, así que un recorte no queda
  redondeado por accidente.
- Se quitó el cuadro gris que Horizon pintaba detrás de la miniatura de la
  barra de compra fija en celular (`--color-background-secondary`), que con
  un PNG recortado se veía como un recuadro alrededor de la prenda.

## Qué avisar después

Cuatro cosas que hay que mirar y que no se pueden anticipar sin verlas — el
dominio de la tienda está bloqueado desde el entorno donde se generan estos
archivos:

1. **Que ninguna prenda se vea lavada.** Es lo que hay que comprobar primero,
   porque es el fallo que ya ocurrió dos veces. Con darken solo no debería
   pasarle a ninguna, pero si alguna se ve descolorida o le falta pliegue,
   dime cuál.
2. **Que no quede ningún recuadro** aparte de los bolsos Praga y Firenze, que
   ya sabemos que se quedan. Si aparece otro, ese producto tiene el fondo por
   debajo de 247 y toca decidir entre recortarlo o reintroducir la rodilla.
3. **El orden de las tallas.** Debería leerse XS S M L en vez de L M S XS.
   Si sigue desordenado, es que Horizon no maqueta ese `<fieldset>` como flex
   ni como grid, y hay que arreglarlo por otro lado (o reordenar los valores
   a mano desde el admin, que es donde de verdad corresponde).
4. **El recorte de la galería.** La ficha usa proporción vertical (1/1.25) y
   recorta para llenar. Con el fondo ya fundido, la prenda queda más
   expuesta; en los bolsos, que son anchos, puede comerse un borde. Si pasa,
   se cambia la proporción a automática y las fotos se muestran enteras.
5. **El carrito.** No pude verificar si el cajón del carrito pinta un cuadro
   gris detrás de la miniatura, como hacía la barra de compra: el archivo son
   31 KB y no lo abrí entero. Agrega algo al carrito y mándame una captura;
   si aparece el cuadrito, es una línea de CSS.
