import datetime

from sqlalchemy import select, insert, update, column, text, delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import insert as postgres_insert

from database.model import ParseChannelsTable, SendChannelsTable


class DataInteraction():
    def __init__(self, session: async_sessionmaker):
        self._sessions = session

    async def add_channels(self, send_channels: list, parse_channels: list, min_hour: int, max_hour: int):
        async with self._sessions() as session:
            if parse_channels:
                stmt = postgres_insert(ParseChannelsTable).values(
                    [{"channel": ch} for ch in parse_channels]
                ).on_conflict_do_nothing(index_elements=['channel'])
                await session.execute(stmt)

            parse_objs = await session.scalars(
                select(ParseChannelsTable).where(ParseChannelsTable.channel.in_(parse_channels))
            )
            parse_map = {obj.channel: obj for obj in parse_objs}

            if send_channels:
                stmt = postgres_insert(SendChannelsTable).values([
                    {
                        "channel": ch,
                        "min_hour": min_hour,
                        "max_hour": max_hour
                    }
                    for ch in send_channels
                ]).on_conflict_do_nothing(index_elements=['channel'])
                await session.execute(stmt)

            for channel in send_channels:
                send_obj = await session.scalar(
                    select(SendChannelsTable).where(SendChannelsTable.channel == channel)
                )
                if send_obj:
                    send_obj.parse_channels = [
                        parse_map[ch] for ch in parse_channels if ch in parse_map
                    ]

            await session.commit()

    async def get_channels(self):
        async with self._sessions() as session:
            result = await session.scalars(select(SendChannelsTable))
        return result.fetchall()

    async def get_parse_channels(self):
        async with self._sessions() as session:
            result = await session.scalars(select(ParseChannelsTable))
        return result.fetchall()

    async def get_channel(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(SendChannelsTable).where(SendChannelsTable.id == id))
        return result

    async def del_channels(self, channels: list):
        async with self._sessions() as session:
            for channel in channels:
                await session.execute(delete(SendChannelsTable).where(SendChannelsTable.id == channel))
            await session.commit()

    async def del_parse_channels(self, channels: list[int]):
        async with self._sessions() as session:
            for channel in channels:
                await session.execute(delete(ParseChannelsTable).where(ParseChannelsTable.id == channel))
            await session.commit()

