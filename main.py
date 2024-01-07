import nextcord, os, random, datetime
from nextcord import Embed
from nextcord import File
from nextcord.ext import commands
from keep_alive import keep_alive
import asyncio  # Agrega esta línea
import string
import datetime
import json
import sys 
import typing
from nextcord.ui import View, Button
from nextcord.ui import Button
import atexit
import copy
from typing import List, Dict
import requests
from tmdbv3api import TMDb, Movie, TV  # Importar las clases Movie y TV


def obtener_info_pelicula(api_key, titulo, idioma="es"):
  base_url = "https://api.themoviedb.org/3/search/movie"
  params = {
      "api_key": api_key,
      "query": titulo,
      "language": idioma
  }

  response = requests.get(base_url, params=params)
  data = response.json()

  if data["results"]:
      movie_id = data["results"][0]["id"]
      return obtener_detalles_pelicula(api_key, movie_id, idioma)
  else:
      return None

def obtener_detalles_pelicula(api_key, movie_id, idioma="es"):
  base_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
  params = {
      "api_key": api_key,
      "language": idioma
  }

  response = requests.get(base_url, params=params)
  data = response.json()

  return data

def obtener_info_serie(api_key, serie, idioma="es"):
  base_url = "https://api.themoviedb.org/3/search/tv"
  params = {
      "api_key": api_key,
      "query": serie,
      "language": idioma,
  }

  response = requests.get(base_url, params=params)
  data = response.json()

  if "results" in data and data["results"]:
      serie_id = data["results"][0].get("id")
      if serie_id:
          # Obtener información detallada de la serie con el nuevo id
          serie_info_url = f"https://api.themoviedb.org/3/tv/{serie_id}"
          params = {
              "api_key": api_key,
              "language": idioma,
          }
          serie_info_response = requests.get(serie_info_url, params=params)
          serie_info_data = serie_info_response.json()

          # Intenta obtener la sinopsis en español, si está disponible
          sinopsis_espanol = serie_info_data.get("overview", "")

          # Verifica si la sinopsis es en español
          if serie_info_data.get("original_language") == "es" or serie_info_data.get("origin_country") == "ES":
              return {
                  "overview": sinopsis_espanol,
                  "backdrop_path": serie_info_data.get("backdrop_path", ""),
              }

  return None



free_gen_channel = 1176193901552480398 # Channel ID here
keep_alive()

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents, help_command=None)


server_name = "ZFLIX"
server_logo = "https://cdn.discordapp.com/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?ex=6547ca6f&is=6535556f&hm=654f2cec7a88da46958a1de81cae56621565b8c65484776896a1af3f22633361&"

# Diccionario para almacenar la configuración del servidor
configuracion_servidores = {}

# Archivo JSON para almacenar la configuración
CONFIG_FILE = 'config.json'
MEMBERS_WELCOMED_FILE = 'members_welcomed.json'
SERVER_LOGO_URL = 'URL_DEL_LOGO_DEL_SERVIDOR'

# Obtener la API key de TMDB desde Replit Secrets
TMDB_API_KEY = os.getenv("TMDB_API_KEY_REPLIT")

idioma = "es"  # Código de idioma para español

TMDB_LANGUAGE = 'es-ES'  # Código de idioma para español castellano

# Crear el bot
bot = nextcord.Client()

# Conjunto para almacenar IDs de miembros que ya recibieron la bienvenida
miembros_bienvenida_enviada = set()

# URL del logo del servidor (constante)
SERVER_LOGO_URL = "https://cdn.discordapp.com/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?ex=6547ca6f&is=6535556f&hm=654f2cec7a88da46958a1de81cae56621565b8c65484776896a1af3f22633361&"

bot = commands.Bot(command_prefix='/', intents=nextcord.Intents.all(), help_command=None)






# Cargar información de miembros que ya han sido bienvenidos
try:
    with open(MEMBERS_WELCOMED_FILE, 'r') as file:
        members_welcomed = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    members_welcomed = {}

@bot.event
async def on_ready():
    print(f'Bot está conectado como {bot.user.name}')

    # Cargar configuración al iniciar el bot
    load_config()

    # Iniciar loop de actualización de presencia
    bot.loop.create_task(update_presence())

async def update_presence():
    while True:
        try:
            for servidor_id, configuracion in configuracion_servidores.items():
                canal_bienvenida_id = configuracion['canal_bienvenida']
                canal_bienvenida = bot.get_channel(canal_bienvenida_id)

                if canal_bienvenida:
                    nuevos_miembros = [
                        miembro for miembro in canal_bienvenida.guild.members
                        if miembro.id not in members_welcomed.get(servidor_id, [])
                    ]

                    for miembro in nuevos_miembros:
                        titulo_bienvenida = "Bienvenid@ a ZFLIX🍿"
                        descripcion_bienvenida = (
                            f"**¡Hey, {miembro.mention}! Agradecemos que confíes en nosotros uniéndote a ZFLIX. "
                            "Aquí encontrarás películas y series a la mejor calidad. Espero que te diviertas.**"
                        )

                        # Obtener una imagen aleatoria de una película o serie de TMDb
                        imagen_peli = get_random_movie_or_tv_show_image()
                      
                        imagen_url = configuracion.get('imagen_url', None)

                        embed = nextcord.Embed(title=titulo_bienvenida, description=descripcion_bienvenida, color=0x00ff00)
                        if imagen_url:
                            embed.set_image(url=imagen_url)
                        embed.set_thumbnail(url=imagen_peli)

                        try:
                            await canal_bienvenida.send(embed=embed)
                            members_welcomed.setdefault(servidor_id, []).append(miembro.id)
                        except nextcord.Forbidden:
                            print(f"No tengo permisos para enviar mensajes en {canal_bienvenida.name}.")
                        except nextcord.HTTPException as e:
                            print(f"Error al enviar mensaje: {e}")

            stock_castellano_pelis = len(os.listdir("stock_castellano/"))
            stock_latino_pelis = len(os.listdir("stock_latino/"))
            stock_castellano_series = len(os.listdir("stock_series_castellano/"))
            stock_latino_series = len(os.listdir("stock_series_latino/"))

            status_message_castellano_pelis = f"Castellano pelis: {stock_castellano_pelis}"
            status_message_latino_pelis = f"Latino pelis: {stock_latino_pelis}"
            status_message_castellano_series = f"Castellano series: {stock_castellano_series}"
            status_message_latino_series = f"Latino series: {stock_latino_series}"

            await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=status_message_castellano_pelis))
            await asyncio.sleep(5)
            await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=status_message_latino_pelis))
            await asyncio.sleep(5)
            await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=status_message_castellano_series))
            await asyncio.sleep(5)
            await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=status_message_latino_series))
            await asyncio.sleep(5)

            with open(MEMBERS_WELCOMED_FILE, 'w') as file:
                json.dump(members_welcomed, file, indent=2)

        except ConnectionResetError as e:
            print(f"Error de conexión: {e}")
            await asyncio.sleep(10)
            continue
        except Exception as e:
            print(f"Error no manejado: {e}")



def load_config():
    global configuracion_servidores
    try:
        with open(CONFIG_FILE, 'r') as file:
            configuracion_servidores = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        print("No se encontró el archivo de configuración o tiene un formato no válido. Creando uno nuevo.")
        configuracion_servidores = {}
        save_config()  # Crear un archivo nuevo si no existe o es inválido

def save_config():
    with open(CONFIG_FILE, 'w') as file:
        json.dump(configuracion_servidores, file, indent=2)


def get_random_movie_or_tv_show_image():
    # Hacer una solicitud a la API de TMDb para obtener una lista de películas populares
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=es'
    response = requests.get(url)
    data = response.json()

    # Elegir una película aleatoria de la lista
    if 'results' in data and data['results']:
        random_movie = random.choice(data['results'])
        poster_path = random_movie.get('poster_path')

        # Construir la URL completa de la imagen
        if poster_path:
            base_url = 'https://image.tmdb.org/t/p/w500'
            return f'{base_url}/{poster_path}'

    return None

# logearse -----------------------------------------

