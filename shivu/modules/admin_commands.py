from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardMarkup as PyrogramInlineKeyboardMarkup, InlineKeyboardButton as PyrogramInlineKeyboardButton
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
import math
import asyncio

from shivu import collection, locked_spawns_collection, shivuu, application, user_collection, group_user_totals_collection, banned_users_collection, OWNER_ID
from shivu.config import Config
from datetime import datetime, timedelta

@shivuu.on_message(filters.command("lockspawn"))
async def lockspawn(client, message):
    """Lock a character from spawning (sudo users only)"""
    sender_id = message.from_user.id
    
    # Check if user is admin
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    if len(message.command) != 2:
        await message.reply_text(
            "📝 <b>Lock Spawn Usage:</b>\n\n"
            "<code>/lockspawn [character_id]</code>\n\n"
            "<b>Example:</b> <code>/lockspawn 123</code>\n\n"
            "This will prevent the character from appearing in spawns.",
            parse_mode='HTML'
        )
        return
    
    character_id = message.command[1]
    
    # Check if character exists
    character = await collection.find_one({'id': character_id})
    if not character:
        await message.reply_text(f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Character with ID <code>{character_id}</code> not found!",
                parse_mode='HTML')
        return
    
    # Check if already locked
    existing_lock = await locked_spawns_collection.find_one({'character_id': character_id})
    if existing_lock:
        await message.reply_text(
            f"<tg-emoji emoji-id='5102920111178647010'>⚠️</tg-emoji> <b>Already Locked!</b>\n\n"
            f"🎴 <b>Character:</b> {character['name']}\n"
            f"<tg-emoji emoji-id='5102990630246680945'>📺</tg-emoji> <b>Anime:</b> {character['anime']}\n"
            f"<tg-emoji emoji-id='5102716405174765315'>🆔</tg-emoji> <b>ID:</b> <code>{character_id}</code>\n\n"
            f"This character is already locked from spawning.",
                parse_mode='HTML'
        )
        return
    
    # Lock the character
    await locked_spawns_collection.insert_one({
        'character_id': character_id,
        'character_name': character['name'],
        'anime': character['anime'],
        'rarity': character['rarity'],
        'locked_by': sender_id,
        'locked_by_username': message.from_user.username or message.from_user.first_name
    })
    
    rarity_emojis = {
        "Common": "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji>",
        "Uncommon": "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji>",
        "Rare": "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji>",
        "Epic": "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji>",
        "Legendary": "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji>",
        "Mythic": "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji>",
        "Retro": "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji>",
        "Star": "<tg-emoji emoji-id='5102825501639050967'>⭐</tg-emoji>",
        "Zenith": "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji>",
        "Limited Edition": "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji>"
    }
    
    rarity_emoji = rarity_emojis.get(character.get('rarity', 'Common'), "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji>")
    
    await message.reply_text(
        f"<tg-emoji emoji-id='5103032978624219059'>🔒</tg-emoji> <b>Spawn Locked!</b>\n\n"
        f"🎴 <b>Character:</b> {character['name']}\n"
        f"<tg-emoji emoji-id='5102990630246680945'>📺</tg-emoji> <b>Anime:</b> {character['anime']}\n"
        f"<tg-emoji emoji-id='5102825501639050967'>🌟</tg-emoji> <b>Rarity:</b> {rarity_emoji} {character['rarity']}\n"
        f"<tg-emoji emoji-id='5102716405174765315'>🆔</tg-emoji> <b>ID:</b> <code>{character_id}</code>\n\n"
        f"<tg-emoji emoji-id='5103087490349139576'>✅</tg-emoji> This character will no longer appear in spawns.",
                parse_mode='HTML'
    )

@shivuu.on_message(filters.command("unlockspawn"))
async def unlockspawn(client, message):
    """Unlock a character from spawn restrictions (sudo users only)"""
    sender_id = message.from_user.id
    
    # Check if user is admin
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    if len(message.command) != 2:
        await message.reply_text(
            "📝 <b>Unlock Spawn Usage:</b>\n\n"
            "<code>/unlockspawn [character_id]</code>\n\n"
            "<b>Example:</b> <code>/unlockspawn 123</code>\n\n"
            "This will allow the character to appear in spawns again.",
            parse_mode='HTML'
        )
        return
    
    character_id = message.command[1]
    
    # Check if character is locked
    locked_character = await locked_spawns_collection.find_one({'character_id': character_id})
    if not locked_character:
        await message.reply_text(f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Character with ID <code>{character_id}</code> is not currently locked!",
                parse_mode='HTML')
        return
    
    # Unlock the character
    await locked_spawns_collection.delete_one({'character_id': character_id})
    
    await message.reply_text(
        f"<tg-emoji emoji-id='5103032978624219059'>🔓</tg-emoji> <b>Spawn Unlocked!</b>\n\n"
        f"🎴 <b>Character:</b> {locked_character['character_name']}\n"
        f"<tg-emoji emoji-id='5102990630246680945'>📺</tg-emoji> <b>Anime:</b> {locked_character['anime']}\n"
        f"<tg-emoji emoji-id='5102716405174765315'>🆔</tg-emoji> <b>ID:</b> <code>{character_id}</code>\n\n"
        f"<tg-emoji emoji-id='5103087490349139576'>✅</tg-emoji> This character can now appear in spawns again.",
                parse_mode='HTML'
    )

