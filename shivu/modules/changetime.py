from pymongo import  ReturnDocument
from pyrogram.enums import ChatMemberStatus, ChatType
from shivu import user_totals_collection, shivuu, sudo_users, application
from pyrogram import Client, filters
from pyrogram.types import Message
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext


@shivuu.on_message(filters.command("changetime"))
async def change_time_pyrogram(client: Client, message: Message):
    
    user_id = message.from_user.id
    chat_id = message.chat.id
        
    # Check if user is a sudo user (not just group admin)
    if str(user_id) not in sudo_users:
        await message.reply_text('🚫 This command is only available to bot administrators.')
        return

    try:
        args = message.command
        if len(args) != 2:
            await message.reply_text('Please use: /changetime NUMBER')
            return

        new_frequency = int(args[1])
        # Allow sudo users to set any frequency (including below 100)
        if new_frequency < 1:
            await message.reply_text('The message frequency must be at least 1.')
            return

    
        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat_id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await message.reply_text(f'Successfully changed {new_frequency}')
    except Exception as e:
        await message.reply_text(f'Failed to change {str(e)}')


# python-telegram-bot version (works with webhooks)
async def change_time(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # Check if user is a sudo user
    if str(user_id) not in sudo_users:
        await update.message.reply_text('🚫 This command is only available to bot administrators.')
        return
    
    try:
        if not context.args or len(context.args) != 1:
            await update.message.reply_text('Please use: /changetime NUMBER')
            return
        
        new_frequency = int(context.args[0])
        # Allow sudo users to set any frequency (including below 100)
        if new_frequency < 1:
            await update.message.reply_text('The message frequency must be at least 1.')
            return
        
        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat_id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        
        await update.message.reply_text(f'Successfully changed to {new_frequency} messages')
    except ValueError:
        await update.message.reply_text('Please provide a valid number')
    except Exception as e:
        await update.message.reply_text(f'Failed to change: {str(e)}')


# Register the handler
application.add_handler(CommandHandler("changetime", change_time, block=False))
