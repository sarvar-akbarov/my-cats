# base requirements
import logging
import traceback
import platform
import time
import datetime
import os
import requests
import json

# telergam methods
from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler,
                          InlineQueryHandler, ChosenInlineResultHandler)
from telegram import InlineKeyboardButton, KeyboardButton, ChatAction
from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
from telegram import InputMediaPhoto

from users.users import Users

# confuguration
from config import (
    TOKEN, 
    APP_NAME, 
    API_KEY,

    STATE_MAIN, 
    # STATE_BREEDS,
    STATE_RANDOM,
    STATE_FAVOURITES,
    STATE_UPLOAD,
    # STATE_TYPE_IMAGE,
    # STATE_TYPE_GIF,

    # BTN_BREEDS,
    BTN_RANDOM,
    BTN_FAVOURITES,
    # BTN_UPLOAD,
    # BTN_TYPE_IMAGE,
    # BTN_TYPE_GIF,

)


def main_btns():
    return [
        [
            # KeyboardButton(BTN_BREEDS),
            KeyboardButton(BTN_RANDOM),
        ],
        [
            KeyboardButton(BTN_FAVOURITES),
        ],
        # [
        #     KeyboardButton(BTN_UPLOAD),
        # ]
    ]

def get_random():
    url = 'https://api.thecatapi.com/v1/images/search'
    response = requests.get(
        url = url, 
        headers={'x-api-key': API_KEY}
    )
    data = response.json()
    return data

def add_favourites(user_id,image_id):
    url = 'https://api.thecatapi.com/v1/favourites'
    headers = {
        'content-type': "application/json",
        'x-api-key': API_KEY
    }
    payload = "{\"image_id\":\"" + image_id + "\",\"sub_id\":\"user-"+str(user_id)+"\"}"
    response = requests.post(
        url = url, 
        data=payload,
        headers=headers
    )
    # print(response.json())
    if response.status_code == 200:
        get_favourites(user_id,0,True)
        return True
    else:
        return False


def get_favourites(user_id,id=0,refresh=False):
    filename = 'datas/{}-favourites.json'.format(str(user_id))
    if os.path.isfile(filename) and not refresh:
        with open(filename) as f:
            data = json.load(f)
    else:
        response = requests.get(
            url='https://api.thecatapi.com/v1/favourites', 
            params={'sub_id' :'user-'+str(user_id)},
            headers={'x-api-key': API_KEY}
        )
        with open(filename, 'wb') as outf:
            outf.write(response.content)
        data = response.json()

    
    return {
        'favourite':data[id],
        'count': len(data)
    }


def start(update, context):
    # print('start')
    try:
        from_user = update.message.from_user
        user = Users(from_user.id)
        if not user.joined():
            user.write(user.template(from_user))
        update.message.reply_html(
            'Hey buddy!', 
            reply_markup=ReplyKeyboardMarkup(
                main_btns(), 
                resize_keyboard=True, 
                one_time_keyboard=True
            )
        )
        return STATE_MAIN
    except Exception as e:
        print(traceback.format_exc())

def choose_menu(update, context):
    # print('choose_menu')
    try:
        if update.callback_query is not None:
            query = update.callback_query
            data = query.data
            split = data.split('-')
            from_user = update.callback_query.message.chat
            if split[0] == 'heart':
                result = add_favourites(from_user.id, split[1])
                if result:
                    query.answer(text="Added ❤️")
                else:
                    query.answer(text="Seems you have already added it.")
            elif split[0] == 'unheart':
                query.answer(text="Not Allowed this action, bcz they all are cute and favourite ❤️", show_alert=True)
            elif split[0] == 'nf':
                id = int(split[1])
                # print(id)
                favourite_info = get_favourites(from_user.id,id)
                count = favourite_info['count']
                favourite = favourite_info['favourite']
                buttons = []
                if id > 0:
                    buttons.append(InlineKeyboardButton('prev', callback_data='nf-'+str(id-1)))
                buttons.append(InlineKeyboardButton('💔', callback_data='unheart'))
                if id < count - 1:
                    buttons.append(InlineKeyboardButton('next', callback_data='nf-'+str(id+1)))
                query.message.edit_media(
                    media=InputMediaPhoto(
                        media=favourite['image']['url'],
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            buttons
                        ]
                    )
                )
            query.answer()

        elif update.message.text is not None and update.message.text in [BTN_FAVOURITES,BTN_RANDOM]:
            from_user = update.message.from_user
            user = Users(from_user.id)
            if update.message.text == BTN_RANDOM:
                random = get_random()[0]
                # print(random)
                button = InlineKeyboardButton('❤️', callback_data='heart-'+str(random['id']))
                update.message.reply_photo(
                    random['url'], 
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                               button
                            ]
                        ]
                    )
                )
            if update.message.text == BTN_FAVOURITES:
                favourite_info = get_favourites(from_user.id)
                count = favourite_info['count']
                favourite = favourite_info['favourite']
                buttons = []
                # print(favourite)
                if count == 0:
                    update.message.reply_html('You favourites list still empty')
                else:
                    buttons.append(InlineKeyboardButton('💔', callback_data='unheart-'+str(favourite['image_id'])))
                    if count > 0:
                        buttons.append(InlineKeyboardButton('next', callback_data='nf-1'))
                    update.message.reply_photo(
                        favourite['image']['url'], 
                        reply_markup=InlineKeyboardMarkup(
                            [
                            buttons
                            ]
                        )
                    )
        else:
            update.message.reply_html(
                'Just choose one below)', 
                reply_markup=ReplyKeyboardMarkup(
                    main_btns(), 
                    resize_keyboard=True, 
                    one_time_keyboard=True
                )
            )
    except Exception as e:
        print(traceback.format_exc())

def main():
    '''
        start - Start the bot
        home - HOME
        random - Get Random Image
        favourites - Favourites
 
        breeds - Breeds
        random - Get Random Image
        favourites - Favourites
        upload - Upload Your Own
    '''
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start',start), 
        ],
        states={
            STATE_MAIN: [
                CommandHandler('start',start),
                CommandHandler('home',start),
                CommandHandler('random',choose_menu),
                CommandHandler('favourites',choose_menu),
                MessageHandler(Filters.all, choose_menu), 
                CallbackQueryHandler(choose_menu), 
            ],
        },
        fallbacks=[CommandHandler('start', start)],
        run_async = True
    )

    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(conversation_handler)
    updater.start_polling(drop_pending_updates=True)
    updater.idle()

if __name__ == '__main__':
    main()
