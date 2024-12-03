from itertools import product
from lib2to3.fixes.fix_input import context
from pyexpat.errors import messages

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import CallbackContext

from buttons import date_, period_, quantity_, edit_entity_, show_confirm_
from db_operations import get_product_name
from utils import CHAT_ORDERS


async def callback_query_handler(update: Update, context: CallbackContext):
    return await ordering(update, context)


async def ordering(update: Update, context: CallbackContext):
    """Основной метод обработки заказа."""
    user_input = None
    print(f"Редактирование ? - {context.user_data.get('edit_order', 'Нет')}")

    # Обрабатываем запросы как от callback_query, так и от message
    if update.callback_query:
        query = update.callback_query
        data = query.data
        message = query.message  # Получаем сообщение из callback_query
    elif update.message:
        user_input = update.message.text.strip()
        message = update.message  # Получаем сообщение из обычного текста

    order_step = context.user_data.get('order_step', 'quantity')

    handlers = {
        'quantity': handle_quantity,
        'address': handle_address,
        'date': handle_date,
        'period': handle_period,
        'phone': handle_phone,
        'confirmation': handle_confirmation,
        'edit': handle_edit,
        'show_confirmation': show_confirmation
    }

    handler = handlers.get(order_step)
    if handler:
        return await handler(update, context, user_input)

    # Если не найден шаг для обработки
    if message:
        await message.reply_text("Произошла ошибка. Попробуйте снова.")
    return False


async def send_order_notification(update: Update,context: CallbackContext):

    print(f"handle_quantity user_data: {context.user_data}")
    user_data = context.user_data
    order_details = (
        f"🔔 <b>Новый заказ</b>! \n\n"
        f"<b>Товар:</b> {get_product_name(user_data.get('edit_product_id', 'Неизвестно'))}\n"
        f"<b>Количество:</b> {user_data['order_quantity']}\n"
        f"<b>Адрес:</b> {user_data['order_address']}\n"
        f"<b>Дата доставки:</b> {user_data['order_date']}\n"
        f"<b>Период доставки:</b> {user_data['order_period']}\n"
        f"<b>Телефон:</b> {user_data['order_phone']}\n\n"
        f"<b>Телеграм:</b> {update.effective_user.name}"
    )
    await context.bot.send_message(
        chat_id=CHAT_ORDERS,
        text=order_details,
        parse_mode=ParseMode.HTML
    )


async def handle_quantity(update, context, user_input=None):
    print(f"handle_quantity user_data: {context.user_data}, data: {update.callback_query.data}")
    query = update.callback_query
    data = query.data
    context.user_data['current_step'] = 'quantity'
    # Получаем текущее количество из данных пользователя
    current_quantity = context.user_data.get('order_quantity', 1)

    # Обработка кнопок увеличения и уменьшения количества
    if data == "increase":
        current_quantity += 1
    elif data == "decrease" and current_quantity > 1:
        current_quantity -= 1
    elif data == "confirm_quantity":
        # Сохраняем выбранное количество в данных пользователя
        context.user_data['order_quantity'] = current_quantity

        # Проверяем флаг редактирования
        if context.user_data.get('edit_order', False):  # Флаг редактирования
            # Если это редактирование, сразу переходим к подтверждению
            context.user_data['order_step'] = 'show_confirmation'
            await show_confirmation(update, context)  # Показываем подтверждение
        else:
            # Если это не редактирование, переходим к вводу адреса
            context.user_data['order_step'] = 'address'
            await query.message.reply_text(
                f"Вы выбрали количество: {current_quantity}. Теперь введите адрес доставки."
            )

        # Завершаем обработку callback
        await query.answer()
        return True
    elif data == "cancel":
        # Отмена выбора количества
        await query.message.reply_text("Выбор количества отменён.")
        context.user_data.clear()  # Очищаем данные пользователя
        await query.answer()
        return True

    # Обновляем количество в данных пользователя
    context.user_data['order_quantity'] = current_quantity
    # Генерируем клавиатуру с обновленным количеством
    keyboard = quantity_(current_quantity)
    # Обновляем сообщение с новой клавиатурой
    await query.edit_message_reply_markup(reply_markup=keyboard)
    await query.answer()
    return True


