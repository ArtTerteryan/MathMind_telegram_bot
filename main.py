from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from config import BOT_TOKEN
from handlers import (
    start,
    handle_id_input,
    handle_subquestion_input,
    error_handler,
    STATE_WAITING_FOR_ID_INPUT,
    STATE_WAITING_FOR_SUBQUESTION_INPUT,
)

def run_bot():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            STATE_WAITING_FOR_ID_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_id_input)
            ],
            STATE_WAITING_FOR_SUBQUESTION_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_subquestion_input)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    application.run_polling()

if __name__ == '__main__':
    run_bot()
