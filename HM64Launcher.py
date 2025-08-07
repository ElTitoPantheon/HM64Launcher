import pygame
import sys
import os
import ctypes
import ctypes.wintypes
import subprocess
import json
import threading
import requests
import zipfile
import shutil
import io
from dotenv import load_dotenv
from win10toast_click import ToastNotifier
from datetime import datetime
import time


pygame.init()
toast = ToastNotifier()

# --- CONFIGURACIÓN ---
ANCHO_VENTANA, ALTO_VENTANA = 750, 520
FPS = 60
COLOR_FONDO = (25, 25, 25)
COLOR_BARRA_LATERAL = (10, 10, 10)
COLOR_TEXTO = (255, 255, 255)
COLOR_TAB_ACTIVA = (0, 200, 255)
COLOR_TAB_INACTIVA = (25, 25, 25)
COLOR_SCROLLBAR = (0, 200, 250)

# --- SETUP DE VENTANA ---
screen = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA), pygame.NOFRAME)
pygame.display.set_caption("HM64 Launcher")
pygame.display.set_icon(pygame.image.load(os.path.join("assets", "hm64.png")))
clock = pygame.time.Clock()

# --- Windows API ---
user32 = ctypes.windll.user32
hwnd = pygame.display.get_wm_info()['window']
WM_NCLBUTTONDOWN = 0x00A1
HTCAPTION = 2

# --- ESTADO ---
version = 1.0
releases_cache = {}
tabs = ["General", "Versiones", "Mods"]
tab_activa = 0
subpestañas_versiones = ["Local", "GitHub"]
subpestaña_versiones_activa = 0
juegos = ["Soh", "2Ship", "Starship", "SpaghettiKart"]
juego_activo = 0
scroll_offset = 0
intervalo_verificacion = 3600  
modo_config = False
arrastrando_slider = False
mostrar_confirmacion_eliminar = False
descargando_en_progreso = False
posicion_click_slider = 0
scroll_offset_versiones_local = 0  
scroll_offset_versiones_online = 0
release_seleccionada_indice = None
mod_seleccionado = None
ruta_a_eliminar = None
angulo_carga = 0
instalacion_preseleccionada = None
boton_jugar_rect = None
boton_seleccionar_rect = None
boton_carpeta_rect = None
boton_eliminar_rect = None
boton_descargar_rect = None
boton_toggle_mod_rect = None
estado_boton_jugar = 0
estado_boton_seleccionar = 0
estado_boton_carpeta = 0
estado_boton_eliminar = 0
estado_boton_descargar = 0
estado_boton_toggle_mod = 0
estado_boton_mas = 0
estado_boton_menos = 0
estado_boton_si = 0
estado_boton_no = 0
escala_boton_jugar = 1.0
escala_boton_seleccionar = 1.0
escala_boton_carpeta = 1.0
escala_boton_eliminar = 1.0
escala_boton_descargar = 1.0
escala_boton_toggle_mod = 1.0
escala_boton_mas = 1.0
escala_boton_menos = 1.0
escala_boton_si = 1.0
escala_boton_no = 1.0
escala_boton_en = 1.0
escala_boton_es = 1.0

idioma_actual = "es"

ruta_instalacion_seleccionada = {
    "Soh": None,
    "2Ship": None,
    "Starship": None,
    "SpaghettiKart": None
}


textos = {

    "titulo_lanzador": {
        "es": "Lanzador v",
        "en": "Launcher v"
    },
    "pestana_versiones": {
        "es": "Versiones",
        "en": "Versions"
    },
    "instalacion_activa": {
        "es": "Instalación activa:",
        "en": "Active installation:"
    },
    "sin_instalacion_activa": {
        "es": "Ninguna",
        "en": "None"
    },
    "advertencia_mods": {
        "es": "¡ADVERTENCIA!",
        "en": "WARNING!"
    },
    "advertencia_mods_desc": {
        "es": "Los mods son proporcionados por terceros y no son respaldados por el equipo oficial.",
        "en": "Mods are provided by third parties and are not officially supported."
    },
    "sin_instalacion": {
        "es": "No hay instalación activa.",
        "en": "No active installation."
    },
    "carpeta_mods_no_encontrada": {
        "es": "No se encontró la carpeta 'mods'.",
        "en": "The 'mods' folder was not found."
    },
    "carpeta_mods_vacia": {
        "es": "La carpeta 'mods' está vacía.",
        "en": "The 'mods' folder is empty."
    },
    "seleccionar_local": {
        "es": "Selecciona una instalación local o descargada desde GitHub",
        "en": "Select a local or downloaded installation from GitHub"
    },
    "seleccionar_version_online": {
        "es": "Selecciona una versión para descargar",
        "en": "Select a version to download"
    },
    "sin_versiones": {
        "es": "No se encontraron versiones.",
        "en": "No versions found."
    },
    "boton_si": {
        "es": "Sí",
        "en": "Yes"
    },
    "boton_no": {
        "es": "No",
        "en": "No"
    },
    "confirmar_eliminar": {
        "es": "¿Deseas eliminar la instalación seleccionada?",
        "en": "Do you want to delete the selected installation?"
    },
    "titulo_notificacion": {
        "es": "¡Nuevas versiones disponibles!",
        "en": "New versions available!"
    },
    "verificacion_intervalo": {
        "es": "¿Cada cuánto quieres revisar actualizaciones? (en minutos):",
        "en": "How often do you want to check for updates? (in minutes):"
    },
    "seleccion_idioma": {
        "es": "Selecciona un idioma:",
        "en": "Select a language:"
    }
}


# --- CARGA DE BACKGROUNDS ---
backgrounds = [
    pygame.image.load(os.path.join("assets", "background1.png")).convert(),
    pygame.image.load(os.path.join("assets", "background2.png")).convert(),
    pygame.image.load(os.path.join("assets", "background3.png")).convert(),
    pygame.image.load(os.path.join("assets", "background4.png")).convert()
]
# --- CARGA DE ICONOS ---
icono_config = pygame.image.load(os.path.join("assets", "config.png")).convert_alpha()
icono_config = pygame.transform.scale(icono_config, (60, 60))
icono_seleccionar = pygame.image.load(os.path.join("assets", "seleccionar.png")).convert_alpha()
icono_seleccionar = pygame.transform.scale(icono_seleccionar, (20, 20))
icono_cargando = pygame.image.load(os.path.join("assets", "loading.png")).convert_alpha()
icono_cargando = pygame.transform.scale(icono_cargando, (32, 32))
icono_carpeta = pygame.image.load(os.path.join("assets", "carpeta.png")).convert_alpha()
icono_carpeta = pygame.transform.scale(icono_carpeta, (20, 20))
icono_papelera = pygame.image.load(os.path.join("assets", "papelera.png")).convert_alpha()
icono_papelera = pygame.transform.scale(icono_papelera, (20, 20))
icono_descargar = pygame.image.load(os.path.join("assets", "descargar.png")).convert_alpha()
icono_descargar = pygame.transform.scale(icono_descargar, (20, 20))
icono_mods = pygame.image.load(os.path.join("assets", "onoff.png")).convert_alpha()
icono_mods = pygame.transform.scale(icono_mods, (20, 20))
icono_jugar = pygame.image.load(os.path.join("assets", "jugar.png")).convert_alpha()
icono_jugar = pygame.transform.scale(icono_jugar, (55, 55))
icono_check = pygame.image.load(os.path.join("assets", "check.png")).convert_alpha()
icono_check = pygame.transform.scale(icono_check, (23, 23))
icono_en = pygame.image.load(os.path.join("assets", "en.png")).convert_alpha()
icono_en = pygame.transform.scale(icono_en, (23, 17))
icono_es = pygame.image.load(os.path.join("assets", "es.png")).convert_alpha()
icono_es = pygame.transform.scale(icono_es, (23, 17))