async def handle_address(update, context, user_input=None):
    print(f"handle_address user_data: {context.user_data}, data: {'empty'}")
    context.user_data['current_step'] = 'date'
    if update.callback_query:
        query = update.callback_query
        data = query.data

        if data == "edit_address":
            # Если выбрано редактирование адреса, то просим пользователя ввести новый адрес
            await query.message.reply_text("Пожалуйста, введите новый адрес доставки.")
            context.user_data['order_step'] = 'address'  # Переход к вводу нового адреса
            await query.answer()
            return True
    elif user_input:
        context.user_data['order_address'] = user_input
        # Если это редактирование, сразу переходим к подтверждению
        if context.user_data.get('edit_order', False):
            context.user_data['order_step'] = 'confirmation'
            await show_confirmation(update, context)  # Показываем подтверждение
        else:
            context.user_data['order_step'] = 'date'
            keyboard = date_()
            await update.message.reply_text("Выберите дату доставки:", reply_markup=keyboard)
        return True

    await update.message.reply_text("Пожалуйста, введите адрес доставки.")
    return False


async def handle_date(update, context, user_input=None):
    print(f"handle_date user_data: {context.user_data}, data: {update.callback_query.data}")
    context.user_data['current_step'] = 'date'
    query = update.callback_query
    data = query.data

    if data == "cancel":
        context.user_data.clear()
        await query.message.reply_text("Оформление заказа отменено.")
        return True

    elif data == "back":
        context.user_data['order_step'] = 'address'
        await query.message.reply_text("Введите адрес доставки.")
        return True

    # Сохраняем выбранную дату
    context.user_data['order_date'] = data

    if context.user_data.get('edit_order', False):  # Если в режиме редактирования
        # Показываем клавиатуру для выбора новой даты
        buttons = date_()
        await query.message.reply_text(
            "Выберите новую дату доставки:",
            reply_markup=buttons
        )
        context.user_data['order_date'] = None
        context.user_data['order_step'] = 'show_confirmation'
        return True

    else:
        # Если это не редактирование, переходим к выбору периода


        context.user_data['order_step'] = 'period'
        await query.answer()
        await query.message.reply_text(
            "Выберите удобный период доставки:",
            reply_markup=period_()
        )
    return True


async def handle_period(update, context, user_input=None):
    print(f"handle_period user_data: {context.user_data}, data: {update.callback_query.data}")
    query = update.callback_query
    data = query.data
    context.user_data['current_step'] = 'period'
    buttons = period_()

    if data == "cancel":
        context.user_data.clear()
        await query.message.reply_text("Оформление заказа отменено.")
        return True
    elif data == "back":
        context.user_data['order_step'] = 'date'
        keyboard = date_()
        await query.message.reply_text("Выберите дату доставки:", reply_markup=keyboard)
        return True

    context.user_data['order_period'] = period_(data)

    # Проверяем флаг редактирования
    if context.user_data.get('edit_order', False):  # Флаг редактирования


        await query.message.reply_text(
            "Выберите новый период дату доставки:",
            reply_markup=buttons
        )
        context.user_data['order_step'] = 'show_confirmation'
        return True
    else:
        # Если это не редактирование, переходим к вводу телефона
        context.user_data['order_step'] = 'phone'
        await query.answer()
        await query.message.reply_text(
            f"Вы выбрали: {context.user_data['order_period']}\nПожалуйста, введите ваш номер телефона."
        )

    return True

