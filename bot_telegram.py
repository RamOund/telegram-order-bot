import re
import pymysql
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import os

host = '31.31.196.85'
user = 'u1971860_default'
password = '86KjTxZ3kZ9tWZcb'
db_name = 'u1971860_default'

try:
    connection = pymysql.connect(
        host=host,
        port=3306,
        user=user,
        password=password,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor
    )
    print('Подключение успешно')
except Exception as ex:
    print('Подключение не удалось')
    print(ex)


class FSMClient(StatesGroup):
    # Хранит этапы диалога с клиентом
    start_order_selected = State()
    name_select = State()
    teleph_num_select = State()
    email_select = State()
    address_select = State()
    answ_client_select = State()
    prod_select = State()
    amount_prod = State()
    all_selected = State()

# bot = Bot(token=os.getenv('TOKEN'))
bot = Bot(token='5649931003:bottoken')

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def on_startup(_):
    print('Бот работает')

# async def on_shutdown(dp):
#     await bot.delete_webhook()

@dp.message_handler(commands=['site'])
async def site(message: types.Message):
    await message.answer('Вот ссылка на наш сайт - http://test.site/')

@dp.message_handler(commands=['start'])
async def start_step(message: types.Message, state: FSMContext) -> None:
    msg = 'Привет, я бот для оформления заказа в компанию. Если уже определился, тогда напиши "Да", чтобы продолжить.'

    y_btn = KeyboardButton('Да')
    n_btn = KeyboardButton('Нет')

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(y_btn,n_btn)

    await message.answer(msg, reply_markup=markup)
    await state.set_state(FSMClient.start_order_selected)

@dp.message_handler(state=FSMClient.start_order_selected)
async def first_step(message: types.Message, state:FSMContext):
    user_msg = message.text
    tg_user_id = message.from_user.id
    if user_msg == 'Да':
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `client` WHERE tg_id_client='{tg_user_id}'")
            result = cursor.fetchone()
            connection.commit()
            if result is None:
                await message.answer('Хорошо, тогда напиши свое ФИО на русском языке, на которое будет оформляться заказ. Например:"Фамилия Имя Отчество", если у вас нету отчества, то вместо него напишите Нет, к примеру: "Фамилия Имя Нет".')
                await state.update_data(tg_u_id=tg_user_id)
                await state.set_state(FSMClient.name_select)
            else:
                with connection.cursor() as cursor:
                    surname = f"SELECT surname FROM `client` WHERE tg_id_client='{tg_user_id}'"
                    cursor.execute(surname)
                    surname = cursor.fetchone()['surname']
                with connection.cursor() as cursor:
                    name = f"SELECT name from `client` WHERE tg_id_client='{tg_user_id}'"
                    cursor.execute(name)
                    name=cursor.fetchone()['name']
                with connection.cursor() as cursor:
                    pathonimic = f"SELECT pathonimic from `client` WHERE tg_id_client='{tg_user_id}'"
                    cursor.execute(pathonimic)
                    pathonimic=cursor.fetchone()['pathonimic']
                with connection.cursor() as cursor:
                    mob_num = f"select tel_num from `client` where tg_id_client='{tg_user_id}'"
                    cursor.execute(mob_num)
                    mob_num=cursor.fetchone()['tel_num']
                with connection.cursor() as cursor:
                    email = f"select email from `client` where tg_id_client='{tg_user_id}'"
                    cursor.execute(email)
                    email=cursor.fetchone()['email']
                fullname = surname + ' ' + name + ' ' + pathonimic
                await state.update_data(tg_u_id=tg_user_id)
                await state.update_data(name=fullname)
                await state.update_data(telephon_num=mob_num)
                await state.update_data(email=email)
                await message.answer(f'Вы уже были нашим клиентом, благодаря этому вы уже находитесь в нашей клиентской базе.\nВаше ФИО: {fullname}\nВаш номер телефона: {mob_num}\nВаша электронная почта: {email}\nТеперь напишите адрес на котором должна будут проводится работы по заказу. Формат адреса: Город, Улица, Дом и т.д.')
                await state.set_state(FSMClient.address_select)
    elif user_msg =='Нет':
        await message.answer('😭До свидания😭')
        await state.finish()

@dp.message_handler(state=FSMClient.name_select)
async def second_step(message: types.Message, state:FSMContext):
    user_msg = message.text
    if user_msg.count(' ') == 2:
        spl = user_msg.split()
        name = spl[1]
        await state.update_data(name=user_msg)
        await message.answer(f'Хорошо, {name}, продолжим оформление заказа. Теперь напишите свой номер телефона для того, чтобы менеджер мог связаться с вами.')
        await state.set_state(FSMClient.teleph_num_select)
    elif user_msg == '/end':
        await state.finish()
        await message.answer('😭До свидания😭 Пишите как только захотите оформить заказ')
    else:
        await message.answer('Увы, но похоже вы ошиблись в наборе ФИО, а именно поставили где-то лишний пробел, проверьте и отправьте снова.')

