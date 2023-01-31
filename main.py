import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
import event
import local_secret

TOKEN = local_secret.TODO_LISTS_BOT_TOKEN

bot = AsyncTeleBot(TOKEN)
print('Ready.')

def markup(lang:str='en') -> telebot.types.InlineKeyboardMarkup:
    m = telebot.types.InlineKeyboardMarkup()
    if lang == 'en':
        m.add(telebot.types.InlineKeyboardButton('Try it', switch_inline_query_current_chat=''), telebot.types.InlineKeyboardButton('Create a to-do', url='t.me/arielstodolistsbot'))
    elif lang == 'zh':
        m.add(telebot.types.InlineKeyboardButton('我也试试', switch_inline_query_current_chat=''), telebot.types.InlineKeyboardButton('创建一个待办', url='t.me/arielstodolistsbot'))
    return m

@bot.message_handler()
async def reply(message: telebot.types.Message) -> int:
    if not message.text.split(' ', 1)[0].startswith('/'):
        # await bot.reply_to(message, 'This is not a valid request. Try something within the command list or see /help')
        return 0
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
            await bot.reply_to(message, event.help(), parse_mode='html')
        elif cmd == '/register':
            if arg == '':
                await bot.reply_to(message, event.register(message.from_user.id))
            else:
                await bot.reply_to(message, 'You cannot create a list for another user.')
        elif cmd == '/get':
            await bot.reply_to(message, event.get(message.from_user.id, arg), parse_mode='html')
            return 0
        elif cmd == '/mark':
            await bot.reply_to(message, event.mark(message.from_user.id, arg), parse_mode='html')
        elif cmd == '/add':
            await bot.reply_to(message, event.add(message.from_user.id, arg), parse_mode='html')
        elif cmd == '/del':
            await bot.reply_to(message, event.delete(message.from_user.id, arg), parse_mode='html')
        elif cmd == '/tag':
            await bot.reply_to(message, event.tag(message.from_user.id, arg), parse_mode='html')
        elif cmd == '/clear':
            await bot.reply_to(message, event.clear(message.from_user.id, arg), parse_mode='html')
        elif cmd == '/complete':
            await bot.reply_to(message, event.complete(message.from_user.id, arg), parse_mode='html')
        elif cmd == '/new_list':
            await bot.reply_to(message, event.newList(message.from_user.id, arg), parse_mode='html')
        else:
            # await bot.reply_to(message, 'This is not a valid request. Try something within the command list or see /help')
            return 0

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

if __name__ == '__main__':
    asyncio.run(bot.polling(non_stop=True, timeout=180))