def get_authenticated_users():
    try:
        with open('authenticated_users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_authenticated_user(user_id):
    authenticated_users = get_authenticated_users()
    authenticated_users.append(user_id)
    with open('authenticated_users.json', 'w') as f:
        json.dump(authenticated_users, f)

def user_exists(username):
    try:
        with open('users.txt', 'r') as f:
            lines = f.readlines()
            for line in lines:
                stored_username = line.strip()
                if username == stored_username:
                    return True
    except FileNotFoundError:
        return False

    return False

def store_user(username):
    # Almacenar el nuevo usuario en el archivo
    with open('users.txt', 'a') as f:
        f.write(f"{username}\n")

def check_credentials(username):
    # Verificar las credenciales con el archivo de usuarios
    return user_exists(username)

@bot.slash_command(name='autenticacion', description='Inicia el proceso de autenticación')
async def autenticacion(ctx):
    message_content = (
        "Elige una opción:\n"
        "/signup - Para registrarte\n"
        "/login - Para iniciar sesión\n"
        "/logout - Para cerrar sesión"
    )
    await ctx.send(message_content)

@bot.slash_command(name='signup', description='Regístrate con un nombre de usuario')
async def signup(ctx):
    username = ctx.user.name  # Change from ctx.author.name to ctx.user.name
    if not user_exists(username):
        store_user(username)
        save_authenticated_user(ctx.user.id)  # Change from ctx.author.id to ctx.user.id
        await ctx.send(f"Cuenta creada exitosamente para {ctx.user.mention}.")
    else:
        await ctx.send("El nombre de usuario ya está en uso. Por favor, elige otro.")

@bot.slash_command(name='login', description='Inicia sesión con tu nombre de usuario')
async def login(ctx):
    username = ctx.user.name  # Change from ctx.author.name to ctx.user.name
    if user_exists(username):
        save_authenticated_user(ctx.user.id)  # Change from ctx.author.id to ctx.user.id
        await ctx.send(f"Autenticación exitosa para {ctx.user.mention}.")
    else:
        await ctx.send("Autenticación fallida. Verifica tus credenciales o regístrate primero.")

@bot.slash_command(name='logout', description='Cierra sesión')
async def logout(ctx):
    user_id = ctx.user.id
    authenticated_users = get_authenticated_users()

    if user_id in authenticated_users:
        # Eliminar al usuario del archivo 'users.txt'
        username = ctx.user.name
        remove_user(username)

        # Actualizar la lista de usuarios autenticados
        authenticated_users.remove(user_id)
        with open('authenticated_users.json', 'w') as f:
            json.dump(authenticated_users, f)

        await ctx.send(f"Sesión cerrada para {ctx.user.mention}.")
    else:
        await ctx.send("No tienes una sesión activa.")

def remove_user(username):
    try:
        with open('users.txt', 'r') as f:
            lines = f.readlines()

        with open('users.txt', 'w') as f:
            for line in lines:
                stored_username = line.strip()
                if username != stored_username:
                    f.write(line)
    except FileNotFoundError:
        pass

#---------------------------------
class VerificationView(View):
    def __init__(self, verification_link):
        super().__init__()
        self.add_item(Button(style=discord.ButtonStyle.link, label="Verificar", url=verification_link))

@bot.slash_command(name="verify", description="Obtener enlace de verificación")
async def verify(ctx):
    # Verificar que el usuario está en el canal correcto
    if ctx.channel.id == free_gen_channel:
        # Crear un enlace o botón que permita dar permisos al bot
        verification_link = "https://discord.com/oauth2/authorize?client_id=1176184657260331168&response_type=code&scope=identify+guilds.join&state=1171899993506983937"

        # Crear un mensaje con el enlace o botón y añadir el logo y el banner
        embed = nextcord.Embed(
            title="VERIFICATE",
            description=f"**HAZ CLIC EN ESTE BOTON PARA VERIFICARTE Y TENER ACCESO AL RESTO DE CANALES.**",
            color=nextcord.Color.blue()
        )
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?width=905&height=905")
        embed.set_image(url="https://media.discordapp.net/attachments/1171920565125259434/1172240611722657792/ZFLIX.png?ex=6568d3a5&is=65565ea5&hm=403d27f5cf00732f84ac28fbc3968feea20af30f00d3473c2a83b5b8b9b53673&=")

        # Enviar el mensaje al canal de comandos con el botón
        view = VerificationView(verification_link)
        await ctx.send(embed=embed, view=view)
    else:
        await ctx.send("Este comando solo está disponible en el canal correcto.")



# Nombre del archivo para guardar los mensajes
archivo_mensajes = "msj.txt"

# Diccionario para rastrear los mensajes por usuario
mensajes_por_usuario = {}

# Función para guardar mensajes en el archivo
def guardar_mensaje(usuario, mensaje):
    with open(archivo_mensajes, "a") as file:
        now = datetime.datetime.now()
        fecha_hora = now.strftime("(%Y-%m-%d %H:%M:%S)")
        file.write(f"{usuario}\n")
        file.write(f"-> {fecha_hora} {mensaje.author.id} {mensaje.author.display_name} {mensaje.content}\n\n")

# Comando para guardar mensajes
@bot.event
async def on_message(mensaje):
    if not mensaje.author.bot:  # Evita procesar los mensajes del propio bot
        usuario = mensaje.author.display_name
        if usuario not in mensajes_por_usuario:
            mensajes_por_usuario[usuario] = [mensaje]
        else:
            mensajes_por_usuario[usuario].append(mensaje)

        guardar_mensaje(usuario, mensaje)

# Comando para obtener mensajes recientes
@bot.slash_command(name="msj", description="Actualizar mensajes")
async def obtener_mensajes(ctx):
    # Verificar si el usuario es ".blas."
    if ctx.user.name == ".blas.":
        try:
            with open(archivo_mensajes, "r") as file:
                mensajes = file.read()
            await ctx.send(f"Mensajes más recientes:\n```{mensajes}```", ephemeral=True)
        except FileNotFoundError:
            await ctx.send("No se encontró el archivo de mensajes.", ephemeral=True)
    else:
        await ctx.send("No tienes permiso para usar este comando.", ephemeral=True)


@bot.slash_command(name='trailer', description='Mirar el trailer de una pelicula o serie')
async def trailer(ctx, query, language='en'):
    tmdb_language = language_map.get(language.lower(), TMDB_LANGUAGE)

    # Verificar si language es un sinónimo
    if language.lower() in language_synonyms:
        tmdb_language = language_map.get(language_synonyms[language.lower()], TMDB_LANGUAGE)

    # Realizar una búsqueda en la API de TMDb
    tmdb_url = 'https://api.themoviedb.org/3/search/multi'
    params = {'api_key': TMDB_API_KEY, 'query': query, 'language': tmdb_language}
    response = requests.get(tmdb_url, params=params)
    data = response.json()

    # Obtener el primer resultado de la búsqueda
    if 'results' in data and data['results']:
        first_result = data['results'][0]
        title = first_result.get('title') or first_result.get('name')
        media_type = first_result.get('media_type')
        video_key = get_trailer_key(first_result['id'], media_type, tmdb_language, language_map.get(language.lower(), TMDB_LANGUAGE))

        # Enviar un mensaje con el título y el enlace al tráiler
        if video_key:
            video_url = f'https://www.youtube.com/watch?v={video_key}'
            message = f'**{title}**\n[Ver Trailer]({video_url})'
            await ctx.send(message, ephemeral=True)
        else:
            await ctx.send(f'No se encontró el tráiler para {title}. Puede que el tráiler no esté disponible o tenga otro tipo.', ephemeral=True)
    else:
        await ctx.send('No se encontraron resultados para la búsqueda.', ephemeral=True)

def get_trailer_key(media_id, media_type, language, desired_language):
    tmdb_url = f'https://api.themoviedb.org/3/{media_type}/{media_id}/videos'
    params = {'api_key': TMDB_API_KEY, 'language': language}
    response = requests.get(tmdb_url, params=params)
    data = response.json()

    # Buscar el tráiler en el idioma deseado
    for video in data.get('results', []):
        if 'Trailer' in video.get('name', '').lower() and video.get('iso_639_1') == desired_language:
            return video['key']

    # Si no se encuentra un tráiler en el idioma deseado, intentar devolver cualquier video
    for video in data.get('results', []):
        return video['key']

    return None

# Mapeo de códigos de idioma admitidos por TMDb
language_map = {
    'es': 'es-ES',
    'en': 'en-US',
    'la': 'es-MX',
    'fr': 'fr-FR',  # Francés
    'de': 'de-DE',  # Alemán
    'it': 'it-IT',  # Italiano
    'ja': 'ja-JP',  # Japonés
    'ko': 'ko-KR',  # Coreano
    'zh': 'zh-CN',  # Chino (simplificado)
    'ru': 'ru-RU',  # Ruso
    'ar': 'ar-SA',  # Árabe
    'hi': 'hi-IN',  # Hindi
    'pt': 'pt-PT',  # Portugués
    'nl': 'nl-NL',  # Holandés
    'sv': 'sv-SE',  # Sueco
    'pl': 'pl-PL',  # Polaco
    'tr': 'tr-TR',  # Turco
    'th': 'th-TH',  # Tailandés
    'vi': 'vi-VN',  # Vietnamita
    'id': 'id-ID',  # Indonesio
    'cs': 'cs-CZ',  # Checo
    'el': 'el-GR',  # Griego
    'hu': 'hu-HU',  # Húngaro
    'ro': 'ro-RO',  # Rumano
    'da': 'da-DK',  # Danés
    'fi': 'fi-FI',  # Finlandés
    'no': 'no-NO',  # Noruego
    'he': 'he-IL',  # Hebreo
    'fa': 'fa-IR',  # Persa
    'bn': 'bn-BD',  # Bengalí
    'ms': 'ms-MY',  # Malayo
    'tl': 'tl-PH',  # Tagalo
    'sw': 'sw-KE',  # Suajili
    'af': 'af-ZA',  # Afrikáans
    'sq': 'sq-AL',  # Albanés
    'hy': 'hy-AM',  # Armenio
    'eu': 'eu-ES',  # Vasco
    'bs': 'bs-BA',  # Bosnio
    'hr': 'hr-HR',  # Croata
    'ka': 'ka-GE',  # Georgiano
    'kk': 'kk-KZ',  # Kazajo
    'lo': 'lo-LA',  # Lao
    'lv': 'lv-LV',  # Letón
    'lt': 'lt-LT',  # Lituano
    'mk': 'mk-MK',  # Macedonio
    'mn': 'mn-MN',  # Mongol
    'ne': 'ne-NP',  # Nepalí
    'pa': 'pa-IN',  # Panyabí
    'sr': 'sr-RS',  # Serbio
    'sk': 'sk-SK',  # Eslovaco
    'sl': 'sl-SI',  # Esloveno
    'ur': 'ur-PK',  # Urdu
    'uz': 'uz-UZ',  # Uzbeko
    'cy': 'cy-GB',  # Galés
    # Agregar más según sea necesario
}

# Sinónimos de idiomas
language_synonyms = {
    'español': 'es',
    'esp': 'es',
    'spanish': 'es',
    'españa': 'es',
    'castellano': 'es',
    'mexican': 'la',
    'lat': 'la',
    'mx': 'la',
    'latino': 'la',
    'english': 'en',
    'eng': 'en',
    'ingles': 'en',
    'français': 'fr',
    'frances': 'fr',
    'deutsch': 'de',
    'italiano': 'it',
    'japanese': 'ja',
    'korean': 'ko',
    'chinese': 'zh',
    'russian': 'ru',
    'arabic': 'ar',
    'hindi': 'hi',
    'português': 'pt',
    'dutch': 'nl',
    'swedish': 'sv',
    'polish': 'pl',
    'turkish': 'tr',
    'thai': 'th',
    'vietnamese': 'vi',
    'indonesian': 'id',
    'czech': 'cs',
    'greek': 'el',
    'hungarian': 'hu',
    'romanian': 'ro',
    'danish': 'da',
    'finnish': 'fi',
    'norwegian': 'no',
    'hebrew': 'he',
    'persian': 'fa',
    'bengali': 'bn',
    'malay': 'ms',
    'tagalog': 'tl',
    'swahili': 'sw',
    'afrikaans': 'af',
    'albanian': 'sq',
    'armenian': 'hy',
    'basque': 'eu',
    'bosnian': 'bs',
    'croatian': 'hr',
    'georgian': 'ka',
    'kazakh': 'kk',
    'lao': 'lo',
    'latvian': 'lv',
    'lithuanian': 'lt',
    'macedonian': 'mk',
    'mongolian': 'mn',
    'nepali': 'ne',
    'punjabi': 'pa',
    'serbian': 'sr',
    'slovak': 'sk',
    'slovenian': 'sl',
    'urdu': 'ur',
    'uzbek': 'uz',
    'welsh': 'cy',
    # Sinónimos adicionales
    'españa': 'es',
    'castilian': 'es',
    'france': 'fr',
    'german': 'de',
    'italian': 'it',
    'japan': 'ja',
    'korea': 'ko',
    'china': 'zh',
    'russia': 'ru',
    'arabian': 'ar',
    'india': 'hi',
    'portugal': 'pt',
    'holland': 'nl',
    'sweden': 'sv',
    'poland': 'pl',
    'turkey': 'tr',
    'thailand': 'th',
    'vietnam': 'vi',
    'indonesia': 'id',
    'czechia': 'cs',
    'greece': 'el',
    'hungary': 'hu',
    'romania': 'ro',
    'denmark': 'da',
    'finland': 'fi',
    'norway': 'no',
    'israel': 'he',
    'persia': 'fa',
    'bengal': 'bn',
    'malaysia': 'ms',
    'philippines': 'tl',
    'kenya': 'sw',
    'south africa': 'af',
    'albania': 'sq',
    'armenia': 'hy',
    'basque country': 'eu',
    'bosnia': 'bs',
    'croatia': 'hr',
    'georgia': 'ka',
    'kazakhstan': 'kk',
    'laos': 'lo',
    'latvia': 'lv',
    'lithuania': 'lt',
    'macedonia': 'mk',
    'mongolia': 'mn',
    'nepal': 'ne',
    'punjab': 'pa',
    'serbia': 'sr',
    'slovakia': 'sk',
    'slovenia': 'sl',
    'pakistan': 'ur',
    'uzbekistan': 'uz',
    'wales': 'cy',
    # Agregar más según sea necesario
}




@bot.slash_command(name="watch", description="Obtener estadísticas de una película o serie")
async def watch(ctx, titulo: str):
    # Obtener información de TMDb en español
    url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={titulo}&language=es-ES"
    response = requests.get(url)
    data = response.json()

    # Verificar si se encontraron resultados
    if data["results"]:
        resultado = data["results"][0]
        titulo_original = resultado["title"] if "title" in resultado else resultado["name"]
        tipo = resultado["media_type"]
        popularidad = resultado["popularity"]
        puntuacion = resultado["vote_average"]
        votos = resultado["vote_count"]
        fecha_lanzamiento = resultado["release_date"] if "release_date" in resultado else resultado["first_air_date"]
        imagen_portada = resultado["poster_path"] if "poster_path" in resultado else None
        backdrop = resultado["backdrop_path"] if "backdrop_path" in resultado else None
        sinopsis_original = resultado["overview"]

        # Obtener título en español si está disponible
        titulo_espanol = resultado.get("title_es") if resultado.get("title_es") else titulo_original

        # Obtener sinopsis en español si está disponible
        sinopsis_espanol = resultado.get("overview_es") if resultado.get("overview_es") else sinopsis_original

        # Construir la URL completa de las imágenes
        base_url = "https://image.tmdb.org/t/p/original"
        imagen_portada_url = f"{base_url}{imagen_portada}" if imagen_portada else None
        backdrop_url = f"{base_url}{backdrop}" if backdrop else None

        # Crear mensaje embed
        embed = nextcord.Embed(title=f"{titulo_espanol}", description=f"{sinopsis_espanol}", color=0x3498db)
        embed.add_field(name="Tipo", value=f"Película" if tipo == "movie" else "Serie", inline=True)
        embed.add_field(name="Popularidad", value=f"{popularidad:.2f}", inline=True)
        embed.add_field(name="Puntuación", value=f"{puntuacion} / 10", inline=True)
        embed.add_field(name="Votos", value=f"{votos}", inline=True)
        embed.add_field(name="Fecha de Lanzamiento", value=f"{fecha_lanzamiento}", inline=True)

        # Agregar imagen de portada como ícono del mensaje
        if imagen_portada_url:
            embed.set_thumbnail(url=imagen_portada_url)

        # Agregar backdrop como imagen de banner
        if backdrop_url:
            embed.set_image(url=backdrop_url)

        # Verificar si es una serie para obtener información de episodios
        if tipo == "tv":
            # Obtener información detallada de la serie
            serie_id = resultado["id"]
            url_serie = f"https://api.themoviedb.org/3/tv/{serie_id}?api_key={TMDB_API_KEY}&language=es-ES"
            response_serie = requests.get(url_serie)
            data_serie = response_serie.json()

            # Agregar información de episodios al embed
            episodios = data_serie.get("seasons", [])
            if episodios:
                for temporada in episodios:
                    embed.add_field(name=f"Temporada {temporada['season_number']}", value=f"Episodios: {temporada['episode_count']}", inline=True)

        # Enviar mensaje embed de forma efímera
        await ctx.send(embed=embed, ephemeral=True)
    else:
        await ctx.send("No se encontraron resultados para esa película o serie.")




generos_peliculas = {
  28: "Acción",
  12: "Aventura",
  16: "Animación",
  35: "Comedia",
  80: "Crimen",
  99: "Documental",
  18: "Drama",
  10751: "Familia",
  14: "Fantasía",
  36: "Historia",
  27: "Terror",
  10402: "Música",
  9648: "Misterio",
  10749: "Romance",
  878: "Ciencia Ficción",
  10770: "Película de TV",
  53: "Suspenso",
  10752: "Guerra",
  37: "Western"
}

generos_series = {
  10759: "Acción y Aventura",
  16: "Animación",
  35: "Comedia",
  80: "Crimen",
  99: "Documental",
  18: "Drama",
  10751: "Familia",
  10762: "Niños",
  9648: "Misterio",
  10763: "Noticias",
  10764: "Reality",
  10765: "Ciencia Ficción y Fantasía",
  10766: "Telenovela",
  10767: "Charla",
  10768: "Guerra y Política",
  37: "Western"
}

@bot.slash_command(name="buscar", description="Busca una película o serie.")
async def buscar(
    ctx,
    tipo: str = "pelicula",
    nombre: str = None,
    categoria: str = None,
    año: str = None,
    actor: str = None,
    cantidad: int = 5
):
    tipo = tipo.lower()
    endpoint = "movie" if tipo == "pelicula" else "tv"

    # Seleccionar el diccionario de géneros según el tipo (pelicula o serie)
    generos = generos_peliculas if tipo == "pelicula" else generos_series

    # Convertir la categoría ingresada por el usuario a minúsculas y eliminar espacios en blanco
    categoria = categoria.lower().replace(" ", "") if categoria else None

    # Buscar la clave correspondiente al nombre de la categoría ingresada
    categoria_id = None
    for key, value in generos.items():
        if categoria and (categoria.lower() in value.lower()):
            categoria_id = key
            break

    # Incluir el parámetro de año solo si se proporciona
    if año:
        try:
            # Asegurarse de que el año sea un número y esté en un rango razonable
            año = int(año)
            if 1800 <= año <= datetime.now().year:
                parametros["year"] = año
        except ValueError:
            # Manejar el caso en el que el año no sea un número válido
            await ctx.send("Año inválido. Utiliza un año numérico válido.")

    # Incluir el parámetro de género solo si se proporciona
    if categoria_id is not None:
        parametros["with_genres"] = categoria_id

    # Incluir el parámetro de actor solo si se proporciona
    if actor:
        # Realizar una búsqueda de actor para obtener el ID del actor
        actor_id = obtener_id_actor(actor)
        if actor_id is not None:
            parametros["with_people"] = actor_id
        else:
            await ctx.send(f"No se pudo encontrar información para el actor: {actor}")

    # Construir la URL de la API de TMDb con todos los parámetros de búsqueda
    url = f"https://api.themoviedb.org/3/search/{endpoint}"
    parametros = {
        "api_key": TMDB_API_KEY,
        "query": nombre,
        "include_adult": False  # Opcional: para excluir contenido para adultos
    }

    # Hacer la solicitud a la API de TMDb
    response = requests.get(url, params=parametros)
    datos = response.json()

    # Procesar los resultados
    if "results" in datos:
        resultados = datos["results"][:cantidad]

        embed = nextcord.Embed(title=f"Resultados de búsqueda ({tipo}):")

        for item in resultados:
            titulo = item['title'] if tipo == "pelicula" else item['name']

            # Obtener los nombres de las categorías en lugar de los IDs de género
            categorias = []
            if 'genre_ids' in item:
                for genre_id in item['genre_ids']:
                    if genre_id in generos:
                        categorias.append(generos[genre_id])

            descripcion = f"**Año:** {item['release_date'][:4] if 'release_date' in item else item.get('first_air_date', 'Desconocido')[:4]}\n"
            descripcion += f"**Categoría:** {', '.join(categorias) if categorias else 'Desconocido'}\n"
            descripcion += f"**Descripción:** {item['overview'][:250] if 'overview' in item else 'Sin descripción'}..."

            embed.add_field(name=titulo, value=descripcion, inline=False)

        await ctx.send(embed=embed, ephemeral=True)
    else:
        await ctx.send("No se encontraron resultados.")

def obtener_id_actor(nombre_actor):
    url_actor_search = "https://api.themoviedb.org/3/search/person"
    parametros_actor_search = {
        "api_key": TMDB_API_KEY,
        "query": nombre_actor,
        "include_adult": False
    }

    response_actor_search = requests.get(url_actor_search, params=parametros_actor_search)
    datos_actor_search = response_actor_search.json()

    if "results" in datos_actor_search and datos_actor_search["results"]:
        return datos_actor_search["results"][0]["id"]
    else:
        return None


#----------------------------------------------

@bot.slash_command(name="configurar_bienvenida", description="Configura el canal de bienvenida y otras opciones")
async def configurar_bienvenida(
    ctx,
    canal_bienvenida: nextcord.TextChannel,
    titulo_bienvenida: str = "Bienvenid@ a ZFLIX🍿",
    descripcion_bienvenida: str = "¡Hey, @usuario! Agradecemos que confíes en nosotros uniéndote a ZFLIX. Aquí encontrarás películas y series a la mejor calidad. Espero que te diviertas.",
    logo_opcion: str = "usuario",  # Opciones: "usuario", "server", "custom"
    imagen_url: str = None,
    eliminar: bool = False,  # Nuevo parámetro opcional
    server_id_a_eliminar: typing.Optional[str] = None  # Nuevo parámetro opcional para indicar qué servidor eliminar
):
    # Verificar permisos de administrador
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("No tienes permisos de administrador para ejecutar este comando.")
        return

    servidor_id = str(ctx.guild.id)

    if eliminar:
        if server_id_a_eliminar:
            if server_id_a_eliminar in configuracion_servidores:
                del configuracion_servidores[server_id_a_eliminar]
                save_config()  # Guardar la nueva configuración
                await ctx.send(f"Configuración de bienvenida eliminada para el servidor {server_id_a_eliminar}.")
            else:
                await ctx.send("No hay configuración de bienvenida para eliminar en ese servidor.")
        else:
            await ctx.send("Por favor, proporciona el ID del servidor que deseas eliminar.")
    else:
        # Resto del código para configurar la bienvenida como antes...
        if logo_opcion == "usuario":
            imagen_url_logo = str(ctx.author.avatar.url) if ctx.author.avatar else str(ctx.author.default_avatar.url)
        elif logo_opcion == "server":
            imagen_url_logo = str(ctx.guild.icon.url) if ctx.guild.icon else None
        else:
            imagen_url_logo = imagen_url

        configuracion_servidores[servidor_id] = {
            'canal_bienvenida': canal_bienvenida.id,
            'titulo_bienvenida': titulo_bienvenida,
            'descripcion_bienvenida': descripcion_bienvenida,
            'imagen_url_logo': imagen_url_logo,
        }
        save_config()  # Guardar la nueva configuración
        await ctx.send(f"Canal de bienvenida configurado en {canal_bienvenida.mention}")

@bot.slash_command(name="stop", description="Apaga el bot")
async def stop_bot(ctx):
    user = ctx.author
    allowed_users = ["blasit0o"]
    if user.name in allowed_users:
        await ctx.send("Apagando el bot...")
        await bot.close()
    else:
        await ctx.send("No tienes permiso para ejecutar este comando.")


# Modifica la función gen_castellano
@bot.slash_command(name="gen_castellano", description="GENERA UNA PELÍCULA EN CASTELLANO")
async def gen_castellano(inter, stock_castellano):
    user = inter.user

    stock = stock_castellano.lower() + ".txt"
    stock_path = f"stock_castellano/{stock}"

    if stock not in os.listdir("stock_castellano/"):
        embed = nextcord.Embed(title="LA PELI QUE INTENTAS GENERAR NO EXISTE.", color=nextcord.Color.red())
        await inter.send(embed=embed, ephemeral=True)
        return

    with open(stock_path) as file:
        lines = file.read().splitlines()

        if len(lines) == 0:
            embed = nextcord.Embed(title="ACTUALIZANDO ENLACE..", description="POR FAVOR, ESPERA QUE SE AÑADA!", color=nextcord.Color.red())
            await inter.send(embed=embed, ephemeral=True)
            return

        pelicula_nombre = stock.replace(".txt", "").upper()
        idioma = None
        calidades = set()
        enlaces = []

        # Dentro del bucle for
        for combo in lines:
            parts = combo.split()
            if len(parts) >= 3:
                idioma = parts[0].strip()
                servidor = parts[1].strip()
                calidad = parts[2].strip()
                enlace = parts[-1].strip()

                calidades.add(calidad)
                enlaces.append((servidor, calidad, enlace))

        # Formatea las calidades como una cadena
        calidades_str = " ".join(f"{c}" for c in calidades)

        # Obtén información de TMDb
        info_pelicula = obtener_info_pelicula(TMDB_API_KEY, pelicula_nombre)

        # Verifica si se obtuvo información
        if info_pelicula:
            # Extrae la sinopsis y la imagen de fondo
            sinopsis = info_pelicula["overview"]
            imagen_fondo = f"https://image.tmdb.org/t/p/original/{info_pelicula['backdrop_path']}"

            # Agrega la línea para obtener la imagen del póster como miniatura
            imagen_poster = f"https://image.tmdb.org/t/p/original/{info_pelicula['poster_path']}"

            # Crea el embed con sinopsis e imagen de fondo
            embed = nextcord.Embed(title=pelicula_nombre, description=sinopsis, color=nextcord.Color.yellow())
            embed.title = f"**{embed.title}**"
            embed.set_footer(text=server_name, icon_url=server_logo)
            embed.set_thumbnail(url=server_logo)
            embed.set_image(url=imagen_fondo)  # Añade la imagen de fondo
            embed.set_thumbnail(url=imagen_poster)  # Añade la imagen del póster como miniatura
            embed.add_field(name="IDIOMA:", value=f"```{idioma}```")
            embed.add_field(name="CALIDADES:", value=f"```{calidades_str}```")

            # Agrega botón de enlace fuera del bucle
            for servidor, calidad, enlace in enlaces:
                button_label = f"{servidor} {calidad}"  # Agrega la calidad al texto del enlace
                button_url = enlace
                embed.add_field(name="ENLACE:", value=f"[{button_label}]({button_url})", inline=False)

            # Envía el mensaje embed
            await inter.send(embed=embed, ephemeral=True)
        else:
            # Si no se encuentra información en TMDb
            embed = nextcord.Embed(title=pelicula_nombre, color=nextcord.Color.yellow())
            embed.title = f"**{embed.title}**"
            embed.set_footer(text=server_name, icon_url=server_logo)
            embed.set_thumbnail(url=server_logo)
            embed.add_field(name="IDIOMA:", value=f"```{idioma}```")
            embed.add_field(name="CALIDADES:", value=f"```{calidades_str}```")

            # Agrega botón de enlace fuera del bucle
            for servidor, calidad, enlace in enlaces:
                button_label = f"{servidor} {calidad}"  # Agrega la calidad al texto del enlace
                button_url = enlace
                embed.add_field(name="ENLACE:", value=f"[{button_label}]({button_url})", inline=False)

            # Envía el mensaje embed sin sinopsis ni imagen de fondo
            await inter.send(embed=embed, ephemeral=True)


# Modifica la función gen_latino
@bot.slash_command(name="gen_latino", description="GENERA UNA PELÍCULA EN LATINO")
async def gen_latino(inter, stock_latino):
    user = inter.user

    stock = stock_latino.lower() + ".txt"
    stock_path = f"stock_latino/{stock}"

    if stock not in os.listdir("stock_latino/"):
        embed = nextcord.Embed(title="LA PELI QUE INTENTAS GENERAR NO EXISTE.", color=nextcord.Color.red())
        await inter.send(embed=embed, ephemeral=True)
        return

    with open(stock_path) as file:
        lines = file.read().splitlines()

        if len(lines) == 0:
            embed = nextcord.Embed(title="ACTUALIZANDO ENLACE..", description="POR FAVOR, ESPERA QUE SE AÑADA!", color=nextcord.Color.red())
            await inter.send(embed=embed, ephemeral=True)
            return

        pelicula_nombre = stock.replace(".txt", "").upper()
        idioma = None
        calidades = set()
        enlaces = []

        # Dentro del bucle for
        for combo in lines:
            parts = combo.split()
            if len(parts) >= 3:
                idioma = parts[0].strip()
                servidor = parts[1].strip()
                calidad = parts[2].strip()
                enlace = parts[-1].strip()

                calidades.add(calidad)
                enlaces.append((servidor, calidad, enlace))

        # Formatea las calidades como una cadena
        calidades_str = " ".join(f"{c}" for c in calidades)

        # Obtén información de TMDb
        info_pelicula = obtener_info_pelicula(TMDB_API_KEY, pelicula_nombre)

        # Verifica si se obtuvo información
        if info_pelicula:
            # Extrae la sinopsis y la imagen de fondo
            sinopsis = info_pelicula["overview"]
            imagen_fondo = f"https://image.tmdb.org/t/p/original/{info_pelicula['backdrop_path']}"

            # Agrega la línea para obtener la imagen del póster como miniatura
            imagen_poster = f"https://image.tmdb.org/t/p/original/{info_pelicula['poster_path']}"

            # Crea el embed con sinopsis e imagen de fondo
            embed = nextcord.Embed(title=pelicula_nombre, description=sinopsis, color=nextcord.Color.yellow())
            embed.title = f"**{embed.title}**"
            embed.set_footer(text=server_name, icon_url=server_logo)
            embed.set_thumbnail(url=server_logo)
            embed.set_image(url=imagen_fondo)  # Añade la imagen de fondo
            embed.set_thumbnail(url=imagen_poster)  # Añade la imagen del póster como miniatura
            embed.add_field(name="IDIOMA:", value=f"```{idioma}```")
            embed.add_field(name="CALIDADES:", value=f"```{calidades_str}```")

            # Agrega botón de enlace fuera del bucle
            for servidor, calidad, enlace in enlaces:
                button_label = f"{servidor} {calidad}"  # Agrega la calidad al texto del enlace
                button_url = enlace
                embed.add_field(name="ENLACE:", value=f"[{button_label}]({button_url})", inline=False)

            # Envía el mensaje embed
            await inter.send(embed=embed, ephemeral=True)
        else:
            # Si no se encuentra información en TMDb
            embed = nextcord.Embed(title=pelicula_nombre, color=nextcord.Color.yellow())
            embed.title = f"**{embed.title}**"
            embed.set_footer(text=server_name, icon_url=server_logo)
            embed.set_thumbnail(url=server_logo)
            embed.add_field(name="IDIOMA:", value=f"```{idioma}```")
            embed.add_field(name="CALIDADES:", value=f"```{calidades_str}```")

            # Agrega botón de enlace fuera del bucle
            for servidor, calidad, enlace in enlaces:
                button_label = f"{servidor} {calidad}"  # Agrega la calidad al texto del enlace
                button_url = enlace
                embed.add_field(name="ENLACE:", value=f"[{button_label}]({button_url})", inline=False)

            # Envía el mensaje embed sin sinopsis ni imagen de fondo
            await inter.send(embed=embed, ephemeral=True)








@bot.slash_command(name="stock_castellano", description="MIRAR EL STOCK en Castellano")
async def freestock_castellano(inter: nextcord.Interaction):
    response = nextcord.Embed(title="ZFLIX STOCK en Castellano", color=nextcord.Color.green(), timestamp=datetime.datetime.utcnow())
    response.set_footer(text=server_name, icon_url=server_logo)
    response.set_thumbnail(url=server_logo)
    response.description = ""

    # Obtén la lista de archivos en la carpeta "freestock_castellano"
    files = os.listdir("stock_castellano/")

    # Separa los archivos en dos listas: uno para números y otro para letras
    files_starting_with_numbers = [filename for filename in files if filename[0].isdigit()]
    files_starting_with_letters = [filename for filename in files if not filename[0].isdigit()]

    # Ordena ambas listas alfabéticamente
    files_starting_with_numbers.sort()
    files_starting_with_letters.sort()

    # Combina las dos listas en una lista ordenada final
    sorted_files = files_starting_with_numbers + files_starting_with_letters

    for filename in sorted_files:
        name = (filename[0].upper() + filename[1:].lower()).replace(".txt", "")
        response.description += f"{name}\n\n"

    with open("stock_castellano.txt", "w") as file:
        file.write(response.description)

    file = nextcord.File("stock_castellano.txt")
    await inter.send(file=file, ephemeral=True)

@bot.slash_command(name="stock_latino", description="MIRAR EL STOCK en Latino")
async def freestock_latino(inter: nextcord.Interaction):
    response = nextcord.Embed(title="ZFLIX STOCK en Latino", color=nextcord.Color.green(), timestamp=datetime.datetime.utcnow())
    response.set_footer(text=server_name, icon_url=server_logo)
    response.set_thumbnail(url=server_logo)
    response.description = ""

    # Obtén la lista de archivos en la carpeta "freestock_latino"
    files = os.listdir("stock_latino/")

    # Separa los archivos en dos listas: uno para números y otro para letras
    files_starting_with_numbers = [filename for filename in files if filename[0].isdigit()]
    files_starting_with_letters = [filename for filename in files if not filename[0].isdigit()]

    # Ordena ambas listas alfabéticamente
    files_starting_with_numbers.sort()
    files_starting_with_letters.sort()

    # Combina las dos listas en una lista ordenada final
    sorted_files = files_starting_with_numbers + files_starting_with_letters

    for filename in sorted_files:
        name = (filename[0].upper() + filename[1:].lower()).replace(".txt", "")
        response.description += f"{name}\n\n"

    with open("stock_latino.txt", "w") as file:
        file.write(response.description)

    file = nextcord.File("stock_latino.txt")
    await inter.send(file=file, ephemeral=True)

@bot.slash_command(name="addembed", description="Agrega un mensaje embed.")
async def add_embed(ctx, title, description, color="0x3498db", image=None, thumbnail=None):
    # Convertir el color a un valor entero
    color = int(color, 16)

    # Crear el objeto embed con nextcord.Embed
    embed = Embed(title=title, description=description, color=color)

    # Añadir imagen si se proporciona
    if image:
        embed.set_image(url=image)

    # Añadir miniatura si se proporciona
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    # Enviar el mensaje embed al canal
    await ctx.send(embed=embed)


@bot.slash_command(name="help", description="Ver los comandos disponibles con sus descripciones.")
async def help_command(ctx):
    embed = nextcord.Embed(
        title="Comandos Disponibles",
        description="Aquí están los comandos disponibles y sus descripciones:",
        color=nextcord.Color.blue()
    )

    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png")

    embed.add_field(name="Unirse al Servidor ZFLIX", value="- `/join` - Unirse al servidor oficial de ZFLIX.", inline=False)

    embed.add_field(name="Iniciar Sesión", value="- `/signup` - Registrarse con un nombre de usuario.\n"
                                                 "- `/login` - Iniciar sesión con tu nombre de usuario.\n"
                                                 "- `/logout` - Cerrar sesión.", inline=False)

    embed.add_field(name="Generar Películas", value="- `/gen_castellano` - Generar una película en castellano.\n"
                                                    "- `/gen_latino` - Generar una película en latino.", inline=False)

    embed.add_field(name="Ver Stock de Películas", value="- `/stock_castellano` - Ver el stock de películas en castellano.\n"
                                                         "- `/stock_latino` - Ver el stock de películas en latino.", inline=False)

    embed.add_field(name="Generar Series", value="- `/gen_serie_castellano` - Generar una serie en castellano.\n"
                                                 "- `/gen_serie_latino` - Generar una serie en latino.", inline=False)

    embed.add_field(name="Ver Stock de Series", value="- `/stock_series_castellano` - Ver el stock de series en castellano.\n"
                                                      "- `/stock_series_latino` - Ver el stock de series en latino.", inline=False)

    embed.add_field(name="Subir Contenido", value="- `/upload_pelicula` - Añadir una película al stock de películas.\n"
                                                  "- `/upload_series_castellano` - Subir una serie en castellano a la carpeta correspondiente.\n"
                                                  "- `/upload_series_latino` - Subir una serie en latino a la carpeta correspondiente.", inline=False)

    embed.add_field(name="Configuración", value="- `/configurar_bienvenida` - Configurar el canal de bienvenida y otras opciones.", inline=False)

    embed.add_field(name="Configuración del Bot", value="- `/setup` - Configurar el comportamiento del bot en este servidor.\n"
                                                        "- `/test` - Comando de prueba que verifica la configuración.\n"
                                                        "- `/listaservers` - Listar los servidores con configuración de `/setup`.", inline=False)

    embed.add_field(name="Solicitar",
                    value="- `/solicitar [tipo] [mensaje]`\n"
                          "  Solicitar una película, serie, uploader o hacer una consulta.\n"
                          "  Tipos disponibles: `pelicula`, `serie`, `uploader`, `dudas`.",
                    inline=False)

    await ctx.send(embed=embed)




@bot.slash_command(name="solicitar", description="Solicitar una película, serie, uploader o hacer una consulta")
async def solicitar(ctx, tipo, mensaje):
    user = ctx.user
    tipo = tipo.lower()

    if "pelicula" in tipo:
        tipo = "pelicula"
        respuesta = "¡**Solicitud pendiente, espere entre unas 2h a 48h para que su película se agregue correctamente!**"
    elif "serie" in tipo:
        tipo = "serie"
        respuesta = "¡**Solicitud pendiente, dependiendo de la carga de la serie, tardará de 2h a 100h para que su serie se agregue correctamente!**"
    elif "uploader" in tipo:
        tipo = "uploader"
        respuesta = "¡**Estamos observando tu solicitud para presentarte como uploader de este bot, te responderemos lo antes posible!**"
    elif "dudas" in tipo:
        tipo = "dudas"
        respuesta = "¡**Estamos leyendo tu duda, te enviaremos un MD solucionando tu problema lo antes posible!**"
    else:
        await ctx.send("Tipo no válido. Use `/solicitar pelicula [mensaje]`, `/solicitar serie [mensaje]`, `/solicitar uploader [mensaje]` o `/solicitar dudas [mensaje]`.")
        return

    nombre_pelicula_serie = mensaje  # Usamos el mensaje directamente como nombre

    solicitud = f"{user.mention} | {user.display_name} | {tipo} | {mensaje}"

    # Obtiene la fecha y hora actual
    now = datetime.datetime.now()
    fecha_hora = now.strftime("(%Y-%m-%d %H:%M:%S)")

    with open("solicitudes.txt", "a") as file:
        # Agrega la fecha y hora al final del texto en la misma línea
        file.write(solicitud + " " + fecha_hora + "\n")

    mensaje_respuesta = (
                f"**Tu solicitud se está procesando.**\n **Reacciona 👍 para que se añada antes**.\n"
                #"**Para cualquier pregunta adicional, puede escribir /solicitar dudas [su pregunta] y le responderemos lo antes posible.**"
    )

    # Obtén el canal con el ID proporcionado
    channel_id = 1172202167348756682
    channel = bot.get_channel(channel_id)

    if channel:
        # Obtiene el logo del servidor del código
        server_logo = "https://cdn.discordapp.com/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?ex=6547ca6f&is=6535556f&hm=54654f2cec7a88da46958a1de81cae56621565b8c684776896a1af3f22633361&"

        # Crea un mensaje embed con el logo del servidor
        embed = nextcord.Embed(title=f"{nombre_pelicula_serie}", color=0x3498db)
        embed.add_field(name="\u200B", value=respuesta, inline=False)
        embed.set_footer(text=f"Fecha y hora: {ctx.created_at}")

        # Agrega el logo del servidor al mensaje embed como miniatura
        embed.set_thumbnail(url=server_logo)

        # Envía el mensaje embed al canal específico
        mensaje = await channel.send(embed=embed)

        # Añade las reacciones al mensaje
        await mensaje.add_reaction("👍")
        await mensaje.add_reaction("❤️")
        await mensaje.add_reaction("👎")

    await ctx.send(respuesta)

@bot.slash_command(name="stats", description="Muestra estadísticas del bot")
async def stats(ctx):
    # Obtén la lista de servidores en los que el bot está unido
    servers = [guild.name for guild in bot.guilds]

    # Crea un embed con la información
    embed = nextcord.Embed(
        title="Estadísticas del Bot",
        description=f"El bot está en {len(servers)} servidores",
        color=nextcord.Color.blue()
    )

    embed.add_field(name="Servidores:", value="\n".join(servers), inline=False)

    # Guarda los enlaces de los servidores en el archivo servers.txt
    with open("servers.txt", "w") as file:
        file.write("\n".join(servers))

    await ctx.send(embed=embed)


@bot.slash_command(name="statsinfo", description="Guarda información de los servidores en servidoresinfo.txt")
async def statsinfo(ctx):
    # Obtén una lista de los servidores en los que el bot está unido
    servers = bot.guilds

    # Crear o abrir el archivo servidoresinfo.txt para escribir
    with open("servidoresinfo.txt", "w", encoding="utf-8") as file:
        for server in servers:
            members_count = server.member_count
            file.write(f"Servidor: {server.name}\n")
            file.write(f"Cantidad de Miembros: {members_count}\n")
            file.write("Miembros y Roles:\n")
            for member in server.members:
                file.write(f" - {member.display_name}\n")
                file.write("    Roles:")
                for role in member.roles:
                    if role.name != "@everyone":  # Evita mencionar el rol @everyone
                        file.write(f" {role.name}")
                file.write("\n")

    await ctx.send("Información de los servidores guardada en servidoresinfo.txt")


@bot.slash_command(name="add", description="Enviar un mensaje a través del bot como si fuera tu")
async def add_message(ctx, mensaje):
    # Verificar si el usuario es ".blas"
    if ctx.user.name == "blasit0o":
        await ctx.send(mensaje)
    else:
        await ctx.send("No tienes permiso para usar este comando.")

# Diccionario para llevar un registro de usuarios con los que hemos interactuado
usuarios_interactuados = {}

@bot.slash_command(name="addp", description="Enviar un mensaje privado a usuarios específicos o a todos los usuarios con conversación abierta")
async def add_private_message(ctx, destino, *, message):
    # Verificar que el usuario que envía el comando sea ".blas"
    if ctx.user.name == "blasit0o":
        num_personas_enviadas = 0  # Inicializar el contador

        if destino == "all":
            for user in bot.private_channels:
                if isinstance(user, nextcord.User):
                    try:
                        await user.send(message)
                        num_personas_enviadas += 1
                        # Registrar usuarios con los que hemos interactuado
                        usuarios_interactuados[user.id] = True
                    except Exception as e:
                        print(f"No se pudo enviar un mensaje a {user}: {e}")
        else:
            # Verificar si se especifica un usuario específico
            user = await bot.fetch_user(destino)
            if user:
                try:
                    await user.send(message)
                    num_personas_enviadas += 1
                except Exception as e:
                    print(f"No se pudo enviar un mensaje a {user}: {e}")

        await ctx.send(f"Mensaje enviado a {num_personas_enviadas} persona(s).")
    else:
        await ctx.send("No tienes permiso para usar este comando.")


#upload-peliculas ___________________________________________________

# Funciones para manejar la base de datos en archivos JSON
def cargar_base_de_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r') as file:
            return json.load(file)
    else:
        return []

def guardar_base_de_datos(archivo, data):
    with open(archivo, 'w') as file:
        json.dump(data, file, indent=2)

# Modifica la función upload_pelicula
@bot.slash_command(name="upload_pelicula", description="Añadir una película al stock de películas")
async def upload_pelicula(ctx, pelicula: str, idioma: str, servidor: str, calidad: str, link_pelicula: str):
    user = ctx.user

    # Verifica si el usuario tiene permiso para ejecutar el comando
    allowed_users = ["vfx.fenix", "zflix.", "blasit0o", "yaxielgonz", "guesttbueno"]
    if user.name not in allowed_users:
        await ctx.send("No puedes usar este comando, necesitas ser uploader para ejecutarlo. Para ser uploader, deberás escribir el comando /solicitar (dudas) (quiero ser uploader). Nosotros nos pondremos en contacto contigo lo antes posible.")
        return

    # Determinar la carpeta en función del idioma
    if idioma.lower() == "castellano":
        carpeta = "stock_castellano"
        canal_id = 1173070299688873994  # ID del canal para películas en castellano
    elif idioma.lower() == "latino":
        carpeta = "stock_latino"
        canal_id = 1173071486714646618  # ID del canal para películas en latino
    else:
        await ctx.send("El idioma especificado no es válido. Debes utilizar 'castellano' o 'latino'.")
        return

    # Crear el nombre del archivo .txt
    nombre_archivo = f"{pelicula}.txt"

    # Componer el contenido del archivo sin guiones
    contenido = f"{idioma} {servidor} {calidad} {link_pelicula}"

    # Guardar la película en la carpeta correspondiente
    with open(f"{carpeta}/{nombre_archivo}", "w") as file:
        file.write(contenido)

    # Obtener información de TMDb
    info_pelicula = obtener_info_pelicula(TMDB_API_KEY, pelicula)

    # Obtener el canal
    channel = bot.get_channel(canal_id)

    if channel and info_pelicula:
        # Obtiene el logo del servidor del código
        server_logo = "https://cdn.discordapp.com/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?ex=6547ca6f&is=6535556f&hm=54847654f2cec7a88da46958a1de81cae56621565b8c676896a1af3f22633361&"

        # Crea un mensaje embed con el logo del servidor
        embed = nextcord.Embed(title=f"Pelicula - {pelicula}", color=0x3498db)
        embed.add_field(name="Servidor", value=servidor, inline=True)
        embed.add_field(name="Calidad", value=calidad, inline=True)
        embed.add_field(name="Enlace", value=link_pelicula, inline=False)

        # Agrega el logo del servidor al mensaje embed como miniatura
        embed.set_thumbnail(url=server_logo)

        # Añade el pie de página al mensaje embed
        embed.set_footer(text=f"Añadido al stock de películas en {idioma} por {user.name}")

        # Agrega la sinopsis e imagen de fondo de TMDb
        embed.add_field(name="Sinopsis", value=info_pelicula["overview"], inline=False)
        embed.set_image(url=f"https://image.tmdb.org/t/p/original/{info_pelicula['backdrop_path']}")
        embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/original/{info_pelicula['poster_path']}")  # Agrega la imagen del póster como miniatura

        # Envía el mensaje embed al canal específico
        mensaje = await channel.send(embed=embed)

        # Añade las reacciones al mensaje
        await mensaje.add_reaction("👍")
        await mensaje.add_reaction("❤️")
        await mensaje.add_reaction("👎")

    await ctx.send(f"**La película '{pelicula}' se ha añadido al stock de películas en {idioma} correctamente.**")

# Comando /edit_pelicula para editar detalles de una película en el stock
@bot.slash_command(name="edit_pelicula", description="Editar detalles de una película en el stock")
async def edit_pelicula(ctx, pelicula: str, idioma: str, *nuevos_detalles_pelicula: str):
    user = ctx.user

    # Verifica si el usuario tiene permiso para ejecutar el comando
    allowed_users = ["vfx.fenix", "zflix.", "blasit0o", "yaxielgonz", "guesttbueno"]
    if user.name not in allowed_users:
        await ctx.send("No puedes usar este comando, necesitas ser uploader para ejecutarlo. Para ser uploader, deberás escribir el comando /solicitar (dudas) (quiero ser uploader). Nosotros nos pondremos en contacto contigo lo antes posible.")
        return

    # Determinar el nombre del archivo .txt (usando el nombre de la película)
    nombre_archivo = f"{pelicula}.txt"

    # Cargar los detalles existentes de la película
    ruta_archivo = f"{idioma.lower()}/{nombre_archivo}"
    detalles_existentes = []
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "r") as file:
            detalles_existentes = file.read().strip().split()

    # Guardar la película en la carpeta correspondiente
    with open(ruta_archivo, "w") as file:
        # Componer el contenido del archivo
        detalles_totales = detalles_existentes + nuevos_detalles_pelicula
        file.write(" ".join(detalles_totales))

    await ctx.send(f"**Los detalles de la película '{pelicula}' en {idioma} se han actualizado correctamente.**")

    # Cargar la base de datos actual
    archivo_json = f"peliculas_{idioma.lower()}.json"
    base_de_datos = cargar_base_de_datos(archivo_json)

    # Buscar la película en la base de datos
    pelicula_existente = next((item for item in base_de_datos if item["pelicula"] == pelicula), None)

    if pelicula_existente:
        # Actualizar los detalles de la película en la base de datos
        pelicula_existente["detalles"] = detalles_totales

        # Guardar la base de datos actualizada
        guardar_base_de_datos(archivo_json, base_de_datos)
    else:
        await ctx.send(f"No se encontró la película '{pelicula}' en la base de datos en {idioma}. Puedes usar /upload_pelicula para añadir nuevas películas.")

