import re
import requests
from bs4 import BeautifulSoup, Tag

TOP_25_ARTICLES_URL : str = 'https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report'
ROOT_URL : str = 'https://en.wikipedia.org'

# Goes to https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report and returns the list of urls to the listed articles
def get_top_25_urls() -> dict[str, str] | None:
    articles : dict[str, str] = {}

    response : requests.Response = requests.get(TOP_25_ARTICLES_URL)
    if response.status_code == 200:
        soup : BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        table : Tag = soup.find(class_='wikitable')

        if table:
            rows : list[Tag] = table.find_all('tr')[1:] # ignore first row (headers)
            for row in rows:
                try:
                    article : Tag = row.find_all('td')[1] # only look at article name column (which has url)
                    url : str = f'{ROOT_URL}{article.find('a').get('href')}'
                    name : str = article.find('a').get_text()
                    articles[name] = url
                except:
                    print('Failed to find link to an article')
        else:
            print('Failed to find wikitable')
            return None
    else:
        print(f'Failed to get URLs with error code: {response.status_code} :(')
        return None

    return articles

# Gets the text of a Wikipedia article its url
def read_article(url : str) -> str:
    response : requests.Response = requests.get(url)
    text : str = ''

    if response.status_code == 200:
        soup : BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        for bad_tag in soup(['script', 'style']): bad_tag.extract()
        content : Tag = soup.find(id='mw-content-text')

        if content:
            text = content.get_text()
            lines = (line.strip().lower() for line in text.splitlines()) # break into lines and remove leading and trailing space on each
            chunks = (phrase.strip() for line in lines for phrase in line.split(' ')) # break multi-headlines into a line each
            text = ' '.join(chunk for chunk in chunks if chunk)  # remove blank lines
            text = re.sub(r'\[\d+]', '', text) # remove citations
            text = re.sub(r'\[[a-z|A-Z]]', '', text) # remove non-numeric citations
            text = re.sub(r'[^\w\s\'\-]', '', text) # remove non-word characters
            text = re.sub(r'\s\s+', ' ', text)  # remove multi-spaces
        else: print(f'Failed to read content of this article: {url}')

    else: print(f'Failed to read {url} with error code: {response.status_code}')

    return text

# Creates a list of the text of the top 25 articles of Wikipedia for the week
def read_top_25_articles() -> dict[str, list[str]] | None:
    articles_text : dict[str, list[str]] = {'name':[], 'text':[]}
    articles_url : dict[str, str] = get_top_25_urls() # get urls to scrape

    if articles_url is None: return articles_text

    for article in articles_url:
        text : str = read_article(articles_url[article])
        if text != '':
            articles_text['name'].append(article)
            articles_text['text'].append(text)

    return articles_text
