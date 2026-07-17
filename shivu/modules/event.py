from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from shivu import application, sudo_users, event_settings_collection, collection
from datetime import datetime

async def startevent(update: Update, context: CallbackContext) -> None:
    """Start the Christmas event - only <tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> characters will spawn"""
    if not update.effective_user or not update.message:
        return
    
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('<tg-emoji emoji-id="5102581715000362771">🤩</tg-emoji> You do not have permission to use this command.')
        return
    
    try:
        christmas_count = await collection.count_documents({'name': {'$regex': '🎄'}})
        
        if christmas_count == 0:
            await update.message.reply_text(
                '<tg-emoji emoji-id="5102920111178647010">🤩</tg-emoji> <b>Cannot start Christmas event!</b>\n\n'
                'No characters with <tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> in their name found in the database.\n\n'
                'Please upload some Christmas-themed characters first using:\n'
                '<code>/upload [url] Character-Name-<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> Anime-Name [rarity]</code>',
                parse_mode='HTML'
            )
            return
        
        existing_event = await event_settings_collection.find_one({'active': True})
        if existing_event:
            await update.message.reply_text(
                f'<tg-emoji emoji-id="5102920111178647010">🤩</tg-emoji> <b>Event already active!</b>\n\n'
                f'<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> Event Type: {existing_event.get("event_type", "unknown").title()}\n'
                f'<tg-emoji emoji-id="5102650803844286939">🔎</tg-emoji> Started: {existing_event.get("started_at", "Unknown")}\n'
                f'<tg-emoji emoji-id="5103039000168367836">👥</tg-emoji> Started by: {existing_event.get("started_by_name", "Unknown")}\n\n'
                f'Use /endevent to end the current event first.',
                parse_mode='HTML'
            )
            return
        
        event_data = {
            'event_type': 'christmas',
            'active': True,
            'started_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'started_by': update.effective_user.id,
            'started_by_name': update.effective_user.first_name,
            'filter_emoji': '<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji>'
        }
        
        await event_settings_collection.insert_one(event_data)
        
        await update.message.reply_text(
            '<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji><tg-emoji emoji-id="5102825501639050967">🌟</tg-emoji> <b>CHRISTMAS EVENT STARTED!</b> <tg-emoji emoji-id="5102825501639050967">🌟</tg-emoji><tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji>\n\n'
            '━━━━━━━━━━━━━━━━━━━━\n'
            '<tg-emoji emoji-id="5103013135875312074">🎌</tg-emoji> Ho ho ho! The Christmas event is now active!\n\n'
            f'<tg-emoji emoji-id="5103000796434270751">🎬</tg-emoji> <b>Available Christmas Cards:</b> {christmas_count}\n'
            '<tg-emoji emoji-id="5103065598900831870">🤩</tg-emoji> Only characters with <tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> in their name will spawn!\n'
            '━━━━━━━━━━━━━━━━━━━━\n\n'
            f'<tg-emoji emoji-id="5103039000168367836">👥</tg-emoji> <b>Started by:</b> {update.effective_user.first_name}\n\n'
            '<tg-emoji emoji-id="5102736905053669429">❄️</tg-emoji> Use /endevent to end the Christmas event.',
            parse_mode='HTML'
        )
        
    except Exception as e:
        await update.message.reply_text(f'<tg-emoji emoji-id="5102920111178647010">🤩</tg-emoji> Error starting event: {str(e)}')