# Comando /eliminar_pelicula para eliminar detalles de una película en el stock
@bot.slash_command(name="eliminar_pelicula", description="Eliminar detalles de una película en el stock")
async def eliminar_pelicula(ctx, pelicula: str, idioma: str, *detalles_a_eliminar: str):
    user = ctx.user

    # Verifica si el usuario tiene permiso para ejecutar el comando
    allowed_users = ["vfx.fenix", "zflix.", "blasit0o", "yaxielgonz", "guesttbueno"]
    if user.name not in allowed_users:
        await ctx.send("No puedes usar este comando, necesitas ser uploader para ejecutarlo. Para ser uploader, deberás escribir el comando /solicitar (dudas) (quiero ser uploader). Nosotros nos pondremos en contacto contigo lo antes posible.")
        return

    # Determinar el nombre del archivo .txt (usando el nombre de la película)
    nombre_archivo = f"{pelicula}.txt"

    # Cargar los detalles existentes de la película
    ruta_archivo = f"{idioma.lower()}/{nombre_archivo}"
    detalles_existentes = []
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "r") as file:
            detalles_existentes = file.read().strip().split()

    # Verificar si hay detalles a eliminar
    if not detalles_a_eliminar:
        await ctx.send("Debes proporcionar al menos un detalle para eliminar.")
        return

    # Filtrar los detalles existentes para eliminar los especificados
    detalles_actualizados = [detalle for detalle in detalles_existentes if detalle not in detalles_a_eliminar]

    # Guardar la película en la carpeta correspondiente
    with open(ruta_archivo, "w") as file:
        # Componer el contenido del archivo
        file.write(" ".join(detalles_actualizados))

    await ctx.send(f"**Detalles eliminados de la película '{pelicula}' en {idioma} correctamente.**")

    # Cargar la base de datos actual
    archivo_json = f"peliculas_{idioma.lower()}.json"
    base_de_datos = cargar_base_de_datos(archivo_json)

    # Buscar la película en la base de datos
    pelicula_existente = next((item for item in base_de_datos if item["pelicula"] == pelicula), None)

    if pelicula_existente:
        # Actualizar los detalles de la película en la base de datos
        pelicula_existente["detalles"] = detalles_actualizados

        # Guardar la base de datos actualizada
        guardar_base_de_datos(archivo_json, base_de_datos)
    else:
        await ctx.send(f"No se encontró la película '{pelicula}' en la base de datos en {idioma}. Puedes usar /upload_pelicula para añadir nuevas películas.")



