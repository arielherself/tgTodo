import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot
import event
import local_secret

TOKEN = local_secret.TODO_LISTS_BOT_TOKEN

bot = AsyncTeleBot(TOKEN)
print('Ready.')

@bot.message_handler()
async def reply(message: telebot.types.Message) -> int:
    if not message.text.split(' ', 1)[0].startswith('/'):
        await bot.reply_to(message, 'This is not a valid request. Try something within the command list or see /help')
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
            if arg == '':
                await bot.reply_to(message, event.get(message.from_user.id), parse_mode='html')
            else:
                await bot.reply_to(message, event.get(arg), parse_mode='html')
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
        else:
            await bot.reply_to(message, 'This is not a valid request. Try something within the command list or see /help')

if __name__ == '__main__':
    asyncio.run(bot.polling(non_stop=True, timeout=180))