async def endevent(update: Update, context: CallbackContext) -> None:
    """End the current active event"""
    if not update.effective_user or not update.message:
        return
    
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('<tg-emoji emoji-id="5102581715000362771">🤩</tg-emoji> You do not have permission to use this command.')
        return
    
    try:
        active_event = await event_settings_collection.find_one({'active': True})
        
        if not active_event:
            await update.message.reply_text(
                '<tg-emoji emoji-id="5102920111178647010">🤩</tg-emoji> <b>No active event!</b>\n\n'
                'There is no event currently running.\n'
                'Use /startevent to start the Christmas event.',
                parse_mode='HTML'
            )
            return
        
        await event_settings_collection.update_one(
            {'_id': active_event['_id']},
            {'$set': {
                'active': False,
                'ended_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ended_by': update.effective_user.id,
                'ended_by_name': update.effective_user.first_name
            }}
        )
        
        event_type = active_event.get('event_type', 'unknown')
        
        if event_type == 'christmas':
            await update.message.reply_text(
                '<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> <b>CHRISTMAS EVENT ENDED!</b> <tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji>\n\n'
                '━━━━━━━━━━━━━━━━━━━━\n'
                '<tg-emoji emoji-id="5102630299670415053">💎</tg-emoji> The Christmas event has ended!\n\n'
                '<tg-emoji emoji-id="5102912496201631597">🎮</tg-emoji> Normal character spawning has resumed.\n'
                'All characters can now spawn again!\n'
                '━━━━━━━━━━━━━━━━━━━━\n\n'
                f'<tg-emoji emoji-id="5103039000168367836">👥</tg-emoji> <b>Ended by:</b> {update.effective_user.first_name}\n\n'
                '<tg-emoji emoji-id="5103065598900831870">🤩</tg-emoji> Thanks for participating in the event!',
                parse_mode='HTML'
            )
        else:
            await update.message.reply_text(
                f'<tg-emoji emoji-id="5102962128843704400">🤩</tg-emoji> <b>Event Ended!</b>\n\n'
                f'Event type: {event_type.title()}\n'
                f'Ended by: {update.effective_user.first_name}\n\n'
                'Normal spawning has resumed.',
                parse_mode='HTML'
            )
        
    except Exception as e:
        await update.message.reply_text(f'<tg-emoji emoji-id="5102920111178647010">🤩</tg-emoji> Error ending event: {str(e)}')

async def eventstatus(update: Update, context: CallbackContext) -> None:
    """Check current event status"""
    if not update.effective_user or not update.message:
        return
    
    try:
        active_event = await event_settings_collection.find_one({'active': True})
        
        if active_event:
            event_type = active_event.get('event_type', 'unknown')
            filter_emoji = active_event.get('filter_emoji', '')
            
            if event_type == 'christmas':
                christmas_count = await collection.count_documents({'name': {'$regex': '🎄'}})
                
                await update.message.reply_text(
                    '<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji><tg-emoji emoji-id="5102825501639050967">🌟</tg-emoji> <b>CHRISTMAS EVENT ACTIVE!</b> <tg-emoji emoji-id="5102825501639050967">🌟</tg-emoji><tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji>\n\n'
                    '━━━━━━━━━━━━━━━━━━━━\n'
                    f'<tg-emoji emoji-id="5103000796434270751">🎬</tg-emoji> <b>Available Cards:</b> {christmas_count}\n'
                    f'<tg-emoji emoji-id="5102913368079992686">🎰</tg-emoji> <b>Filter:</b> Characters with {filter_emoji}\n'
                    f'<tg-emoji emoji-id="5102650803844286939">🔎</tg-emoji> <b>Started:</b> {active_event.get("started_at", "Unknown")}\n'
                    f'<tg-emoji emoji-id="5103039000168367836">👥</tg-emoji> <b>Started by:</b> {active_event.get("started_by_name", "Unknown")}\n'
                    '━━━━━━━━━━━━━━━━━━━━\n\n'
                    '<tg-emoji emoji-id="5102736905053669429">❄️</tg-emoji> Only Christmas-themed cards are spawning!',
                    parse_mode='HTML'
                )
            else:
                await update.message.reply_text(
                    f'<tg-emoji emoji-id="5103027133173731788">🤩</tg-emoji> <b>Event Active!</b>\n\n'
                    f'Type: {event_type.title()}\n'
                    f'Started: {active_event.get("started_at", "Unknown")}\n'
                    f'By: {active_event.get("started_by_name", "Unknown")}',
                    parse_mode='HTML'
                )
        else:
            await update.message.reply_text(
                '<tg-emoji emoji-id="5102882435725527517">🤩</tg-emoji> <b>No Active Event</b>\n\n'
                'There is no event currently running.\n'
                'Normal character spawning is active.\n\n'
                '<tg-emoji emoji-id="5102852035947005651">🤩</tg-emoji> Admins can use /startevent to start the Christmas event!',
                parse_mode='HTML'
            )
        
    except Exception as e:
        await update.message.reply_text(f'<tg-emoji emoji-id="5102920111178647010">🤩</tg-emoji> Error checking event: {str(e)}')

STARTEVENT_HANDLER = CommandHandler('startevent', startevent, block=False)
application.add_handler(STARTEVENT_HANDLER)
ENDEVENT_HANDLER = CommandHandler('endevent', endevent, block=False)
application.add_handler(ENDEVENT_HANDLER)
EVENTSTATUS_HANDLER = CommandHandler('eventstatus', eventstatus, block=False)
application.add_handler(EVENTSTATUS_HANDLER)
