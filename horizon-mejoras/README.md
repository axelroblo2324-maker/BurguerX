# LevelUP — mejoras al tema Horizon

Respaldo de los archivos que se subieron al tema **borrador** "LevelUP FINAL —
mejorado" (`gid://shopify/OnlineStoreTheme/187613413671`). El tema activo no se
tocó en ningún momento.

## Carpetas

| Carpeta | Qué es |
|---|---|
| `actual/` | Estado de las plantillas **antes** de estos cambios. Es la base desde la que trabaja el generador, no lo borres. |
| `theme/` | Lo que quedó subido al borrador. Refleja 1:1 los archivos del tema. |
| `build.py` | Genera `theme/` a partir de `actual/`. Idempotente: se puede volver a correr. |
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

## Qué falta verificar

La revisión visual en 390×844, 768×1024 y 1440×900 no se pudo hacer: el dominio
`levelupmx.myshopify.com` está bloqueado por la política de red del entorno
donde se generaron estos archivos.
