import json

class Database:
    def __init__(self, filename='voice_channels.json'):
        self.filename = filename
        self.load()

    def load(self):
        """Carrega os dados do arquivo JSON."""
        try:
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def save(self):
        """Salva os dados no arquivo JSON."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f)

    async def get_voice_channels(self, guild_id):
        """Retorna os canais de voz personalizados para um guild_id."""
        return self.data.get(str(guild_id), [])

    async def save_voice_channel(self, guild_id, channel_id):
        """Adiciona um canal de voz à lista do guild_id."""
        if str(guild_id) not in self.data:
            self.data[str(guild_id)] = []
        if channel_id not in self.data[str(guild_id)]:
            self.data[str(guild_id)].append(channel_id)
            self.save()

    async def remove_voice_channel(self, guild_id, channel_id):
        """Remove um canal de voz da lista do guild_id."""
        if str(guild_id) in self.data and channel_id in self.data[str(guild_id)]:
            self.data[str(guild_id)].remove(channel_id)
            self.save()