@shivuu.on_message(filters.command("lockedspawns"))
async def lockedspawns(client, message, page=0):
    """View all currently locked spawn characters with pagination"""
    
    locked_characters = await locked_spawns_collection.find().to_list(length=None)
    
    if not locked_characters:
        await message.reply_text(
            "<tg-emoji emoji-id='5103032978624219059'>🔓</tg-emoji> <b>No Locked Spawns</b>\n\n"
            "There are currently no characters locked from spawning.",
            parse_mode='HTML'
        )
        return
    
    # Items per page
    items_per_page = 20
    total_pages = math.ceil(len(locked_characters) / items_per_page)
    
    # Ensure valid page
    if page < 0 or page >= total_pages:
        page = 0
    
    # Get characters for current page
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_page_chars = locked_characters[start_idx:end_idx]
    
    # Group by rarity
    rarity_groups = {}
    for char in current_page_chars:
        rarity = char.get('rarity', 'Common')
        if rarity not in rarity_groups:
            rarity_groups[rarity] = []
        rarity_groups[rarity].append(char)
    
    rarity_emojis = {
        "Common": "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji>",
        "Uncommon": "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji>",
        "Rare": "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji>",
        "Epic": "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji>",
        "Legendary": "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji>",
        "Mythic": "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji>",
        "Retro": "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji>",
        "Star": "<tg-emoji emoji-id='5102825501639050967'>⭐</tg-emoji>",
        "Zenith": "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji>",
        "Limited Edition": "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji>"
    }
    
    message_text = f"<tg-emoji emoji-id='5103032978624219059'>🔒</tg-emoji> <b>Locked Spawn Characters</b> - Page {page+1}/{total_pages}\n"
    
    for rarity in ["Limited Edition", "Star", "Zenith", "Retro", "Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]:
        if rarity in rarity_groups:
            rarity_emoji = rarity_emojis.get(rarity, "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji>")
            message_text += f"\n{rarity_emoji} <b>{rarity}:</b>\n"
            
            for char in rarity_groups[rarity]:
                message_text += f"• <code>{char['character_id']}</code> - {char['character_name']} ({char['anime']})\n"
    
    message_text += f"\n<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Total Locked:</b> {len(locked_characters)} characters"
    
    # Add pagination buttons if needed
    keyboard = None
    if total_pages > 1:
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton("<tg-emoji emoji-id='5102857782613248388'>⬅️</tg-emoji> Previous", callback_data=f"lockedspawns:{page-1}"))
        if page < total_pages - 1:
            buttons.append(InlineKeyboardButton("Next <tg-emoji emoji-id='5102932600943544398'>➡️</tg-emoji>", callback_data=f"lockedspawns:{page+1}"))
        
        if buttons:
            keyboard = InlineKeyboardMarkup([buttons])
    
    await message.reply_text(message_text, parse_mode='HTML', reply_markup=keyboard)

@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data.startswith("lockedspawns:")))
async def lockedspawns_callback(client, callback_query):
    """Handle lockedspawns pagination"""
    try:
        page = int(callback_query.data.split(":")[1])
        
        # Get locked characters
        locked_characters = await locked_spawns_collection.find().to_list(length=None)
        
        if not locked_characters:
            await callback_query.answer("No locked spawns available!", show_alert=True)
            return
        
        # Items per page
        items_per_page = 20
        total_pages = math.ceil(len(locked_characters) / items_per_page)
        
        # Ensure valid page
        if page < 0 or page >= total_pages:
            page = 0
        
        # Get characters for current page
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_chars = locked_characters[start_idx:end_idx]
        
        # Group by rarity
        rarity_groups = {}
        for char in current_page_chars:
            rarity = char.get('rarity', 'Common')
            if rarity not in rarity_groups:
                rarity_groups[rarity] = []
            rarity_groups[rarity].append(char)
        
        rarity_emojis = {
            "Common": "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji>",
            "Uncommon": "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji>",
            "Rare": "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji>",
            "Epic": "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji>",
            "Legendary": "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji>",
            "Mythic": "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji>",
            "Retro": "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji>",
            "Star": "<tg-emoji emoji-id='5102825501639050967'>⭐</tg-emoji>",
            "Zenith": "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji>",
            "Limited Edition": "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji>"
        }
        
        message_text = f"<tg-emoji emoji-id='5103032978624219059'>🔒</tg-emoji> <b>Locked Spawn Characters</b> - Page {page+1}/{total_pages}\n"
        
        for rarity in ["Limited Edition", "Star", "Zenith", "Retro", "Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]:
            if rarity in rarity_groups:
                rarity_emoji = rarity_emojis.get(rarity, "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji>")
                message_text += f"\n{rarity_emoji} <b>{rarity}:</b>\n"
                
                for char in rarity_groups[rarity]:
                    message_text += f"• <code>{char['character_id']}</code> - {char['character_name']} ({char['anime']})\n"
        
        message_text += f"\n<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Total Locked:</b> {len(locked_characters)} characters"
        
        # Add pagination buttons if needed
        keyboard = None
        if total_pages > 1:
            buttons = []
            if page > 0:
                buttons.append(InlineKeyboardButton("<tg-emoji emoji-id='5102857782613248388'>⬅️</tg-emoji> Previous", callback_data=f"lockedspawns:{page-1}"))
            if page < total_pages - 1:
                buttons.append(InlineKeyboardButton("Next <tg-emoji emoji-id='5102932600943544398'>➡️</tg-emoji>", callback_data=f"lockedspawns:{page+1}"))
            
            if buttons:
                keyboard = InlineKeyboardMarkup([buttons])
        
        await callback_query.edit_message_text(message_text, parse_mode='HTML', reply_markup=keyboard)
        await callback_query.answer()
        
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)}", show_alert=True)