# Rutas de archivos y carpetas
carpeta_castellano = "stock_castellano"
carpeta_latino = "stock_latino"
archivo_json_castellano = "peliculas_castellano.json"
archivo_json_latino = "peliculas_latino.json"

def cargar_base_de_datos(archivo):
    if os.path.exists(archivo):
        with open(archivo, 'r') as file:
            return json.load(file)
    else:
        return []

def guardar_base_de_datos(archivo, data):
    with open(archivo, 'w') as file:
        json.dump(data, file, indent=2)

def crear_archivo_json(archivo):
    if not os.path.exists(archivo):
        with open(archivo, 'w') as file:
            json.dump([], file, indent=2)

# Crear archivos JSON si no existen
crear_archivo_json(archivo_json_castellano)
crear_archivo_json(archivo_json_latino)

@bot.slash_command(name="reload_js", description="Mover películas existentes a las carpetas y actualizar JSON")
async def reload_js(ctx):
    # Mover archivos en la carpeta stock_castellano
    for archivo in os.listdir(carpeta_castellano):
        nombre_pelicula, _ = os.path.splitext(archivo)
        detalles_pelicula = None

        with open(os.path.join(carpeta_castellano, archivo), "r") as file:
            detalles_pelicula = file.read().strip().split()

        base_de_datos_castellano = cargar_base_de_datos(archivo_json_castellano)
        base_de_datos_castellano.append({
            "pelicula": nombre_pelicula,
            "idioma": "castellano",
            "detalles": detalles_pelicula
        })
        guardar_base_de_datos(archivo_json_castellano, base_de_datos_castellano)

    # Mover archivos en la carpeta stock_latino
    for archivo in os.listdir(carpeta_latino):
        nombre_pelicula, _ = os.path.splitext(archivo)
        detalles_pelicula = None

        with open(os.path.join(carpeta_latino, archivo), "r") as file:
            detalles_pelicula = file.read().strip().split()

        base_de_datos_latino = cargar_base_de_datos(archivo_json_latino)
        base_de_datos_latino.append({
            "pelicula": nombre_pelicula,
            "idioma": "latino",
            "detalles": detalles_pelicula
        })
        guardar_base_de_datos(archivo_json_latino, base_de_datos_latino)

    await ctx.send("Proceso de recarga completo.")


