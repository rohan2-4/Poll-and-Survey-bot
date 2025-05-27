from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)
from config import BOT_TOKEN
import sqlite3
import csv
import os

# Database initialization
def init_db():
    conn = sqlite3.connect('polls.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS polls
                 (poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  admin_id INTEGER,
                  question TEXT,
                  options TEXT,
                  is_anonymous BOOLEAN)''')
                  
    c.execute('''CREATE TABLE IF NOT EXISTS responses
                 (response_id INTEGER PRIMARY KEY AUTOINCREMENT,
                  poll_id INTEGER,
                  user_id INTEGER,
                  answer TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# Conversation states
QUESTION, OPTIONS, ANONYMITY = range(3)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 Welcome to Poll Bot!\n\n"
        "Create polls with /createpoll\n"
        "Vote using /vote <poll_id>\n"
        "Export results with /export <poll_id>"
    )

async def create_poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != 'private':
        await update.message.reply_text("⚠️ Please create polls in a private chat with me.")
        return ConversationHandler.END
    
    await update.message.reply_text("📝 Please enter your poll question:")
    return QUESTION

async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question'] = update.message.text
    await update.message.reply_text("🔢 Enter options separated by commas (e.g., Option 1, Option 2, Option 3):")
    return OPTIONS

async def receive_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    options = [opt.strip() for opt in update.message.text.split(',') if opt.strip()]
    if len(options) < 2:
        await update.message.reply_text("❌ Please provide at least 2 options.")
        return OPTIONS
    
    context.user_data['options'] = options
    
    keyboard = [
        [InlineKeyboardButton("Anonymous 🙈", callback_data='True'),
         InlineKeyboardButton("Non-Anonymous 👤", callback_data='False')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("🔒 Choose poll type:", reply_markup=reply_markup)
    return ANONYMITY

async def receive_anonymity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    is_anonymous = query.data == 'True'
    admin_id = query.from_user.id
    
    # Save to database
    conn = sqlite3.connect('polls.db')
    c = conn.cursor()
    c.execute('''INSERT INTO polls (admin_id, question, options, is_anonymous)
                 VALUES (?, ?, ?, ?)''',
              (admin_id, 
               context.user_data['question'],
               ','.join(context.user_data['options']),
               is_anonymous))
    conn.commit()
    poll_id = c.lastrowid
    conn.close()
    
    # Create confirmation message
    options_text = '\n'.join([f"▫️ {opt}" for opt in context.user_data['options']])
    await query.edit_message_text(
        f"✅ Poll Created Successfully!\n\n"
        f"📌 Question: {context.user_data['question']}\n"
        f"📋 Options:\n{options_text}\n\n"
        f"🆔 Poll ID: {poll_id}\n"
        f"🔗 Share this ID with participants to collect responses"
    )
    return ConversationHandler.END

async def export_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /export <poll_id>\nExample: /export 123")
        return
    
    poll_id = context.args[0]
    
    conn = sqlite3.connect('polls.db')
    c = conn.cursor()
    
    # Verify poll ownership
    c.execute('SELECT admin_id FROM polls WHERE poll_id = ?', (poll_id,))
    poll = c.fetchone()
    
    if not poll:
        await update.message.reply_text("❌ Poll not found!")
        return
    
    if poll[0] != update.message.from_user.id:
        await update.message.reply_text("⛔ You must be the poll creator to export results!")
        return
    
    # Get results
    c.execute('SELECT answer, COUNT(*) FROM responses WHERE poll_id = ? GROUP BY answer', (poll_id,))
    results = c.fetchall()
    
    if not results:
        await update.message.reply_text("❌ No responses found for this poll!")
        return
    
    # Generate CSV
    filename = f"poll_{poll_id}_results.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Answer', 'Votes'])
        writer.writerows(results)
    
    # Send file
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=filename,
        caption=f"📤 Exported results for Poll {poll_id}"
    )
    
    # Cleanup
    os.remove(filename)
    conn.close()

# Voting
async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Usage: /vote <poll_id>")
        return

    poll_id = context.args[0]

    conn = sqlite3.connect('polls.db')
    c = conn.cursor()
    c.execute("SELECT question, options, is_anonymous FROM polls WHERE poll_id = ?", (poll_id,))
    poll = c.fetchone()
    conn.close()

    if not poll:
        await update.message.reply_text("❌ Poll not found!")
        return

    question, options, is_anonymous = poll
    options = options.split(',')

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"{poll_id}:{opt}")] for opt in options]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(f"🗳️ {question}", reply_markup=reply_markup)

async def handle_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        poll_id, answer = query.data.split(':', 1)
        user_id = query.from_user.id

        conn = sqlite3.connect('polls.db')
        c = conn.cursor()

        c.execute("SELECT * FROM responses WHERE poll_id = ? AND user_id = ?", (poll_id, user_id))
        if c.fetchone():
            await query.edit_message_text("❗ You have already voted in this poll.")
            conn.close()
            return

        c.execute("INSERT INTO responses (poll_id, user_id, answer) VALUES (?, ?, ?)", (poll_id, user_id, answer))
        conn.commit()
        conn.close()

        await query.edit_message_text("✅ Your vote has been recorded. Thank you!")

    except Exception as e:
        await query.edit_message_text("⚠️ Failed to record your vote. Please try again.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('createpoll', create_poll)],
        states={
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question)],
            OPTIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_options)],
            ANONYMITY: [
                CallbackQueryHandler(
                    receive_anonymity,
                    pattern='^(True|False)$'
                )
            ]
        },
        fallbacks=[],
        per_message=False
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('export', export_results))
    application.add_handler(CommandHandler('vote', vote))
    application.add_handler(CallbackQueryHandler(handle_vote, pattern=r'^\d+:.+'))

    application.run_polling()

if __name__ == '__main__':
    main()
