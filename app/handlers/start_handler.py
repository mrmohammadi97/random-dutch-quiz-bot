from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.user_service import UserService

class StartHandler:
    def __init__(self):
        self.user_service = UserService()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = self.user_service.get_or_create_user(update)
        context.user_data['user_id'] = user.id

        keyboard = [
            [InlineKeyboardButton("🔢 Nummers Quiz", callback_data="mode_numbers")],
            [InlineKeyboardButton("🕐 Tijd Quiz", callback_data="mode_time")],
            [InlineKeyboardButton("📊 Mijn Statistieken", callback_data="stats")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "🇳🇱 Welkom bij de Nederlandse Quiz!\n"
            "Kies een quiz type:",
            reply_markup=reply_markup
        )
        return 1  # ASKING state