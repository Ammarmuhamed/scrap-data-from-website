import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HtmlScraperService:
    def __init__(self):
        self.client = requests.Session()

    def fetch_html(self, url):
        try:
            response = self.client.get(url)
            response.raise_for_status()  # This will raise an HTTPError for bad responses
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {e}")
            return None

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        jobs = soup.select('a[href^="https://wuzzuf.net/jobs/p/"]')
        data = []

        for job in jobs:
            job_data = {
                'name': job.text.strip(),
                'url': job['href']
            }
            job_parent = job.find_parent().find_parent()
            if job_parent:
                company_name = job_parent.select_one('div > a').text.strip()
                company_location = job_parent.select_one('div > span').text.strip()
                job_data['company'] = {
                    'name': company_name,
                    'location': company_location
                }
                tags = []
                tag_elements = job_parent.find_parent().select("div:nth-child(2) a")
                for tag in tag_elements:
                    if tag.find('span'):
                        name = tag.find('span').text.strip()
                    else:
                        name = tag.text.strip()
                    if not 'href' in tag:
                        continue
                    link = tag['href']
                    tags.append({
                        'name': name,
                        'link': link
                    })
                job_data['tags'] = tags
            data.append(job_data)
        
        return data

async def scrap(update: Update, context: CallbackContext) -> None:
    # Send initial message
    await update.message.reply_text("Scraping in progress...")

    scraper = HtmlScraperService()
    url = 'https://wuzzuf.net/search/jobs/?q=back%20end%20laravel%20&a=hpb'
    html = scraper.fetch_html(url)
    if html:
        jobs = scraper.parse_html(html)
        for job in jobs:
            job_text = f"Job Name: {job['name']}\nURL: {job['url']}\nCompany: {job['company']['name']}\nLocation: {job['company']['location']}"
            if 'tags' in job:
                tags = ', '.join([tag['name'] for tag in job['tags']])
                job_text += f"\nTags: {tags}"
            await update.message.reply_text(job_text)
    else:
        await update.message.reply_text("Failed to fetch jobs.")
    print("Job completed.")



def main() -> None:
    try:
        # Replace 'YOUR_ACTUAL_BOT_TOKEN' with your bot's token
        application = Application.builder().token("7387923572:AAErpRicTTlEhrTtJGFK4MEst0CSfEtHlgM").build()

        # on different commands - answer in Telegram
        application.add_handler(CommandHandler("scrap", scrap))

        # Start the Bot
        application.run_polling()

    except Exception as e:
        logger.error(f"Failed to start the bot: {e}")

if __name__ == '__main__':
    main()
