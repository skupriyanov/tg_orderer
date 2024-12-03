from telegram import *
from telegram.ext import ContextTypes

from bot_messages import *
from buttons import adm_product_actions_, add_product_button, catalog_main_, adm_add_desc_button_, usr_product_actions_, \
    quantity_
from db_operations import *
from order_process import ordering, send_order_notification
from ui_handlers import start

DEFAULT_MODE = "user"  # Константа для режима по умолчанию


# Обработчик переключения режима представления меню (Администратор/Пользователь)
async def toggle_access_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Получаем текущий режим, если не установлен — используем режим по умолчанию
    current_mode = context.user_data.get("access_mode", DEFAULT_MODE)

    # Определяем новый режим
    new_mode = "admin" if current_mode == "user" else "user"
    context.user_data["access_mode"] = new_mode

    # Логирование для отладки
    await update.message.delete()

    # Запуск главного меню с обновленным режимом
    await start(update, context)



# Обработчик кнопки каталог
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_mode = context.user_data.get("access_mode", "user")

    catalog = get_products()
    await update.message.delete()
    if access_mode == 'admin':
        if catalog:
            # Если товары есть, отображаем их и кнопку "Добавить товар"
            buttons = add_product_button + catalog_main_(catalog)  # создаем новый список, не модифицируем глобальный
            markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text("Каталог товаров:", reply_markup=markup)
        else:
            # Если товаров нет, показываем только кнопку "Добавить товар"
            markup = InlineKeyboardMarkup(add_product_button)
            await update.message.reply_text("Список товаров пуст. Вы можете добавить новые товары.",
                                            reply_markup=markup)
    else:
        # Для обычных пользователей и суперадмина в режиме пользователя
        if not catalog:
            await update.message.reply_text("Список товаров пуст. Скоро добавим новые товары!")
        else:
            # Если товары есть, показываем их без кнопки "Добавить товар"
            buttons = catalog_main_(catalog)
            markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text("Каталог товаров:", reply_markup=markup)



# Обработчик действий с каталогом (Администратор/Пользователь)
async def catalog_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_mode = context.user_data.get('access_mode',DEFAULT_MODE)
    query = update.callback_query
    action_type = f"{query.data.split('_')[0]}_{query.data.split('_')[1]}"

    if access_mode == 'admin':
        if action_type == 'add_product':
            context.user_data['edit_mode'] = 'add_product'
            await query.message.reply_text("Введите наименование и цену товара в формате 'Наименование, цена'.")
        elif action_type == 'select_product':
            product_id = int(query.data.split('_')[2])
            context.user_data['edit_mode'] = 'select_product'
            await query.message.reply_text(f"Вы выбрали товар с ID {product_id}. Выберите действие:",
                                           reply_markup=adm_product_actions_(product_id))
    elif access_mode == 'user':
        if action_type == 'select_product':
            product_id = int(query.data.split('_')[2])
            context.user_data['edit_mode'] = 'select_product'
            await query.message.reply_text(f"Вы выбрали товар с ID {product_id}. Выберите действие:",
                                           reply_markup=usr_product_actions_(product_id))





# Обработчик действий с кнопками продукта (Администратор/Пользователь)
async def product_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_mode = context.user_data.get('access_mode', DEFAULT_MODE)
    query = update.callback_query
    action_type = f"{query.data.split('_')[0]}_{query.data.split('_')[1]}"
    product_id = query.data.split('_')[-1]
    print(f'button_handle → product_action:\n access: {access_mode} →\n action: {action_type} →\n id: {product_id}')

    if access_mode == 'admin':
        if action_type == 'edit_price':
            context.user_data['edit_mode'] = action_type
            context.user_data['edit_product_id'] = product_id
            await query.message.reply_text("Введите новую цену для товара:")
        elif action_type == 'edit_desc':
            context.user_data['edit_mode'] = action_type
            context.user_data['edit_product_id'] = product_id
            await query.message.reply_text("Введите новое описание товара:")
        elif action_type == 'show_desc':
            await query.answer()
            desc = get_product_description(product_id)
            product_name = get_product_name(product_id)
            if desc:
                await query.message.reply_text(f"Описание для товара '{product_name}':\n{desc}")
            else:
                await query.message.reply_text(desc_msg(product_name,desc)['adm_empty'],
                                               reply_markup=adm_add_desc_button_(product_id))
        elif action_type == 'delete_product':
            await query.answer()
            product_name = get_product_name(product_id)
            delete_product(product_id)  # Предположим, что есть функция для удаления товара
            await query.message.reply_text(f"Товар '{product_name}' был успешно удален.")
    elif access_mode == 'user':
        if action_type == 'show_desc':
            await query.answer()
            desc = get_product_description(product_id)
            product_name = get_product_name(product_id)
            if desc:
                await query.message.reply_text(desc_msg(product_name,desc)['desc'])
            else:
                await query.message.reply_text(desc_msg(product_name,desc)['usr_empty'])
        elif action_type == 'order_product':
            context.user_data['edit_mode'] = action_type
            context.user_data['edit_product_id'] = product_id  # Сохраняем ID товара
            context.user_data['order_quantity'] = 1
            context.user_data['user'] = update.effective_user.name

                # Отображаем клавиатуру выбора количества
            keyboard = quantity_(1)
            await update.callback_query.message.reply_text("Выберите количество товара:", reply_markup=keyboard)
            await query.answer()

# Обработчик действий с кнопками заказа (Администратор/Пользователь)
async def order_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    access_mode = context.user_data.get('access_mode', DEFAULT_MODE)
    query = update.callback_query
    action_type = f"{query.data.split('_')[0]}_{query.data.split('_')[1]}"
    product_id = query.data.split('_')[-1]
    print(f'button_handle → order_action:\n access: {access_mode} →\n action: {action_type} →\n id: {product_id}')

    query = update.callback_query
    data = query.data
    if access_mode == 'user':
        if data == "confirm_order":
            await update.message.reply_text("Ваш заказ подтвержден! Спасибо!")
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