async def handle_phone(update, context, user_input=None):
    print(f"handle_phone user_data: {context.user_data}, data: 'empty'")
    context.user_data['current_step'] = 'phone'

    # message = update.message if update.message else update.callback_query.message
    if update.callback_query:
        query = update.callback_query
        data = query.data
        if data == 'edit_phone':
            await query.message.reply_text("Пожалуйста, введите новый номер телефона:")
            context.user_data['order_step'] = 'phone'  # Переход к вводу нового телефона
            await query.answer()
            return True

    elif user_input:
        user_input = user_input.strip()
        is_valid = (user_input.startswith('+7') and len(user_input) == 12 and user_input[1:].isdigit()) or \
           (user_input.startswith('8') and len(user_input) == 11 and user_input.isdigit())

        if not is_valid:
            await update.message.reply_text(
                "Ошибка: Укажите корректный номер телефона. Допустимые форматы:\n"
                "+79998887766\n"
                "89998887766"
            )
            return False
        context.user_data['order_phone'] = user_input or ''


    context.user_data['order_step'] = 'confirmation'
    await show_confirmation(update, context)

    return True

async def show_confirmation(update, context, user_input=None):
    """Отображает этап подтверждения заказа."""
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>show confirm')
    order_date = ''
    order_period = ''
    order_quantity = context.user_data.get('order_quantity',0)
    phone = context.user_data.get('order_phone',911)
    address = context.user_data.get('order_address','Тридевятое царство')
    product_name = get_product_name(context.user_data.get('edit_product_id', 'Неизвестно'))

    # Проверяем данные пользователя
    if update.callback_query:

        if context.user_data['current_step'] == 'date':
            order_date = update.callback_query.data
            context.user_data['order_date'] = order_date
        else:
            order_date = context.user_data.get('order_date')

        if context.user_data['current_step'] == 'period':
            order_period = period_(update.callback_query.data)
            context.user_data['order_period'] = order_period
        else:
            order_period = context.user_data.get('order_period')
    else:
        order_date = context.user_data.get('order_date')
        order_period = context.user_data.get('order_period')
    # Подготовка текста заказа для отображения
    order_details = (
        f"Товар: {product_name}\n"
        f"Количество: {order_quantity}\n"
        f"Адрес: {address}\n"
        f"Дата доставки: {order_date}\n"
        f"Период доставки: {order_period}\n"
        f"Телефон: {phone}"
    )

    # Клавиатура для подтверждения, редактирования или отмены


    context.user_data['order_step'] = 'confirmation'
    if update.callback_query:
        query = update.callback_query
        await query.message.reply_text(f"Ваш заказ:\n\n{order_details}", reply_markup=show_confirm_())
        await query.answer()  # Подтверждаем обработку callback
    else:
        # Если это обычное сообщение (не через callback)
        await update.message.reply_text(f"Ваш заказ:\n\n{order_details}", reply_markup=show_confirm_())

async def handle_confirmation(update, context, user_input=None):
    query = update.callback_query
    data = query.data

    if data == "confirm_order":
        await update.callback_query.message.reply_text("Ваш заказ подтвержден! Спасибо!")
        await send_order_notification(update,context)
        context.user_data.clear()
        return True
    elif data == "edit_order":
        context.user_data['order_step'] = 'edit'
        await query.message.reply_text("Что вы хотите изменить?", reply_markup=edit_entity_())
        return True
    elif data == "cancel":
        context.user_data.clear()
        await query.message.reply_text("Оформление заказа отменено.")
        return True

async def handle_edit(update, context, user_input=None):
    query = update.callback_query
    data = query.data
    print(f"data in handle edit -  {data}")
    edit_steps = {
        "edit_quantity": "quantity",
        "edit_address": "address",
        "edit_date": "date",
        "edit_period": "period",
        "edit_phone": "phone"
    }

    if data in edit_steps:
        context.user_data['order_step'] = edit_steps[data]
        context.user_data['edit_order'] = True
        await ordering(update, context)  # Возвращаемся к редактируемому шагу
        return True
