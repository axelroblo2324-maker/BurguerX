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

`theme/assets/levelup-fondos.css` lo resuelve sin tocar ni una imagen. Pero
**no hace lo mismo con todas las prendas**, y conviene entender por qué.

### Lo que pasó con las prendas blancas

La primera versión aplicaba una sola receta a todas las fotos: una curva que
empujaba a blanco puro todo lo que pasara de 0.90 (229) y encima
`mix-blend-mode: darken`. Con lo oscuro funciona perfecto. Con lo blanco no:
**se comía la prenda entera**.

Midiendo una captura de la tienda píxel a píxel, contra el color exacto de la
página:

| Producto | Parte de la ficha idéntica a la página |
|---|---|
| Top Amelie (blanco) | **93.0%** |
| Chaqueta Margot (blanco) | **94.7%** |
| Vestido Noir (blanco) | 75.8% |
| Blazer Verona (crema) | 66.3% |
| Chaqueta Sahara (khaki) | 44.4% ← eso es su fondo, está bien |
| Jeans (denim) | 9.0% ← idem, perfecto |

No es que se vieran pálidos: estaban **borrados**. La prenda valía lo mismo
que el fondo, así que se fue con él.

### Y por qué no se arregla moviendo el umbral

Las fichas de "Compra por categoría" no llevan filtro (`toggle_overlay` está
en `false`), así que enseñan el fondo crudo del proveedor tal cual llega.
Midiéndolo ahí: **va de 234 a 255**, con el viñeteo típico de un ciclorama.
Una prenda blanca vive **de 230 a 255**.

Son el mismo rango. Cualquier regla que mire sólo el color de un píxel —una
curva, `darken`, un croma— borra los dos o deja los dos. No existe el número
que los separe, y por eso subir o bajar el `0.88` no era la solución: sólo
elegía a cuál de los dos problemas rendirse.

Lo que sí los distingue es la **forma**, y eso sólo lo hace un recorte de
verdad (más abajo). Mientras tanto el tema hace lo razonable: tratar distinto
lo que es distinto.

### Tratamiento 1 — prendas oscuras y medias (14 de 20)

Lo de siempre, intacto, porque funciona:

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

Simulado canal por canal:

| Color | Resultado |
|---|---|
| Fondo blanco puro `(255,255,255)` | borrado exacto |
| Fondo crema `(247,244,239)` | borrado exacto |
| Fondo gris `#EDEDED` | borrado exacto |
| Fondo gris `#E5E5E5` | borrado exacto |
| Fondo gris `#DCDCDC` | queda un resto de 15/255 ← **el límite** |
| Denim oscuro `(30,45,80)` | intacto, bit a bit |
| Negro `(18,18,20)` | intacto, bit a bit |
| Gris medio `(128,128,128)` | intacto, bit a bit |
| Khaki claro `(198,180,140)` | +1/255, imperceptible |

### Tratamiento 2 — las seis prendas claras

Aquí **no se toca el color**: ni curva ni mezcla. La foto se ve tal cual es,
así que la prenda se ve entera. A cambio vuelve el recuadro del fondo, y eso
se ataja por otro lado: **una máscara que funde el borde del encuadre**, un 6%
a los lados y un 4% arriba y abajo.

La idea es que lo que delata un recuadro no es tanto que el fondo sea más
claro que la página —son 8 niveles— como que el borde sea recto y duro. Al
fundirlo deja de leerse como una caja pegada. El fondo del centro sigue ahí;
el marco, no.

La máscara va **sólo** en estas seis. En las oscuras el encuadre suele ir a
sangre —los jeans casi tocan arriba y abajo— y fundirles el borde les comería
la pernera. Las seis claras están holgadas, así que la máscara sólo muerde
fondo.

Las seis son: **Blazer Verona, Blusa París, Bolso Seúl, Chaqueta Margot, Top
Amelie y Vestido Noir**.

Se seleccionan de dos maneras a la vez, y hacen falta las dos:

- **En las tarjetas**, por el nombre del archivo dentro de `src`/`srcset`
  (en `levelup-fondos.css`). Es la única señal que existe igual en portada,
  colección, carrito, buscador y recomendados. Están las tres primeras fotos
  de cada producto, que es lo que llega a enseñar una tarjeta.