@shivuu.on_message(filters.command("rarity"))
async def rarity(client, message):
    """Show all rarities and their spawn rates"""
    
    message_text = (
        "<tg-emoji emoji-id='5102663817595193122'>🎏</tg-emoji> 𝘊𝘩𝘢𝘳𝘢𝘤𝘵𝘦𝘳 𝘙𝘢𝘳𝘪𝘵𝘺 𝘚𝘺𝘴𝘵𝘦𝘮 <tg-emoji emoji-id='5102663817595193122'>🎏</tg-emoji>\n\n"
        "<tg-emoji emoji-id='5102722031581923128'>🎐</tg-emoji> 𝘙𝘦𝘨𝘶𝘭𝘢𝘳 𝘚𝘱𝘢𝘸𝘯𝘴 (𝘦𝘷𝘦𝘳𝘺 100 𝘮𝘦𝘴𝘴𝘢𝘨𝘦𝘴)\n\n"
        "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji> 𝘊𝘰𝘮𝘮𝘰𝘯 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji> 𝘜𝘯𝘤𝘰𝘮𝘮𝘰𝘯 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji> 𝘙𝘢𝘳𝘦 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji> 𝘌𝘱𝘪𝘤 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji> 𝘓𝘦𝘨𝘦𝘯𝘥𝘢𝘳𝘺 : 2% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji> 𝘔𝘺𝘵𝘩𝘪𝘤 : 0.8% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji> 𝘙𝘦𝘵𝘳𝘰 : 0.4% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji> 𝘡𝘦𝘯𝘪𝘵𝘩 : 0.01% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji> 𝘓𝘪𝘮𝘪𝘵𝘦𝘥 𝘌𝘥𝘪𝘵𝘪𝘰𝘯 : 0.001% 𝘤𝘩𝘢𝘯𝘤𝘦\n\n"
        "<tg-emoji emoji-id='5102587667825035890'>👾</tg-emoji> 𝘊𝘶𝘴𝘵𝘰𝘮 𝘊𝘩𝘢𝘳𝘢𝘤𝘵𝘦𝘳𝘴 𝘢𝘳𝘦 𝘰𝘳𝘥𝘦𝘳𝘦𝘥 𝘵𝘰 𝘛𝘩𝘦 𝘖𝘸𝘯𝘦𝘳 𝘢𝘯𝘥 𝘵𝘩𝘦𝘺 𝘤𝘢𝘯 𝘰𝘯𝘭𝘺 𝘩𝘢𝘷𝘦 𝘶𝘱 𝘵𝘰 2 𝘖𝘸𝘯𝘦𝘳𝘴. (𝘛𝘩𝘦𝘺 𝘸𝘪𝘭𝘭 𝘯𝘦𝘷𝘦𝘳 𝘴𝘱𝘢𝘸𝘯)"
    )
  
    await message.reply_text(message_text, parse_mode='HTML')


# python-telegram-bot versions (work with webhooks)
async def lockspawn_ptb(update: Update, context: CallbackContext):
    """Lock a character from spawning (sudo users only) - PTB version"""
    sender_id = update.effective_user.id
    
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await update.message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "📝 <b>Lock Spawn Usage:</b>\n\n"
            "<code>/lockspawn [character_id]</code>\n\n"
            "<b>Example:</b> <code>/lockspawn 123</code>\n\n"
            "This will prevent the character from appearing in spawns.",
            parse_mode='HTML'
        )
        return
    
    character_id = context.args[0]
    
    character = await collection.find_one({'id': character_id})
    if not character:
        await update.message.reply_text(f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Character with ID <code>{character_id}</code> not found!",
                parse_mode='HTML')
        return
    
    existing_lock = await locked_spawns_collection.find_one({'character_id': character_id})
    if existing_lock:
        await update.message.reply_text(
            f"<tg-emoji emoji-id='5102920111178647010'>⚠️</tg-emoji> <b>Already Locked!</b>\n\n"
            f"🎴 <b>Character:</b> {character['name']}\n"
            f"<tg-emoji emoji-id='5102990630246680945'>📺</tg-emoji> <b>Anime:</b> {character['anime']}\n"
            f"<tg-emoji emoji-id='5102716405174765315'>🆔</tg-emoji> <b>ID:</b> <code>{character_id}</code>\n\n"
            f"This character is already locked from spawning.",
                parse_mode='HTML'
        )
        return
    
    await locked_spawns_collection.insert_one({
        'character_id': character_id,
        'character_name': character['name'],
        'anime': character['anime'],
        'rarity': character['rarity'],
        'locked_by': sender_id,
        'locked_by_username': update.effective_user.username or update.effective_user.first_name
    })
    
    rarity_emojis = {
        "Common": "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji>", "Uncommon": "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji>", "Rare": "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji>", "Epic": "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji>",
        "Legendary": "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji>", "Mythic": "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji>", "Retro": "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji>", "Star": "<tg-emoji emoji-id='5102825501639050967'>⭐</tg-emoji>",
        "Zenith": "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji>", "Limited Edition": "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji>"
    }
    
    rarity_emoji = rarity_emojis.get(character.get('rarity', 'Common'), "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji>")
    
    await update.message.reply_text(
        f"<tg-emoji emoji-id='5103032978624219059'>🔒</tg-emoji> <b>Spawn Locked!</b>\n\n"
        f"🎴 <b>Character:</b> {character['name']}\n"
        f"<tg-emoji emoji-id='5102990630246680945'>📺</tg-emoji> <b>Anime:</b> {character['anime']}\n"
        f"<tg-emoji emoji-id='5102825501639050967'>🌟</tg-emoji> <b>Rarity:</b> {rarity_emoji} {character['rarity']}\n"
        f"<tg-emoji emoji-id='5102716405174765315'>🆔</tg-emoji> <b>ID:</b> <code>{character_id}</code>\n\n"
        f"<tg-emoji emoji-id='5103087490349139576'>✅</tg-emoji> This character will no longer appear in spawns.",
                parse_mode='HTML'
    )


async def unlockspawn_ptb(update: Update, context: CallbackContext):
    """Unlock a character from spawn restrictions - PTB version"""
    sender_id = update.effective_user.id
    
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await update.message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    if not context.args or len(context.args) != 1:
        await update.message.reply_text(
            "📝 <b>Unlock Spawn Usage:</b>\n\n"
            "<code>/unlockspawn [character_id]</code>\n\n"
            "<b>Example:</b> <code>/unlockspawn 123</code>\n\n"
            "This will allow the character to appear in spawns again.",
            parse_mode='HTML'
        )
        return
    
    character_id = context.args[0]
    
    locked_character = await locked_spawns_collection.find_one({'character_id': character_id})
    if not locked_character:
        await update.message.reply_text(f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Character with ID <code>{character_id}</code> is not currently locked!",
                parse_mode='HTML')
        return
    
    await locked_spawns_collection.delete_one({'character_id': character_id})
    
    await update.message.reply_text(
        f"<tg-emoji emoji-id='5103032978624219059'>🔓</tg-emoji> <b>Spawn Unlocked!</b>\n\n"
        f"🎴 <b>Character:</b> {locked_character['character_name']}\n"
        f"<tg-emoji emoji-id='5102990630246680945'>📺</tg-emoji> <b>Anime:</b> {locked_character['anime']}\n"
        f"<tg-emoji emoji-id='5102716405174765315'>🆔</tg-emoji> <b>ID:</b> <code>{character_id}</code>\n\n"
        f"<tg-emoji emoji-id='5103087490349139576'>✅</tg-emoji> This character can now appear in spawns again.",
                parse_mode='HTML'
    )


