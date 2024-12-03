from telegram import *
from telegram.ext import *

from bot_messages import *
from buttons_handlers import *
from logging_config import logger
from order_process import ordering
from utils import *
from buttons import *
from db_operations import *
DEFAULT_MODE = "user"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    context.user_data.clear()
    access_mode = context.user_data.get('access_mode',DEFAULT_MODE)
    user_id = update.effective_user.id
    user_name = update.effective_user.name
    context.user_data['user_name'] = user_name


    logger.warning(f"Активный пользователь: \nИмя - {user_name}, \nID - {user_id}, \nРежим - {access_mode}")
    if is_superadmin_as_user(user_id, access_mode):
        main_panel = sa_main_as_usr
    elif is_superadmin(user_id):
        main_panel = sa_main
    elif is_admin(user_id):
        main_panel = adm_main
    else:
        main_panel = usr_main

    markup = ReplyKeyboardMarkup(main_panel, resize_keyboard=True)
    await (update.message.reply_text(
        hello_msg(user_name,access_mode), reply_markup=markup
    ))

async def incoming_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_input = update.message.text.strip()
    product_id = context.user_data.get('edit_product_id','')
    edit_mode = context.user_data.get('edit_mode')
    order_step = context.user_data.get('order_step','')

    access_mode = context.user_data.get('access_mode', DEFAULT_MODE)
    print(f'ui_handlers → incoming_text_handler: product_id - {product_id}, access - {access_mode}, edit_mode - {edit_mode}, order_step - {order_step}')
    if access_mode == 'admin':

        if edit_mode == 'add_product':
            await update.message.delete()
            if ',' in user_input:
                parts = user_input.split(',', 1)
            else:
                await update.message.reply_text(add_product_err()['format'])
                return
            if len(parts) != 2:
                await update.message.reply_text(add_product_err()['type'])
                return
            name, price_str = parts[0].strip(), parts[1].strip()
            try:
                price = float(price_str)
            except ValueError:
                await update.message.reply_text(add_product_err()['price'])
                return

            add_product(name, price)
            await update.message.reply_text(f"Товар '{name}' с ценой {price:.2f} руб. успешно добавлен.")

        elif edit_mode == 'edit_price':
            await update.message.delete()
            if user_input.replace('.', '', 1).isdigit():
                new_price = float(user_input)
                update_product_price(product_id, new_price)
                await update.message.reply_text(f"Цена товара с ID {product_id} обновлена до {new_price:.2f}!")
            else:
                await update.message.delete()
                await update.message.reply_text("Ошибка: Введите корректное число для цены.")
        elif edit_mode == 'edit_desc':
            update_product_desc(product_id, user_input)
            await update.message.reply_text(f"Описание товара с ID {get_product_name(product_id)} успешно обновлено.")

    elif access_mode == 'user':
        if edit_mode == 'order_product':
            await ordering(update,context)


