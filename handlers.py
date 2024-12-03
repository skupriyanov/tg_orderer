from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from db_operations import *
from utils import is_admin, is_superadmin
from logging_config import logger
from telegram.ext import CallbackContext
from datetime import datetime, timedelta


def create_period_keyboard():
    keyboard = [
        [InlineKeyboardButton("Утро (9:00 - 12:00)", callback_data='morning')],
        [InlineKeyboardButton("День (12:00 - 18:00)", callback_data='afternoon')],
        [InlineKeyboardButton("Вечер (18:00 - 21:00)", callback_data='evening')]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} начал работу с ботом.")

    # Проверка, является ли пользователь суперадминистратором
    if is_superadmin(user_id):
        # Устанавливаем режим по умолчанию, если он не установлен
        if "mode" not in context.user_data:
            context.user_data["mode"] = "user"

        mode = context.user_data["mode"]
        if mode == "admin":
            # Для суперадминистратора, находящегося в режиме администратора, добавим кнопку для переключения
            reply_keyboard = [
                ["Каталог", "Управление заказами"],
                ["Переключить на режим пользователя"]
            ]
        else:
            # Для суперадминистратора, находящегося в пользовательском режиме
            reply_keyboard = [
                ["Каталог", "Мои заказы"],
                ["Переключить на режим администратора"]
            ]
    elif is_admin(user_id):
        # Для обычного администратора
        reply_keyboard = [
            ["Каталог", "Управление заказами"]
        ]
    else:
        # Для обычного пользователя
        reply_keyboard = [
            ["Каталог", "Мои заказы"]
        ]

    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать в магазин! Выберите действие из меню ниже.",
        reply_markup=markup
    )


async def toggle_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_superadmin(user_id):
        await update.message.reply_text("У вас нет прав для переключения режимов.")
        return

    current_mode = context.user_data.get("mode", "user")
    new_mode = "admin" if current_mode == "user" else "user"
    context.user_data["mode"] = new_mode

    await update.message.reply_text(f"Режим переключен на: {new_mode.capitalize()}.")
    await start(update, context)


async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mode = context.user_data.get("mode", "user")
    products = get_products()
    logger.warning(f'mode = {mode}')

    if mode == 'admin':  # Админ видит кнопку "Добавить товар" в любом режиме
        # Кнопка "Добавить товар" всегда видна для админов
        keyboard = [[InlineKeyboardButton("Добавить товар", callback_data="add_product")]]

        if products:
            # Если товары есть, отображаем их и кнопку "Добавить товар"
            product_buttons = [
                [InlineKeyboardButton(f"{product[1]} - ${product[2]:.2f}", callback_data=f"product_{product[0]}")]
                for product in products
            ]
            keyboard.extend(product_buttons)
            markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Каталог товаров:", reply_markup=markup)
        else:
            # Если товаров нет, показываем только кнопку "Добавить товар"
            markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Список товаров пуст. Вы можете добавить новые товары.",
                                            reply_markup=markup)
    else:
        # Для обычных пользователей и суперадмина в режиме пользователя
        if not products:
            await update.message.reply_text("Список товаров пуст. Скоро добавим новые товары!")
        else:
            # Если товары есть, показываем их без кнопки "Добавить товар"
            product_buttons = [
                [InlineKeyboardButton(f"{product[1]} - ${product[2]:.2f}", callback_data=f"product_{product[0]}")]
                for product in products
            ]
            markup = InlineKeyboardMarkup(product_buttons)
            await update.message.reply_text("Каталог товаров:", reply_markup=markup)


async def handle_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['edit_mode'] = 'new_product'
    await query.answer()
    logger.info("Добавление товара: кнопка 'Добавить товар' нажата.")

    # Запрашиваем у пользователя наименование и цену товара
    await query.message.reply_text(
        "Введите наименование и цену товара в формате 'Наименование, цена' или 'Наименование цена':")

async def handle_edit_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = query.data.split('_')[2]
    context.user_data['edit_product_id'] = product_id
    context.user_data['edit_mode'] = 'price'
    await query.answer()
    logger.info("Изменение цены: кнопка 'Изменить цену' нажата.")
    await query.message.reply_text("Введите новую цену товара в формате 'Цена'. Например 1000)")

async def handle_edit_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = query.data.split('_')[2]
    context.user_data['edit_product_id'] = product_id
    context.user_data['edit_mode'] = 'desc'
    await query.answer()
    logger.info("Изменение описания: кнопка 'Изменить описание' нажата.")
    await query.message.reply_text("Введите новую описание для товара.")

async def handle_order_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = query.data.split('_')[2]
    context.user_data['edit_product_id'] = product_id
    context.user_data['edit_mode'] = 'order'
    await query.answer()
    logger.info("Заказ товара: кнопка 'Заказать товар' нажата.")
    await query.message.reply_text("Введите количество товара для заказа.")




