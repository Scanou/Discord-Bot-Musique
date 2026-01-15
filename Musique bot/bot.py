#!/usr/bin/env python3
"""
Bot Discord Delamain - Bot musical
"""

import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from config import PREFIX, COMMANDS_CHANNEL, COMMANDS_MESSAGE


class Delamain(commands.Bot):
    """Bot principal Delamain."""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix=PREFIX,
            intents=intents,
            help_command=None,  # On désactive la commande help par défaut
        )
    
    async def setup_hook(self):
        """Charge les cogs au démarrage."""
        await self.load_extension("cogs.music")
        print("✅ Cog Music chargé")
        
        # Sync les slash commands
        await self.tree.sync()
        print("✅ Slash commands synchronisées")
    
    async def on_ready(self):
        """Événement de démarrage."""
        print(f"{'='*40}")
        print(f"🤖 {self.user.name} est en ligne !")
        print(f"📡 Connecté sur {len(self.guilds)} serveur(s)")
        print(f"{'='*40}")
        
        # Envoie le message d'aide dans le salon #commands
        await self._send_commands_message()
        
        # Définit le statut
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="!play"
            )
        )
    
    async def _send_commands_message(self):
        """Envoie le message des commandes si nécessaire."""
        for guild in self.guilds:
            channel = discord.utils.get(guild.text_channels, name=COMMANDS_CHANNEL)
            
            if not channel:
                continue
            
            # Vérifie si le message existe déjà
            async for message in channel.history(limit=10):
                if message.author == self.user and "Commands Delamain" in message.content:
                    return
            
            await channel.send(COMMANDS_MESSAGE)
            print(f"📨 Message des commandes envoyé dans #{COMMANDS_CHANNEL}")
    
    async def on_message(self, message: discord.Message):
        """Gère les messages entrants."""
        # Ignore les bots
        if message.author.bot:
            return
        
        # Easter egg
        if message.content.lower() == "salut delamain":
            await message.channel.send("Dites-moi, que puis-je faire pour vous ?")
        
        # Process les commandes
        await self.process_commands(message)


# =========================================
# Commandes générales (hors cog)
# =========================================

bot = Delamain()


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    """Vérifie la latence du bot."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong ! Latence : {latency}ms")


@bot.command(name="help", aliases=["h", "aide"])
async def help_command(ctx: commands.Context):
    """Affiche l'aide."""
    embed = discord.Embed(
        title="🎶 Delamain - Aide",
        description="Bot musical pour Discord",
        color=discord.Color.blurple(),
    )
    
    embed.add_field(
        name="🎵 Musique",
        value=(
            "`!play <titre/url>` - Joue une musique\n"
            "`!pause` / `!resume` - Pause/Reprendre\n"
            "`!skip` - Musique suivante\n"
            "`!queue` - Voir la queue\n"
            "`!stop` - Arrêter"
        ),
        inline=False,
    )
    
    embed.add_field(
        name="🔊 Vocal",
        value=(
            "`!join` - Rejoindre le vocal\n"
            "`!leave` - Quitter le vocal"
        ),
        inline=False,
    )
    
    embed.add_field(
        name="📌 Autre",
        value="`!ping` - Latence du bot",
        inline=False,
    )
    
    await ctx.send(embed=embed)


# =========================================
# Point d'entrée
# =========================================

def main():
    """Lance le bot."""
    load_dotenv()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ DISCORD_TOKEN non trouvé dans le fichier .env")
        return
    
    print("🚀 Activation du BOT Delamain...")
    bot.run(token)


if __name__ == "__main__":
    main()
