import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
import event
import local_secret

TOKEN = local_secret.TODO_LISTS_BOT_TOKEN

bot = AsyncTeleBot(TOKEN)
recycleBin:list = []
print('Ready.')

def markup(lang:str='en') -> telebot.types.InlineKeyboardMarkup:
    m = telebot.types.InlineKeyboardMarkup()
    if lang == 'en':
        m.add(telebot.types.InlineKeyboardButton('Try it', switch_inline_query_current_chat=''), telebot.types.InlineKeyboardButton('Create a to-do', url='t.me/arielstodolistsbot'))
    elif lang == 'zh':
        m.add(telebot.types.InlineKeyboardButton('我也试试', switch_inline_query_current_chat=''), telebot.types.InlineKeyboardButton('创建一个待办', url='t.me/arielstodolistsbot'))
    return m

def multipleMarkup(listNamesArg: str, chatID: int, messageID: int, userID: int) -> telebot.types.InlineKeyboardMarkup:
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton('Update', callback_data=f'{chatID} {messageID} {userID} update {listNamesArg}'),
            telebot.types.InlineKeyboardButton('Close', callback_data=f'{chatID} {messageID} {userID} close'))
    return m

def closeMarkup(chatID: int, messageID: int, userID: int) -> telebot.types.InlineKeyboardMarkup:
    m = telebot.types.InlineKeyboardMarkup()
    m.add(telebot.types.InlineKeyboardButton('Close', callback_data=f'{chatID} {messageID} {userID} close'))
    return m

@bot.message_handler()
async def reply(message: telebot.types.Message) -> int:
    global recycleBin
    r = None
    f = False
    flag = False
    if not message.text.split(' ', 1)[0].startswith('/'):
        # await bot.reply_to(message, 'This is not a valid request. Try something within the command list or see /help')
        f = True
    else:
        l = message.text.split(' ', 1)
        if len(l) == 1:
            cmd = l[0]
            arg = ''
        else:
            cmd, arg = l
        if '@' in cmd:
            cmd = cmd[:cmd.find('@')]

        if cmd in ['/start', '/help']:
            r = await bot.reply_to(message, event.help(), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/register':
            if arg == '':
                r = await bot.reply_to(message, event.register(message.from_user.id), reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
            else:
                r = await bot.reply_to(message, 'You cannot create a list for another user.', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/get':
            flag = True
            f = True
            r = await bot.reply_to(message, event.get(message.from_user.id, arg), parse_mode='html', reply_markup=multipleMarkup(arg, message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/mark':
            r = await bot.reply_to(message, event.mark(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/add':
            r = await bot.reply_to(message, event.add(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/del':
            r = await bot.reply_to(message, event.delete(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/tag':
            r = await bot.reply_to(message, event.tag(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/clear':
            r = await bot.reply_to(message, event.clear(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/complete':
            r = await bot.reply_to(message, event.complete(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/new_list':
            r = await bot.reply_to(message, event.newList(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        elif cmd == '/del_list':
            r = await bot.reply_to(message, event.delList(message.from_user.id, arg), parse_mode='html', reply_markup=closeMarkup(message.chat.id, message.message_id, message.from_user.id))
        else:
            # await bot.reply_to(message, 'This is not a valid request. Try something within the command list or see /help')
            f = True
    await asyncio.sleep(10)
    if r != None and (not flag):
        recycleBin.append(r)
    if not f:
        recycleBin.append(message)

@bot.inline_handler(lambda _: True)
async def inline_reply(inline_query: telebot.types.InlineQuery):
    try:
        r1text = event.checkin(inline_query.from_user.id, inline_query.query, 'en')
        r2text = event.checkin(inline_query.from_user.id, inline_query.query, 'zh')
        r1 = telebot.types.InlineQueryResultArticle('1', 'English', telebot.types.InputTextMessageContent(r1text, 'html'), description='Generate an English check-in message', reply_markup=markup('en'))
        r2 = telebot.types.InlineQueryResultArticle('2', '中文', telebot.types.InputTextMessageContent(r2text, 'html'), description='生成中文打卡消息', reply_markup=markup('zh'))
        await bot.answer_inline_query(str(inline_query.id), [r1, r2])
    except Exception as e:
        print(f'Error when handling an inline request from {str(inline_query.from_user.id)}: {e}')

@bot.callback_query_handler(lambda _: True)
async def delete_on_callback(callback_query: telebot.types.CallbackQuery):
    try:
        chatID1, messageID1, userID, operation = callback_query.data.split(' ', 3)
        chatID2, messageID2 = callback_query.message.chat.id, callback_query.message.message_id
        if operation == 'close':
            await bot.delete_message(int(chatID1), int(messageID1))
            await bot.delete_message(int(chatID2), int(messageID2))
        elif operation.startswith('update '):
            await bot.edit_message_text(event.get(userID, operation[7:]), chatID2, messageID2, parse_mode='html', reply_markup=multipleMarkup(operation[7:], int(chatID1), int(messageID1), int(userID)))
    except Exception as e:
        print(f'Error when handling a "close" request: {e}')

async def autodel():
    global recycleBin
    while True:
        try:
            for each in recycleBin:
                await bot.delete_message(each.chat.id, each.message_id)
                recycleBin.remove(each)
            await asyncio.sleep(10)
        except:
            pass

async def main():
    t1 = asyncio.create_task(bot.polling(non_stop=True, timeout=180))
    t2 = asyncio.create_task(autodel())
    await t1
    await t2

if __name__ == '__main__':
    asyncio.run(main())