async def lockedspawns_ptb(update: Update, context: CallbackContext, page=0):
    """View all locked spawn characters with pagination - PTB version"""
    locked_characters = await locked_spawns_collection.find().to_list(length=None)
    
    if not locked_characters:
        await update.message.reply_text(
            "<tg-emoji emoji-id='5103032978624219059'>🔓</tg-emoji> <b>No Locked Spawns</b>\n\n"
            "There are currently no characters locked from spawning.",
            parse_mode='HTML'
        )
        return
    
    items_per_page = 20
    total_pages = math.ceil(len(locked_characters) / items_per_page)
    
    if page < 0 or page >= total_pages:
        page = 0
    
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_page_chars = locked_characters[start_idx:end_idx]
    
    rarity_groups = {}
    for char in current_page_chars:
        rarity = char.get('rarity', 'Common')
        if rarity not in rarity_groups:
            rarity_groups[rarity] = []
        rarity_groups[rarity].append(char)
    
    rarity_emojis = {
        "Common": "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji>", "Uncommon": "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji>", "Rare": "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji>", "Epic": "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji>",
        "Legendary": "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji>", "Mythic": "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji>", "Retro": "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji>", "Star": "<tg-emoji emoji-id='5102825501639050967'>⭐</tg-emoji>",
        "Zenith": "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji>", "Limited Edition": "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji>"
    }
    
    message_text = f"<tg-emoji emoji-id='5103032978624219059'>🔒</tg-emoji> <b>Locked Spawn Characters</b> - Page {page+1}/{total_pages}\n"
    
    for rarity in ["Limited Edition", "Star", "Zenith", "Retro", "Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]:
        if rarity in rarity_groups:
            rarity_emoji = rarity_emojis.get(rarity, "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji>")
            message_text += f"\n{rarity_emoji} <b>{rarity}:</b>\n"
            
            for char in rarity_groups[rarity]:
                message_text += f"• <code>{char['character_id']}</code> - {char['character_name']} ({char['anime']})\n"
    
    message_text += f"\n<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Total Locked:</b> {len(locked_characters)} characters"
    
    keyboard = None
    if total_pages > 1:
        buttons = []
        if page > 0:
            buttons.append(InlineKeyboardButton("<tg-emoji emoji-id='5102857782613248388'>⬅️</tg-emoji> Previous", callback_data=f"lockedspawns:{page-1}"))
        if page < total_pages - 1:
            buttons.append(InlineKeyboardButton("Next <tg-emoji emoji-id='5102932600943544398'>➡️</tg-emoji>", callback_data=f"lockedspawns:{page+1}"))
        
        if buttons:
            keyboard = InlineKeyboardMarkup([buttons])
    
    await update.message.reply_text(message_text, parse_mode='HTML', reply_markup=keyboard)


async def lockedspawns_callback_ptb(update: Update, context: CallbackContext):
    """Handle lockedspawns pagination - PTB version"""
    query = update.callback_query
    
    try:
        page = int(query.data.split(":")[1])
        
        locked_characters = await locked_spawns_collection.find().to_list(length=None)
        
        if not locked_characters:
            await query.answer("No locked spawns available!", show_alert=True)
            return
        
        items_per_page = 20
        total_pages = math.ceil(len(locked_characters) / items_per_page)
        
        if page < 0 or page >= total_pages:
            page = 0
        
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_chars = locked_characters[start_idx:end_idx]
        
        rarity_groups = {}
        for char in current_page_chars:
            rarity = char.get('rarity', 'Common')
            if rarity not in rarity_groups:
                rarity_groups[rarity] = []
            rarity_groups[rarity].append(char)
        
        rarity_emojis = {
            "Common": "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji>", "Uncommon": "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji>", "Rare": "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji>", "Epic": "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji>",
            "Legendary": "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji>", "Mythic": "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji>", "Retro": "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji>", "Star": "<tg-emoji emoji-id='5102825501639050967'>⭐</tg-emoji>",
            "Zenith": "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji>", "Limited Edition": "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji>"
        }
        
        message_text = f"<tg-emoji emoji-id='5103032978624219059'>🔒</tg-emoji> <b>Locked Spawn Characters</b> - Page {page+1}/{total_pages}\n"
        
        for rarity in ["Limited Edition", "Star", "Zenith", "Retro", "Mythic", "Legendary", "Epic", "Rare", "Uncommon", "Common"]:
            if rarity in rarity_groups:
                rarity_emoji = rarity_emojis.get(rarity, "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji>")
                message_text += f"\n{rarity_emoji} <b>{rarity}:</b>\n"
                
                for char in rarity_groups[rarity]:
                    message_text += f"• <code>{char['character_id']}</code> - {char['character_name']} ({char['anime']})\n"
        
        message_text += f"\n<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Total Locked:</b> {len(locked_characters)} characters"
        
        keyboard = None
        if total_pages > 1:
            buttons = []
            if page > 0:
                buttons.append(InlineKeyboardButton("<tg-emoji emoji-id='5102857782613248388'>⬅️</tg-emoji> Previous", callback_data=f"lockedspawns:{page-1}"))
            if page < total_pages - 1:
                buttons.append(InlineKeyboardButton("Next <tg-emoji emoji-id='5102932600943544398'>➡️</tg-emoji>", callback_data=f"lockedspawns:{page+1}"))
            
            if buttons:
                keyboard = InlineKeyboardMarkup([buttons])
        
        await query.edit_message_text(message_text, parse_mode='HTML', reply_markup=keyboard)
        await query.answer()
        
    except Exception as e:
        await query.answer(f"Error: {str(e)}", show_alert=True)


async def rarity_ptb(update: Update, context: CallbackContext):
    """Show all rarities and their spawn rates - PTB version"""
    
    message_text = (
        "<tg-emoji emoji-id='5102663817595193122'>🎏</tg-emoji> 𝘊𝘩𝘢𝘳𝘢𝘤𝘵𝘦𝘳 𝘙𝘢𝘳𝘪𝘵𝘺 𝘚𝘺𝘴𝘵𝘦𝘮 <tg-emoji emoji-id='5102663817595193122'>🎏</tg-emoji>\n\n"
        "<tg-emoji emoji-id='5102722031581923128'>🎐</tg-emoji> 𝘙𝘦𝘨𝘶𝘭𝘢𝘳 𝘚𝘱𝘢𝘸𝘯𝘴 (𝘦𝘷𝘦𝘳𝘺 100 𝘮𝘦𝘴𝘴𝘢𝘨𝘦𝘴)\n\n"
        "<tg-emoji emoji-id='5102863490624784495'>⚪️</tg-emoji> 𝘊𝘰𝘮𝘮𝘰𝘯 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102906715175651186'>🟢</tg-emoji> 𝘜𝘯𝘤𝘰𝘮𝘮𝘰𝘯 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102814377673754670'>🔵</tg-emoji> 𝘙𝘢𝘳𝘦 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5103060513659554158'>🟣</tg-emoji> 𝘌𝘱𝘪𝘤 : 20% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102990767685634240'>🟡</tg-emoji> 𝘓𝘦𝘨𝘦𝘯𝘥𝘢𝘳𝘺 : 2% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102655962100008917'>🏵</tg-emoji> 𝘔𝘺𝘵𝘩𝘪𝘤 : 0.8% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5102698301887612539'>🍥</tg-emoji> 𝘙𝘦𝘵𝘳𝘰 : 0.4% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5103065238123578838'>🪩</tg-emoji> 𝘡𝘦𝘯𝘪𝘵𝘩 : 0.01% 𝘤𝘩𝘢𝘯𝘤𝘦\n"
        "<tg-emoji emoji-id='5103127253156367234'>🍬</tg-emoji> 𝘓𝘪𝘮𝘪𝘵𝘦𝘥 𝘌𝘥𝘪𝘵𝘪𝘰𝘯 : 0.001% 𝘤𝘩𝘢𝘯𝘤𝘦\n\n"
        "<tg-emoji emoji-id='5102587667825035890'>👾</tg-emoji> 𝘊𝘶𝘴𝘵𝘰𝘮 𝘊𝘩𝘢𝘳𝘢𝘤𝘵𝘦𝘳𝘴 𝘢𝘳𝘦 𝘰𝘳𝘥𝘦𝘳𝘦𝘥 𝘵𝘰 𝘛𝘩𝘦 𝘖𝘸𝘯𝘦𝘳 𝘢𝘯𝘥 𝘵𝘩𝘦𝘺 𝘤𝘢𝘯 𝘰𝘯𝘭𝘺 𝘩𝘢𝘷𝘦 𝘶𝘱 𝘵𝘰 2 𝘖𝘸𝘯𝘦𝘳𝘴. (𝘛𝘩𝘦𝘺 𝘸𝘪𝘭𝘭 𝘯𝘦𝘷𝘦𝘳 𝘴𝘱𝘢𝘸𝘯)"
    )
  
    await update.message.reply_text(message_text, parse_mode='HTML')


# ============== BROADCAST COMMAND ==============

@shivuu.on_message(filters.command("broadcast"))
async def broadcast(client, message):
    """Broadcast a message to all players and/or groups (owner only)"""
    sender_id = message.from_user.id
    
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    if not message.reply_to_message and len(message.command) < 2:
        await message.reply_text(
            "<tg-emoji emoji-id='5103061849394382829'>📢</tg-emoji> <b>Broadcast Command</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/broadcast [message]</code> - Send to all users & groups\n"
            "<code>/broadcast -users [message]</code> - Send to users only\n"
            "<code>/broadcast -groups [message]</code> - Send to groups only\n\n"
            "<b>Or:</b> Reply to any message with <code>/broadcast</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/broadcast Hello everyone! New update is here!</code>",
            parse_mode='HTML'
        )
        return
    
    args = message.command[1:] if len(message.command) > 1 else []
    
    send_to_users = True
    send_to_groups = True
    
    if args and args[0] == "-users":
        send_to_groups = False
        args = args[1:]
    elif args and args[0] == "-groups":
        send_to_users = False
        args = args[1:]
    
    if message.reply_to_message:
        broadcast_message = message.reply_to_message
        is_reply = True
    else:
        broadcast_text = " ".join(args)
        if not broadcast_text:
            await message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Please provide a message to broadcast!",
                parse_mode='HTML')
            return
        is_reply = False
    
    status_msg = await message.reply_text("<tg-emoji emoji-id='5103061849394382829'>📡</tg-emoji> Starting broadcast...",
                parse_mode='HTML')
    
    success_users = 0
    failed_users = 0
    success_groups = 0
    failed_groups = 0
    
    if send_to_users:
        all_users = await user_collection.find({}).to_list(length=None)
        total_users = len(all_users)
        
        for i, user in enumerate(all_users):
            try:
                user_id = user.get('id')
                if not user_id:
                    continue
                    
                if is_reply:
                    await broadcast_message.copy(chat_id=user_id)
                else:
                    await client.send_message(chat_id=user_id, text=broadcast_text)
                    
                success_users += 1
                
                if (i + 1) % 25 == 0:
                    await status_msg.edit_text(
                        f"<tg-emoji emoji-id='5103061849394382829'>📡</tg-emoji> <b>Broadcasting...</b>\n\n"
                        f"<tg-emoji emoji-id='5103039000168367836'>👥</tg-emoji> Users: {success_users}/{total_users} sent\n"
                        f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Failed: {failed_users}",
                parse_mode='HTML'
                    )
                    
                await asyncio.sleep(0.05)
                
            except Exception as e:
                failed_users += 1
    
    if send_to_groups:
        all_groups = await group_user_totals_collection.distinct('group_id')
        total_groups = len(all_groups)
        
        for i, group_id in enumerate(all_groups):
            try:
                if not group_id:
                    continue
                    
                chat_id = int(group_id) if isinstance(group_id, str) else group_id
                    
                if is_reply:
                    await broadcast_message.copy(chat_id=chat_id)
                else:
                    await client.send_message(chat_id=chat_id, text=broadcast_text)
                    
                success_groups += 1
                
                if (i + 1) % 10 == 0:
                    await status_msg.edit_text(
                        f"<tg-emoji emoji-id='5103061849394382829'>📡</tg-emoji> <b>Broadcasting...</b>\n\n"
                        f"<tg-emoji emoji-id='5103039000168367836'>👥</tg-emoji> Users: {success_users} sent, {failed_users} failed\n"
                        f"<tg-emoji emoji-id='5102685219417229681'>💬</tg-emoji> Groups: {success_groups}/{total_groups} sent\n"
                        f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Failed: {failed_groups}",
                parse_mode='HTML'
                    )
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_groups += 1
    
    target_text = ""
    if send_to_users and send_to_groups:
        target_text = "users & groups"
    elif send_to_users:
        target_text = "users only"
    else:
        target_text = "groups only"
    
    await status_msg.edit_text(
        f"<tg-emoji emoji-id='5103087490349139576'>✅</tg-emoji> <b>Broadcast Complete!</b>\n\n"
        f"<tg-emoji emoji-id='5103061849394382829'>📢</tg-emoji> Target: {target_text}\n\n"
        f"<tg-emoji emoji-id='5103039000168367836'>👥</tg-emoji> <b>Users:</b>\n"
        f"   ✓ Sent: {success_users}\n"
        f"   ✗ Failed: {failed_users}\n\n"
        f"<tg-emoji emoji-id='5102685219417229681'>💬</tg-emoji> <b>Groups:</b>\n"
        f"   ✓ Sent: {success_groups}\n"
        f"   ✗ Failed: {failed_groups}\n\n"
        f"<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Total:</b> {success_users + success_groups} messages sent",
                parse_mode='HTML'
    )


