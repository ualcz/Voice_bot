import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from Command.CommandVoice import CommandVoice

from Command.VoiceManager import ChannelManager
from Command.Erro import Erro
from Data.data import Database
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DB_DSN = os.getenv('DATABASE_URL')

data = Database(DB_DSN)

class MyClient(discord.Client):
    def __init__(self, *, db, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.database = db

    async def setup_hook(self):
        await self.database.connect()
        await self.tree.sync()

intents = discord.Intents.default()
client = MyClient(intents=intents, db=data)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    

# Configure and setup Voice 
Channel_Voice = ChannelManager(client=client)
Channel_Voice.setup()

Voice_comannd= CommandVoice(client=client)
Voice_comannd.setup()


# Configure and setup Erro
Erro= Erro(client=client)
Erro.setup()


client.run(DISCORD_TOKEN)