def generate_date_keyboard():
    today = datetime.today()
    keyboard = []

    # Добавляем кнопки с датами (например, на ближайшие 7 дней)
    for i in range(7):  # выбираем 7 дней для примера
        day = today + timedelta(days=i)
        date_button = InlineKeyboardButton(day.strftime('%d-%m-%Y'), callback_data=day.strftime('%d-%m-%Y'))
        keyboard.append([date_button])

    # Кнопка "Назад" и "Отмена"
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel")])
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back")])

    return InlineKeyboardMarkup(keyboard)

def create_period_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("Утро (9:00 - 12:00)", callback_data='morning')],
        [InlineKeyboardButton("День (12:00 - 18:00)", callback_data='afternoon')],
        [InlineKeyboardButton("Вечер (18:00 - 21:00)", callback_data='evening')],
        [InlineKeyboardButton("Назад", callback_data="back")],
        [InlineKeyboardButton("Отмена", callback_data="cancel")]
    ])


# Функция для обработки выбора периода



async def handle_product_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the selection of a product, showing appropriate actions based on user role.
    """
    mode = context.user_data.get("mode", "user")
    query = update.callback_query
    await query.answer()
    product_id = int(query.data.split('_')[1])  # Extract product ID from callback_data
    logger.warning(f"Product ID selected: {product_id}")

    user_id = update.effective_user.id

    if mode == 'admin':
        # Admin actions: edit price or delete product
        keyboard = [
            [InlineKeyboardButton("Изменить цену", callback_data=f"edit_price_{product_id}")],
            [InlineKeyboardButton("Изменить описание", callback_data=f"edit_desc_{product_id}")],
            [InlineKeyboardButton("Удалить товар", callback_data=f"delete_product_{product_id}")]
        ]
        await query.message.reply_text(f"Вы выбрали товар с ID {product_id}. Выберите действие:",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
    elif mode == 'user':
        # User actions: view description or order the product
        keyboard = [
            [InlineKeyboardButton("Просмотреть описание", callback_data=f"view_description_{product_id}")],
            [InlineKeyboardButton("Заказать товар", callback_data=f"order_product_{product_id}")]
        ]
        await query.message.reply_text(
            f"Вы выбрали товар с ID {product_id}.\nВыберите действие:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await query.message.reply_text("У вас недостаточно прав для выполнения действий с товаром.")
        logger.warning(f"User {user_id} attempted unauthorized action on product {product_id}.")




def callback_query_handler(update: Update, context: CallbackContext):
    return handle_order_step(update, context)


async def handle_order_step(update: Update, context: CallbackContext):
    """
    Handles step-by-step order creation.
    """
    order_step = context.user_data.get('order_step')
    user_input = None

    # Если это текстовое сообщение (например, ввод количества, адреса)
    if update.message:
        user_input = update.message.text.strip()

    logger.warning(f'ORDER STEP = {order_step}')

    if order_step == 'quantity':
        if not user_input.isdigit():
            await update.message.reply_text("Ошибка: Введите корректное количество товара.")
            return False
        context.user_data['order_quantity'] = int(user_input)
        context.user_data['order_step'] = 'address'
        await update.message.reply_text("Введите адрес доставки.")
        return True

    if order_step == 'address':
        context.user_data['order_address'] = user_input
        context.user_data['order_step'] = 'date'
        # Отправляем клавиатуру с датами (будет доступно ближайшие 7 дней)
        keyboard = generate_date_keyboard()
        await update.message.reply_text("Выберите дату доставки:", reply_markup=keyboard)
        return True

    if order_step == 'date':
        # Обработка callback_query для выбора даты
        if update.callback_query:
            query = update.callback_query
            if query.data == "cancel":
                context.user_data.clear()
                await query.message.reply_text("Оформление заказа отменено.")
                return True
            elif query.data == "back":
                context.user_data['order_step'] = 'address'
                await query.message.reply_text("Введите адрес доставки.")
                return True
            selected_date = query.data  # Это выбранная дата в формате "ДД-ММ-ГГГГ"
            context.user_data['order_date'] = selected_date
            context.user_data['order_step'] = 'period'

            # Ответ на callback_query, чтобы убрать индикацию загрузки
            await query.answer()

            # Подтверждаем выбор даты и переходим к следующему шагу
            await query.message.reply_text(
                f"Вы выбрали дату доставки: {selected_date}\nТеперь выберите период доставки.")

            # Показ клавиатуры с выбором периода
            keyboard = create_period_keyboard()  # Создайте эту клавиатуру для выбора периода
            await query.message.reply_text("Выберите удобный период доставки:", reply_markup=keyboard)
            return True

    if order_step == 'period':
        query = update.callback_query
        if query.data == "cancel":
            context.user_data.clear()
            await query.message.reply_text("Оформление заказа отменено.")
            return True
        elif query.data == "back":
            context.user_data['order_step'] = 'date'
            await query.message.reply_text("Выберите дату доставки.")
            keyboard = generate_date_keyboard()
            await query.message.reply_text("Выберите дату доставки:", reply_markup=keyboard)
            return True

        selected_period = query.data
        if selected_period == 'morning':
            period = "Утро (9:00 - 12:00)"
        elif selected_period == 'afternoon':
            period = "День (12:00 - 18:00)"
        elif selected_period == 'evening':
            period = "Вечер (18:00 - 21:00)"

        context.user_data['order_period'] = period
        context.user_data['order_step'] = 'phone'

        await query.answer()  # Ответить на callback_query, чтобы убрать загрузку
        await query.message.reply_text(f"Вы выбрали: {period}\nПожалуйста, введите ваш номер телефона.")
        return True

    if order_step == 'phone':
        if not user_input.startswith('8') or user_input.startswith('+') or not user_input[1:].isdigit():
            await update.message.reply_text("Ошибка: Укажите корректный номер телефона в формате +79998887766.")
            return False
        context.user_data['order_phone'] = user_input

        # Завершаем заказ
        await update.message.reply_text(
            f"Ваш заказ оформлен!\n\n"
            f"Товар: {get_product_name(context.user_data.get('edit_product_id'))}\n"
            f"Количество: {context.user_data['order_quantity']}\n"
            f"Адрес: {context.user_data['order_address']}\n"
            f"Дата доставки: {context.user_data['order_date']}\n"
            f"Период доставки: {context.user_data['order_period']}\n"
            f"Телефон: {context.user_data['order_phone']}"
        )
        context.user_data.clear()
        return True

    return False


async def process_edit_mode(update: Update, context: ContextTypes.DEFAULT_TYPE, edit_mode, user_input, product_id):
    """
    Processes different edit modes.
    """
    if edit_mode == 'price':
        if user_input.replace('.', '', 1).isdigit():
            new_price = float(user_input)
            update_product_price(product_id, new_price)
            await update.message.reply_text(f"Цена товара с ID {product_id} обновлена до {new_price:.2f}!")
        else:
            await update.message.reply_text("Ошибка: Введите корректное число для цены.")

    elif edit_mode == 'new_product':
        if ',' in user_input:
            parts = user_input.split(',', 1)
        elif ' ' in user_input:
            parts = user_input.split(' ', 1)
        else:
            await update.message.reply_text("Ошибка: Неверный формат ввода. Используйте 'Наименование, цена'.")
            return

        if len(parts) != 2:
            await update.message.reply_text("Ошибка: Неверный формат ввода. Укажите наименование и цену.")
            return

        name, price_str = parts[0].strip(), parts[1].strip()
        try:
            price = float(price_str)
        except ValueError:
            await update.message.reply_text("Ошибка: Цена должна быть числом.")
            return

        add_product(name, price)
        await update.message.reply_text(f"Товар '{name}' с ценой ${price:.2f} успешно добавлен.")

    elif edit_mode == 'desc':
        update_product_desc(product_id, user_input)
        await update.message.reply_text(f"Описание товара с ID {product_id} успешно обновлено.")


async def update_product_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles product info updates or actions based on the edit mode.
    """
    product_id = context.user_data.get('edit_product_id')
    edit_mode = context.user_data.get('edit_mode')

    if not edit_mode:
        await update.message.reply_text("Ошибка: Не хватает данных для редактирования.")
        logger.warning("Missing product ID or edit mode in context")
        return

    user_input = update.message.text.strip()
    logger.debug(f"Received input for edit_mode '{edit_mode}': {user_input}")

    if edit_mode == 'order':
        order_step_success = await handle_order_step(update, context)
        if not order_step_success:
            logger.debug("Order step processing failed.")
        return

    await process_edit_mode(update, context, edit_mode, user_input, product_id)

    # Clear context if the mode is not 'order'
    if edit_mode != 'order':
        context.user_data['edit_product_id'] = None
        context.user_data['edit_mode'] = None
    logger.debug("Context cleared after processing user input.")




