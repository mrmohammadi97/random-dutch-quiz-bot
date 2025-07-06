from telegram.ext import ApplicationBuilder, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, \
    filters
from app.config.settings import settings
from app.handlers.start_handler import StartHandler
from app.handlers.quiz_handler import QuizHandler
from app.handlers.callback_handler import CallbackHandler
from app.models.user import create_tables


def main():
    # Create database tables
    create_tables()

    # Initialize handlers
    start_handler = StartHandler()
    quiz_handler = QuizHandler()
    callback_handler = CallbackHandler()

    # Build application
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Define conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start_handler.start)],
        states={
            1: [  # ASKING state
                MessageHandler(filters.TEXT & ~filters.COMMAND, quiz_handler.handle_answer),
                CallbackQueryHandler(callback_handler.handle_callback)
            ]
        },
        fallbacks=[CommandHandler("cancel", quiz_handler.cancel)]
    )

    app.add_handler(conv_handler)

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()