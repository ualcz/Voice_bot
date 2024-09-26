import discord
from config import *
import traceback

class ChannelManager:
    def __init__(self, client: discord.Client):
        self.client = client
        self.created_voice_channels = []

    def setup(self):
        @self.client.event
        async def on_voice_state_update(member, before, after):
            guild_id = after.channel.guild.id if after.channel else None
            voice_channels = await self.client.database.get_voice_channels(guild_id) if guild_id else []

            if guild_id and before.channel != after.channel and after.channel and after.channel.id in voice_channels:
                guild = after.channel.guild
                category = after.channel.category

                if category is None:
                    return

                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(connect=True, view_channel=True),
                    member: discord.PermissionOverwrite(connect=True, manage_channels=True),
                }

                voice_channel = await category.create_voice_channel(name=f"{member.display_name}'s Channel", overwrites=overwrites)
                self.created_voice_channels.append(voice_channel)
                await member.move_to(voice_channel)

                text_channel = self.client.get_channel(voice_channel.id)
                if text_channel:
                    await text_channel.send(f"{member.mention}, canal de voz criado!", view=SelectView(guild.members))

            await self.check_and_delete_empty_channel(before.channel)
            await self.check_and_delete_empty_channel(after.channel)

    async def check_and_delete_empty_channel(self, channel):
        if isinstance(channel, discord.VoiceChannel) and channel in self.created_voice_channels and len(channel.members) == 0:
            self.created_voice_channels.remove(channel)
            await channel.delete()

class ChannelManagementSelect(discord.ui.Select):
    def __init__(self, members):
        options = [
            discord.SelectOption(label="Alterar Permissões", emoji="🔒", description="Alterar permissões do canal"),
            discord.SelectOption(label="Bloquear Membros", emoji="🚫", description="Bloquear membros de acessar o canal"),
            discord.SelectOption(label="Desbloquear Membros", emoji="✅", description="Desbloquear membros de acessar o canal"),
            discord.SelectOption(label="Definir Limite de Membros", emoji="🔢", description="Definir limite de membros para o canal"),
            discord.SelectOption(label="Alterar Nome do Canal", emoji="✏️", description="Alterar o nome do canal"),
        ]
        super().__init__(placeholder="Selecione uma opção", max_values=1, min_values=1, options=options)
        self.members = members

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]

        if selected_option == "Alterar Permissões":
            await self.change_permissions(interaction)
        elif selected_option == "Bloquear Membros":
            await self.show_block_select(interaction)
        elif selected_option == "Desbloquear Membros":
            await self.show_unblock_select(interaction)
        elif selected_option == "Definir Limite de Membros":
            await self.show_member_limit_modal(interaction)
        elif selected_option == "Alterar Nome do Canal":
            await self.show_channel_name_modal(interaction)

    async def change_permissions(self, interaction: discord.Interaction):
        await interaction.response.send_message("Alterando permissões do canal...", ephemeral=True)

    async def show_block_select(self, interaction: discord.Interaction):
        block_view = BlockView(self.members, block=True)
        await interaction.response.send_message("Selecione um membro para bloquear:", view=block_view, ephemeral=True)

    async def show_unblock_select(self, interaction: discord.Interaction):
        unblock_view = BlockView(self.members, block=False)
        await interaction.response.send_message("Selecione um membro para desbloquear:", view=unblock_view, ephemeral=True)

    async def show_member_limit_modal(self, interaction: discord.Interaction):
        modal = MemberLimitModal()
        await interaction.response.send_modal(modal)

    async def show_channel_name_modal(self, interaction: discord.Interaction):
        modal = ChannelNameModal()
        await interaction.response.send_modal(modal)

class BlockSelect(discord.ui.Select):
    def __init__(self, members, block):
        block_options = [discord.SelectOption(label=member.display_name, value=str(member.id)) for member in members]
        placeholder = "Selecione um membro para bloquear" if block else "Selecione um membro para desbloquear"
        super().__init__(placeholder=placeholder, max_values=1, min_values=1, options=block_options)
        self.members = members
        self.block = block

    async def callback(self, interaction: discord.Interaction):
        member_id = int(self.values[0])
        member = interaction.guild.get_member(member_id)

        if member:
            voice_channel = interaction.user.voice.channel
            if self.block:
                overwrite = discord.PermissionOverwrite()
                overwrite.connect = False
                await voice_channel.set_permissions(member, overwrite=overwrite)
                await interaction.response.edit_message(content=f"{member.display_name} foi bloqueado de entrar no canal de voz.")
            else:
                await voice_channel.set_permissions(member, overwrite=None)
                await interaction.response.edit_message(content=f"{member.display_name} foi desbloqueado para entrar no canal de voz.")
        else:
            await interaction.response.edit_message(content=f"Não foi possível encontrar o usuário com ID {member_id}.")

class BlockView(discord.ui.View):
    def __init__(self, members, block, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(BlockSelect(members, block))

class SelectView(discord.ui.View):
    def __init__(self, members, *, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(ChannelManagementSelect(members))

class MemberLimitModal(discord.ui.Modal, title='Definir Limite de Membros'):
    limit = discord.ui.TextInput(
        label='Limite de Membros',
        placeholder='Digite o limite de membros...',
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel
        if channel:
            member_limit = int(self.limit.value)
            await channel.edit(user_limit=member_limit)
            await interaction.response.send_message(f'Limite de membros definido para {member_limit}.', ephemeral=True)
        else:
            await interaction.response.send_message('Você não está em um canal de voz.', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Algo deu errado.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)

class ChannelNameModal(discord.ui.Modal, title='Alterar Nome do Canal'):
    name = discord.ui.TextInput(
        label='Nome do Canal',
        placeholder='Digite o novo nome do canal...',
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        channel = interaction.user.voice.channel
        if channel:
            new_name = self.name.value
            await channel.edit(name=new_name)
            await interaction.response.send_message(f'Nome do canal alterado para {new_name}.', ephemeral=True)
        else:
            await interaction.response.send_message('Você não está em um canal de voz.', ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Algo deu errado.', ephemeral=True)
        traceback.print_exception(type(error), error, error.__traceback__)
