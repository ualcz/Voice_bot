import discord
from typing import Optional
from discord import app_commands

class CommandVoice:
    def __init__(self, client):
        self.client = client

    def setup(self):
        # Comando para adicionar um canal de voz personalizado
        @self.client.tree.command(name="add_voice_channel", description="Adiciona um canal de voz para criar canais de voz personalizados")
        @app_commands.checks.has_permissions(administrator=True)
        async def add_voice_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
            guild_id = interaction.guild.id
            await self.client.database.save_voice_channel(guild_id, channel.id)
            await interaction.response.send_message(f"Canal de voz {channel.name} adicionado para criação de canais personalizados.", ephemeral=True)

        # Comando para listar todos os canais de voz personalizados do servidor
        @self.client.tree.command(name="list_voice_channels", description="Lista todos os canais de voz personalizados deste servidor")
        async def list_voice_channels(interaction: discord.Interaction):
            guild_id = interaction.guild.id
            channels = await self.client.database.get_voice_channels(guild_id)
            if channels:
                channel_mentions = ', '.join([f'<#{channel_id}>' for channel_id in channels])
                await interaction.response.send_message(f"Canais de voz personalizados: {channel_mentions}", ephemeral=True)
            else:
                await interaction.response.send_message("Nenhum canal de voz personalizado encontrado.", ephemeral=True)

        # Comando para remover um canal de voz da lista de canais personalizados
        @self.client.tree.command(name="remove_voice_channel", description="Remove um canal de voz da lista de canais personalizados")
        @app_commands.checks.has_permissions(administrator=True)
        async def remove_voice_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
            guild_id = interaction.guild.id
            await self.client.database.remove_voice_channel(guild_id, channel.id)
            await interaction.response.send_message(f"Canal de voz {channel.name} removido da lista de canais personalizados.", ephemeral=True)
