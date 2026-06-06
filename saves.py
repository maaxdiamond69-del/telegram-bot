import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

BOT_TOKEN = "8763008810:AAFHttywsRDFSBhvnyEwnwH1uJg9lKKRnEs"

WEBSITE_1 = "https://ffaccesstokenconverter.onrender.com/"
WEBSITE_2 = "https://version-common-redflamenco.vercel.app/"

async def process_flow(user_link):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Website 1
        await page.goto(WEBSITE_1, wait_until="networkidle")
        await page.fill("input", user_link)
        await page.click("button")
        await page.wait_for_timeout(8000)

        text1 = await page.locator("body").inner_text()
        match = re.search(r"[a-fA-F0-9]{40,}", text1)

        if not match:
            await browser.close()
            return "❌ Access Token not found"

        token = match.group(0)

        # Website 2
        await page.goto(WEBSITE_2, wait_until="networkidle")
        await page.fill("input", token)

        await page.get_by_role("button", name=re.compile("verify", re.I)).click()
        await page.wait_for_timeout(8000)

        final_text = await page.locator("body").inner_text()

        await browser.close()

        return final_text.strip()

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_link = update.message.text.strip()

    msg = await update.message.reply_text("⏳ Processing...")

    try:
        result = await process_flow(user_link)

        if len(result) > 4000:
            result = result[:4000]

        await msg.edit_text(result)

    except Exception as e:
        await msg.edit_text(f"❌ Error\n\n{str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

import asyncio

async def main():
    print("Bot Running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
