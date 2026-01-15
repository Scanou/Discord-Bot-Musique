"""
Cog Music - Gestion de la musique pour Delamain
"""

import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp

from config import YTDL_OPTIONS, FFMPEG_OPTIONS


class Song:
    """Représente une chanson dans la queue."""
    
    def __init__(self, title: str, url: str, webpage: str, thumbnail: str = None):
        self.title = title
        self.url = url
        self.webpage = webpage
        self.thumbnail = thumbnail
    
    @classmethod
    def from_info(cls, info: dict) -> "Song":
        """Crée une Song depuis les infos yt-dlp."""
        return cls(
            title=info.get("title", "Titre inconnu"),
            url=info.get("url"),
            webpage=info.get("webpage_url", ""),
            thumbnail=info.get("thumbnail"),
        )
    
    def to_embed(self) -> discord.Embed:
        """Génère un embed pour la chanson en cours."""
        embed = discord.Embed(
            title="🎶 Lecture en cours",
            description=f"**{self.title}**",
            color=discord.Color.blurple(),
        )
        if self.webpage:
            embed.add_field(name="Lien", value=f"[YouTube]({self.webpage})")
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed


class MusicControls(discord.ui.View):
    """Boutons de contrôle pour le lecteur."""
    
    def __init__(self, cog: "Music"):
        super().__init__(timeout=None)
        self.cog = cog
    
    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.primary)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Pause", ephemeral=True)
        else:
            await interaction.response.send_message("Rien en lecture", ephemeral=True)
    
    @discord.ui.button(label="▶️ Reprendre", style=discord.ButtonStyle.success)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Reprise", ephemeral=True)
        else:
            await interaction.response.send_message("Pas en pause", ephemeral=True)
    
    @discord.ui.button(label="⏭️ Suivant", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()  # Déclenche play_next via le callback
            await interaction.response.send_message("⏭️ Suivant", ephemeral=True)
        else:
            await interaction.response.send_message("Rien à passer", ephemeral=True)


class Music(commands.Cog):
    """Commandes musicales du bot."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)
        self.queues: dict[int, list[Song]] = {}  # guild_id -> queue
    
    def get_queue(self, guild_id: int) -> list[Song]:
        """Récupère ou crée la queue d'un serveur."""
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
    
    def play_next(self, ctx: commands.Context):
        """Joue la chanson suivante dans la queue."""
        queue = self.get_queue(ctx.guild.id)
        
        if queue and ctx.voice_client:
            song = queue.pop(0)
            source = discord.FFmpegPCMAudio(song.url, **FFMPEG_OPTIONS)
            ctx.voice_client.play(
                source,
                after=lambda e: self.play_next(ctx)
            )
    
    async def _play_song(self, ctx: commands.Context, song: Song):
        """Lance la lecture d'une chanson."""
        source = discord.FFmpegPCMAudio(song.url, **FFMPEG_OPTIONS)
        ctx.voice_client.play(
            source,
            after=lambda e: self.play_next(ctx)
        )
        await ctx.send(embed=song.to_embed(), view=MusicControls(self))
    
    # =========================================
    # Commandes vocales
    # =========================================
    
    @commands.command(name="join")
    async def join(self, ctx: commands.Context):
        """Rejoint le salon vocal de l'utilisateur."""
        if not ctx.author.voice:
            return await ctx.send("❌ Vous devez être dans un salon vocal.")
        
        if ctx.voice_client:
            return await ctx.send("🔊 Je suis déjà connecté.")
        
        await ctx.author.voice.channel.connect()
        await ctx.send("🔊 Connexion établie.")
    
    @commands.command(name="leave")
    async def leave(self, ctx: commands.Context):
        """Quitte le salon vocal."""
        if ctx.voice_client:
            self.get_queue(ctx.guild.id).clear()
            await ctx.voice_client.disconnect()
            await ctx.send("🔌 Déconnexion.")
        else:
            await ctx.send("❌ Je ne suis pas connecté.")
    
    # =========================================
    # Commandes de lecture
    # =========================================
    
    @commands.command(name="play", aliases=["p"])
    async def play(self, ctx: commands.Context, *, search: str):
        """Joue une musique ou l'ajoute à la queue."""
        # Auto-join si pas connecté
        if not ctx.voice_client:
            if not ctx.author.voice:
                return await ctx.send("❌ Vous devez être dans un salon vocal.")
            await ctx.author.voice.channel.connect()
        
        queue = self.get_queue(ctx.guild.id)
        
        # Gestion des playlists
        if "playlist" in search.lower():
            await self._handle_playlist(ctx, search, queue)
            return
        
        # Recherche simple
        try:
            info = self.ytdl.extract_info(search, download=False)
            
            # Si c'est une recherche YouTube
            if "entries" in info:
                info = info["entries"][0]
            
            song = Song.from_info(info)
            
            if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
                queue.append(song)
                await ctx.send(f"➕ Ajouté à la queue : **{song.title}**")
            else:
                await self._play_song(ctx, song)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur : {e}")
    
    async def _handle_playlist(self, ctx: commands.Context, url: str, queue: list[Song]):
        """Gère l'ajout d'une playlist."""
        try:
            playlist = self.ytdl.extract_info(url, download=False)
            
            if not playlist or "entries" not in playlist:
                return await ctx.send("❌ Playlist introuvable.")
            
            count = 0
            for entry in playlist["entries"]:
                if entry:
                    queue.append(Song.from_info(entry))
                    count += 1
            
            await ctx.send(f"📂 Playlist ajoutée ({count} titres)")
            
            # Lance la lecture si rien ne joue
            if not ctx.voice_client.is_playing():
                self.play_next(ctx)
                
        except Exception as e:
            await ctx.send(f"❌ Erreur playlist : {e}")
    
    @commands.command(name="pause")
    async def pause(self, ctx: commands.Context):
        """Met en pause la lecture."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Pause")
        else:
            await ctx.send("❌ Rien en lecture.")
    
    @commands.command(name="resume", aliases=["unpause"])
    async def resume(self, ctx: commands.Context):
        """Reprend la lecture."""
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Reprise")
        else:
            await ctx.send("❌ Pas en pause.")
    
    @commands.command(name="skip", aliases=["next", "s"])
    async def skip(self, ctx: commands.Context):
        """Passe à la musique suivante."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()  # Déclenche play_next
            await ctx.send("⏭️ Musique suivante")
        else:
            await ctx.send("❌ Rien à passer.")
    
    @commands.command(name="stop")
    async def stop(self, ctx: commands.Context):
        """Arrête la lecture et vide la queue."""
        if ctx.voice_client:
            self.get_queue(ctx.guild.id).clear()
            ctx.voice_client.stop()
            await ctx.send("⏹️ Arrêt")
        else:
            await ctx.send("❌ Rien en lecture.")
    
    @commands.command(name="queue", aliases=["q", "queue_list"])
    async def queue_list(self, ctx: commands.Context):
        """Affiche la queue actuelle."""
        queue = self.get_queue(ctx.guild.id)
        
        if not queue:
            return await ctx.send("📭 La queue est vide.")
        
        lines = [f"{i}. {song.title}" for i, song in enumerate(queue, 1)]
        message = "🎶 **Queue actuelle :**\n" + "\n".join(lines[:15])
        
        if len(queue) > 15:
            message += f"\n... et {len(queue) - 15} autres"
        
        await ctx.send(message)
    
    # =========================================
    # Slash commands
    # =========================================
    
    @app_commands.command(name="play", description="Joue une musique")
    @app_commands.describe(search="Titre ou lien YouTube")
    async def slash_play(self, interaction: discord.Interaction, search: str):
        """Version slash de la commande play."""
        await interaction.response.defer()
        ctx = await self.bot.get_context(interaction)
        await self.play(ctx, search=search)


async def setup(bot: commands.Bot):
    """Charge le cog."""
    await bot.add_cog(Music(bot))
