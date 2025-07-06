from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.services.quiz_service import QuizService
from app.services.audio_service import AudioService
from app.handlers.quiz_handler import QuizHandler


class CallbackHandler:
    def __init__(self):
        self.quiz_service = QuizService()
        self.audio_service = AudioService()
        self.quiz_handler = QuizHandler()

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        callback_data = query.data

        if callback_data == "mode_time":
            await self._start_time_quiz(query, context)
        elif callback_data == "mode_numbers":
            await self._start_numbers_quiz(query, context)
        elif callback_data == "try_again":
            await self._try_again(query, context)
        elif callback_data == "next_question":
            await self._next_question(query, context)
        elif callback_data == "show_answer":
            await self._show_answer(query, context)
        elif callback_data == "play_audio":
            await self._play_audio(query, context)
        elif callback_data == "back_to_menu":
            await self._back_to_menu(query, context)

    async def _edit_or_send_message(self, query, text, reply_markup=None, parse_mode='Markdown'):
        """Helper method to edit message or send new one if editing fails"""
        try:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception:
            await query.message.delete()
            await query.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )

    async def _start_time_quiz(self, query, context: ContextTypes.DEFAULT_TYPE):
        user_id = context.user_data.get('user_id')
        question = self.quiz_service.generate_time_question(user_id)
        context.user_data['current_question'] = question
        context.user_data['attempts'] = 0

        text = (
            f"🕐 **Tijd Quiz**\n\n"
            f"Hoe zeg je deze tijd in het Nederlands?\n\n"
            f"**{question['display']}**\n\n"
            f"Type je antwoord:"
        )

        await self._edit_or_send_message(query, text)

    async def _start_numbers_quiz(self, query, context: ContextTypes.DEFAULT_TYPE):
        user_id = context.user_data.get('user_id')
        question = self.quiz_service.generate_number_question(user_id)
        context.user_data['current_question'] = question
        context.user_data['attempts'] = 0

        text = (
            f"🔢 **Nummers Quiz**\n\n"
            f"Hoe zeg je dit nummer in het Nederlands?\n\n"
            f"**{question['display']}**\n\n"
            f"Type je antwoord:"
        )

        await self._edit_or_send_message(query, text)

    async def _try_again(self, query, context: ContextTypes.DEFAULT_TYPE):
        question = context.user_data.get('current_question')
        if not question:
            await self._edit_or_send_message(query, "No active question. Use /start to begin.")
            return

        context.user_data['attempts'] = 0  # Reset attempts

        quiz_type = "🕐 **Tijd Quiz**" if question['type'] == 'time' else "🔢 **Nummers Quiz**"
        question_text = "Hoe zeg je deze tijd in het Nederlands?" if question['type'] == 'time' else "Hoe zeg je dit nummer in het Nederlands?"

        text = (
            f"{quiz_type}\n\n"
            f"{question_text}\n\n"
            f"**{question['display']}**\n\n"
            f"Type je antwoord:"
        )

        await self._edit_or_send_message(query, text)

    async def _next_question(self, query, context: ContextTypes.DEFAULT_TYPE):
        current_question = context.user_data.get('current_question')
        if not current_question:
            await self._edit_or_send_message(query, "No active quiz. Use /start to begin.")
            return

        user_id = context.user_data.get('user_id')

        # Generate new question of the same type
        if current_question['type'] == 'time':
            question = self.quiz_service.generate_time_question(user_id)
            quiz_type = "🕐 **Tijd Quiz**"
            question_text = "Hoe zeg je deze tijd in het Nederlands?"
        else:
            question = self.quiz_service.generate_number_question(user_id)
            quiz_type = "🔢 **Nummers Quiz**"
            question_text = "Hoe zeg je dit nummer in het Nederlands?"

        context.user_data['current_question'] = question
        context.user_data['attempts'] = 0

        text = (
            f"{quiz_type}\n\n"
            f"{question_text}\n\n"
            f"**{question['display']}**\n\n"
            f"Type je antwoord:"
        )

        await self._edit_or_send_message(query, text)

    async def _show_answer(self, query, context: ContextTypes.DEFAULT_TYPE):
        quiz_data = context.user_data.get('current_question')
        if not quiz_data:
            await self._edit_or_send_message(query, "No active question found.")
            return

        # Create a mock update object for the quiz handler method
        class MockUpdate:
            def __init__(self, query):
                self.effective_chat = query.message.chat

        mock_update = MockUpdate(query)
        await self.quiz_handler.send_answer_text(mock_update, context, quiz_data)

    async def _play_audio(self, query, context: ContextTypes.DEFAULT_TYPE):
        quiz_data = context.user_data.get('current_question')
        if not quiz_data:
            await self._edit_or_send_message(query, "No active question found.")
            return

        # Create a mock update object for the quiz handler method
        class MockUpdate:
            def __init__(self, query):
                self.effective_chat = query.message.chat

        mock_update = MockUpdate(query)
        await self.quiz_handler.send_audio_with_answer(mock_update, context, quiz_data)

    async def _back_to_menu(self, query, context: ContextTypes.DEFAULT_TYPE):
        text = (
            "🎯 **Nederlandse Quiz Bot**\n\n"
            "Welkom! Kies een quiz om te beginnen:\n\n"
            "• **Tijd Quiz**: Leer tijden uitspreken\n"
            "• **Nummers Quiz**: Leer getallen uitspreken"
        )

        keyboard = [
            [InlineKeyboardButton("🕐 Tijd Quiz", callback_data="mode_time")],
            [InlineKeyboardButton("🔢 Nummers Quiz", callback_data="mode_numbers")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._edit_or_send_message(query, text, reply_markup)