async def broadcast_ptb(update: Update, context: CallbackContext) -> None:
    """PTB wrapper for broadcast command"""
    sender_id = update.effective_user.id
    
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await update.message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    args = context.args if context.args else []
    
    if not update.message.reply_to_message and len(args) < 1:
        await update.message.reply_text(
            "<tg-emoji emoji-id='5103061849394382829'>📢</tg-emoji> <b>Broadcast Command</b>\n\n"
            "<b>Usage:</b>\n"
            "<code>/broadcast [message]</code> - Send to all users & groups\n"
            "<code>/broadcast -users [message]</code> - Send to users only\n"
            "<code>/broadcast -groups [message]</code> - Send to groups only\n\n"
            "<b>Or:</b> Reply to any message with <code>/broadcast</code>\n\n"
            "<b>Example:</b>\n"
            "<code>/broadcast Hello everyone! New update is here!</code>",
            parse_mode='HTML'
        )
        return
    
    send_to_users = True
    send_to_groups = True
    
    if args and args[0] == "-users":
        send_to_groups = False
        args = args[1:]
    elif args and args[0] == "-groups":
        send_to_users = False
        args = args[1:]
    
    if update.message.reply_to_message:
        is_reply = True
        reply_msg = update.message.reply_to_message
    else:
        broadcast_text = " ".join(args)
        if not broadcast_text:
            await update.message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Please provide a message to broadcast!",
                parse_mode='HTML')
            return
        is_reply = False
    
    status_msg = await update.message.reply_text("<tg-emoji emoji-id='5103061849394382829'>📡</tg-emoji> Starting broadcast...",
                parse_mode='HTML')
    
    success_users = 0
    failed_users = 0
    success_groups = 0
    failed_groups = 0
    
    if send_to_users:
        all_users = await user_collection.find({}).to_list(length=None)
        total_users = len(all_users)
        
        for i, user in enumerate(all_users):
            try:
                user_id = user.get('id')
                if not user_id:
                    continue
                    
                if is_reply:
                    await reply_msg.copy(chat_id=user_id)
                else:
                    await context.bot.send_message(chat_id=user_id, text=broadcast_text)
                    
                success_users += 1
                
                if (i + 1) % 25 == 0:
                    await status_msg.edit_text(
                        f"<tg-emoji emoji-id='5103061849394382829'>📡</tg-emoji> <b>Broadcasting...</b>\n\n"
                        f"<tg-emoji emoji-id='5103039000168367836'>👥</tg-emoji> Users: {success_users}/{total_users} sent\n"
                        f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Failed: {failed_users}",
                        parse_mode='HTML'
                    )
                    
                await asyncio.sleep(0.05)
                
            except Exception as e:
                failed_users += 1
    
    if send_to_groups:
        all_groups = await group_user_totals_collection.distinct('group_id')
        total_groups = len(all_groups)
        
        for i, group_id in enumerate(all_groups):
            try:
                if not group_id:
                    continue
                    
                chat_id = int(group_id) if isinstance(group_id, str) else group_id
                    
                if is_reply:
                    await reply_msg.copy(chat_id=chat_id)
                else:
                    await context.bot.send_message(chat_id=chat_id, text=broadcast_text)
                    
                success_groups += 1
                
                if (i + 1) % 10 == 0:
                    await status_msg.edit_text(
                        f"<tg-emoji emoji-id='5103061849394382829'>📡</tg-emoji> <b>Broadcasting...</b>\n\n"
                        f"<tg-emoji emoji-id='5103039000168367836'>👥</tg-emoji> Users: {success_users} sent, {failed_users} failed\n"
                        f"<tg-emoji emoji-id='5102685219417229681'>💬</tg-emoji> Groups: {success_groups}/{total_groups} sent\n"
                        f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Failed: {failed_groups}",
                        parse_mode='HTML'
                    )
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                failed_groups += 1
    
    target_text = ""
    if send_to_users and send_to_groups:
        target_text = "users & groups"
    elif send_to_users:
        target_text = "users only"
    else:
        target_text = "groups only"
    
    await status_msg.edit_text(
        f"<tg-emoji emoji-id='5103087490349139576'>✅</tg-emoji> <b>Broadcast Complete!</b>\n\n"
        f"<tg-emoji emoji-id='5103061849394382829'>📢</tg-emoji> Target: {target_text}\n\n"
        f"<tg-emoji emoji-id='5103039000168367836'>👥</tg-emoji> <b>Users:</b>\n"
        f"   ✓ Sent: {success_users}\n"
        f"   ✗ Failed: {failed_users}\n\n"
        f"<tg-emoji emoji-id='5102685219417229681'>💬</tg-emoji> <b>Groups:</b>\n"
        f"   ✓ Sent: {success_groups}\n"
        f"   ✗ Failed: {failed_groups}\n\n"
        f"<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Total:</b> {success_users + success_groups} messages sent",
        parse_mode='HTML'
    )


