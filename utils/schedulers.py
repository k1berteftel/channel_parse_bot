import asyncio
from aiogram import Bot
from aiogram_dialog import DialogManager
from aiogram.types import InlineKeyboardMarkup, Message
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.action_data_class import DataInteraction


async def copy_post(bot: Bot, msg_id: int, from_chat_id, chat_id: int, job_id: str, scheduler: AsyncIOScheduler):
    try:
        await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=msg_id
        )
    except Exception:
        ...
    job = scheduler.get_job(job_id)
    if job:
        job.remove()

