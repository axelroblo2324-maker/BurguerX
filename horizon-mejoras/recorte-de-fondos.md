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

`theme/assets/levelup-fondos.css` lo resuelve sin tocar ni una imagen, en dos
pasos que van en este orden.

**1. Estirar el punto blanco** (`filter: url(#lu-blanquear)`). Una curva por
canal que deja quieto todo lo que esté por debajo de 0.75 y empuja a blanco
puro lo que pase de 0.90. Sirve para que un fondo que **no** era blanco —el
crema o el gris claro de un ciclorama— llegue a 255.

**2. Mezclar en oscuro** (`mix-blend-mode: darken`). Se queda, canal por
canal, con el valor más oscuro entre la foto y lo que hay detrás. Un fondo ya
en blanco contra el crema (247,244,239) pierde en los tres canales: **el fondo
desaparece exacto**. Cualquier píxel más oscuro que el crema gana, intacto.

Se eligió `darken` y no `multiply`, que era la opción obvia: multiply oscurece
todo un 4-6% y le mete un velo cálido a la prenda entera. Darken no toca nada
que ya sea más oscuro que la página, que es prácticamente toda la prenda.

El paso 1 es nuevo y es el que arregla tu queja del **fondo gris**. Con darken
solo no había forma: un gris es más *oscuro* que la página, así que darken se
quedaba con el gris y el recuadro sobrevivía. Estirando el punto blanco antes,
ese gris llega a 255 y entonces sí se puede morder.

El filtro tiene que ser un `<svg>` de verdad dentro de la página —Safari no
resuelve `filter: url()` contra un `data:` URI—, así que viaja pegado a la
etiqueta del CSS en la sección "Animaciones LevelUP" del pie. Los dos se
cargan en **todas** las páginas, no sólo en producto, porque las tarjetas de
producto están en todas partes.

### Comprobado, canal por canal

Simulando la curva y la mezcla sobre colores concretos:

| Color | Resultado |
|---|---|
| Fondo blanco puro `(255,255,255)` | borrado exacto |
| Fondo crema `(247,244,239)` | borrado exacto |
| Fondo gris `#EDEDED` | borrado exacto |
| Fondo gris `#E5E5E5` | borrado exacto |
| Fondo gris `#DCDCDC` | queda un resto de 15/255 ← **el límite** |
| Denim oscuro `(30,45,80)` | intacto, bit a bit |
| Negro `(18,18,20)` | intacto, bit a bit |
| Rojo `(170,40,45)` | intacto, bit a bit |
| Gris medio `(128,128,128)` | intacto, bit a bit |
| Khaki claro `(198,180,140)` | +1/255, imperceptible |

### Los dos casos donde esto no alcanza

1. **Fondos por debajo de `#DCDCDC`**: ya son demasiado oscuros para
   separarlos de la prenda sin comérsela. Queda un recuadro tenue.
2. **Productos blancos o muy claros**: por encima de 0.90 se recortan al color
   de la página, o sea que un blanco puro se ve crema. Es el mismo mecanismo
   que borra el fondo — no distingue fondo de prenda. Con el darken solo esto
   ya pasaba por encima de 0.96; la curva baja ese techo a 0.90, así que una
   prenda blanca pierde algo más de pliegue. El candidato obvio es el **Bolso
   Seúl**, que ya es PNG y puede que venga recortado de origen.

   Si se nota, en la sección "Animaciones LevelUP" del pie cambia el `0.88`
   de los tres `tableValues` por `0.95`: sube el techo y respeta más el
   blanco, a cambio de dejar más gris de fondo.

Los dos se arreglan recortando la foto de verdad. Y las dos cosas conviven
sin pelearse: sobre una foto ya recortada no queda nada blanco que morder, y
la parte transparente deja ver la página igual.

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
cambiaron varias cuentas). Hacerlas todas es mucho y, ahora que el tema borra
también el gris, **ya no es urgente**: sólo vale la pena en las fotos con
fondo por debajo de `#DCDCDC` y en los productos claros.

Si aun así quieres hacerlo bien de una vez, este es el orden que rinde:

1. **Las 20 fotos principales.** Son las que salen en portada, colecciones,
   buscador, carrito y recomendados: el 90% del efecto por el 15% del trabajo.
2. **Las 2 o 3 primeras de cada ficha**, que son las que se ven antes de que
   el visitante decida seguir bajando.
3. El resto, si queda ánimo.

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

Tres cosas que hay que mirar y que no se pueden anticipar sin verlas — el
dominio de la tienda está bloqueado desde el entorno donde se generan estos
archivos:

1. **Si algún fondo se resiste.** Darken sólo borra lo que es más claro que
   `#F7F4EF`. Si alguna foto tenía fondo gris, va a quedar un recuadro
   tenue. Mándame cuáles y te digo si conviene recortarlas o subir un pelo la
   claridad de la página.
2. **El recorte de la galería.** La ficha usa proporción vertical (1/1.25) y
   recorta para llenar. Con el fondo ya fundido, la prenda queda más
   expuesta; en los bolsos, que son anchos, puede comerse un borde. Si pasa,
   se cambia la proporción a automática y las fotos se muestran enteras.
3. **El carrito.** No pude verificar si el cajón del carrito pinta un cuadro
   gris detrás de la miniatura, como hacía la barra de compra: el archivo son
   31 KB y no lo abrí entero. Agrega algo al carrito y mándame una captura;
   si aparece el cuadrito, es una línea de CSS.
