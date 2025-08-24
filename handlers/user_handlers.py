import random

from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.schedulers import copy_post
from utils.build_ids import get_random_id
from database.action_data_class import DataInteraction
from database.model import ParseChannelsTable
from states.state_groups import startSG


user_router = Router()


@user_router.message(CommandStart())
async def start_dialog(msg: Message, dialog_manager: DialogManager, session: DataInteraction):
    await dialog_manager.start(state=startSG.start, mode=StartMode.RESET_STACK)


@user_router.channel_post()
async def send_channel_post(msg: Message, session: DataInteraction, scheduler: AsyncIOScheduler):
    channels = await session.get_channels()
    for channel in channels:
        parse_channels: list[ParseChannelsTable] = list(channel.parse_channels)
        channels_ids = [parse_channel.channel for parse_channel in parse_channels]
        print(channels_ids)
        if msg.chat.username and '@' + msg.chat.username in channels_ids:
            job_id = get_random_id()
            try:
                chat = await msg.bot.get_chat(channel.channel)
                chat_id = chat.id
            except Exception:
                continue
            if channel.min_hour and channel.max_hour:
                hour = random.choice(channel.hour_range)
                minutes = random.randint(0, 60)
                print(hour)
                new_hour = list(channel.hour_range)
                new_hour.remove(hour)
                if not new_hour:
                    new_hour = range(channel.min_hour, channel.max_hour + 1)
                print(new_hour)
                scheduler.add_job(
                    copy_post,
                    'interval',
                    args=[msg.bot, msg.message_id, msg.chat.id, chat_id, job_id, scheduler],
                    id=job_id,
                    hours=hour,
                    minutes=minutes
                )
                await session.update_hour_range(channel.id, new_hour)
            else:
                await copy_post(msg.bot, msg.message_id, msg.chat.id, chat_id, job_id, scheduler)




