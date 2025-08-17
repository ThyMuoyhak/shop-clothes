import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from TikTokApi import TikTokApi

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# TikTok URL regex
TIKTOK_URL_PATTERN = re.compile(r'https?://(www\.)?(tiktok\.com|vm\.tiktok\.com|m\.tiktok\.com)/')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Send me a TikTok link to download!")

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if not TIKTOK_URL_PATTERN.match(url):
        await update.message.reply_text("❌ Invalid TikTok URL.")
        return

    msg = await update.message.reply_text("⏳ Downloading video, please wait...")
    
    try:
        # Async TikTok session
        async with TikTokApi() as api:
            video = await api.video(url=url)
            video_bytes = await video.bytes()
            
            await msg.delete()
            
            await update.message.reply_video(video=video_bytes, caption="✅ Downloaded!")
            logger.info(f"Video sent to user {update.effective_user.id}")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await msg.edit_text(f"❌ Error downloading video: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a TikTok video link and I will download it for you!")

async def handle_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎵 Please send a TikTok video link!")

def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set in environment!")
        return

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'tiktok\.com|vm\.tiktok\.com|m\.tiktok\.com'), download_tiktok))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_other))
    
    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