# ============== BONK/UNBONK COMMANDS ==============

@shivuu.on_message(filters.command("bonk"))
async def bonk(client, message):
    """Ban a user from using the bot for 2 weeks (owner only)"""
    sender_id = message.from_user.id
    
    if sender_id != int(OWNER_ID):
        await message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to the bot owner.",
                parse_mode='HTML')
        return
    
    target_user = None
    target_id = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
    elif len(message.command) >= 2:
        try:
            target_id = int(message.command[1])
        except ValueError:
            await message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Invalid user ID!",
                parse_mode='HTML')
            return
    else:
        await message.reply_text(
            "🔨 <b>Bonk Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• Reply to a user's message with <code>/bonk</code>\n"
            "• Or use <code>/bonk [user_id]</code>\n\n"
            "This will ban the user from using the bot for 2 weeks.",
            parse_mode='HTML'
        )
        return
    
    if target_id == int(OWNER_ID):
        await message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> You can't bonk yourself!",
                parse_mode='HTML')
        return
    
    existing_ban = await banned_users_collection.find_one({'user_id': target_id})
    if existing_ban:
        unban_date = existing_ban.get('unban_date')
        remaining = unban_date - datetime.now()
        days = remaining.days
        await message.reply_text(
            f"<tg-emoji emoji-id='5102920111178647010'>⚠️</tg-emoji> User is already bonked!\n"
            f"<tg-emoji emoji-id='5102843841149405078'>🕐</tg-emoji> Remaining: {days} days",
                parse_mode='HTML'
        )
        return
    
    ban_date = datetime.now()
    unban_date = ban_date + timedelta(weeks=2)
    
    await banned_users_collection.insert_one({
        'user_id': target_id,
        'banned_by': sender_id,
        'ban_date': ban_date,
        'unban_date': unban_date,
        'reason': 'Spamming'
    })
    
    target_name = target_user.first_name if target_user else str(target_id)
    
    await message.reply_text(
        f"🔨 <b>BONK!</b>\n\n"
        f"<tg-emoji emoji-id='5102763490901231643'>👤</tg-emoji> <b>User:</b> {target_name} (<code>{target_id}</code>)\n"
        f"⏰ <b>Duration:</b> 2 weeks\n"
        f"<tg-emoji emoji-id='5102862902214265154'>📅</tg-emoji> <b>Unbanned on:</b> {unban_date.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"They won't be able to use the bot until then!",
        parse_mode='HTML'
    )