# --- FUENTES ---
fuente = pygame.font.SysFont("Segoe UI", 16)
fuente_bold = pygame.font.SysFont("Segoe UI", 14, bold=True)
fuente_logo = pygame.font.SysFont("Segoe UI", 28, bold=True)
fuente_pequena = pygame.font.SysFont("Segoe UI", 16)
fuente_pestañas = pygame.font.SysFont("Segoe UI", 13, bold=True)

# --- JSON DE PERSISTENCIA ---
RUTA_JSON = "config.json"

load_dotenv("releases.env")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPOS = {
    "soh": "HarbourMasters/Shipwright",
    "2ship": "HarbourMasters/2ship2harkinian",
    "starship": "HarbourMasters/Starship",
    "spaghettikart": "HarbourMasters/SpaghettiKart",
    "Lanzador": "ElTitoPantheon/HM64Launcher"
}

NOMBRE_A_CLAVE = {
    "Soh": "soh",
    "2Ship": "2ship",
    "Starship": "starship",
    "SpaghettiKart": "spaghettikart"
}

# --- FUNCIONES ---
def obtener_releases(repo):
    releases = []
    pagina = 1
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    while True:
        url = f"https://api.github.com/repos/{repo}/releases?page={pagina}&per_page=100"
        try:
            respuesta = requests.get(url, headers=headers, timeout=10)
            if respuesta.status_code != 200:
                print("Fallo de conexión con GitHub.")
                break
            datos = respuesta.json()
            if not datos:
                break
            releases.extend(datos)
            pagina += 1
        except requests.exceptions.RequestException:
            print("Error de conexión.")
            break
    return releases

def carpeta_presente(nombre_asset, carpetas_locales):
    return any(nombre_asset.startswith(carpeta) for carpeta in carpetas_locales)

def verificar_version_local(release, carpetas_locales):
    for asset in release.get("assets", []):
        asset_name = asset.get("name", "")
        if carpeta_presente(asset_name, carpetas_locales):
            return True
    return False

def obtener_carpetas_del_port(clave):
    ruta_base = os.path.join("Ports", clave)
    if not os.path.isdir(ruta_base):
        return []
    return [nombre for nombre in os.listdir(ruta_base) if os.path.isdir(os.path.join(ruta_base, nombre))]

def obtener_releases_formateadas(nombre_juego):
    if nombre_juego in releases_cache:
        return releases_cache[nombre_juego]

    clave = NOMBRE_A_CLAVE.get(nombre_juego)
    if not clave:
        return ["(Juego no soportado)"]

    repo = REPOS.get(clave)
    if not repo:
        return ["(Repositorio no encontrado)"]

    releases = obtener_releases(repo)
    carpetas_locales = obtener_carpetas_del_port(clave)

    resultado = []
    for release in releases:
        nombre = release.get("name") or release.get("tag_name") or "Sin nombre"
        instalado = ""
        if verificar_version_local(release, carpetas_locales):
            instalado = " [instalado]"

        fecha_iso = release.get("published_at")
        fecha_str = ""
        if fecha_iso:
            try:
                fecha_dt = datetime.fromisoformat(fecha_iso.rstrip("Z"))

                fecha_str = fecha_dt.strftime(" (%Y-%m-%d)")
            except Exception:
                fecha_str = ""

        resultado.append(f"{nombre}{instalado}")

    if not resultado:
        resultado = []

    releases_cache[nombre_juego] = resultado
    return resultado

def precargar_releases():
    for juego in juegos:
        obtener_releases_formateadas(juego)

def descargar_y_extraer_release(nombre_juego, indice_release, destino_base="Ports"):
    clave = NOMBRE_A_CLAVE.get(nombre_juego)
    if not clave or nombre_juego not in releases_cache:
        print("No hay releases en caché o clave no válida.")
        return

    repo = REPOS[clave]
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    releases_todas = obtener_releases(repo)
    if indice_release >= len(releases_todas):
        print("Índice fuera de rango.")
        return

    release = releases_todas[indice_release]
    assets = release.get("assets", [])
    tag = release.get("tag_name", "").lower()
    nombre_release = release.get("name", "").lower()

    zips = [a for a in assets if a.get("name", "").endswith(".zip")]
    if not zips:
        print("No hay assets .zip en esta release.")
        return

    asset = next((a for a in zips if "win64" in a["name"].lower()), None)
    if not asset:
        asset = next((a for a in zips if "windows" in a["name"].lower()), None)
    if not asset:
        asset = next((a for a in zips if tag in a["name"].lower() or nombre_release in a["name"].lower()), None)
    if not asset:
        asset = zips[0]

    nombre = asset["name"]
    nombre_base = os.path.splitext(nombre)[0]
    destino = os.path.join(destino_base, clave, nombre_base)

    if os.path.exists(destino):
        print(f"Ya existe: {destino}, omitiendo descarga.")
        return

    print(f"Descargando: {nombre}")
    r = requests.get(asset["browser_download_url"], headers=headers)
    r.raise_for_status()
    zip_data = io.BytesIO(r.content)

    os.makedirs(destino, exist_ok=True)
    with zipfile.ZipFile(zip_data) as z:
        for member in z.infolist():
            ruta_destino = os.path.join(destino, member.filename)
            if member.is_dir():
                os.makedirs(ruta_destino, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(ruta_destino), exist_ok=True)
                with z.open(member) as fuente, open(ruta_destino, "wb") as salida:
                    shutil.copyfileobj(fuente, salida)

    print(f"Asset extraído en {destino}")


def cargar_config():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r") as f:
            return json.load(f)
    return {}

def guardar_config(config):
    with open(RUTA_JSON, "w") as f:
        json.dump(config, f, indent=2)

def obtener_fecha_ultima_release(repo):
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    try:
        url = f"https://api.github.com/repos/{repo}/releases"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        datos = r.json()
        if datos:
            return datos[0]["published_at"]
    except Exception as e:
        print("error de conexión")
    return None

