# 🤖 Delamain - Bot Musical Discord

Bot Discord musical inspiré de Cyberpunk 2077.

## 📁 Structure

```
delamain-bot/
├── bot.py              # Point d'entrée principal
├── config.py           # Configuration centralisée
├── cogs/
│   ├── __init__.py
│   └── music.py        # Commandes musicales
├── .env.example        # Template des variables d'environnement
├── .env                # Variables d'environnement (à créer)
└── requirements.txt    # Dépendances Python
```

## 🚀 Installation

### 1. Cloner et installer les dépendances

```bash
cd delamain-bot
pip install -r requirements.txt
```

### 2. Installer FFmpeg

**Ubuntu/Debian :**
```bash
sudo apt update && sudo apt install ffmpeg
```

**MacOS :**
```bash
brew install ffmpeg
```

**Windows :**
Télécharger depuis [ffmpeg.org](https://ffmpeg.org/download.html) et ajouter au PATH.

### 3. Configurer le token Discord

```bash
cp .env.example .env
```

Puis éditer `.env` et remplacer `votre_token_discord_ici` par votre vrai token.

### 4. Lancer le bot

```bash
python bot.py
```

## 🎮 Commandes

| Commande | Description |
|----------|-------------|
| `!play <titre/url>` | Joue une musique ou l'ajoute à la queue |
| `!pause` | Met en pause |
| `!resume` | Reprend la lecture |
| `!skip` | Passe à la musique suivante |
| `!queue` | Affiche la queue |
| `!stop` | Arrête et vide la queue |
| `!join` | Rejoint le salon vocal |
| `!leave` | Quitte le salon vocal |
| `!ping` | Affiche la latence |
| `!help` | Affiche l'aide |

### Slash Commands

- `/play <search>` - Joue une musique

## 🔧 Configuration

Modifiez `config.py` pour personnaliser :

- `PREFIX` - Préfixe des commandes (défaut: `!`)
- `COMMANDS_CHANNEL` - Salon pour le message d'aide
- Options `yt-dlp` et `FFmpeg`

## 📝 Notes

- Le bot crée une queue séparée par serveur
- Support des playlists YouTube
- Boutons de contrôle interactifs sur le lecteur
- Easter egg : écrivez "salut delamain" 😉