@dp.message_handler(state=FSMClient.teleph_num_select)
async def third_step(message: types.Message, state:FSMContext):
    user_msg = message.text
    if len(user_msg) == 11:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `client` WHERE tel_num='{user_msg}'")
            client_id = cursor.fetchone()
            connection.commit()
            if client_id is None:
                await state.update_data(telephon_num=user_msg)
                await message.answer('Хорошо, напишите вашу электронную почту, как резервный способ связи.')
                await state.set_state(FSMClient.email_select)
            else:
                await message.answer(('Увы, на такой номер телефона уже есть зарегистрированный клиент'))
    elif user_msg == '/end':
        await state.finish()
        await message.answer('😭До свидания😭 Пишите как только захотите оформить заказ')
    else:
        tr_user_msg = re.sub(r'[+.,()-]', '', user_msg)
        if len(tr_user_msg) == 11:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `client` WHERE tel_num='{user_msg}'")
                client_id = cursor.fetchone()
                connection.commit()
                if client_id is None:
                    await state.update_data(telephon_num=user_msg)
                    await message.answer('Хорошо, напишите вашу электронную почту, как резервный способ связи.')
                    await state.set_state(FSMClient.email_select)
                else:
                    await message.answer(('Увы, на такой номер телефона уже есть зарегистрированный клиент'))
        else:
            await message.answer('Упс, возможно у вас ошибка в номере телефона, проверьте номер и пришлите исправленный')

@dp.message_handler(state=FSMClient.email_select)
async def four_step(message: types.Message, state:FSMContext):
    user_msg = message.text
    ch1 = '.'
    ch2 = '@'
    if ch1 in user_msg and ch2 in user_msg:
        await state.update_data(email=user_msg)
        await message.answer('Теперь напишите адрес на котором должна будет проводится работа по заказу. Формат адреса: Город, Улица, Дом и т.д.')
        await state.set_state(FSMClient.address_select)
    elif user_msg == '/end':
        await state.finish()
        await message.answer('😭До свидания😭 Пишите как только захотите оформить заказ')
    else:
        await message.answer(f'Упс. В адресе электронной ошибка. Проверьте, возможно в адресе отстуствуют символ {ch1} или {ch2}.')

@dp.message_handler(state=FSMClient.address_select)
async def third_step(message: types.Message, state:FSMContext):
    user_msg = message.text
    if user_msg == '/end':
        await state.finish()
        await message.answer('😭До свидания😭 Пишите как только захотите оформить заказ')
    else:
        f_btn = KeyboardButton('Установка системы видеонаблюдения')
        s_btn = KeyboardButton('Проверка системы видеонаблюдения')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(f_btn, s_btn)

        await state.update_data(address_client=user_msg)
        await message.answer('Выберите с каким вопросом вы обратились к нам в компанию.', reply_markup=markup)
        await state.set_state(FSMClient.answ_client_select)


@dp.message_handler(state=FSMClient.answ_client_select)
async def five_step(message: types.Message, state:FSMContext):
    user_msg = message.text
    if user_msg == 'Установка системы видеонаблюдения':
        await state.update_data(answ_client=user_msg)

        c1_btn = KeyboardButton('BOLID V-1')
        c2_btn = KeyboardButton('BOLID V-2')
        c3_btn = KeyboardButton('BOLID V-3')
        c4_btn = KeyboardButton('BOLID V-4')
        c5_btn = KeyboardButton('BOLID V-5')
        c6_btn = KeyboardButton('BOLID V-6')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(c1_btn, c2_btn, c3_btn)
        markup.row(c4_btn, c5_btn, c6_btn)

        await message.answer('Теперь выберите, какую видеокамеру вы хотите установить. Более подробную информацию о продукции компании вы можете узнать на сайте.', reply_markup=markup)
        await state.set_state(FSMClient.prod_select)
    elif user_msg == '/end':
        await state.finish()
        await message.answer('😭До свидания😭 Пишите как только захотите оформить заказ')
    elif user_msg == 'Проверка системы видеонаблюдения':
        with connection.cursor() as cursor:
            getid = f"SELECT id_product FROM `product` WHERE name_product='{user_msg}'"
            cursor.execute(getid)
            getid = cursor.fetchone()['id_product']
        await state.update_data(answ_client=user_msg)
        await state.update_data(prod_sel=getid)
        await state.update_data(am_prod='')
        user_state_data = await state.get_data()
        name_sel = user_state_data['name']
        tel_num = user_state_data['telephon_num']
        em = user_state_data['email']
        adr_cl = user_state_data['address_client']
        ans_cl = user_state_data['answ_client']

        g_order_btn = KeyboardButton('Оформить заказ')
        e_order_btn = KeyboardButton('Отмена')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(g_order_btn, e_order_btn)

        await message.answer(f'''😁Мы почти закончили!😁 Проверьте введенные данные перед отправкой:\nВаше ФИО: {name_sel}\nОбращение по вопросу: {ans_cl}\nАдрес: {adr_cl}\nНомер телефона: {tel_num}\ne-mail: {em}''', reply_markup=markup)
        await state.set_state(FSMClient.all_selected)
    else:
        await message.answer('Пока что я могу оформлять заказ только на установку или проверку системы видеонаблюдения.')