def revisar_nuevas_releases():
    config = cargar_config()
    cambios = False
    nuevos = []

    if "last_seen_releases" not in config:
        config["last_seen_releases"] = {}

    for clave, repo in REPOS.items():
        fecha_ultima = obtener_fecha_ultima_release(repo)
        if not fecha_ultima:
            continue

        fecha_guardada = config["last_seen_releases"].get(clave)
        if not fecha_guardada or fecha_ultima > fecha_guardada:
            try:
                headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
                url = f"https://api.github.com/repos/{repo}/releases"
                r = requests.get(url, headers=headers, timeout=10)
                r.raise_for_status()
                datos = r.json()
                if datos:
                    release_name = datos[0].get("name") or datos[0].get("tag_name") or "(sin nombre)"
                    nuevos.append((clave, release_name))
                    config["last_seen_releases"][clave] = fecha_ultima
                    cambios = True
            except Exception as e:
                print(f"[ERROR] al obtener nombre de la release de {repo}: {e}")

    if nuevos:
        lineas = [f"{clave.upper()}: {nombre}" for clave, nombre in nuevos]
        mensaje = "\n".join(lineas)
        tex = textos["titulo_notificacion"][idioma_actual]
        toast.show_toast(
            tex,
            mensaje,
            icon_path="hm64.ico",
            duration=10,
            threaded=True
        )

    if cambios:
        guardar_config(config)

def ciclo_verificacion_periodica(obtener_intervalo):  
    while True:
        print("[INFO] Ejecutando revisión periódica de releases...")

        releases_cache.clear()         
        precargar_releases()           
        revisar_nuevas_releases()      

        time.sleep(obtener_intervalo())

def comenzar_arrastre():
    user32.ReleaseCapture()
    user32.SendMessageW(hwnd, WM_NCLBUTTONDOWN, HTCAPTION, 0)

def cargar_selecciones():
    global ruta_instalacion_seleccionada
    global intervalo_verificacion
    global idioma_actual
    config = cargar_config()
    for k in ruta_instalacion_seleccionada:
        if k in config:
            ruta_instalacion_seleccionada[k] = config[k]
    intervalo_verificacion = config.get("intervalo_verificacion", 3600)
    idioma_actual = config.get("idioma_actual", "es")


def guardar_selecciones():
    config = cargar_config()
    for k in ruta_instalacion_seleccionada:
        config[k] = ruta_instalacion_seleccionada[k]
    config["intervalo_verificacion"] = intervalo_verificacion
    config["idioma_actual"] = idioma_actual
    guardar_config(config)

def obtener_carpeta_juego():
    nombre = juegos[juego_activo]
    return {
        "Soh": "Ports/soh/",
        "2Ship": "Ports/2ship/",
        "Starship": "Ports/Starship/",
        "SpaghettiKart": "Ports/SpaghettiKart/"
    }[nombre]

def obtener_nombre_exe():
    return {
        "Soh": "soh.exe",
        "2Ship": "2ship.exe",
        "Starship": "Starship.exe",
        "SpaghettiKart": "Spaghettify.exe"
    }[juegos[juego_activo]]

def listar_instalaciones():
    ruta_base = obtener_carpeta_juego()
    if not os.path.isdir(ruta_base):
        return []
    return [nombre for nombre in os.listdir(ruta_base)
            if os.path.isdir(os.path.join(ruta_base, nombre))]

def ejecutar_juego():
    seleccion = ruta_instalacion_seleccionada[juegos[juego_activo]]
    if not seleccion:
        print("No hay instalación seleccionada.")
        return
    exe = obtener_nombre_exe()
    ruta_exe = os.path.join(seleccion, exe)
    if os.path.isfile(ruta_exe):
        print(f"Ejecutando: {ruta_exe}")
        subprocess.Popen([ruta_exe], cwd=seleccion)
    else:
        print(f"Ejecutable no encontrado: {ruta_exe}")

        
# --- FUNCIONES DE DIBUJADO ---

