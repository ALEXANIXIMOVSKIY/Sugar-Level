from aiogram import types
from dispatcher import dp
import config
import re
from bot import BotDB

@dp.message_handler(commands = "start")
async def start(message: types.Message):
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)

    await message.bot.send_message(message.from_user.id,
        '''Добро пожаловать! Данный бот поможет Вам 
    синхронизировать данные о времени приема пищи,
    результат измерения уровня глюкозы.
    Для ввода времени приема пищы введите /п пробел время,
    ввода результата /р пробел показание,
    вывода отчета -- /о.''')

@dp.message_handler(commands = ("пища", "результат", "п", "р"), commands_prefix = "/")
async def start(message: types.Message):
    cmd_variants = (('/пища', '/п'), ('/результат', '/р'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'

    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if(len(value)):
        x = re.findall(r"\d+(?:.\d+)?", value)
        if(len(x)):
            value = float(x[0].replace(',', '.'))

            BotDB.add_record(message.from_user.id, operation, value)

            if(operation == '-'):
                await message.reply("✅ Запись о <u><b>приеме пищы</b></u> успешно внесена!")
            else:
                await message.reply("✅ Ваш <u><b>результат</b></u> успешно внесен!")
        else:
            await message.reply("Не удалось определить значение глюкозы!")
    else:
        await message.reply("Не введен результат глюкозы!")

@dp.message_handler(commands = ("отчет", "о"), commands_prefix = "/")
async def start(message: types.Message):
    cmd_variants = ('/отчет', '/о')
    within_als = {
        "day": ('today', 'day', 'сегодня', 'день'),
        "month": ('month', 'месяц'),
        "year": ('year', 'год'),
    }

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = 'day'
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if(als == cmd):
                    within = k

    records = BotDB.get_records(message.from_user.id, within)

    if(len(records)):
        answer = f"🕘 Отчет о ваших измерениях за {within_als[within][-1]}\n\n"

        for r in records:
            answer += "<b>" + (" Прием пищи" if not r[2] else "Результат") + "</b>"
            answer += f" - {r[3]}"
            answer += f" <i>({r[4]})</i>\n"

        await message.reply(answer)
    else:
        await message.reply("Записей не обнаружено!")