@shivuu.on_message(filters.command("unbonk"))
async def unbonk(client, message):
    """Unban a user from using the bot (owner only)"""
    sender_id = message.from_user.id
    
    if sender_id != int(OWNER_ID):
        await message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to the bot owner.",
                parse_mode='HTML')
        return
    
    target_user = None
    target_id = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
    elif len(message.command) >= 2:
        try:
            target_id = int(message.command[1])
        except ValueError:
            await message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Invalid user ID!",
                parse_mode='HTML')
            return
    else:
        await message.reply_text(
            "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji> <b>Unbonk Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• Reply to a user's message with <code>/unbonk</code>\n"
            "• Or use <code>/unbonk [user_id]</code>\n\n"
            "This will remove the ban and allow them to use the bot again.",
            parse_mode='HTML'
        )
        return
    
    existing_ban = await banned_users_collection.find_one({'user_id': target_id})
    if not existing_ban:
        await message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> This user is not bonked!",
                parse_mode='HTML')
        return
    
    await banned_users_collection.delete_one({'user_id': target_id})
    
    target_name = target_user.first_name if target_user else str(target_id)
    
    await message.reply_text(
        f"<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji> <b>UNBONKED!</b>\n\n"
        f"<tg-emoji emoji-id='5102763490901231643'>👤</tg-emoji> <b>User:</b> {target_name} (<code>{target_id}</code>)\n\n"
        f"They can now use the bot again!",
        parse_mode='HTML'
    )


async def bonk_ptb(update: Update, context: CallbackContext) -> None:
    """PTB wrapper for bonk command"""
    sender_id = update.effective_user.id
    
    if sender_id != int(OWNER_ID):
        await update.message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to the bot owner.",
                parse_mode='HTML')
        return
    
    target_user = None
    target_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args and len(context.args) >= 1:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Invalid user ID!",
                parse_mode='HTML')
            return
    else:
        await update.message.reply_text(
            "🔨 <b>Bonk Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• Reply to a user's message with <code>/bonk</code>\n"
            "• Or use <code>/bonk [user_id]</code>\n\n"
            "This will ban the user from using the bot for 2 weeks.",
            parse_mode='HTML'
        )
        return
    
    if target_id == int(OWNER_ID):
        await update.message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> You can't bonk yourself!",
                parse_mode='HTML')
        return
    
    existing_ban = await banned_users_collection.find_one({'user_id': target_id})
    if existing_ban:
        unban_date = existing_ban.get('unban_date')
        remaining = unban_date - datetime.now()
        days = remaining.days
        await update.message.reply_text(
            f"<tg-emoji emoji-id='5102920111178647010'>⚠️</tg-emoji> User is already bonked!\n"
            f"<tg-emoji emoji-id='5102843841149405078'>🕐</tg-emoji> Remaining: {days} days",
                parse_mode='HTML'
        )
        return
    
    ban_date = datetime.now()
    unban_date = ban_date + timedelta(weeks=2)
    
    await banned_users_collection.insert_one({
        'user_id': target_id,
        'banned_by': sender_id,
        'ban_date': ban_date,
        'unban_date': unban_date,
        'reason': 'Spamming'
    })
    
    target_name = target_user.first_name if target_user else str(target_id)
    
    await update.message.reply_text(
        f"🔨 <b>BONK!</b>\n\n"
        f"<tg-emoji emoji-id='5102763490901231643'>👤</tg-emoji> <b>User:</b> {target_name} (<code>{target_id}</code>)\n"
        f"⏰ <b>Duration:</b> 2 weeks\n"
        f"<tg-emoji emoji-id='5102862902214265154'>📅</tg-emoji> <b>Unbanned on:</b> {unban_date.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"They won't be able to use the bot until then!",
        parse_mode='HTML'
    )