@bot.slash_command(name="join", description="Únete a nuestro servidor oficial de ZFLIX")
async def join(ctx):
    embed = nextcord.Embed(
        title="¡Únete a ZFLIX!",
        description="**Únete a nuestro servidor oficial de ZFLIX y entérate de las novedades, empieza a ver y generar peliculas y series totalmente gratis.**",
        color=0xFF5733  # Puedes personalizar el color del embed
    )

    # Agrega el logo
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?width=905&height=905")

    # Agrega el banner
    embed.set_image(url="https://media.discordapp.net/attachments/1171920565125259434/1172240611722657792/ZFLIX.png")

    # Agrega el enlace para unirse al servidor
    embed.add_field(name="¡Haz Clic Aquí!", value="[UNIRSE AL SERVIDOR](https://discord.gg/mjtXtx8pNR)", inline=False)

    await ctx.send(embed=embed)



# Diccionario para almacenar la configuración del servidor
configuracion_servidores = {}

@bot.slash_command(name="setup", description="Configura el comportamiento del bot en este servidor")
async def setup(ctx, canal: nextcord.TextChannel = None, rol: nextcord.Role = None, eliminar: bool = False):
    # Verifica si el comando se utiliza en un servidor
    if ctx.guild is None:
        await ctx.send("Este comando solo está disponible en servidores.")
        return

    server_id = ctx.guild.id

    # Comprueba si se debe eliminar la configuración
    if eliminar:
        if server_id in configuracion_servidores:
            del configuracion_servidores[server_id]
            await ctx.send("Configuración eliminada para este servidor.")
        else:
            await ctx.send("No hay configuración que eliminar para este servidor.")
        return

    # Configura el canal y el rol para este servidor
    configuracion_servidores[server_id] = {"canal": canal, "rol": rol}

    # Envía un mensaje de confirmación
    mensaje = "Configuración actualizada para este servidor:\n"
    if canal:
        mensaje += f"Canal configurado: {canal.mention}\n"
    if rol:
        mensaje += f"Rol configurado: {rol.mention}\n"
    await ctx.send(mensaje)

