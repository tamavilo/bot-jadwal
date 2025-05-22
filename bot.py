import os
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)
import gspread
from oauth2client.service_account import ServiceAccountCredentials
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ====== GOOGLE SHEETS SETUP ======
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key("1VZxKAAVADC45dAliQhJ5MWT0g7jlD-UC5IjFlfVRE4U").sheet1  # Ganti dengan nama sheet kamu

# ====== CONVERSATION STATES ======
(TIM1, LOGO1, TIM2, LOGO2, TANGGAL, JAM, KOMPETISI, LINK, LINK2) = range(9)

# ====== BOT COMMANDS ======

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Selamat datang! Bot Ini dibuat oleh @iwan.alfr\n"
        "Gunakan perintah:\n"
        "/mulai - Tambah data\n"
        "/hapus <baris> - Hapus baris data\n"
        "/cancel - Batalkan proses"
    )

async def mulai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏟️ Masukkan nama Tim 1:")
    return TIM1

async def get_tim1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tim1"] = update.message.text
    await update.message.reply_text("🖼️ Masukkan URL Logo Tim 1:")
    return LOGO1

async def get_logo1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["logo1"] = update.message.text
    await update.message.reply_text("🏟️ Masukkan nama Tim 2:")
    return TIM2

async def get_tim2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tim2"] = update.message.text
    await update.message.reply_text("🖼️ Masukkan URL Logo Tim 2:")
    return LOGO2

async def get_logo2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["logo2"] = update.message.text
    await update.message.reply_text("📅 Masukkan Tanggal (cth: 2025-05-21):")
    return TANGGAL

async def get_tanggal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tanggal"] = update.message.text
    await update.message.reply_text("⏰ Masukkan Jam (cth: 20:00):")
    return JAM

async def get_jam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["jam"] = update.message.text
    await update.message.reply_text("🏆 Masukkan Nama Kompetisi:")
    return KOMPETISI

async def get_kompetisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["kompetisi"] = update.message.text
    await update.message.reply_text("🔗 Masukkan Link 1:")
    return LINK

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link"] = update.message.text
    await update.message.reply_text("🔗 Masukkan Link 2:")
    return LINK2

async def get_link2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["link2"] = update.message.text

    data = [
        context.user_data["tim1"],
        context.user_data["logo1"],
        context.user_data["tim2"],
        context.user_data["logo2"],
        context.user_data["tanggal"],
        context.user_data["jam"],
        context.user_data["kompetisi"],
        context.user_data["link"],
        context.user_data["link2"],
    ]

    sheet.append_row(data)
    await update.message.reply_text("✅ Data berhasil disimpan ke Google Sheets.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Proses dibatalkan.")
    return ConversationHandler.END

# ====== FITUR HAPUS BARIS ======



async def hapus_semua(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        all_data = sheet.get_all_values()
        total_rows = len(all_data)

        if total_rows <= 1:
            await update.message.reply_text("✅ Tidak ada data untuk dihapus.")
            return

        # Hapus dari baris terakhir ke baris ke-2 (agar index tetap valid saat delete)
        for i in range(total_rows, 1, -1):
            sheet.delete_rows(i)

        await update.message.reply_text(f"✅ {total_rows - 1} baris berhasil dihapus (kecuali header).")
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal menghapus semua data: {e}")


# ====== MAIN ======

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()  # Ganti token bot

    # Conversation untuk tambah data
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("mulai", mulai)],
        states={
            TIM1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tim1)],
            LOGO1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_logo1)],
            TIM2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tim2)],
            LOGO2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_logo2)],
            TANGGAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tanggal)],
            JAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_jam)],
            KOMPETISI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_kompetisi)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
            LINK2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link2)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Tambahkan handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("hapus_semua", hapus_semua)) #fitur hapus
    app.add_handler(conv_handler)

    print("✅ Bot berjalan...")
    app.run_polling()
