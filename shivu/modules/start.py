import random
from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from shivu import (
    application,
    PHOTO_URL,
    SUPPORT_CHAT,
    UPDATE_CHAT,
    BOT_USERNAME,
    db,
    GROUP_ID,
)
from shivu import pm_users as collection


async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        await collection.insert_one(
            {
                "_id": user_id,
                "first_name": first_name,
                "username": username,
                "characters": [],
            }
        )

        # Optional: Send notification to group when new users start (uncomment if you have a group set up)
        # await context.bot.send_message(chat_id=GROUP_ID,
        #                                text=f"New user Started The Bot..\n User: <a href='tg://user?id={user_id}'>{escape(first_name)})</a>",
        #                                parse_mode='HTML')
    else:
        if user_data["first_name"] != first_name or user_data["username"] != username:
            await collection.update_one(
                {"_id": user_id},
                {"$set": {"first_name": first_name, "username": username}},
            )

    if update.effective_chat.type == "private":
        caption = f"""
<tg-emoji emoji-id="5102638339849192814">✨</tg-emoji> <b>Welcome to Waifu & Husbando Catcher!</b> <tg-emoji emoji-id="5102638339849192814">✨</tg-emoji>

<tg-emoji emoji-id="5103027133173731788">💕</tg-emoji> <b>Your ultimate anime character collection bot!</b>

<tg-emoji emoji-id="5102912496201631597">🎮</tg-emoji> <b>How it works:</b>
• Add me to your group and I'll send random anime characters every 100 messages
• Use /marry to catch characters and add them to your collection
• Build your dream collection and trade with friends!
• View your collection anytime with /collection

<tg-emoji emoji-id="5102825501639050967">🌟</tg-emoji> <b>Ready to start your anime adventure?</b> Add me to your group now!
        """

        keyboard = [
            [
                InlineKeyboardButton(
                    "SUPPORT", url=f"http://t.me/CollectorOfficialGroup"
                )
            ],
            [InlineKeyboardButton("HELP", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        from shivu import process_image_url

        photo_url = await process_image_url(random.choice(PHOTO_URL))

        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML',
        )

    else:
        from shivu import process_image_url

        photo_url = await process_image_url(random.choice(PHOTO_URL))
        keyboard = [
            [
                InlineKeyboardButton(
                    "SUPPORT", url=f"http://t.me/CollectorOfficialGroup"
                )
            ],
            [InlineKeyboardButton("HELP", callback_data="help")],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_url,
            caption="🎴Alive!?... \n connect to me in PM For more information ",
            reply_markup=reply_markup,
        )


async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        help_text = """
    *<b>Help Section:</b>*
    
*<b>/marry: To catch and marry characters (only works in group)</b>*
*<b>/fav: Add Your fav</b>*
*<b>/trade : To trade Characters</b>*
*<b>/gift: Give any Character from Your Collection to another user.. (only works in groups)</b>*
*<b>/collection: To see Your Collection</b>*
*<b>/topgroups : See Top Groups.. Ppl Guesses Most in that Groups</b>*
*<b>/top: Too See Top Users</b>*
*<b>/ctop : Your ChatTop</b>*
*<b>/changetime: Change Character appear time (only works in Groups)</b>*
   """
        help_keyboard = [[InlineKeyboardButton("⤾ Bᴀᴄᴋ", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(help_keyboard)

        await context.bot.edit_message_caption(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            caption=help_text,
            reply_markup=reply_markup,
            parse_mode='HTML',
        )

    elif query.data == "back":
        caption = f"""
<tg-emoji emoji-id="5102638339849192814">✨</tg-emoji> <b>Welcome to Waifu & Husbando Catcher!</b> <tg-emoji emoji-id="5102638339849192814">✨</tg-emoji>

<tg-emoji emoji-id="5103027133173731788">💕</tg-emoji> <b>Your ultimate anime character collection bot!</b>

<tg-emoji emoji-id="5102912496201631597">🎮</tg-emoji> <b>How it works:</b>
• Add me to your group and I'll send random anime characters every 100 messages
• Use /marry to catch characters and add them to your collection
• Build your dream collection and trade with friends!
• View your collection anytime with /collection

<tg-emoji emoji-id="5102825501639050967">🌟</tg-emoji> <b>Ready to start your anime adventure?</b> Add me to your group now!
        """

        keyboard = [
            [
                InlineKeyboardButton(
                    "SUPPORT", url=f"http://t.me/CollectorOfficialGroup"
                )
            ],
            [InlineKeyboardButton("HELP", callback_data="help")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.edit_message_caption(
            chat_id=update.effective_chat.id,
            message_id=query.message.message_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode='HTML',
        )


application.add_handler(
    CallbackQueryHandler(button, pattern="^help$|^back$", block=False)
)
start_handler = CommandHandler("start", start, block=False)
application.add_handler(start_handler)
