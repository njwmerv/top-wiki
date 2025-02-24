import re
import requests
from bs4 import BeautifulSoup, Tag

TOP_25_ARTICLES_URL : str = 'https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report'
ROOT_URL : str = 'https://en.wikipedia.org'

# Goes to https://en.wikipedia.org/wiki/Wikipedia:Top_25_Report and returns the list of urls to the listed articles
def get_top_25_urls() -> list[str]:
    urls : list[str] = []

    response : requests.Response = requests.get(TOP_25_ARTICLES_URL)
    if response.status_code == 200:
        soup : BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        table : Tag = soup.find(class_='wikitable')

        if table:
            rows : list[Tag] = table.find_all('tr')[1:] # ignore first row (headers)
            for row in rows:
                try:
                    article : Tag = row.find_all('td')[1] # only look at article name column (which has url)
                    urls.append(f'{ROOT_URL}{article.find('a').get('href')}')
                except:
                    print('Failed to find link to an article')
        else:
            print('Failed to find wikitable')
            return []
    else:
        print(f'Failed to get URLs with error code: {response.status_code} :(')
        return []

    return urls

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
            lines = (line.strip() for line in text.splitlines()) # break into lines and remove leading and trailing space on each
            chunks = (phrase.strip() for line in lines for phrase in line.split('  ')) # break multi-headlines into a line each
            text = ' '.join(chunk for chunk in chunks if chunk)  # remove blank lines
            text = re.sub(r'\[\d+]', '', text)
            text = re.sub(r'\[a]', '', text)
        else:
            print(f'Failed to read content of this article: {url}')
    else:
        print(f'Failed to read {url} with error code: {response.status_code}')
    return text

# Creates a list of the text of the top 25 articles of Wikipedia for the week
def read_top_25_articles() -> list[str]:
    articles : list[str] = []
    urls : list[str] = get_top_25_urls()
    for article_url in urls:
        article_text : str = read_article(article_url)
        if article_text != '': articles.append(article_text)
    return articles

