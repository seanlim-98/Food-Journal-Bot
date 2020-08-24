import telebot
from telebot import types
import time
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, RegexHandler, Filters, PicklePersistence
ADD, RATE, ADD_PROMPT = range(3)

bot_token = '1124420900:AAEDfPtcTM6i_2nXrkVg1G0RPXFTAguntrM'
persistence = PicklePersistence(filename = 'bot_data', store_user_data = True, store_bot_data = True, single_file = True)

def hello(update, context):
    reply = update.message.from_user.first_name
    update.message.reply_text('Hello {}'.format(reply))
    return ADD_PROMPT

updater = Updater(token=bot_token, persistence=persistence, use_context=True)
updater.dispatcher.add_handler(CommandHandler('hello', hello))
dispatcher = updater.dispatcher

# Callback functions
def add_prompt(update,context):
    update.message.reply_text('Type in the name of the restaurant you want to record.')
    return ADD

# Add a visited food place to your journal
def add_place(update, context):
    place = {}
    place['name'] = update.message.text
    place['rating'] = 0.0

    if ('visited' not in context.user_data):
        context.user_data['visited'] = []

    if (any(x['name'] == place['name'] for x in context.user_data['visited'])):
        for loc in context.user_data['visited']:
            if (loc['name'] == place['name']):
                loc['num_visits'] += 1
        update.message.reply_text('Visit added for ' + place['name'] + '.')
    else:
        place['num_visits'] = 1
        context.user_data['visited'].append(place)
        update.message.reply_text('Added ' + place['name'] + ' to your journal.')

    update.message.reply_text('Add a rating with the following syntax: /rate <place> <rating>')
    return ConversationHandler.END

# Rate place
def rate_place(update, context):
    rating = update.message.text.split(' ')[-1]
    place = ' '.join(update.message.text.split(' ')[1:-1])

    if (not any(x['name'] == place for x in context.user_data['visited'])):
        update.message.reply_text(place + ' is not your journal.')
    else:
        rate_index(update, context, place, rating)

# Helper function that finds place in database to update data
def rate_index(update, context, target, rating):
    for data in context.user_data['visited']:
        if (data['name']==target):
            if (data['rating'] != 0.0):
                data['rating'] = (float(data['rating']) + float(rating)) / data['num_visits'] # average ratings
            else:
                data['rating'] = rating
        else:
            continue
    update.message.reply_text('Rating recorded!')

# Return your rating of a visited food place
def eval_place(update, context):
    place = update.message.text.split(' ')[1]
    if (not any(x['name'] == place for x in context.user_data['visited'])):
        update.message.reply_text(place + ' is not in your journal.')
    else:
        for places in context.user_data['visited']:
            if (places['name'] == place):
                update.message.reply_text(place + ' has a rating of ' + places['rating'])

# Reset your database
def reset_database(update, context):
    context.user_data['visited'] = []

# List of all the places you've visited before
def list_places(update, context):
    output = ''
    if (len(context.user_data['visited']) == 0 or 'visited' not in context.user_data):
        output = 'N/A'
    else:
        for place in context.user_data['visited']:
            result = place['name']
            output += result
            output += '\n'
    update.message.reply_text('List of places visited: ' + output)

# Return sorted list of places (descending order)
def sort_list_places(update, context):
    output = ''
    if (len(context.user_data['visited']) == 0 or 'visited' not in context.user_data):
        output = 'N/A'
    else:
        newlist = sorted(context.user_data['visited'], key = lambda x: float(x['rating']), reverse=True)
        for place in newlist[:5]:
            result = place['name'] + ' ' + str(place['rating']) + '/10'
            output += result
            output += '\n'
    update.message.reply_text('Top 5 Rated Places (Average Ratings):\n' + output)

# Most visited Places
def sort_num_visit(update, context):
    output = ''
    if (len(context.user_data['visited']) == 0 or 'visited' not in context.user_data):
        output = 'N/A'
    else:
        newlist = sorted(context.user_data['visited'], key = lambda x: int(x['num_visits']), reverse=True)
        for place in newlist[:5]:
            result = place['name'] + ' - No. of Visits: ' + str(place['num_visits'])
            output += result
            output += '\n'
    update.message.reply_text('Top 5 Most Visited Places:\n' + output)

# Handle commands
rating_handler = CommandHandler('rate',rate_place)
dispatcher.add_handler(rating_handler)

find_rating_handler = CommandHandler('eval', eval_place)
dispatcher.add_handler(find_rating_handler)

reset_handler = CommandHandler('reset',reset_database)
dispatcher.add_handler(reset_handler)

list_handler = CommandHandler('list', list_places)
dispatcher.add_handler(list_handler)

sorted_list_handler = CommandHandler('sort_rating', sort_list_places)
dispatcher.add_handler(sorted_list_handler)

sorted_visit_handler = CommandHandler('sort_visited', sort_num_visit)
dispatcher.add_handler(sorted_visit_handler)

conv_handler = ConversationHandler(
    entry_points = [CommandHandler('start', hello), CommandHandler('add', add_prompt)],

    states = {
        ADD_PROMPT: [MessageHandler(Filters.text, add_prompt)],
        ADD: [MessageHandler(Filters.text, add_place)],
        RATE: [MessageHandler(Filters.text, rate_place)]
    },

    fallbacks = []
)

updater.dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()