@dp.message_handler(state=FSMClient.prod_select)
async def prodstep(message: types.Message, state:FSMContext):
    user_msg = message.text
    if user_msg == '/end':
        await state.finish()
        await message.answer('😭До свидания😭 Пишите как только захотите оформить заказ')
    else:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `product` WHERE name_product='{user_msg}'")
            result = cursor.fetchone()
            connection.commit()
            if result is None:
                await message.reply('Увы, такой продукции у нас нету, выберите ее из списка, либо напишите название, если его еще нету в списке.')
            else:
                with connection.cursor() as cursor:
                    getid = f"SELECT id_product FROM `product` WHERE name_product='{user_msg}'"
                    cursor.execute(getid)
                    getid = cursor.fetchone()['id_product']
                await state.update_data(prod_sel=getid)
                await state.update_data(prname=user_msg)
                await message.answer('Теперь напишите количество камер, которое вы планируете установить на объекте.')
                await state.set_state(FSMClient.amount_prod)


@dp.message_handler(state=FSMClient.amount_prod)
async def amprod(message: types.Message, state:FSMContext):
    user_msg = message.text
    if user_msg.isnumeric() == True:
        await state.update_data(am_prod=user_msg)
        user_state_data = await state.get_data()
        name_sel = user_state_data['name']
        tel_num = user_state_data['telephon_num']
        em = user_state_data['email']
        adr_cl = user_state_data['address_client']
        ans_cl = user_state_data['answ_client']
        prod_cl = user_state_data['prod_sel']
        am_of_prod = user_state_data['am_prod']
        # pr_cl это название продукта, а prod_cl это ID продукта для запроса
        pr_cl = user_state_data['prname']

        g_order_btn = KeyboardButton('Оформить заказ')
        e_order_btn = KeyboardButton('Отмена')

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(g_order_btn, e_order_btn)
        await message.answer(f'''😁Мы почти закончили!😁 Проверьте введенные данные перед отправкой:\nВаше ФИО: {name_sel}\nОбращение по вопросу: {ans_cl} {pr_cl} в количестве {am_of_prod} \nАдрес: {adr_cl}\nНомер телефона: {tel_num}\ne-mail: {em}''', reply_markup=markup)
        await state.set_state(FSMClient.all_selected)
    else:
        await message.answer('Количество камер указывается просто цифрой.')