def dibujar_encabezado():
    global version
    pygame.draw.rect(screen, (10, 10, 10), (0, 0, ANCHO_VENTANA, 60))
    texto_logo = fuente_logo.render("HM", True, (0, 200, 255))
    texto_64 = fuente_logo.render("64", True, (255, 50, 50))
    texto_titulo = textos["titulo_lanzador"].get(idioma_actual, "Lanzador v")
    texto_version = fuente.render(f"{texto_titulo}{version}", True, COLOR_TEXTO)
    screen.blit(texto_logo, (20, 15))
    screen.blit(texto_64, (20 + texto_logo.get_width() + 5, 15))
    screen.blit(texto_version, (20 + texto_logo.get_width() + texto_64.get_width() + 20, 20))

    global x_boton_min, x_boton_x, boton_ancho, boton_alto
    boton_ancho, boton_alto = 40, 30
    padding = 10
    x_boton_x = ANCHO_VENTANA - boton_ancho - padding
    x_boton_min = x_boton_x - boton_ancho - 5
    y_boton = 15

    pygame.draw.rect(screen, (60, 60, 60), (x_boton_min, y_boton, boton_ancho, boton_alto), border_radius=4)
    pygame.draw.rect(screen, (200, 60, 60), (x_boton_x, y_boton, boton_ancho, boton_alto), border_radius=4)

    texto_min = fuente_bold.render("-", True, COLOR_TEXTO)
    texto_cerrar = fuente_bold.render("X", True, COLOR_TEXTO)

    screen.blit(texto_min, (x_boton_min + (boton_ancho - texto_min.get_width()) // 2,
                            y_boton + (boton_alto - texto_min.get_height()) // 2))
    screen.blit(texto_cerrar, (x_boton_x + (boton_ancho - texto_cerrar.get_width()) // 2,
                               y_boton + (boton_alto - texto_cerrar.get_height()) // 2))

def dibujar_barra_lateral():
    pygame.draw.rect(screen, COLOR_BARRA_LATERAL, (0, 60, 120, ALTO_VENTANA - 60))
    for i, nombre in enumerate(juegos):
        y = 80 + i * 80
        color = COLOR_TAB_ACTIVA if i == juego_activo else COLOR_TEXTO
        texto = fuente_bold.render(nombre, True, color)
        screen.blit(texto, (15, y))
    x_icono = (120 - 65) // 2
    y_icono = ALTO_VENTANA - 90
    if modo_config:
        icono_tintado = icono_config.copy()
        icono_tintado.fill((3, 137, 173) + (0,), special_flags=pygame.BLEND_RGBA_ADD)
        screen.blit(icono_tintado, (x_icono, y_icono))
    else:
        screen.blit(icono_config, (x_icono, y_icono))
    return pygame.Rect(x_icono, y_icono, 60, 60)

def dibujar_pestanas():
    if modo_config:
        return
    ancho_tab = 160
    alto_tab = 40
    for i, nombre in enumerate(tabs):
        x = 120 + i * ancho_tab
        y = 60
        pygame.draw.rect(screen, COLOR_TAB_INACTIVA, (x, y, ancho_tab, alto_tab))
        
        
        if i == tab_activa:
            pygame.draw.line(screen, COLOR_TAB_ACTIVA, (x, y + alto_tab - 2), (x + ancho_tab - 60, y + alto_tab - 2), 4)

        
        if nombre == "Versiones":
            nombre_mostrado = textos["pestana_versiones"].get(idioma_actual, nombre)
        else:
            nombre_mostrado = nombre

        texto = fuente.render(nombre_mostrado, True, COLOR_TEXTO)
        screen.blit(texto, (x + 20, y + 10))


def dibujar_boton_jugar():
    global escala_boton_jugar

    ancho_base, alto_base = 120, 40
    margen = 40
    x_base = ANCHO_VENTANA - ancho_base - margen
    y_base = ALTO_VENTANA - alto_base - margen


    mouse_x, mouse_y = pygame.mouse.get_pos()
    rect_hover = pygame.Rect(x_base, y_base, ancho_base, alto_base)
    en_hover = rect_hover.collidepoint(mouse_x, mouse_y)

    
    if en_hover:
        escala_boton_jugar = min(1.1, escala_boton_jugar + 0.02)
    else:
        escala_boton_jugar = max(1.0, escala_boton_jugar - 0.02)

    
    ancho_esc = int(ancho_base * escala_boton_jugar)
    alto_esc = int(alto_base * escala_boton_jugar)
    x = x_base + (ancho_base - ancho_esc) // 2
    y = y_base + (alto_base - alto_esc) // 2

    color_boton = (255, 100, 100) if estado_boton_jugar > 0 else (200, 60, 60)
    pygame.draw.rect(screen, color_boton, (x, y, ancho_esc, alto_esc), border_radius=8)

    icono_esc = pygame.transform.scale(icono_jugar, (int(55 * escala_boton_jugar), int(55 * escala_boton_jugar)))
    icono_rect = icono_esc.get_rect(center=(x + ancho_esc // 2, y + alto_esc // 2))
    screen.blit(icono_esc, icono_rect)

    return pygame.Rect(x_base, y_base, ancho_base, alto_base)  

def dibujar_panel():
    global boton_seleccionar_rect, boton_eliminar_rect, boton_carpeta_rect, arrastrando_slider, posicion_click_slider
    global rects_releases, rects_mods, boton_descargar_rect, boton_toggle_mod_rect
    global estado_boton_seleccionar, estado_boton_descargar, estado_boton_toggle_mod
    global escala_boton_seleccionar, escala_boton_eliminar, escala_boton_carpeta
    global escala_boton_descargar, escala_boton_toggle_mod, escala_boton_mas, escala_boton_menos
    global escala_boton_en, escala_boton_es

    rects_releases = []
    rects_mods = []

    x = 120
    y = 100
    ancho = ANCHO_VENTANA - x
    alto = ALTO_VENTANA - y

    if modo_config:
        pygame.draw.rect(screen, (40, 40, 40), (x, y - 40, ancho, alto + 40))
        tex = textos["verificacion_intervalo"][idioma_actual] 
        texto = fuente_pestañas.render(tex, True, COLOR_TEXTO)
        screen.blit(texto, (x + 20, y + -20))

        minutos = intervalo_verificacion // 60
        texto_valor = fuente_bold.render(str(minutos), True, COLOR_TAB_ACTIVA)
        screen.blit(texto_valor, (x + 30, y + 20))

        # Botón +
        boton_mas = pygame.Rect(x + 80, y + 17, 30, 30)
        en_hover_mas = boton_mas.collidepoint(pygame.mouse.get_pos())
        escala_boton_mas = min(1.1, escala_boton_mas + 0.02) if en_hover_mas else max(1.0, escala_boton_mas - 0.02)
        ancho_mas = int(30 * escala_boton_mas)
        alto_mas = int(30 * escala_boton_mas)
        x_mas = boton_mas.x + (30 - ancho_mas) // 2
        y_mas = boton_mas.y + (30 - alto_mas) // 2
        pygame.draw.rect(screen, (255, 100, 100) if estado_boton_mas > 0 else (200, 60, 60), (x_mas, y_mas, ancho_mas, alto_mas), border_radius=6)
        texto_mas = fuente_bold.render("+", True, COLOR_TEXTO)
        screen.blit(texto_mas, (x_mas + (ancho_mas - texto_mas.get_width()) // 2, y_mas + 5))

        # Botón -
        boton_menos = pygame.Rect(x + 120, y + 17, 30, 30)
        en_hover_menos = boton_menos.collidepoint(pygame.mouse.get_pos())
        escala_boton_menos = min(1.1, escala_boton_menos + 0.02) if en_hover_menos else max(1.0, escala_boton_menos - 0.02)
        ancho_menos = int(30 * escala_boton_menos)
        alto_menos = int(30 * escala_boton_menos)
        x_menos = boton_menos.x + (30 - ancho_menos) // 2
        y_menos = boton_menos.y + (30 - alto_menos) // 2
        pygame.draw.rect(screen, (255, 100, 100) if estado_boton_menos > 0 else (200, 60, 60), (x_menos, y_menos, ancho_menos, alto_menos), border_radius=6)
        texto_menos = fuente_bold.render("-", True, COLOR_TEXTO)
        screen.blit(texto_menos, (x_menos + (ancho_menos - texto_menos.get_width()) // 2, y_menos + 5))

        tex = textos["seleccion_idioma"][idioma_actual]  
        texto = fuente_pestañas.render(tex, True, COLOR_TEXTO)
        screen.blit(texto, (x + 20, y + +70))


        # Botón EN
        boton_en = pygame.Rect(x + 30, y + 100, 23, 17)
        en_hover = boton_en.collidepoint(pygame.mouse.get_pos())
        escala_boton_en = min(1.1, escala_boton_en + 0.02) if en_hover else max(1.0, escala_boton_en - 0.02)
        ancho_en = int(23 * escala_boton_en)
        alto_en = int(17 * escala_boton_en)
        x_en = boton_en.x + (23 - ancho_en) // 2
        y_en = boton_en.y + (17 - alto_en) // 2
        icono_esc_en = pygame.transform.scale(icono_en, (ancho_en, alto_en))
        screen.blit(icono_esc_en, (x_en, y_en))

        # Botón ES
        boton_es = pygame.Rect(x + 70, y + 100, 23, 17)
        es_hover = boton_es.collidepoint(pygame.mouse.get_pos())
        escala_boton_es = min(1.1, escala_boton_es + 0.02) if es_hover else max(1.0, escala_boton_es - 0.02)
        ancho_es = int(23 * escala_boton_es)
        alto_es = int(17 * escala_boton_es)
        x_es = boton_es.x + (23 - ancho_es) // 2
        y_es = boton_es.y + (17 - alto_es) // 2
        icono_esc_es = pygame.transform.scale(icono_es, (ancho_es, alto_es))
        screen.blit(icono_esc_es, (x_es, y_es))


        return boton_mas, boton_menos, boton_en, boton_es

    pygame.draw.rect(screen, (40, 40, 40), (x, y, ancho, alto))

    if tabs[tab_activa] == "General":
        fondo = pygame.transform.scale(backgrounds[juego_activo], (ancho, alto))
        screen.blit(fondo, (x, y))
        overlay = pygame.Surface((ancho, alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (x, y))
        instalacion_texto = textos["instalacion_activa"].get(idioma_actual, "Instalación activa:")
        ruta_activa = ruta_instalacion_seleccionada[juegos[juego_activo]]
        nombre_instalacion = os.path.basename(ruta_activa) if ruta_activa else textos["sin_instalacion_activa"].get(idioma_actual, "Sin instalación activa")
        texto = fuente_pestañas.render(f"{instalacion_texto} {nombre_instalacion}", True, COLOR_TEXTO)

        screen.blit(texto, (x + 20, y + 20))
        return dibujar_boton_jugar()

    elif tabs[tab_activa] == "Versiones":
        ancho_sub = 80
        alto_sub = 30
        for i, nombre in enumerate(subpestañas_versiones):
            sub_x = x + i * ancho_sub + 20
            sub_y = y + 10
            color = (200, 60, 60) if i == subpestaña_versiones_activa else (70, 70, 70)
            pygame.draw.rect(screen, color, (sub_x, sub_y, ancho_sub - 10, alto_sub), border_radius=6)
            texto = fuente_pestañas.render(nombre, True, (255, 255, 255))
            screen.blit(texto, (sub_x + 10, sub_y + 5))

        if subpestaña_versiones_activa == 0 and instalacion_preseleccionada:
            boton_x = x + 450
            boton_y = y + 100

            mouse_x, mouse_y = pygame.mouse.get_pos()

            # --- BOTÓN SELECCIONAR ---
            seleccionar_hover = pygame.Rect(boton_x, boton_y, 35, alto_sub).collidepoint(mouse_x, mouse_y)
            escala_boton_seleccionar = min(1.1, escala_boton_seleccionar + 0.02) if seleccionar_hover else max(1.0, escala_boton_seleccionar - 0.02)

            ancho_sel = int(35 * escala_boton_seleccionar)
            alto_sel = int(alto_sub * escala_boton_seleccionar)
            x_sel = boton_x + (35 - ancho_sel) // 2
            y_sel = boton_y + (alto_sub - alto_sel) // 2

            color_sel = (255, 100, 100) if estado_boton_seleccionar > 0 else (200, 60, 60)
            pygame.draw.rect(screen, color_sel, (x_sel, y_sel, ancho_sel, alto_sel), border_radius=6)

            icono_sel = pygame.transform.scale(icono_seleccionar, (int(20 * escala_boton_seleccionar), int(20 * escala_boton_seleccionar)))
            icono_rect = icono_sel.get_rect(center=(x_sel + ancho_sel // 2, y_sel + alto_sel // 2))
            screen.blit(icono_sel, icono_rect)

            boton_seleccionar_rect = pygame.Rect(boton_x, boton_y, 35, alto_sub)

            # --- BOTÓN CARPETA ---
            boton_carpeta_y = boton_y + alto_sub + 10
            carpeta_hover = pygame.Rect(boton_x + 45, boton_carpeta_y - 40, 35, alto_sub).collidepoint(mouse_x, mouse_y)
            escala_boton_carpeta = min(1.1, escala_boton_carpeta + 0.02) if carpeta_hover else max(1.0, escala_boton_carpeta - 0.02)

            ancho_carp = int(35 * escala_boton_carpeta)
            alto_carp = int(alto_sub * escala_boton_carpeta)
            x_carp = boton_x + 45 + (35 - ancho_carp) // 2
            y_carp = boton_carpeta_y - 40 + (alto_sub - alto_carp) // 2

            color_carpeta = (255, 100, 100) if estado_boton_carpeta > 0 else (200, 60, 60)
            pygame.draw.rect(screen, color_carpeta, (x_carp, y_carp, ancho_carp, alto_carp), border_radius=6)

            icono_carp = pygame.transform.scale(icono_carpeta, (int(20 * escala_boton_carpeta), int(20 * escala_boton_carpeta)))
            icono_rect = icono_carp.get_rect(center=(x_carp + ancho_carp // 2, y_carp + alto_carp // 2))
            screen.blit(icono_carp, icono_rect)

            boton_carpeta_rect = pygame.Rect(boton_x + 45, boton_carpeta_y - 40, 35, alto_sub)

            # --- BOTÓN ELIMINAR ---
            boton_eliminar_y = boton_y + alto_sub + 10
            eliminar_hover = pygame.Rect(boton_x + 90, boton_eliminar_y - 40, 35, alto_sub).collidepoint(mouse_x, mouse_y)
            escala_boton_eliminar = min(1.1, escala_boton_eliminar + 0.02) if eliminar_hover else max(1.0, escala_boton_eliminar - 0.02)

            ancho_eli = int(35 * escala_boton_eliminar)
            alto_eli = int(alto_sub * escala_boton_eliminar)
            x_eli = boton_x + 90 + (35 - ancho_eli) // 2
            y_eli = boton_eliminar_y - 40 + (alto_sub - alto_eli) // 2

            color_eli = (255, 100, 100) if estado_boton_eliminar > 0 else (200, 60, 60)
            pygame.draw.rect(screen, color_eli, (x_eli, y_eli, ancho_eli, alto_eli), border_radius=6)

            icono_eli = pygame.transform.scale(icono_papelera, (int(20 * escala_boton_eliminar), int(20 * escala_boton_eliminar)))
            icono_rect = icono_eli.get_rect(center=(x_eli + ancho_eli // 2, y_eli + alto_eli // 2))
            screen.blit(icono_eli, icono_rect)

            boton_eliminar_rect = pygame.Rect(boton_x + 90, boton_eliminar_y - 40, 35, alto_sub)

            

        else:
            boton_seleccionar_rect = None
            boton_eliminar_rect = None
            boton_carpeta_rect = None

        marco_x = x + 10
        marco_y = y + 90
        marco_ancho = ancho - 200
        marco_alto = alto - 120
        pygame.draw.rect(screen, (25, 25, 25), (marco_x, marco_y, marco_ancho, marco_alto), width=2, border_radius=6)

        superficie = pygame.Surface((marco_ancho - 14, marco_alto - 4))
        superficie.fill((40, 40, 40))

        if subpestaña_versiones_activa == 0:
            elementos = listar_instalaciones()
            scroll_offset_vers = scroll_offset_versiones_local
            tex = textos["seleccionar_local"][idioma_actual]
            adv = fuente_pestañas.render(tex, True, (255, 255, 255))
            screen.blit(adv, (x + 20, y + 60))
        else:
            elementos = obtener_releases_formateadas(juegos[juego_activo])
            scroll_offset_vers = scroll_offset_versiones_online
            tex = textos["seleccionar_version_online"][idioma_actual]
            adv = fuente_pestañas.render(tex, True, (255, 255, 255))
            screen.blit(adv, (x + 20, y + 60))

        visibles = (marco_alto - 20) // 30
        total = len(elementos)
        max_scroll = max(0, total - visibles)
        scroll_offset_clamped = max(0, min(scroll_offset_vers, max_scroll))

        if not elementos:
            tex = textos["sin_versiones"][idioma_actual]
            texto = fuente.render(tex, True, COLOR_TEXTO)
            superficie.blit(texto, (10, 5))
        else:
            for i, nombre in enumerate(elementos[scroll_offset_clamped:]):
                item_y = i * 30
                if item_y + 30 > superficie.get_height():
                    break

                color = COLOR_TEXTO
                if subpestaña_versiones_activa == 0:
                    ruta = os.path.join(obtener_carpeta_juego(), nombre)
                    color = COLOR_TAB_ACTIVA if ruta == instalacion_preseleccionada else COLOR_TEXTO

                if subpestaña_versiones_activa == 1:
                    if (i + scroll_offset_clamped) == release_seleccionada_indice:
                        color = COLOR_TAB_ACTIVA
                    else:
                        color = COLOR_TEXTO

                nombre_limpio = nombre.replace(" [instalado]", "")
                texto = fuente.render(nombre_limpio, True, color)
                superficie.blit(texto, (10, item_y + 5))

               
                if "[instalado]" in nombre:
                    superficie.blit(icono_check, (10 + texto.get_width() + 5, item_y + 5))

                rect = pygame.Rect(marco_x + 12, marco_y + 2 + item_y, marco_ancho - 28, 30)
                rects_releases.append((rect, i + scroll_offset_clamped))

        screen.blit(superficie, (marco_x + 2, marco_y + 2))

        if total > visibles:
            barra_x = marco_x + marco_ancho - 10
            barra_y = marco_y + 2
            barra_alto = marco_alto - 4
            proporcion = visibles / total
            alto_slider = max(20, int(barra_alto * proporcion))
            pos_slider = int((barra_alto - alto_slider) * (scroll_offset_clamped / max_scroll))
            rect_slider = pygame.Rect(barra_x + 1, barra_y + pos_slider, 4, alto_slider)
            pygame.draw.rect(screen, COLOR_SCROLLBAR, rect_slider, border_radius=3)

        if subpestaña_versiones_activa == 1 and release_seleccionada_indice is not None:
            release_texto = obtener_releases_formateadas(juegos[juego_activo])[release_seleccionada_indice]
            if "[instalado]" not in release_texto:
                boton_x = x + 450
                boton_y = y + 100
                rect_descargar = pygame.Rect(boton_x, boton_y, 35, 30)
                en_hover = rect_descargar.collidepoint(pygame.mouse.get_pos())
                escala_boton_descargar = min(1.1, escala_boton_descargar + 0.02) if en_hover else max(1.0, escala_boton_descargar - 0.02)
                ancho_esc = int(35 * escala_boton_descargar)
                alto_esc = int(30 * escala_boton_descargar)
                x_esc = boton_x + (35 - ancho_esc) // 2
                y_esc = boton_y + (30 - alto_esc) // 2
                color_descargar = (255, 100, 100) if estado_boton_descargar > 0 else (200, 60, 60)
                pygame.draw.rect(screen, color_descargar, (x_esc, y_esc, ancho_esc, alto_esc), border_radius=6)
                screen.blit(icono_descargar, (x_esc + ancho_esc // 2 - 10, y_esc + alto_esc // 2 - 10))
                boton_descargar_rect = pygame.Rect(boton_x, boton_y, 35, 30)
                if descargando_en_progreso:
                    icono_rotado = pygame.transform.rotate(icono_cargando, angulo_carga)
                    rect = icono_rotado.get_rect(center=(boton_x + 65, boton_y + 15))
                    screen.blit(icono_rotado, rect)

        return None

    else:  # Mods
        seleccion = ruta_instalacion_seleccionada[juegos[juego_activo]]
        if not seleccion:
            tex = textos["sin_instalacion"][idioma_actual]
            texto = fuente.render(tex, True, COLOR_TEXTO)
            screen.blit(texto, (x + 20, y + 20))
            return None

        ruta_mods = os.path.join(seleccion, "mods")
        if not os.path.isdir(ruta_mods):
            tex = textos["carpeta_mods_no_encontrada"][idioma_actual]
            texto = fuente.render(tex, True, COLOR_TEXTO)
            screen.blit(texto, (x + 20, y + 20))
            return None

        archivos = os.listdir(ruta_mods)
        if not archivos:
            tex = textos["carpeta_mods_vacia"][idioma_actual]
            texto = fuente.render(tex, True, COLOR_TEXTO)
            screen.blit(texto, (x + 20, y + 20))
            return None
        tex = textos["advertencia_mods"][idioma_actual]
        adv = fuente_pestañas.render(tex, True, COLOR_TAB_ACTIVA)
        screen.blit(adv, (x + 250, y + 20))
        tex = textos["advertencia_mods_desc"][idioma_actual]
        adv1 = fuente_pestañas.render(tex, True, COLOR_TAB_ACTIVA)
        screen.blit(adv1, (x + 20, y + 45))

        marco_x = x + 10
        marco_y = y + 90
        marco_ancho = ancho - 200
        marco_alto = alto - 140
        pygame.draw.rect(screen, (25, 25, 25), (marco_x, marco_y, marco_ancho, marco_alto), width=2, border_radius=6)

        superficie_mods = pygame.Surface((marco_ancho - 14, marco_alto - 4))
        superficie_mods.fill((40, 40, 40))

        mods_visibles = (marco_alto - 20) // 30
        total_mods = len(archivos)
        max_scroll = max(0, total_mods - mods_visibles)
        scroll_offset_clamped = max(0, min(scroll_offset, max_scroll))

        for i, archivo in enumerate(archivos[scroll_offset_clamped:]):
            item_y = i * 30
            if item_y + 30 > superficie_mods.get_height():
                break

            
            if archivo.endswith(".disabled"):
                nombre_mostrado = archivo[:-9]
                color = (200, 60, 60)
            elif archivo.endswith(".otr") or archivo.endswith(".o2r"):
                nombre_mostrado = archivo[:-4]
                color = (60, 200, 60)
            else:
                nombre_mostrado = archivo
                color = COLOR_TEXTO

            
            if archivo == mod_seleccionado:
                color = COLOR_TAB_ACTIVA

            texto = fuente_pestañas.render(nombre_mostrado, True, color)
            superficie_mods.blit(texto, (10, item_y + 5))

            rect_mod = pygame.Rect(marco_x + 12, marco_y + 2 + item_y, marco_ancho - 28, 30)
            rects_mods.append((rect_mod, archivo))

        screen.blit(superficie_mods, (marco_x + 2, marco_y + 2))

        if total_mods > mods_visibles:
            barra_x = marco_x + marco_ancho - 10
            barra_y = marco_y + 2
            barra_alto = marco_alto - 4
            proporcion = mods_visibles / total_mods
            alto_slider = max(20, int(barra_alto * proporcion))
            pos_slider = int((barra_alto - alto_slider) * (scroll_offset_clamped / max_scroll))
            rect_slider = pygame.Rect(barra_x + 1, barra_y + pos_slider, 4, alto_slider)
            pygame.draw.rect(screen, COLOR_SCROLLBAR, rect_slider, border_radius=3)

        if mod_seleccionado:
            ruta_mod = os.path.join(ruta_mods, mod_seleccionado)
            if os.path.isfile(ruta_mod):
                boton_x = x + 450
                boton_y = y + 100
                rect_toggle = pygame.Rect(boton_x, boton_y, 35, 30)
                en_hover = rect_toggle.collidepoint(pygame.mouse.get_pos())
                escala_boton_toggle_mod = min(1.1, escala_boton_toggle_mod + 0.02) if en_hover else max(1.0, escala_boton_toggle_mod - 0.02)
                ancho_esc = int(35 * escala_boton_toggle_mod)
                alto_esc = int(30 * escala_boton_toggle_mod)
                x_esc = boton_x + (35 - ancho_esc) // 2
                y_esc = boton_y + (30 - alto_esc) // 2
                color_toggle = (255, 100, 100) if estado_boton_toggle_mod > 0 else (200, 60, 60)
                pygame.draw.rect(screen, color_toggle, (x_esc, y_esc, ancho_esc, alto_esc), border_radius=6)
                screen.blit(icono_mods, (x_esc + ancho_esc // 2 - 10, y_esc + alto_esc // 2 - 10))
                boton_toggle_mod_rect = pygame.Rect(boton_x, boton_y, 35, 30)

        return None

def dibujar_ventana_confirmacion(texto_linea1, texto_linea2):
    global escala_boton_si, escala_boton_no

    ancho = 400
    alto = 160
    x = (ANCHO_VENTANA - ancho) // 2
    y = (ALTO_VENTANA - alto) // 2

    pygame.draw.rect(screen, (35, 35, 35), (x, y, ancho, alto), border_radius=10)
    pygame.draw.rect(screen, (25, 25, 25), (x, y, ancho, alto), 2, border_radius=10)

    texto1 = fuente_pestañas.render(texto_linea1, True, (255, 255, 255))
    texto2 = fuente.render(texto_linea2, True, (255, 255, 255))
    screen.blit(texto1, (x + (ancho - texto1.get_width()) // 2, y + 20))
    screen.blit(texto2, (x + (ancho - texto2.get_width()) // 2, y + 45))

    mouse_x, mouse_y = pygame.mouse.get_pos()

    
    boton_si_base = pygame.Rect(x + 60, y + 100, 100, 30)
    hover_si = boton_si_base.collidepoint(mouse_x, mouse_y)
    escala_boton_si = min(1.1, escala_boton_si + 0.02) if hover_si else max(1.0, escala_boton_si - 0.02)

    ancho_si = int(100 * escala_boton_si)
    alto_si = int(30 * escala_boton_si)
    x_si = boton_si_base.x + (100 - ancho_si) // 2
    y_si = boton_si_base.y + (30 - alto_si) // 2
    boton_si = pygame.Rect(x_si, y_si, ancho_si, alto_si)

    color_si = (255, 100, 100) if estado_boton_si > 0 else (200, 60, 60)
    pygame.draw.rect(screen, color_si, boton_si, border_radius=6)
    tex = textos["boton_si"][idioma_actual]
    texto_si = fuente_bold.render(tex, True, (255, 255, 255))
    screen.blit(texto_si, (x_si + (ancho_si - texto_si.get_width()) // 2, y_si + 5))

    
    boton_no_base = pygame.Rect(x + 240, y + 100, 100, 30)
    hover_no = boton_no_base.collidepoint(mouse_x, mouse_y)
    escala_boton_no = min(1.1, escala_boton_no + 0.02) if hover_no else max(1.0, escala_boton_no - 0.02)

    ancho_no = int(100 * escala_boton_no)
    alto_no = int(30 * escala_boton_no)
    x_no = boton_no_base.x + (100 - ancho_no) // 2
    y_no = boton_no_base.y + (30 - alto_no) // 2
    boton_no = pygame.Rect(x_no, y_no, ancho_no, alto_no)
    
    color_no = (255, 100, 100) if estado_boton_no > 0 else (200, 60, 60)
    pygame.draw.rect(screen, color_no, boton_no, border_radius=6)
    tex = textos["boton_no"][idioma_actual]
    texto_no = fuente_bold.render(tex, True, (255, 255, 255))
    screen.blit(texto_no, (x_no + (ancho_no - texto_no.get_width()) // 2, y_no + 5))

    return boton_si, boton_no
        


cargar_selecciones()
revisar_nuevas_releases()
threading.Thread(target=precargar_releases, daemon=True).start()
threading.Thread(target=ciclo_verificacion_periodica, args=(lambda: intervalo_verificacion,), daemon=True).start()


# --- Bucle principal ---
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            x, y = evento.pos

            if mostrar_confirmacion_eliminar:
                if boton_si_rect.collidepoint(x, y):
                    estado_boton_si = 5
                    try:
                        shutil.rmtree(ruta_a_eliminar)
                        if ruta_instalacion_seleccionada[juegos[juego_activo]] == ruta_a_eliminar:
                            ruta_instalacion_seleccionada[juegos[juego_activo]] = None
                        guardar_selecciones()
                        instalacion_preseleccionada = None

                        clave = NOMBRE_A_CLAVE[juegos[juego_activo]]
                        carpetas_locales = obtener_carpetas_del_port(clave)
                        lista = releases_cache.get(juegos[juego_activo], [])
                        for i, texto in enumerate(lista):
                            if "[instalado]" in texto:
                                if not verificar_version_local(obtener_releases(REPOS[clave])[i], carpetas_locales):
                                    lista[i] = texto.replace(" [instalado]", "")
                        print("Instalación eliminada.")
                    except Exception as e:
                        print("Error al eliminar:", e)
                    mostrar_confirmacion_eliminar = False
                    ruta_a_eliminar = None

                elif boton_no_rect.collidepoint(x, y):
                    estado_boton_no = 5
                    mostrar_confirmacion_eliminar = False
                    ruta_a_eliminar = None

                continue

            if y < 60 and not (x_boton_min <= x <= x_boton_min + boton_ancho or x_boton_x <= x <= x_boton_x + boton_ancho):
                comenzar_arrastre()

            if not modo_config:
                for i in range(len(tabs)):
                    tab_x = 120 + i * 160
                    if tab_x <= x <= tab_x + 160 and 60 <= y <= 100:
                        tab_activa = i
                        release_seleccionada_indice = None

            if tabs[tab_activa] == "Versiones":
                base_x = 120
                base_y = 100
                ancho_sub = 80
                alto_sub = 30

                for i in range(len(subpestañas_versiones)):
                    sub_x = base_x + i * ancho_sub + 20
                    sub_y = base_y + 10
                    if sub_x <= x <= sub_x + ancho_sub - 10 and sub_y <= y <= sub_y + alto_sub:
                        subpestaña_versiones_activa = i
                        instalacion_preseleccionada = None
                        release_seleccionada_indice = None

                if subpestaña_versiones_activa == 0:
                    lista = listar_instalaciones()
                    for rect, i in rects_releases:
                        if rect.collidepoint(x, y):
                            if i < len(lista):
                                instalacion_preseleccionada = os.path.join(obtener_carpeta_juego(), lista[i])
                            break

                    if boton_seleccionar_rect and boton_seleccionar_rect.collidepoint(x, y):
                        ruta_instalacion_seleccionada[juegos[juego_activo]] = instalacion_preseleccionada
                        guardar_selecciones()
                        estado_boton_seleccionar = 5

                    if boton_eliminar_rect and boton_eliminar_rect.collidepoint(x, y):
                        if instalacion_preseleccionada and os.path.isdir(instalacion_preseleccionada):
                            mostrar_confirmacion_eliminar = True
                            ruta_a_eliminar = instalacion_preseleccionada
                            estado_boton_eliminar = 5

                    if boton_carpeta_rect and boton_carpeta_rect.collidepoint(x, y):
                        if instalacion_preseleccionada and os.path.isdir(instalacion_preseleccionada):
                            ruta_absoluta = os.path.abspath(instalacion_preseleccionada)
                            estado_boton_carpeta = 5
                            if os.path.isdir(ruta_absoluta):
                                os.startfile(ruta_absoluta)
                            else:
                                print(f"[ERROR] Carpeta no encontrada: {ruta_absoluta}")

                elif subpestaña_versiones_activa == 1:
                    for rect, indice_release in rects_releases:
                        if rect.collidepoint(x, y):
                            release_seleccionada_indice = indice_release
                            break

                    if boton_descargar_rect and boton_descargar_rect.collidepoint(x, y):
                        if release_seleccionada_indice is not None:
                            estado_boton_descargar = 5

                            def hilo_descarga(juego, indice):
                                global descargando_en_progreso
                                descargando_en_progreso = True
                                try:
                                    descargar_y_extraer_release(juego, indice)
                                finally:
                                    descargando_en_progreso = False

                                clave = NOMBRE_A_CLAVE[juego]
                                carpetas_locales = obtener_carpetas_del_port(clave)
                                lista = releases_cache.get(juego, [])
                                if 0 <= indice < len(lista):
                                    if "[instalado]" not in lista[indice]:
                                        lista[indice] = lista[indice].replace(")", " [instalado])") if ")" in lista[indice] else lista[indice] + " [instalado]"

                            threading.Thread(target=hilo_descarga, args=(juegos[juego_activo], release_seleccionada_indice), daemon=True).start()

            if tabs[tab_activa] == "Mods":
                for rect, archivo in rects_mods:
                    if rect.collidepoint(x, y):
                        mod_seleccionado = archivo
                        break

                if boton_toggle_mod_rect and boton_toggle_mod_rect.collidepoint(x, y):
                    seleccion = ruta_instalacion_seleccionada[juegos[juego_activo]]
                    estado_boton_toggle_mod = 5
                    if seleccion:
                        ruta_mods = os.path.join(seleccion, "mods")
                        ruta_mod = os.path.join(ruta_mods, mod_seleccionado)
                        if os.path.isfile(ruta_mod):
                            nombre_base, extension = os.path.splitext(mod_seleccionado)
                            if extension == ".disabled":
                                nueva_ext = ".otr" if juegos[juego_activo].lower() == "soh" else ".o2r"
                            else:
                                nueva_ext = ".disabled"
                            nuevo_nombre = nombre_base + nueva_ext
                            nueva_ruta = os.path.join(ruta_mods, nuevo_nombre)
                            try:
                                os.rename(ruta_mod, nueva_ruta)
                                mod_seleccionado = nuevo_nombre
                            except Exception as e:
                                print(f"Error al renombrar el mod: {e}")

            for i in range(len(juegos)):
                juego_y = 80 + i * 80
                if 0 <= x <= 120 and juego_y <= y <= juego_y + 40:
                    juego_activo = i
                    modo_config = False
                    instalacion_preseleccionada = None
                    scroll_offset_versiones_local = 0
                    scroll_offset_versiones_online = 0
                    scroll_offset = 0
                    release_seleccionada_indice = None

            if evento.button == 4 or evento.button == 5:
                scroll_cambio = -1 if evento.button == 4 else 1
                mx, my = pygame.mouse.get_pos()
                if tabs[tab_activa] == "Versiones":
                    if subpestaña_versiones_activa == 0:
                        elementos = listar_instalaciones()
                        visibles = (ALTO_VENTANA - 100 - 120 - 20) // 30
                        max_scroll = max(0, len(elementos) - visibles)
                        scroll_offset_versiones_local = max(0, min(scroll_offset_versiones_local + scroll_cambio, max_scroll))
                    else:
                        elementos = obtener_releases_formateadas(juegos[juego_activo])
                        visibles = (ALTO_VENTANA - 100 - 120 - 20) // 30
                        max_scroll = max(0, len(elementos) - visibles)
                        scroll_offset_versiones_online = max(0, min(scroll_offset_versiones_online + scroll_cambio, max_scroll))
                elif tabs[tab_activa] == "Mods":
                    seleccion = ruta_instalacion_seleccionada[juegos[juego_activo]]
                    if seleccion:
                        ruta_mods = os.path.join(seleccion, "mods")
                        if os.path.isdir(ruta_mods):
                            archivos = os.listdir(ruta_mods)
                            visibles = (ALTO_VENTANA - 100 - 140 - 20) // 30
                            max_scroll = max(0, len(archivos) - visibles)
                            scroll_offset = max(0, min(scroll_offset + scroll_cambio, max_scroll))

            if 15 <= y <= 45:
                if x_boton_min <= x <= x_boton_min + boton_ancho:
                    pygame.display.iconify()
                elif x_boton_x <= x <= x_boton_x + boton_ancho:
                    pygame.quit()
                    sys.exit()

            if boton_jugar_rect and boton_jugar_rect.collidepoint(x, y):
                estado_boton_jugar = 5
                ejecutar_juego()

            if "rect_config" in globals() and rect_config.collidepoint(x, y):
                modo_config = True

            if modo_config:
                if boton_mas_rect and boton_mas_rect.collidepoint(x, y):
                    intervalo_verificacion = min(21600, intervalo_verificacion + 300)
                    estado_boton_mas = 5
                    guardar_selecciones()
                elif boton_menos_rect and boton_menos_rect.collidepoint(x, y):
                    intervalo_verificacion = max(1800, intervalo_verificacion - 300)
                    estado_boton_menos = 5
                    guardar_selecciones()
                if boton_en_rect and boton_en_rect.collidepoint(x, y):
                    idioma_actual = "en"
                    guardar_selecciones()
                if boton_es_rect and boton_es_rect.collidepoint(x, y):
                    idioma_actual = "es"
                    guardar_selecciones()
                        

        elif evento.type == pygame.MOUSEBUTTONUP:
            arrastrando_slider = False

    screen.fill(COLOR_FONDO)
    rect_config = dibujar_barra_lateral()
    dibujar_encabezado()
    dibujar_pestanas()
    
    if not modo_config:
        boton_jugar_rect = dibujar_panel()
    if modo_config:
        resultado_panel = dibujar_panel()
    if modo_config and resultado_panel:
        juego_activo = -1
        boton_mas_rect, boton_menos_rect, boton_en_rect, boton_es_rect = resultado_panel
    else:
        boton_mas_rect = boton_menos_rect = boton_en_rect = boton_es_rect = None

    if mostrar_confirmacion_eliminar:
        tex = textos["confirmar_eliminar"][idioma_actual]
        boton_si_rect, boton_no_rect = dibujar_ventana_confirmacion(
            tex,
            os.path.basename(ruta_a_eliminar or ""),
        )

    if estado_boton_seleccionar > 0:
        estado_boton_seleccionar -= 1
    if estado_boton_descargar > 0:
        estado_boton_descargar -= 1
    if estado_boton_jugar > 0:
        estado_boton_jugar -= 1
    if estado_boton_eliminar > 0:
        estado_boton_eliminar -= 1
    if estado_boton_carpeta > 0:
        estado_boton_carpeta -= 1
    if estado_boton_toggle_mod > 0:
        estado_boton_toggle_mod -= 1
    if estado_boton_mas > 0:
        estado_boton_mas -= 1
    if estado_boton_menos > 0:
        estado_boton_menos -= 1
    if estado_boton_si > 0:
        estado_boton_si -= 1
    if estado_boton_no > 0:
        estado_boton_no -= 1    

    if descargando_en_progreso:
        angulo_carga = (angulo_carga + 5) % 360

    pygame.display.flip()
    clock.tick(FPS)