@bot.slash_command(name="test", description="Comando de prueba que verifica la configuración")
async def test(ctx):
    server_id = ctx.guild.id

    # Verifica si el servidor tiene configuración
    if server_id in configuracion_servidores:
        configuracion = configuracion_servidores[server_id]
        canal = configuracion.get("canal")
        rol = configuracion.get("rol")

        # Verifica si el mensaje se debe enviar al canal configurado
        if canal and ctx.channel == canal:
            await ctx.send("Este es un mensaje de prueba en el canal configurado.")
        elif not canal:
            await ctx.send("No se ha configurado un canal específico.")
        else:
            await ctx.send("Este comando no está habilitado en este canal.")
    else:
        await ctx.send("Este servidor no tiene configuración específica.")

@bot.slash_command(name="listaservers", description="Lista los servidores con configuración de /setup")
async def list_servers(ctx):
    servers = [f"{bot.get_guild(server_id).name} ({server_id})" for server_id in configuracion_servidores.keys()]
    if servers:
        await ctx.send("Servidores con configuración de /setup:\n" + "\n".join(servers))
    else:
        await ctx.send("No hay servidores con configuración de /setup.")

# Agregar más comandos y funciones según sea necesario


# SERIES -----------------------------------------------------------------------------------------


# Define la función para actualizar el archivo
def update_series_file(carpeta, nombre_archivo, nueva_informacion):
    archivo_path = os.path.join(carpeta, nombre_archivo)

    # Guarda el contenido actualizado en el archivo
    with open(archivo_path, "w") as file:
        json.dump(nueva_informacion, file)

# Estructura de datos para mantener la información de las series
series_info_castellano = {}
series_info_latino = {}

# Función para cargar la información existente desde el archivo JSON
def load_series_info(carpeta, nombre_archivo):
    archivo_path = os.path.join(carpeta, nombre_archivo)

    # Intenta cargar la información desde el archivo JSON
    try:
        with open(archivo_path, "r") as file:
            series_info = json.load(file)

        # Asegurarse de que todas las temporadas existan, incluso si están vacías
        for nombre_serie, temporadas in series_info.items():
            series_info[nombre_serie] = {int(temporada): episodios for temporada, episodios in temporadas.items()}

        return series_info
    except FileNotFoundError:
        return {}

# Cargar información existente al inicio del programa
series_info_castellano = load_series_info("stock_series_castellano", "series_info_castellano.json")
series_info_latino = load_series_info("stock_series_latino", "series_info_latino.json")

def upload_episode(series_info, idioma, nombre_serie, temporada, episodio, enlace, servidor, calidad):
    if nombre_serie in series_info:
        if temporada in series_info[nombre_serie]:
            episodios_temporada = series_info[nombre_serie][temporada]
            # Verifica si el episodio ya existe en la temporada
            episodio_existente = next((ep for ep in episodios_temporada if ep[0] == episodio), None)
            if episodio_existente:
                # Si el episodio existe, actualiza la información
                indice = episodios_temporada.index(episodio_existente)
                episodios_temporada[indice] = (episodio, servidor, calidad, enlace)
            else:
                # Si el episodio no existe, agrega una nueva entrada
                episodios_temporada.append((episodio, servidor, calidad, enlace))

                # Ordena la lista de episodios después de agregar uno nuevo
                episodios_temporada.sort(key=lambda x: x[0])
        else:
            # Si la temporada no existe, crea una nueva entrada para la temporada
            series_info[nombre_serie][temporada] = [(episodio, servidor, calidad, enlace)]
    else:
        # Crea una nueva entrada para la serie y la temporada
        series_info[nombre_serie] = {temporada: [(episodio, servidor, calidad, enlace)]}

    # Ordena las temporadas después de agregar o actualizar una temporada
    series_info[nombre_serie] = {k: sorted(v, key=lambda x: x[0]) for k, v in series_info[nombre_serie].items()}

    # Guarda la información actualizada en el archivo JSON
    update_series_file(f"stock_series_{idioma.lower()}", f"series_info_{idioma.lower()}.json", series_info)


# Cargar información existente al inicio del programa
series_info_castellano = load_series_info("stock_series_castellano", "series_info_castellano.json")
series_info_latino = load_series_info("stock_series_latino", "series_info_latino.json")

