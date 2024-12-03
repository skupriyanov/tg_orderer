from telegram import *
from datetime import datetime, timedelta

usr_main = [["Каталог", "Мои заказы"],['Назад', 'На главную']]

adm_main = [["Каталог", "Управление заказами"],['Назад', 'На главную']]

sa_main = [["Каталог", "Управление заказами"],["Активировать режим пользователя"],['Назад', 'На главную']]

sa_main_as_usr = [["Каталог", "Мои заказы"],["Активировать режим администратора"],['Назад', 'На главную']]

add_product_button = [[InlineKeyboardButton("Добавить товар", callback_data="add_product")]]

def adm_add_desc_button_(product_id):
    buttons = [[InlineKeyboardButton("Добавить описание", callback_data=f"edit_desc_{product_id}")]]
    return InlineKeyboardMarkup(buttons)
def adm_product_actions_(product_id):
   buttons = [
            [InlineKeyboardButton("Изменить цену", callback_data=f"edit_price_{product_id}")],
            [InlineKeyboardButton("Изменить описание", callback_data=f"edit_desc_{product_id}")],
            [InlineKeyboardButton("Просмотреть описание", callback_data=f"show_desc_{product_id}")],
            [InlineKeyboardButton("Удалить товар", callback_data=f"delete_product_{product_id}")]
        ]
   return InlineKeyboardMarkup(buttons)

def usr_product_actions_(product_id):
   buttons =  [
            [InlineKeyboardButton("Заказать товар", callback_data=f"order_product_{product_id}")],
            [InlineKeyboardButton("Просмотреть описание", callback_data=f"show_desc_{product_id}")]
        ]
   return InlineKeyboardMarkup(buttons)

def catalog_main_(catalog):
    return [
                [InlineKeyboardButton(f"{product[1]} - {product[2]:.2f} руб.", callback_data=f"select_product_{product[0]}")]
                for product in catalog
            ]


from typing import Union


def period_(*args) -> Union[str, InlineKeyboardMarkup]:
    periods = {
        'morning': "Утро (9:00 - 12:00)",
        'afternoon': "День (12:00 - 18:00)",
        'evening': "Вечер (18:00 - 21:00)"
    }

    if len(args) == 0:
     # Возвращаем разметку кнопок
        buttons = []
        for key, value in periods.items():
            button = InlineKeyboardButton(text=value, callback_data=key)
            buttons.append([button])

        return InlineKeyboardMarkup(inline_keyboard=buttons)

    elif len(args) == 1:
        data = args[0]
        return periods.get(data)
    else:
        raise ValueError("Неверный вызов функции")


def date_():
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


def quantity_(current_quantity: int):
    buttons = [
        [InlineKeyboardButton(f"➖ 1", callback_data="decrease"),
         InlineKeyboardButton(f"Количество: {current_quantity}", callback_data="current"),
         InlineKeyboardButton(f"➕ 1", callback_data="increase")],
        [InlineKeyboardButton("Подтвердить", callback_data="confirm_quantity"),
         InlineKeyboardButton("Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(buttons)

def edit_entity_():
    """Генерирует клавиатуру для выбора шага редактирования."""
    keyboard = [
        [InlineKeyboardButton("Количество", callback_data="edit_quantity")],
        [InlineKeyboardButton("Адрес", callback_data="edit_address")],
        [InlineKeyboardButton("Дата", callback_data="edit_date")],
        [InlineKeyboardButton("Период", callback_data="edit_period")],
        [InlineKeyboardButton("Телефон", callback_data="edit_phone")],
        [InlineKeyboardButton("⬅️ Вернуться", callback_data="confirm_order")]
    ]
    return InlineKeyboardMarkup(keyboard)


def show_confirm_():
    buttons = [
            [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_order")],
            [InlineKeyboardButton("✏️ Редактировать", callback_data="edit_order")],
         [InlineKeyboardButton("❌ Отменить", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(buttons)



