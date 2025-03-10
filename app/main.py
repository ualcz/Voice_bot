import os
import discord
from discord import app_commands
from app.config.config import DB_DSN, DISCORD_TOKEN, BOT_VERSION
from app.command.command_voice import CommandVoice
from app.command.voice_manager import ChannelManager
from app.command.erro import Erro
from app.database.data import Database


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.database = Database(DB_DSN)
        self.channel_manager = None
        self.command_voice = None
        self.error_handler = None

    async def setup_hook(self):
        """Configuração inicial do bot quando ele se conecta."""
        await self.database.connect()
        await self.tree.sync()
        
        # Inicializa e configura os gerenciadores
        self.channel_manager = ChannelManager(client=self)
        self.channel_manager.setup()
        
        self.command_voice = CommandVoice(client=self)
        self.command_voice.setup()
        
        self.error_handler = Erro(client=self)
        self.error_handler.setup()

    async def on_ready(self):
        """Evento disparado quando o bot está pronto e conectado."""
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print(f'Version: {BOT_VERSION}')
        print('------')


def main():
    """Função principal para iniciar o bot."""
    intents = discord.Intents.default()
    client = MyClient(intents=intents)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()