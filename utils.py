SUPERADMIN_ID = 541806760  # ID суперадмина
ADMIN_IDS = [541806760] # ID администраторов
CHAT_ORDERS = -1002313675232

# Утилиты для проверки ролей
def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_superadmin(user_id):
    return user_id == SUPERADMIN_ID

def is_superadmin_as_user(user_id,mode):
    return user_id == SUPERADMIN_ID and mode == 'user'



#TODO админы в статусах заказов видят тг контакт, того кто заказал