async def handle_user_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user actions: view description or order product.
    """
    query = update.callback_query
    await query.answer()
    action, product_id = f"{query.data.split('_')[0]}_{query.data.split('_')[1]}", int(query.data.split('_')[2])

    if action == 'view_description':
        description = get_product_description(product_id)
        await query.message.reply_text(f"Описание товара с ID {product_id}: {description}")
    elif action == 'order_product':
        context.user_data['edit_product_id'] = product_id
        context.user_data['edit_mode'] = 'order'
        context.user_data['order_step'] = 'quantity'  # Начинаем с ввода количества
        await query.message.reply_text("Введите количество товара для заказа.")
    else:
        await query.message.reply_text("Неизвестное действие.")



# Helper functions


#///////////////////////////////////////////////////////////////////////////
# Обработчик для изменения цены товара


async def handle_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_id = query.data.split('_')[2]  # Получаем ID товара
    logger.warning(f'ID = {product_id}')
    # Выполняем удаление товара и подтверждаем удаление пользователю
    delete_product(product_id)  # Предположим, что есть функция для удаления товара
    await query.message.reply_text(f"Товар с ID {product_id} был успешно удален.")


async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text("У вас нет прав на просмотр заказов.")
        return

    orders = get_orders()
    if not orders:
        await update.message.reply_text("Нет новых заказов.")
        return

    order_list = "\n".join([f"Заказ #{order[0]}: {order[2]} ({order[3]} шт.)" for order in orders])
    await update.message.reply_text(f"Список заказов:\n{order_list}")