- **En la ficha**, por `product.handle` desde la sección "Animaciones
  LevelUP" del pie. Ahí Liquid sí sabe qué producto es, así que apaga el
  tratamiento para **todas** las fotos, no sólo las tres listadas.

Se comprobó contra las 128 imágenes de los 20 productos: cero falsos
positivos (ninguna prenda oscura queda pescada por error) y las seis portadas
claras cubiertas.

⚠️ **Si cambian las fotos de esos seis productos hay que actualizar las dos
listas.** Los identificadores salen de la API: `products → media → image →
url`.

### Si hay que ajustarlo

- ¿Alguna prenda clara queda mordida por el borde? Baja `--lu-fundido-x` /
  `--lu-fundido-y` en `levelup-fondos.css`. Están juntas y solas a propósito.
- ¿Todavía se ve la caja? Súbelas.
- ¿Alguna prenda que no está en la lista se ve lavada? Añádela a las dos
  listas y listo.

El filtro tiene que ser un `<svg>` de verdad dentro de la página —Safari no
resuelve `filter: url()` contra un `data:` URI—, así que viaja pegado a la
etiqueta del CSS en la sección "Animaciones LevelUP" del pie. Los dos se
cargan en **todas** las páginas, no sólo en producto, porque las tarjetas de
producto están en todas partes.

### Lo que sigue sin resolverse desde el tema

1. **Fondos por debajo de `#DCDCDC`** en las prendas oscuras: demasiado
   oscuros para separarlos sin comerse la prenda. Queda un recuadro tenue.
2. **Los bolsos Praga y Firenze**, que están fotografiados sobre un fondo
   tostado, no blanco. Ese color no es más claro que la página, así que
   `darken` no lo toca y el recuadro se ve entero. No es un fallo del filtro:
   es un fondo de color, y sólo el recorte lo quita.
3. **Las seis prendas claras** siguen enseñando su fondo, ahora con el borde
   fundido en vez de recto. Mejor, pero no borrado.

Los tres se arreglan recortando la foto de verdad. Y conviven sin pelearse:
sobre una foto ya recortada no queda nada blanco que morder, y la parte
transparente deja ver la página igual.

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
falta**: en las 14 prendas oscuras el tema ya borra el fondo exacto.

Lo que sí rinde, por orden:

1. **Las 8 portadas que el tema no puede resolver.** Las seis prendas claras
   (Blazer Verona, Blusa París, Bolso Seúl, Chaqueta Margot, Top Amelie,
   Vestido Noir) y los dos bolsos con fondo tostado (Praga y Firenze). Son
   ocho imágenes y se llevan todo lo que queda por arreglar.
2. **Las 2 o 3 primeras de la ficha de esos ocho**, que son las que se ven
   antes de que el visitante decida seguir bajando.
3. El resto, sólo si queda ánimo. No se va a notar.

Cuando recortes una de las seis claras, quítala también de las dos listas
(`levelup-fondos.css` y el `lu_claros` del pie): ya no necesita el apaño, y
sin él vuelve a beneficiarse del borrado normal.

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

1. **Las seis prendas claras, que ahora se ven.** Es el cambio grande: antes
   estaban borradas y ahora se enseñan enteras, con su fondo y el borde
   fundido. Mira si el fundido queda bien o si en alguna se come un trozo de
   prenda — son dos números (`--lu-fundido-x` y `--lu-fundido-y`) y se
   ajustan en un minuto.

   Y al revés: si alguna prenda **que no está en la lista** se ve lavada,
   dime cuál. Se añade y queda igual que estas seis.
2. **El recorte de la galería.** La ficha usa proporción vertical (1/1.25) y
   recorta para llenar. Con el fondo ya fundido, la prenda queda más
   expuesta; en los bolsos, que son anchos, puede comerse un borde. Si pasa,
   se cambia la proporción a automática y las fotos se muestran enteras.
3. **El carrito.** No pude verificar si el cajón del carrito pinta un cuadro
   gris detrás de la miniatura, como hacía la barra de compra: el archivo son
   31 KB y no lo abrí entero. Agrega algo al carrito y mándame una captura;
   si aparece el cuadrito, es una línea de CSS.
