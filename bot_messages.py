def add_product_err():
    return dict(format="Ошибка: Неверный формат ввода. Используйте 'Наименование, цена'.",
                       type="Ошибка: Неверный формат ввода. Укажите наименование и цену.",
                       price="Ошибка: Цена должна быть числом.")

def hello_msg(user_name,access_mode):
     return f"{user_name}, Добро пожаловать в магазин! Выберите действие из меню ниже({access_mode})."

def desc_msg(product_name,desc):
    return dict(desc=f"{product_name}:\n\n{desc}",
                usr_empty=f"Описание для товара '{product_name}' отсутствует, скоро обновим!",
                adm_empty=f"Описание для товара '{product_name}' отсутствует, добавьте его сейчас.")
