from typing import List
from sqlalchemy import BigInteger, VARCHAR, ForeignKey, DateTime, Boolean, Column, Integer, String, func, ARRAY, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


association_table = Table(
    "send_parse_association",
    Base.metadata,
    Column("send_channel_id", Integer, ForeignKey("send-channels.id", ondelete="CASCADE")),
    Column("parse_channel_id", Integer, ForeignKey("parse-channels.id", ondelete="CASCADE"))
)


class SendChannelsTable(Base):
    __tablename__ = 'send-channels'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    channel: Mapped[str] = mapped_column(VARCHAR, unique=True)
    min_hour: Mapped[int] = mapped_column(Integer)
    max_hour: Mapped[int] = mapped_column(Integer)
    parse_channels = relationship("ParseChannelsTable", secondary=association_table, lazy="selectin")


class ParseChannelsTable(Base):
    __tablename__ = 'parse-channels'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    channel: Mapped[str] = mapped_column(VARCHAR, unique=True)

