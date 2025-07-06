from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from app.services.quiz_service import QuizService
from app.services.audio_service import AudioService
from app.services.user_service import UserService


class QuizHandler:
    def __init__(self):
        self.quiz_service = QuizService()
        self.audio_service = AudioService()
        self.user_service = UserService()

    async def handle_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = context.user_data.get('user_id')
        if not user_id:
            await update.message.reply_text("Please start the bot with /start")
            return ConversationHandler.END

        user_text = update.message.text.strip().lower()
        quiz_data = context.user_data.get('current_question')

        if not quiz_data:
            await update.message.reply_text("No active question. Use /start to begin.")
            return ConversationHandler.END

        attempts = context.user_data.get('attempts', 0) + 1
        context.user_data['attempts'] = attempts

        is_correct = self.quiz_service.check_answer(user_text, quiz_data['answer'])

        # Save quiz session
        self.quiz_service.save_quiz_session(
            user_id, quiz_data, user_text, is_correct, attempts
        )

        if is_correct:
            await self._send_correct_response(update, context, quiz_data, attempts)
        else:
            await self._send_wrong_response(update, context, quiz_data)

        return 1  # Stay in ASKING state

    async def _send_correct_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_data: dict, attempts: int):
        attempt_text = "eerste poging" if attempts == 1 else f"{attempts} pogingen"

        # Prepare the answer message with audio
        answer_text = (
            f"✅ Correct op de {attempt_text}!\n\n"
            f"💡 Het juiste antwoord is:\n"
            f"**{quiz_data['display']}** = **{quiz_data['answer']}**\n\n"
            f"🔊 Luister naar de uitspraak:"
        )

        # Create buttons
        current_type = quiz_data['type']
        other_type = 'time' if current_type == 'numbers' else 'numbers'
        other_emoji = '🕐' if other_type == 'time' else '🔢'
        other_label = 'Tijd Quiz' if other_type == 'time' else 'Nummers Quiz'

        keyboard = [
            [InlineKeyboardButton("🎯 Nog een vraag", callback_data="next_question")],
            [InlineKeyboardButton(f"{other_emoji} {other_label}", callback_data=f"mode_{other_type}")],
            [InlineKeyboardButton("🏠 Hoofdmenu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send audio with the answer text and buttons
        try:
            audio_buffer = self.audio_service.create_audio(quiz_data['answer'])
            await update.message.reply_audio(
                audio_buffer,
                caption=answer_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception:
            # Fallback if audio fails
            await update.message.reply_text(
                f"{answer_text}\n\n🔊 Audio niet beschikbaar\n\nWat wil je nu doen?",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def _send_wrong_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_data: dict):
        keyboard = [
            [InlineKeyboardButton("🔄 Probeer opnieuw", callback_data="try_again")],
            [InlineKeyboardButton("💡 Toon antwoord", callback_data="show_answer")],
            [InlineKeyboardButton("🔊 Hoor uitspraak", callback_data="play_audio")],
            [InlineKeyboardButton("🏠 Hoofdmenu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "❌ Helaas, dat is niet correct.\n\n"
            "Wat wil je doen?",
            reply_markup=reply_markup
        )

    async def send_audio_with_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_data: dict):
        """Method to send audio with answer and proper buttons - for callback handler"""
        current_type = quiz_data['type']
        other_type = 'time' if current_type == 'numbers' else 'numbers'
        other_emoji = '🕐' if other_type == 'time' else '🔢'
        other_label = 'Tijd Quiz' if other_type == 'time' else 'Nummers Quiz'

        keyboard = [
            [InlineKeyboardButton("🔄 Probeer opnieuw", callback_data="try_again")],
            [InlineKeyboardButton("🎯 Volgende vraag", callback_data="next_question")],
            [InlineKeyboardButton(f"{other_emoji} {other_label}", callback_data=f"mode_{other_type}")],
            [InlineKeyboardButton("🏠 Hoofdmenu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get the correct answer text - check multiple possible keys
        answer_text = (
            quiz_data.get('answer') or
            quiz_data.get('dutch') or
            quiz_data.get('pronunciation') or
            "onbekend"
        )

        display_text = (
            quiz_data.get('display') or
            quiz_data.get('question') or
            quiz_data.get('time') or
            quiz_data.get('number') or
            "onbekend"
        )

        # Prepare caption with answer
        caption_text = (
            f"💡 Het juiste antwoord is:\n"
            f"**{display_text}** = **{answer_text}**\n\n"
            f"🔊 Uitspraak van '{answer_text}'\n\n"
            f"Wat wil je nu doen?"
        )

        try:
            audio_buffer = self.audio_service.create_audio(answer_text)
            await context.bot.send_audio(
                chat_id=update.effective_chat.id,
                audio=audio_buffer,
                caption=caption_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            # Debug: show what's actually in quiz_data
            debug_text = f"Debug - quiz_data keys: {list(quiz_data.keys())}\nValues: {quiz_data}"
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{caption_text}\n\n🔊 Audio niet beschikbaar\n\n{debug_text}",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def send_answer_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, quiz_data: dict):
        """Method to send answer text with buttons - for callback handler"""
        current_type = quiz_data['type']
        other_type = 'time' if current_type == 'numbers' else 'numbers'
        other_emoji = '🕐' if other_type == 'time' else '🔢'
        other_label = 'Tijd Quiz' if other_type == 'time' else 'Nummers Quiz'

        keyboard = [
            [InlineKeyboardButton("🔄 Probeer opnieuw", callback_data="try_again")],
            [InlineKeyboardButton("🔊 Hoor uitspraak", callback_data="play_audio")],
            [InlineKeyboardButton("🎯 Volgende vraag", callback_data="next_question")],
            [InlineKeyboardButton(f"{other_emoji} {other_label}", callback_data=f"mode_{other_type}")],
            [InlineKeyboardButton("🏠 Hoofdmenu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Get the correct answer text - check multiple possible keys
        answer_text = (
            quiz_data.get('answer') or
            quiz_data.get('dutch') or
            quiz_data.get('pronunciation') or
            "onbekend"
        )

        display_text = (
            quiz_data.get('display') or
            quiz_data.get('question') or
            quiz_data.get('time') or
            quiz_data.get('number') or
            "onbekend"
        )

        answer_message = (
            f"💡 Het juiste antwoord is:\n"
            f"**{display_text}** = **{answer_text}**\n\n"
            f"Wat wil je nu doen?"
        )

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=answer_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("👋 Tot ziens!")
        return ConversationHandler.END