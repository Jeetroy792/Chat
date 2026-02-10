import os
import logging
import re
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
MAIN_BOT_TOKEN = '8367209194:AAG9KjF5v5ti8KCedqqiX1sVl1PlOed30c4' 
OWNER_ID = 8229228616
LOG_CHANNEL_ID = -1003841412573 
# ---------------------

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- চাইল্ড বটের লজিক ---
async def run_new_bot(token):
    try:
        new_app = Application.builder().token(token).build()

        async def child_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("<b>Welcome! 👋</b>\nSend your message below. The team will reply soon.", parse_mode='HTML')

        async def child_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if not update.message.chat.id == LOG_CHANNEL_ID and update.effective_user.id != OWNER_ID:
                user_id = update.effective_user.id
                text = update.message.text
                log_text = f"📩 <b>New Message</b>\n<b>From ID:</b> <code>{user_id}</code>\n---------------------------\n{text}"
                await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=log_text, parse_mode='HTML')
                await update.message.reply_text("<i>Your message has been sent to support!</i>", parse_mode='HTML')

            elif update.message.reply_to_message:
                match = re.search(r'ID:\s*(\d+)', update.message.reply_to_message.text)
                if match:
                    target_id = int(match.group(1))
                    await context.bot.send_message(chat_id=target_id, text=f"<b>Reply from Support:</b>\n\n{update.message.text}", parse_mode='HTML')
                    await update.message.reply_text(f"✅ Reply delivered to {target_id}")

        new_app.add_handler(CommandHandler("start", child_start))
        new_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, child_handle))
        
        await new_app.initialize()
        await new_app.start()
        await new_app.updater.start_polling(drop_pending_updates=True)
        return True
    except Exception as e:
        logging.error(f"Error starting child bot: {e}")
        return False

# --- মেইন মাস্টার বটের কমান্ডস ---
async def add_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("Usage: /addbot [TOKEN]")
        return
    
    token = context.args[0]
    await update.message.reply_text("🔄 Connecting...")
    if await run_new_bot(token):
        await update.message.reply_text("✅ Bot Connected!")
    else:
        await update.message.reply_text("❌ Failed!")

async def main_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"<b>Jeet's Bot Factory 🏭</b>\nOwner: {OWNER_ID}", parse_mode='HTML')

def main():
    # মাস্টার বট সেটআপ
    master_app = Application.builder().token(MAIN_BOT_TOKEN).build()
    
    master_app.add_handler(CommandHandler("start", main_start))
    master_app.add_handler(CommandHandler("addbot", add_bot))
    
    print("Master Bot is starting...")
    
    # এটিই সমাধান: drop_pending_updates=True দিলে কনফ্লিক্ট হবে না
    master_app.run_polling(drop_pending_updates=True, close_loop=False)

if __name__ == '__main__':
    main()
    
