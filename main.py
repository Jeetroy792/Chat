import os
import logging
import re
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
MAIN_BOT_TOKEN = '8367209194:AAEdIaBp0SKGyb1OGhtueHJupM3DMXUMXsk' 
OWNER_ID = 8229228616
# যে চ্যানেলে সব চাইল্ড বটের মেসেজ ফরওয়ার্ড হবে
LOG_CHANNEL_ID = -1003841412573 
# ---------------------

logging.basicConfig(level=logging.INFO)
app = Flask('')

@app.route('/')
def home(): return "Multi-Bot Factory with Channel Support is Live!"

def run_flask(): app.run(host='0.0.0.0', port=8000)

# --- চাইল্ড বটের লজিক ---
async def run_new_bot(token):
    try:
        new_app = Application.builder().token(token).build()

        async def child_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("<b>Welcome! 👋</b>\nSend your message below. The team will reply soon.", parse_mode='HTML')

        async def child_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # ১. ইউজার মেসেজ দিলে সেটি চ্যানেলে যাবে
            if not update.message.chat.id == LOG_CHANNEL_ID and update.effective_user.id != OWNER_ID:
                user_id = update.effective_user.id
                text = update.message.text
                
                log_text = f"📩 <b>New Message (Child Bot)</b>\n"
                log_text += f"<b>From ID:</b> <code>{user_id}</code>\n"
                log_text += f"---------------------------\n{text}"
                
                await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=log_text, parse_mode='HTML')
                await update.message.reply_text("<i>Your message has been sent to support!</i>", parse_mode='HTML')

            # ২. চ্যানেল থেকে রিপ্লাই দিলে ইউজারের কাছে যাবে
            elif update.message.reply_to_message:
                try:
                    original_text = update.message.reply_to_message.text
                    # Regex দিয়ে আইডি খুঁজে বের করা
                    match = re.search(r'ID:\s*(\d+)', original_text)
                    if match:
                        target_id = int(match.group(1))
                        await context.bot.send_message(chat_id=target_id, text=f"<b>Reply from Support:</b>\n\n{update.message.text}", parse_mode='HTML')
                        await update.message.reply_text(f"✅ Reply delivered to {target_id}")
                except Exception as e:
                    print(f"Reply Error: {e}")

        new_app.add_handler(CommandHandler("start", child_start))
        new_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, child_handle))
        
        await new_app.initialize()
        await new_app.start()
        await new_app.updater.start_polling()
        return True
    except Exception as e:
        print(f"Error starting child bot: {e}")
        return False

# --- মেইন মাস্টার বটের কমান্ডস ---
async def add_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    
    if len(context.args) == 0:
        await update.message.reply_text("Usage: /addbot [TOKEN]")
        return
    
    token = context.args[0]
    await update.message.reply_text("🔄 Connecting your bot to the support channel...")
    
    success = await run_new_bot(token)
    if success:
        await update.message.reply_text(f"✅ <b>Bot Connected!</b>\nAll messages will now go to channel: <code>{LOG_CHANNEL_ID}</code>", parse_mode='HTML')
    else:
        await update.message.reply_text("❌ Failed! Check token or bot admin rights.")

async def main_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>Jeet's Bot Factory 🏭</b>\nUse /addbot [token] to link a support bot to your channel.", parse_mode='HTML')

def main():
    Thread(target=run_flask).start()
    master_app = Application.builder().token(MAIN_BOT_TOKEN).build()
    master_app.add_handler(CommandHandler("start", main_start))
    master_app.add_handler(CommandHandler("addbot", add_bot))
    
    print("Master Bot is running...")
    master_app.run_polling()

if __name__ == '__main__':
    main()
  