@dp.message_handler(state=FSMClient.all_selected)
async def finish_process(message: types.Message, state: FSMContext):
    user_msg = message.text
    if user_msg == 'Оформить заказ':
        user_state_data = await state.get_data()
        tg_user_id = user_state_data['tg_u_id']
        name_sel = user_state_data['name']
        ans_cl = user_state_data['answ_client']
        prod_cl = user_state_data['prod_sel']
        am_of_prod = user_state_data['am_prod']
        adr_cl = user_state_data['address_client']
        tel_num = user_state_data['telephon_num']
        em = user_state_data['email']
        # pr_cl это название продукта, а prod_cl это ID продукта для запроса
        if am_of_prod == '':
            msg = f'''🤝Ваш заказ: на имя {name_sel}, по вопросу {ans_cl} , на адрес {adr_cl} оформлен. Контакты для связи: {tel_num} и {em}. После проверки вашего заказа с вами свяжется менеджер для уточнения необходимых вопросов. Ваш уникальный номер клиента: {tg_user_id}🤝'''
            await message.answer(msg)
        else:
            msg = f'''🤝Ваш заказ: на имя {name_sel}, по вопросу {ans_cl}   в количестве {am_of_prod}, на адрес {adr_cl} оформлен. Контакты для связи: {tel_num} и {em}. После проверки вашего заказа с вами свяжется менеджер для уточнения необходимых вопросов. Ваш уникальный номер клиента: {tg_user_id}🤝'''
            await message.answer(msg)

        spl = name_sel.split()
        surname = spl[0]
        name = spl[1]
        pathonimic = spl[2]
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM `client` WHERE tg_id_client='{tg_user_id}'")
                client_id = cursor.fetchone()
                connection.commit()
                if client_id is None:
                    if not am_of_prod:
                        print('Проверка видеонаблюдения')
                        # insert data
                        with connection.cursor() as cursor:
                            insert_query1 = f"INSERT INTO `client` (tg_id_client, surname, name, pathonimic, tel_num, email) VALUES ('{tg_user_id}', '{surname}', '{name}', '{pathonimic}', '{tel_num}', '{em}')"
                            cursor.execute(insert_query1)
                            id_client = cursor.lastrowid
                            connection.commit()

                        with connection.cursor() as cursor:
                            insert_query2 = f"INSERT INTO orders (id_client, id_employee, address_client, date_ad, state) VALUES ('{id_client}', '1', '{adr_cl}', NOW(), 'Новый');"
                            cursor.execute(insert_query2)
                            id_order = cursor.lastrowid
                            connection.commit()

                        with connection.cursor() as cursor:
                            insert_query3 = f"INSERT INTO `order_list` (id_order, id_product, amount) VALUES ('{id_order}', '{prod_cl}', '{am_of_prod}');"
                            cursor.execute(insert_query3)
                            connection.commit()
                    else:
                        print('Установка видеонаблюдения')
                        # insert data
                        with connection.cursor() as cursor:
                            insert_query1 = f"INSERT INTO `client` (tg_id_client, surname, name, pathonimic, tel_num, email) VALUES ('{tg_user_id}', '{surname}', '{name}', '{pathonimic}', '{tel_num}', '{em}')"
                            cursor.execute(insert_query1)
                            id_client = cursor.lastrowid
                            connection.commit()

                        with connection.cursor() as cursor:
                            insert_query2 = f"INSERT INTO orders (id_client, id_employee, address_client, date_ad, state) VALUES ('{id_client}', '1', '{adr_cl}', NOW(), 'Новый');"
                            cursor.execute(insert_query2)
                            id_order = cursor.lastrowid
                            connection.commit()

                        with connection.cursor() as cursor:
                            insert_query3 = f"INSERT INTO `order_list` (id_order, id_product, amount) VALUES ('{id_order}', '{prod_cl}', '{am_of_prod}');"
                            cursor.execute(insert_query3)
                            connection.commit()
                else:
                    if not am_of_prod:
                        with connection.cursor() as cursor:
                            id_client = f"SELECT id_client FROM `client` WHERE tg_id_client='{tg_user_id}'"
                            cursor.execute(id_client)
                            id_client = cursor.fetchone()['id_client']

                        with connection.cursor() as cursor:
                            insert_query2 = f"INSERT INTO orders (id_client, id_employee, address_client, date_ad, state) VALUES ('{id_client}', '1', '{adr_cl}', NOW(), 'Новый');"
                            cursor.execute(insert_query2)
                            id_order = cursor.lastrowid
                            connection.commit()

                        with connection.cursor() as cursor:
                            insert_query3 = f"INSERT INTO `order_list` (id_order, id_product, amount) VALUES ('{id_order}', '{prod_cl}', '{am_of_prod}');"
                            cursor.execute(insert_query3)
                            connection.commit()
                    else:
                        with connection.cursor() as cursor:
                            id_client = f"SELECT id_client FROM `client` WHERE tg_id_client='{tg_user_id}'"
                            cursor.execute(id_client)
                            id_client = cursor.fetchone()['id_client']

                        with connection.cursor() as cursor:
                            insert_query2 = f"INSERT INTO orders (id_client, id_employee, address_client, date_ad, state) VALUES ('{id_client}', '1', '{adr_cl}', NOW(), 'Новый');"
                            cursor.execute(insert_query2)
                            id_order = cursor.lastrowid
                            connection.commit()

                        with connection.cursor() as cursor:
                            insert_query3 = f"INSERT INTO `order_list` (id_order, id_product, amount) VALUES ('{id_order}', '{prod_cl}', '{am_of_prod}');"
                            cursor.execute(insert_query3)
                            connection.commit()
        finally:
            # connection.close()
            print('Заполнение закончено')
    else:
        await message.answer('😭До свидания😭')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

# executor.start_webhook(
#     dispatcher=dp,
#     webhook_path='',
#     on_startup=on_startup,
#     on_shutdown=on_shutdown,
#     skip_updates=True,
#     host='31.31.196.85',
#     port=3306
# )