# Función para obtener información de TMDb
def obtener_info_serie(api_key, nombre_serie):
    url = f"https://api.themoviedb.org/3/search/tv"
    params = {
        "api_key": api_key,
        "query": nombre_serie,
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["results"]:
        # Devuelve la información de la primera serie encontrada
        return {
            "overview": data["results"][0]["overview"],
            "backdrop_path": data["results"][0]["backdrop_path"],
        }
    else:
        return None

# Actualización de las funciones de carga de series
@bot.slash_command(name="upload_series_castellano", description="Sube una serie en castellano a la carpeta correspondiente.")
async def upload_series_castellano(inter, nombre_serie: str, temporada: int, episodio: int, enlace: str, servidor: str, calidad: str):
    user = inter.user

    # Verifica si el usuario tiene permiso para ejecutar el comando
    if user.name not in ["vfx.fenix", "zflix.", "blasit0o", "yaxielgonz", "guesttbueno"]:
        await inter.send("No puedes usar este comando, necesitas ser uploader para ejecutarlo. Para ser uploader, deberás escribir el comando /solicitar (dudas) (quiero ser uploader). Nosotros nos pondremos en contacto contigo lo antes posible.", ephemeral=True)
        return

    # Determina la carpeta en función del idioma
    carpeta = "stock_series_castellano"
    nombre_archivo = f"{nombre_serie}.txt"

    # Define el idioma
    idioma = "castellano"

    # Define el diccionario correspondiente
    series_info = series_info_castellano

    upload_episode(series_info, idioma, nombre_serie, temporada, episodio, enlace, servidor, calidad)

    # Actualiza el archivo con la nueva información
    contenido_actualizado = f"{nombre_serie.upper()}\n\n"
    for temp, epis in sorted(series_info[nombre_serie].items(), key=lambda x: int(x[0])):
        contenido_actualizado += f"Temporada {temp}\n"
        for e in sorted(epis, key=lambda x: x[0]):
            contenido_actualizado += f"  Episodio {e[0]}\n"
            contenido_actualizado += f"    Servidor: {e[1]}\n"
            contenido_actualizado += f"    Calidad: {e[2]}\n"
            contenido_actualizado += f"    Enlace: {e[3]}\n"
        contenido_actualizado += "\n"

    # Usa el bloque with para asegurar que el archivo se cierre correctamente
    with open(os.path.join(carpeta, nombre_archivo), "w") as file:
        file.write(contenido_actualizado)

    canal_id = 1173070299688873994  # ID del canal para series en castellano
    channel = bot.get_channel(canal_id)

    if channel:
        # Obtiene el logo del servidor del código
        server_logo = "https://cdn.discordapp.com/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?ex=6547ca6f&is=6535556f&hm=554847654f2cec7a88da46958a1de81cae5662156b8c676896a1af3f22633361&"

        # Crea el mensaje embed
        embed = nextcord.Embed(title=f"Serie - {nombre_serie}", color=nextcord.Color.green())
        embed.add_field(name="Temporada", value=temporada, inline=True)
        embed.add_field(name="Episodio", value=episodio, inline=True)
        embed.add_field(name="Servidor", value=servidor, inline=True)
        embed.add_field(name="Calidad", value=calidad, inline=True)
        embed.add_field(name="Enlace", value=enlace, inline=False)
        embed.set_thumbnail(url=server_logo)  # Agrega el logo del servidor al mensaje embed como miniatura

        # Obtener información de TMDb
        info_serie = obtener_info_serie(TMDB_API_KEY, nombre_serie)

        if info_serie:
            # Agrega la sinopsis e imagen de TMDb al mensaje embed
            embed.add_field(name="Overview", value=info_serie["overview"], inline=False)
            embed.set_image(url=f"https://image.tmdb.org/t/p/original/{info_serie['backdrop_path']}")
            embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/original/{info_serie['poster_path']}")  # Agrega la imagen del póster como miniatura

        # Añade las reacciones al mensaje
        mensaje = await channel.send(embed=embed)
        await mensaje.add_reaction('❤️')
        await mensaje.add_reaction('👍')
        await mensaje.add_reaction('👎')

    embed_respuesta = nextcord.Embed(title=f"Serie '{nombre_serie}' en castellano actualizada correctamente.", color=nextcord.Color.green())
    await inter.send(embed=embed_respuesta, ephemeral=True)

# Función para subir una serie en latino
@bot.slash_command(name="upload_series_latino", description="Sube una serie en latino a la carpeta correspondiente.")
async def upload_series_latino(inter, nombre_serie: str, temporada: int, episodio: int, enlace: str, servidor: str, calidad: str):
    user = inter.user

    # Verifica si el usuario tiene permiso para ejecutar el comando
    if user.name not in ["vfx.fenix", "zflix.", "blasit0o", "yaxielgonz", "guesttbueno"]:
        await inter.send("No puedes usar este comando, necesitas ser uploader para ejecutarlo. Para ser uploader, deberás escribir el comando /solicitar (dudas) (quiero ser uploader). Nosotros nos pondremos en contacto contigo lo antes posible.", ephemeral=True)
        return

    # Determina la carpeta en función del idioma
    carpeta = "stock_series_latino"
    nombre_archivo = f"{nombre_serie}.txt"

    # Define el idioma
    idioma = "latino"

    # Define el diccionario correspondiente
    series_info = series_info_latino

    upload_episode(series_info, idioma, nombre_serie, temporada, episodio, enlace, servidor, calidad)

    # Actualiza el archivo con la nueva información
    contenido_actualizado = f"{nombre_serie.upper()}\n\n"
    for temp, epis in sorted(series_info[nombre_serie].items(), key=lambda x: int(x[0])):
        contenido_actualizado += f"Temporada {temp}\n"
        for e in sorted(epis, key=lambda x: x[0]):
            contenido_actualizado += f"  Episodio {e[0]}\n"
            contenido_actualizado += f"    Servidor: {e[1]}\n"
            contenido_actualizado += f"    Calidad: {e[2]}\n"
            contenido_actualizado += f"    Enlace: {e[3]}\n"
        contenido_actualizado += "\n"

    # Usa el bloque with para asegurar que el archivo se cierre correctamente
    with open(os.path.join(carpeta, nombre_archivo), "w") as file:
        file.write(contenido_actualizado)

    canal_id = 1173070583146350081  # ID del canal para series en latino
    channel = bot.get_channel(canal_id)

    if channel:
        # Obtiene el logo del servidor del código
        server_logo = "https://cdn.discordapp.com/attachments/1159589125725376544/1165696466078154882/project_20231022_1824446-01.png?ex=6547ca6f&is=6535556f&hm=554847654f2cec7a88da46958a1de81cae5662156b8c676896a1af3f22633361&"

        # Crea el mensaje embed
        embed = nextcord.Embed(title=f"Serie - {nombre_serie}", color=nextcord.Color.green())
        embed.add_field(name="Temporada", value=temporada, inline=True)
        embed.add_field(name="Episodio", value=episodio, inline=True)
        embed.add_field(name="Servidor", value=servidor, inline=True)
        embed.add_field(name="Calidad", value=calidad, inline=True)
        embed.add_field(name="Enlace", value=enlace, inline=False)
        embed.set_thumbnail(url=server_logo)  # Agrega el logo del servidor al mensaje embed como miniatura

        # Obtener información de TMDb
        info_serie = obtener_info_serie(TMDB_API_KEY, nombre_serie)

        if info_serie:
            # Agrega la sinopsis e imagen de TMDb al mensaje embed
            embed.add_field(name="Overview", value=info_serie["overview"], inline=False)
            embed.set_image(url=f"https://image.tmdb.org/t/p/original/{info_serie['backdrop_path']}")
            embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/original/{info_serie['poster_path']}")  # Agrega la imagen del póster como miniatura

        # Añade las reacciones al mensaje
        mensaje = await channel.send(embed=embed)
        await mensaje.add_reaction('❤️')
        await mensaje.add_reaction('👍')
        await mensaje.add_reaction('👎')

    embed_respuesta = nextcord.Embed(title=f"Serie '{nombre_serie}' en latino actualizada correctamente.", color=nextcord.Color.green())
    await inter.send(embed=embed_respuesta, ephemeral=True)




# Función para obtener información de TMDb
def obtener_info_serie(api_key, titulo, idioma="es-ES"):
    url = f"https://api.themoviedb.org/3/search/multi?api_key={api_key}&query={titulo}&language={idioma}"
    response = requests.get(url)
    data = response.json()
    if "results" in data and data["results"]:
        return data["results"][0]
    return None

# Modifica la función gen_serie_castellano
@bot.slash_command(name="gen_serie_castellano", description="Genera una serie en castellano.")
async def gen_serie_castellano(inter, serie: str):
    await send_series_file(inter, serie, "castellano")

# Modifica la función send_series_file para agregar información de TMDb
async def send_series_file(inter, serie, idioma):
    user = inter.user

    # Determina la carpeta en función del idioma
    carpeta = f"stock_series_{idioma.lower()}"

    # Busca un archivo que coincida con el nombre de la serie
    archivos = [f for f in os.listdir(carpeta) if serie.lower() in f.lower()]

    if not archivos:
        embed = nextcord.Embed(title="La serie que intentas generar no existe.", color=nextcord.Color.red())
        await inter.send(embed=embed, ephemeral=True)
        return

    # Suponiendo que solo se encontró un archivo, se enviará como archivo adjunto
    archivo_path = os.path.join(carpeta, archivos[0])

    # Obtener información de TMDb en castellano
    info_serie = obtener_info_serie(TMDB_API_KEY, serie)

    # Verifica si se obtuvo información
    if info_serie:
        # Extrae la sinopsis, la imagen de fondo y la imagen del póster
        sinopsis = info_serie.get("overview", "Sin sinopsis disponible.")
        imagen_fondo = f"https://image.tmdb.org/t/p/original/{info_serie.get('backdrop_path', '')}"
        imagen_poster = f"https://image.tmdb.org/t/p/original/{info_serie.get('poster_path', '')}"

        # Crea un mensaje embed con la información de la serie
        embed = nextcord.Embed(title=f"Serie - {serie}", color=nextcord.Color.green())
        embed.add_field(name="Sinopsis", value=sinopsis, inline=False)
        embed.set_image(url=imagen_fondo)
        embed.set_thumbnail(url=imagen_poster)  # Utiliza la imagen del póster como miniatura

        # Envía el mensaje embed al usuario
        await inter.send(embed=embed, ephemeral=True)

    # Envía el archivo como mensaje
    await inter.send(file=nextcord.File(archivo_path))

# Modifica la función gen_serie_latino
@bot.slash_command(name="gen_serie_latino", description="Genera una serie en latino.")
async def gen_serie_latino(inter, serie: str):
    await send_series_file_latino(inter, serie, "latino")

# Modifica la función send_series_file_latino para agregar información de TMDb
async def send_series_file_latino(inter, serie, idioma):
    user = inter.user

    # Determina la carpeta en función del idioma
    carpeta = f"stock_series_{idioma.lower()}"

    # Busca un archivo que coincida con el nombre de la serie
    archivos = [f for f in os.listdir(carpeta) if serie.lower() in f.lower()]

    if not archivos:
        embed = nextcord.Embed(title="La serie que intentas generar no existe.", color=nextcord.Color.red())
        await inter.send(embed=embed, ephemeral=True)
        return

    # Suponiendo que solo se encontró un archivo, se enviará como archivo adjunto
    archivo_path = os.path.join(carpeta, archivos[0])

    # Obtener información de TMDb en castellano
    info_serie = obtener_info_serie(TMDB_API_KEY, serie)

    # Verifica si se obtuvo información
    if info_serie:
        # Extrae la sinopsis, la imagen de fondo y la imagen del póster
        sinopsis = info_serie.get("overview", "Sin sinopsis disponible.")
        imagen_fondo = f"https://image.tmdb.org/t/p/original/{info_serie.get('backdrop_path', '')}"
        imagen_poster = f"https://image.tmdb.org/t/p/original/{info_serie.get('poster_path', '')}"

        # Crea un mensaje embed con la información de la serie
        embed = nextcord.Embed(title=f"Serie - {serie}", color=nextcord.Color.green())
        embed.add_field(name="Sinopsis", value=sinopsis, inline=False)
        embed.set_image(url=imagen_fondo)
        embed.set_thumbnail(url=imagen_poster)  # Utiliza la imagen del póster como miniatura

        # Envía el mensaje embed al usuario
        await inter.send(embed=embed, ephemeral=True)

    # Envía el archivo como mensaje
    await inter.send(file=nextcord.File(archivo_path))




# Comando para ver el stock de series en castellano
@bot.slash_command(name="stock_series_castellano", description="Mira el stock de series en castellano.")
async def stock_series_castellano(inter: nextcord.Interaction):
    await view_stock(inter, "castellano")

# Comando para ver el stock de series en latino
@bot.slash_command(name="stock_series_latino", description="Mira el stock de series en latino.")
async def stock_series_latino(inter: nextcord.Interaction):
    await view_stock(inter, "latino")

# Función para mostrar el stock de series en el idioma especificado
async def view_stock(inter, idioma):
    carpeta = f"stock_series_{idioma.lower()}"
    response = nextcord.Embed(title=f"ZFLIX STOCK de Series en {idioma.capitalize()}", color=nextcord.Color.green(), timestamp=datetime.datetime.utcnow())
    response.set_footer(text=server_name, icon_url=server_logo)
    response.set_thumbnail(url=server_logo)
    response.description = ""

    # Filtrar archivos con extensión .txt
    files = [filename for filename in os.listdir(carpeta) if filename.endswith(".txt")]

    series = []  # Crear una lista para almacenar los nombres de las series

    for filename in files:
        name = filename.replace(".txt", "").replace("_", " ").upper()  # Convertir a mayúsculas
        series.append(name)

    series.sort(key=lambda x: ''.join([c for c in x if c in string.ascii_lowercase + '0123456789']))

    for name in series:
        response.description += f"{name}\n\n"  # Agregar "\n\n" para un espacio en blanco entre series

    with open(f"stock_series_{idioma.lower()}.txt", "w") as file:
        file.write(response.description)

    file = nextcord.File(f"stock_series_{idioma.lower()}.txt")
    await inter.send(file=file, ephemeral=True)




@bot.slash_command(name="gen", description="Genera una película o serie del stock global")
async def gen(inter, title, language='es'):
    tmdb_language = language_map.get(language.lower(), TMDB_LANGUAGE)

    # Realizar búsqueda en la API de TMDb
    tmdb_url = 'https://api.themoviedb.org/3/search/multi'
    params = {'api_key': TMDB_API_KEY, 'query': title, 'language': tmdb_language}
    response = requests.get(tmdb_url, params=params)
    data = response.json()

    # Obtener el primer resultado de la búsqueda
    if 'results' in data and data['results']:
        first_result = data['results'][0]
        title = first_result.get('title') or first_result.get('name')
        media_type = first_result.get('media_type')

        # Obtener información de TMDb para el comando /watch
        watch_result = await watch_info(inter, title, media_type, tmdb_language)

        # Obtener el tráiler para el comando /trailer
        video_key = get_trailer_key(first_result['id'], media_type, tmdb_language)

        # Obtener los enlaces según el stock disponible
        enlaces = await get_links(title, language)

        # Enviar un mensaje con el título, enlaces y estadísticas
        if video_key:
            video_url = f'https://www.youtube.com/watch?v={video_key}'
            message = f'**{title}**\n\nEnlaces:\n{enlaces}\n\nEstadísticas según `/watch`:\n{watch_result}\n\nTrailer: [Ver Trailer]({video_url})'
            await inter.send(message, ephemeral=True)
        else:
            await inter.send(f'No se encontró el tráiler para {title}. Puede que el tráiler no esté disponible o tenga otro tipo.', ephemeral=True)
    else:
        await inter.send('No se encontraron resultados para la búsqueda.', ephemeral=True)






@bot.slash_command(name='info', description='Toda la info de una pelicula o serie')
async def info(ctx, option: str, media_type: str = "peliculas", search_query: str = "", results: int = 5):
    embed = nextcord.Embed(color=0x3498db)  # Color azul para el embed

    if option == 'trailer':
        # Obtener información de la película o serie de TMDb
        movie_data = get_movie_data(search_query)
        if movie_data:
            trailer_key = get_trailer_key(movie_data['id'])
            if trailer_key:
                trailer_url = f'https://www.youtube.com/watch?v={trailer_key}'
                embed.title = f'Tráiler de {search_query}'
                embed.add_field(name='Enlace', value=f'[Ver tráiler]({trailer_url})')
            else:
                embed.title = f'No se encontró tráiler para {search_query}.'
        else:
            embed.title = f'No se encontró información para {search_query}.'
    elif option == 'detalles':
        movie_data = get_movie_data(search_query)
        if movie_data:
            embed.title = f'Detalles de {movie_data["title"]}'
            embed.add_field(name='Sinopsis', value=movie_data['overview'])
            embed.add_field(name='Fecha de lanzamiento', value=movie_data['release_date'])
            embed.add_field(name='Tipo', value=get_media_type(movie_data))
            embed.add_field(name='Puntuación', value=movie_data['vote_average'])
            embed.add_field(name='Popularidad', value=movie_data['popularity'])
        else:
            embed.title = f'No se encontró información para {search_query}.'
    elif option == 'actor':
        movie_list, series_list = get_actor_movies(search_query)

        if movie_list or series_list:
            if movie_list:
                embed.add_field(name='Peliculas', value='\n'.join(['- ' + movie for movie in movie_list]))
            if series_list:
                embed.add_field(name='Series', value='\n'.join(['- ' + series for series in series_list]))
        else:
            embed.title = f'No se encontraron películas o series para el actor {search_query}.'

    elif option == 'recomendaciones':
        recommendations = get_recommendations(search_query)
        if recommendations:
            embed.title = f'Recomendaciones para {search_query}'
            embed.description = '\n'.join(['- ' + recommendation for recommendation in recommendations[:results]])
        else:
            embed.title = f'No se encontraron recomendaciones para {search_query}.'

    elif option == 'año':
        movie_list = get_movies_by_year(search_query)
        series_list = get_series_by_year(search_query)

        if movie_list or series_list:
            embed.title = f'Contenido del año {search_query}'
            description = ''  # Initialize description as an empty string
            if movie_list:
                description += '\n\nPelículas:'
                description += '\n'.join(['- ' + movie for movie in movie_list])
            if series_list:
                description += '\n\nSeries:'
                description += '\n'.join(['- ' + series for series in series_list])
            embed.description = description
        else:
            embed.title = f'No se encontró contenido para el año {search_query}.'

    elif option == 'categoria':
        # Verifica si el tipo de medio es "peliculas" o "series"
        if media_type.lower() == "peliculas":
            # Obtén la lista de películas por categoría
            movie_list = get_movies_by_category(search_query)
            if movie_list:
                embed.title = f'Películas en la categoría {search_query}'
                embed.description = '\n'.join(['- ' + movie for movie in movie_list])
            else:
                embed.title = f'No se encontraron películas para la categoría {search_query}.'
        elif media_type.lower() == "series":
            # Obtén la lista de series por categoría
            series_list = get_series_by_category(search_query)
            if series_list:
                embed.title = f'Series en la categoría {search_query}'
                embed.description = '\n'.join(['- ' + series for series in series_list])
            else:
                embed.title = f'No se encontraron series para la categoría {search_query}.'
        else:
            embed.title = 'Tipo de medio no válido. Debe ser "peliculas" o "series".'

    else:
        embed.title = 'Opción no válida.'
        embed.description = 'Las opciones son: trailer, detalles, actor, recomendaciones, año, categoria.'

    await ctx.send(embed=embed)

def get_movie_data(query):
    url = f'https://api.themoviedb.org/3/search/multi'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'es-ES',  # Puedes ajustar el idioma según tus preferencias
        'query': query
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data and data['results']:
        return data['results'][0]  # Devuelve la primera coincidencia
    else:
        return None

def get_media_data(query, media_type='movie'):
  url = f'https://api.themoviedb.org/3/search/{media_type}'
  params = {
      'api_key': TMDB_API_KEY,
      'language': 'es-ES',
      'query': query
  }
  response = requests.get(url, params=params)
  data = response.json()

  if 'results' in data and data['results']:
      return data['results'][0]  # Devuelve el primer resultado
  else:
      return None

def create_movie_details_response(movie_data):
    # Aquí puedes personalizar la respuesta según tus necesidades
    return f'''Detalles de {movie_data['title']}:
    Sinopsis: {movie_data['overview']}
    Fecha de lanzamiento: {movie_data['release_date']}
    Tipo: {get_media_type(movie_data)}
    Puntuación: {movie_data['vote_average']}
    Popularidad: {movie_data['popularity']}
    '''

def get_media_type(media_data):
    # Determina si es una película o una serie según la respuesta de TMDb
    return 'película' if media_data['media_type'] == 'movie' else 'serie'

def get_actor_movies(actor_name):
    url = f'https://api.themoviedb.org/3/search/person'
    params = {'api_key': TMDB_API_KEY, 'language': 'es-ES', 'query': actor_name}
    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data and data['results']:
        actor_id = data['results'][0]['id']
        actor_movies_url = f'https://api.themoviedb.org/3/person/{actor_id}/combined_credits'
        actor_movies_params = {'api_key': TMDB_API_KEY, 'language': 'es-ES'}
        actor_movies_response = requests.get(actor_movies_url, params=actor_movies_params)
        actor_movies_data = actor_movies_response.json()

        movie_list = [f'{item["title"]}' for item in actor_movies_data['cast'] if 'title' in item and item["media_type"] == "movie"]
        series_list = [f'{item["name"]}' for item in actor_movies_data['cast'] if 'name' in item and item["media_type"] == "tv"]
        return movie_list, series_list

    return [], []

def get_recommendations(query):
    movie_data = get_movie_data(query)

    if movie_data:
        movie_recommendations_url = f'https://api.themoviedb.org/3/movie/{movie_data["id"]}/recommendations'
        series_recommendations_url = f'https://api.themoviedb.org/3/tv/{movie_data["id"]}/recommendations'
        recommendations_params = {'api_key': TMDB_API_KEY, 'language': 'es-ES', 'page': 1}

        try:
            # Obtener recomendaciones para películas
            movie_recommendations_response = requests.get(movie_recommendations_url, params=recommendations_params)
            movie_recommendations_response.raise_for_status()
            movie_recommendations_data = movie_recommendations_response.json()

            # Usar el método get para obtener la lista de recomendaciones
            movie_recommendations = [f'{item.get("title", "")}' for item in movie_recommendations_data.get('results', [])]

            if movie_recommendations:
                return movie_recommendations

            # Obtener recomendaciones para series
            series_recommendations_response = requests.get(series_recommendations_url, params=recommendations_params)
            series_recommendations_response.raise_for_status()
            series_recommendations_data = series_recommendations_response.json()

            # Usar el método get para obtener la lista de recomendaciones para series
            series_recommendations = [f'{item.get("name", "")}' for item in series_recommendations_data.get('results', [])]

            if series_recommendations:
                return series_recommendations

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener recomendaciones: {e}")

    return []


def get_movies_by_year(year):
    url = f'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'es-ES',
        'sort_by': 'popularity.desc',
        'include_adult': 'false',
        'include_video': 'false',
        'primary_release_year': year
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data:
        movie_list = [f'{item["title"]}' for item in data['results'] if 'title' in item]
        return movie_list

    return []

def get_movies_by_category(category):
    url = f'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': TMDB_API_KEY,
        'language': 'es-ES',
        'sort_by': 'popularity.desc',
        'include_adult': 'false',
        'include_video': 'false',
        'with_genres': get_genre_id(category)
    }
    response = requests.get(url, params=params)
    data = response.json()

    if 'results' in data:
        movie_list = [f'{item["title"]}' for item in data['results'] if 'title' in item]
        return movie_list

    return []

