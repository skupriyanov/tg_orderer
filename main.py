from buttons_handlers import toggle_access_mode, show_catalog, catalog_action, product_action
from config import TOKEN
from telegram.ext import *
from logging_config import logger
from db_operations import init_db
from order_process import callback_query_handler, ordering
# from order_process import ordering_handler
from ui_handlers import start, incoming_text_handler




def main():
    # Инициализация базы данных
    init_db()

    # Создание приложения
    app = ApplicationBuilder().token(TOKEN).build()

    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))


    app.add_handler(MessageHandler(filters.Regex("^Активировать режим администратора"), toggle_access_mode))
    app.add_handler(MessageHandler(filters.Regex("^Активировать режим пользователя$"), toggle_access_mode))


    app.add_handler(MessageHandler(filters.Regex("^Каталог$"), show_catalog))
    app.add_handler(MessageHandler(filters.Regex("^На главную$"), start))

    app.add_handler(CallbackQueryHandler(catalog_action, pattern="^select_product"))
    app.add_handler(CallbackQueryHandler(catalog_action, pattern="^add_product"))

    app.add_handler(CallbackQueryHandler(product_action, pattern="^edit_price"))
    app.add_handler(CallbackQueryHandler(product_action, pattern="^delete_product"))
    app.add_handler(CallbackQueryHandler(product_action, pattern="^edit_desc"))
    app.add_handler(CallbackQueryHandler(product_action, pattern="^show_desc"))
    app.add_handler(CallbackQueryHandler(product_action, pattern="^order_product"))

    app.add_handler(CallbackQueryHandler(ordering, pattern="^confirm_order"))
    app.add_handler(CallbackQueryHandler(ordering, pattern="^edit_order"))
    app.add_handler(CallbackQueryHandler(ordering, pattern="^cancel"))
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, incoming_text_handler))


    # app.add_handler(ordering_handler)

    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
