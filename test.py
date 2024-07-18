import requests
from bs4 import BeautifulSoup

class HtmlScraperService:
    def __init__(self):
        self.client = requests.Session()

    def fetch_html(self, url):
        try:
            response = self.client.get(url)
            response.raise_for_status()  # This will raise an HTTPError for bad responses
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
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

# Example usage
if __name__ == "__main__":
    scraper = HtmlScraperService()
    url = 'https://wuzzuf.net/search/jobs/?q=back%20end%20laravel%20&a=hpb'
    html = scraper.fetch_html(url)
    if html:
        jobs = scraper.parse_html(html)
        for job in jobs:
            print(job)
