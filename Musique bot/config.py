"""
Configuration centralisée du bot Delamain
"""

# Préfixe des commandes
PREFIX = "!"

# Nom du salon pour afficher les commandes
COMMANDS_CHANNEL = "commands"

# Message d'aide affiché au démarrage
COMMANDS_MESSAGE = """**🎶 Commands Delamain Music**

`!join` → Rejoindre le salon vocal
`!play <titre | url | playlist>` → Jouer ou ajouter à la queue
`!pause` / `!resume` → Pause / Reprendre
`!skip` → Musique suivante
`!queue` → Voir la queue
`!stop` → Arrêter la lecture
`!leave` → Quitter le salon vocal
"""

# Configuration yt-dlp
YTDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": False,
    "default_search": "ytsearch",
    "source_address": "0.0.0.0",
    "extract_flat": False,
}

# Configuration FFmpeg
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}