def get_genre_id(category):
    # Mapeo de nombres de categorías a IDs de género según TMDb
    genre_mapping = {
        'acción': 28,
        'aventura': 12,
        'animación': 16,
        'comedia': 35,
        'crimen': 80,
        'documental': 99,
        'drama': 18,
        'familia': 10751,
        'fantasía': 14,
        'historia': 36,
        'terror': 27,
        'misterio': 9648,
        'música': 10402,
        'romance': 10749,
        'ciencia ficción': 878,
        'película de televisión': 10770,
        'thriller': 53,
        'bélica': 10752,
        'western': 37
    }
    return genre_mapping.get(category.lower(), 0)

def search_media(query, media_type='peliculas'):
  # Función para buscar películas o series basadas en un término de búsqueda y tipo de medio (película o serie)
  url = f'https://api.themoviedb.org/3/search/multi'  # Utilizamos 'multi' para buscar tanto películas como series
  params = {
      'api_key': TMDB_API_KEY,
      'language': 'es-ES',
      'query': query
  }
  response = requests.get(url, params=params)
  data = response.json()

  if 'results' in data:
      # Filtramos los resultados según el tipo de medio especificado
      if media_type == 'peliculas':
          search_results = [f'{item["title"]}' for item in data['results'] if 'title' in item and item["media_type"] == "movie"]
      elif media_type == 'series':
          search_results = [f'{item["name"]}' for item in data['results'] if 'name' in item and item["media_type"] == "tv"]
      else:
          search_results = []

      return search_results
  else:
      return []


def get_series_by_category(category):
  # Obtener series de TMDB por categoría
  url = 'https://api.themoviedb.org/3/discover/tv'
  params = {
      'api_key': TMDB_API_KEY,
      'with_genres': get_genre_id(category),
  }

  response = requests.get(url, params=params)
  series_data = response.json().get('results', [])
  series_list = [series['name'] for series in series_data]
  return series_list

def get_series_by_year(year):
  # Obtener series de TMDB por año
  url = 'https://api.themoviedb.org/3/discover/tv'
  params = {
      'api_key': TMDB_API_KEY,
      'first_air_date_year': year,
  }

  response = requests.get(url, params=params)
  series_data = response.json().get('results', [])
  series_list = [series['name'] for series in series_data]
  return series_list


bot.run(os.environ["token"])

