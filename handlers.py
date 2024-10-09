import asyncio
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import logger, VALID_SUBQUESTIONS
from db import fetch_answer_image_path, fetch_general_information
from utils import validate_id_format, send_image

# Define conversation states
STATE_WAITING_FOR_ID_INPUT = 1
STATE_WAITING_FOR_SUBQUESTION_INPUT = 2

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Բարի գալուստ MathMind-ի տելեգրամյան բոտ: Խնդիրները կարող եք որոնել x/x/x/x ֆորմատով:'
        'Օրինակ 1/1/2/3 որոնման արդյունքում կստանաք 1-ին շտեմարանի, 1-ին գլխի, 2-րդ բաժնի, 3-րդ խնդիրը:'
        "Բոտում հասանելի են միայն 1-ին շտեմարանի, 1-ին գլխի 'Արտահայտությունների ձևափոխություն և արժեքների հաշվում', 'Հավասարումներ' և 'Անհավասարումներ' բաժինների խնդիրները:"
        "1-ին շտեմարանի բոլոր խնդիրներին հասանելիություն ստանալու համար այցելեք մեր պաշտոնական կայքը:"  
    )

    return STATE_WAITING_FOR_ID_INPUT

# Handle ID input
async def handle_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text.strip()

    # Validate input format
    if not validate_id_format(user_input):
        await update.message.reply_text('Սխալ հարցում: Օգտագործեք x/x/x/x ֆորմատը')
        return STATE_WAITING_FOR_ID_INPUT

    # Convert user input from x/x/x/x to x_x_x_x
    id_value = user_input.replace('/', '_')

    try:
        # Check if the ID exists and fetch general information
        general_info = await asyncio.get_event_loop().run_in_executor(
            None, fetch_general_information, id_value
        )

        if not general_info:
            await update.message.reply_text('Տվյալ համարով խնդիրները հասանելի չեն:')
            return STATE_WAITING_FOR_ID_INPUT

        # If 'general_information' is not null, send its content
        if general_info.get('general_information'):
            general_info_path = general_info['general_information']
            
            try:
                await send_image(update, general_info_path)
            except Exception as e:
                logger.error(f"Error sending general information image: {e}", exc_info=True)
                await update.message.reply_text('An error occurred while sending the general information image. Please try again later.')

        # Ask for sub-question number
        await update.message.reply_text('Ընտրեք ենթահարցի համարը (1, 2, 3, or 4)')
        context.user_data['id_value'] = id_value
        return STATE_WAITING_FOR_SUBQUESTION_INPUT

    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        await update.message.reply_text('An unexpected error occurred. Please try again later.')
        return ConversationHandler.END

# Handle sub-question input
async def handle_subquestion_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    subquestion_input = update.message.text.strip()
    id_value = context.user_data.get('id_value')

    # Validate sub-question number
    if subquestion_input not in VALID_SUBQUESTIONS:
        await update.message.reply_text(f'Ենթահարցի համարը սխալ է: Ընտրեք նշված համարներից որևէ մեկը: {", ".join(VALID_SUBQUESTIONS)}.')
        return STATE_WAITING_FOR_SUBQUESTION_INPUT

    try:
        subquestion_number = subquestion_input

        # Fetch answer image path
        answer_result = await asyncio.get_event_loop().run_in_executor(
            None, fetch_answer_image_path, id_value, subquestion_number
        )

        if not answer_result or not answer_result.get('image_path'):
            await update.message.reply_text(f'There is no answer image for sub-question {subquestion_number}.')
            return STATE_WAITING_FOR_SUBQUESTION_INPUT

        answer_image_path = answer_result['image_path']
        logger.info(f"Answer image path: {answer_image_path}")

        # Send answer image
        await send_image(update, answer_image_path)

        # Prompt for another ID
        await update.message.reply_text('Որոնեք այլ խնդիրներ օգտագործելով x/x/x/x ֆորմատը:')

        return STATE_WAITING_FOR_ID_INPUT

    except Exception as e:
        logger.error(f'Unexpected error: {e}', exc_info=True)
        await update.message.reply_text('An unexpected error occurred. Please try again later.')
        return ConversationHandler.END

# Global error handler
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f'Update {update} caused error {context.error}', exc_info=True)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text('An unexpected error occurred. Please try again later.')
