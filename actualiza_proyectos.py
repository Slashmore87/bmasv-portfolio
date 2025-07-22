import os
import re
import yaml

CARPETA_PROYECTOS = "proyectos"
ARCHIVO_HTML = "index.html"

def cargar_proyectos():
    proyectos = []
    for archivo in os.listdir(CARPETA_PROYECTOS):
        if archivo.endswith(".md"):
            with open(os.path.join(CARPETA_PROYECTOS, archivo), encoding="utf-8") as f:
                contenido = f.read()
                frontmatter = re.match(r"---(.*?)---", contenido, re.DOTALL)
                if not frontmatter:
                    continue
                data = yaml.safe_load(frontmatter.group(1))
                data["_archivo"] = archivo  # opcional: por si quieres ordenar por archivo si todo es igual
                proyectos.append(data)
    # Ordena por campo "orden" (menor a mayor), luego por año descendente, luego por título
    return sorted(proyectos, key=lambda x: (
        int(x.get("orden", 9999)),
        -int(str(x.get("year", 0))[:4]),
        x.get("title", ""),
        x["_archivo"]
    ))

def generar_html(proyecto, index):
    title = proyecto.get("title", "")
    year = proyecto.get("year", "")
    description = proyecto.get("description", "")
    thumbnail = proyecto.get("thumbnail", "")
    imagenes = proyecto.get("imagen_full", [])
    filtro = proyecto.get("filtro", "arq")
    if isinstance(imagenes, str):
        imagenes = [imagenes]
    gallery_id = f"gallery{100+index}"

    # Primer enlace, muestra overlay y título
    bloque = f'''                <li class="item-thumbs span3 {filtro}">
                  <!-- Fancybox - Gallery Enabled - Title - Full Image --> <a class="hover-wrap fancybox"
                    data-fancybox-group="{gallery_id}" title="{title}"
                    href="{imagenes[0] if imagenes else ''}">
                    <span class="overlay-img"></span> <span class="overlay-img-thumb">{title}<br>
                      {year}</span> </a>\n'''

    # Enlaces adicionales (si hay más de una imagen)
    for img in imagenes[1:]:
        bloque += f'                  <a class="hover-wrap fancybox" data-fancybox-group="{gallery_id}" title="{title}" href="{img}"></a>\n'

    bloque += f'                  <!-- Thumb Image and Description --> <img src="{thumbnail}" alt="{description}">\n                </li>\n'
    return bloque

def reemplazar_seccion(html, inicio, fin, nuevo_bloque):
    return re.sub(
        rf"({inicio})(.|\s)*?({fin})",
        f"{inicio}\n{nuevo_bloque}                {fin}",
        html,
        flags=re.DOTALL
    )

if __name__ == "__main__":
    proyectos = cargar_proyectos()
    html_proyectos = "".join([generar_html(p, i) for i, p in enumerate(proyectos)])

    with open(ARCHIVO_HTML, encoding="utf-8") as f:
        html = f.read()

    html_nuevo = reemplazar_seccion(
        html,
        "<!-- INICIO_PROYECTOS -->",
        "<!-- End Item Project -->",
        html_proyectos
    )

    with open(ARCHIVO_HTML, "w", encoding="utf-8") as f:
        f.write(html_nuevo)

    print("¡Proyectos actualizados en el index.html!")