async def unbonk_ptb(update: Update, context: CallbackContext) -> None:
    """PTB wrapper for unbonk command"""
    sender_id = update.effective_user.id
    
    if sender_id != int(OWNER_ID):
        await update.message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to the bot owner.",
                parse_mode='HTML')
        return
    
    target_user = None
    target_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args and len(context.args) >= 1:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Invalid user ID!",
                parse_mode='HTML')
            return
    else:
        await update.message.reply_text(
            "<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji> <b>Unbonk Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• Reply to a user's message with <code>/unbonk</code>\n"
            "• Or use <code>/unbonk [user_id]</code>\n\n"
            "This will remove the ban and allow them to use the bot again.",
            parse_mode='HTML'
        )
        return
    
    existing_ban = await banned_users_collection.find_one({'user_id': target_id})
    if not existing_ban:
        await update.message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> This user is not bonked!",
                parse_mode='HTML')
        return
    
    await banned_users_collection.delete_one({'user_id': target_id})
    
    target_name = target_user.first_name if target_user else str(target_id)
    
    await update.message.reply_text(
        f"<tg-emoji emoji-id='5102638339849192814'>✨</tg-emoji> <b>UNBONKED!</b>\n\n"
        f"<tg-emoji emoji-id='5102763490901231643'>👤</tg-emoji> <b>User:</b> {target_name} (<code>{target_id}</code>)\n\n"
        f"They can now use the bot again!",
        parse_mode='HTML'
    )


# Helper function to check if user is banned
async def check_ban(user_id: int):
    """Check if a user is banned and return ban info if so"""
    ban = await banned_users_collection.find_one({'user_id': user_id})
    if ban:
        unban_date = ban.get('unban_date')
        if datetime.now() >= unban_date:
            await banned_users_collection.delete_one({'user_id': user_id})
            return None
        remaining = unban_date - datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600
        return {'banned': True, 'days': days, 'hours': hours}
    return None


# ============== RESETM COMMAND ==============

@shivuu.on_message(filters.command("resetm"))
async def resetm(client, message):
    """Reset a user's daily marriage limit (sudo users only)"""
    sender_id = message.from_user.id
    
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    target_user = None
    target_id = None
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        target_id = target_user.id
    elif len(message.command) >= 2:
        try:
            target_id = int(message.command[1])
        except ValueError:
            await message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Invalid user ID!",
                parse_mode='HTML')
            return
    else:
        await message.reply_text(
            "<tg-emoji emoji-id='5102621864354645825'>💒</tg-emoji> <b>Reset Marriage Limit Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• Reply to a user's message with <code>/resetm</code>\n"
            "• Or use <code>/resetm [user_id]</code>\n\n"
            "This will reset their daily marriage limit to 0/30.",
            parse_mode='HTML'
        )
        return
    
    user = await user_collection.find_one({'id': target_id})
    if not user:
        await message.reply_text(f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> User ID <code>{target_id}</code> not found in database!",
                parse_mode='HTML')
        return
    
    await user_collection.update_one(
        {'id': target_id},
        {'$set': {'daily_marriages': {}}}
    )
    
    target_name = target_user.first_name if target_user else str(target_id)
    
    await message.reply_text(
        f"<tg-emoji emoji-id='5102621864354645825'>💒</tg-emoji> <b>Marriage Limit Reset!</b>\n\n"
        f"<tg-emoji emoji-id='5102763490901231643'>👤</tg-emoji> <b>User:</b> {target_name} (<code>{target_id}</code>)\n"
        f"<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Status:</b> Set to 0/30\n\n"
        f"They can now marry up to 30 characters again!",
        parse_mode='HTML'
    )


async def resetm_ptb(update: Update, context: CallbackContext) -> None:
    """PTB wrapper for resetm command"""
    sender_id = update.effective_user.id
    
    if str(sender_id) not in [str(u) for u in Config.sudo_users]:
        await update.message.reply_text("<tg-emoji emoji-id='5102920111178647010'>🚫</tg-emoji> This command is only available to administrators.",
                parse_mode='HTML')
        return
    
    target_user = None
    target_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_id = target_user.id
    elif context.args and len(context.args) >= 1:
        try:
            target_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> Invalid user ID!",
                parse_mode='HTML')
            return
    else:
        await update.message.reply_text(
            "<tg-emoji emoji-id='5102621864354645825'>💒</tg-emoji> <b>Reset Marriage Limit Command</b>\n\n"
            "<b>Usage:</b>\n"
            "• Reply to a user's message with <code>/resetm</code>\n"
            "• Or use <code>/resetm [user_id]</code>\n\n"
            "This will reset their daily marriage limit to 0/30.",
            parse_mode='HTML'
        )
        return
    
    user = await user_collection.find_one({'id': target_id})
    if not user:
        await update.message.reply_text(f"<tg-emoji emoji-id='5102962128843704400'>❌</tg-emoji> User ID <code>{target_id}</code> not found in database!",
                parse_mode='HTML')
        return
    
    await user_collection.update_one(
        {'id': target_id},
        {'$set': {'daily_marriages': {}}}
    )
    
    target_name = target_user.first_name if target_user else str(target_id)
    
    await update.message.reply_text(
        f"<tg-emoji emoji-id='5102621864354645825'>💒</tg-emoji> <b>Marriage Limit Reset!</b>\n\n"
        f"<tg-emoji emoji-id='5102763490901231643'>👤</tg-emoji> <b>User:</b> {target_name} (<code>{target_id}</code>)\n"
        f"<tg-emoji emoji-id='5102802918701008521'>📊</tg-emoji> <b>Status:</b> Set to 0/30\n\n"
        f"They can now marry up to 30 characters again!",
        parse_mode='HTML'
    )


# Register handlers
application.add_handler(CommandHandler("lockspawn", lockspawn_ptb, block=False))
application.add_handler(CommandHandler("unlockspawn", unlockspawn_ptb, block=False))
application.add_handler(CommandHandler("lockedspawns", lockedspawns_ptb, block=False))
application.add_handler(CommandHandler("rarity", rarity_ptb, block=False))
application.add_handler(CommandHandler("broadcast", broadcast_ptb, block=False))
application.add_handler(CommandHandler("bonk", bonk_ptb, block=False))
application.add_handler(CommandHandler("unbonk", unbonk_ptb, block=False))
application.add_handler(CommandHandler("resetm", resetm_ptb, block=False))
application.add_handler(CallbackQueryHandler(lockedspawns_callback_ptb, pattern="^lockedspawns:", block=False))

