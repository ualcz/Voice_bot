import asyncpg

class Database:
    def __init__(self, dsn):
        self.dsn = dsn

    async def connect(self):
        """Conecta ao banco de dados."""
        self.pool = await asyncpg.create_pool(self.dsn)
        await self.create_table()

    async def create_table(self):
        """Cria a tabela se ela não existir."""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS voice_channels (
                    guild_id BIGINT,
                    channel_id BIGINT,
                    PRIMARY KEY (guild_id, channel_id)
                )
            ''')

    async def get_voice_channels(self, guild_id):
        """Retorna os canais de voz personalizados para um guild_id."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch('SELECT channel_id FROM voice_channels WHERE guild_id = $1', guild_id)
            return [row['channel_id'] for row in rows]

    async def save_voice_channel(self, guild_id, channel_id):
        """Adiciona um canal de voz à lista do guild_id."""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO voice_channels (guild_id, channel_id) 
                VALUES ($1, $2) 
                ON CONFLICT DO NOTHING
            ''', guild_id, channel_id)

    async def remove_voice_channel(self, guild_id, channel_id):
        """Remove um canal de voz da lista do guild_id."""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM voice_channels WHERE guild_id = $1 AND channel_id = $2', guild_id, channel_id)

    async def close(self):
        """Fecha a conexão com o banco de dados."""
        await self.pool.close()
