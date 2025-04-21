import requests
from bs4 import BeautifulSoup
import time
from google import genai

client = genai.Client(api_key = "API_KEY_HERE")

def fetch_article_links(site_url):
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }
  data = requests.get(site_url, headers = headers, timeout = 360)

  soup = BeautifulSoup(data.text, 'html.parser')

  links = []

  article_cards = soup.select('.card')
  headline_cards = soup.select('.primaryHeadlineLink')

  for headline in headline_cards:
    parent = headline.parent
    if (headline.select_one('.flag-video') or (parent and parent.select_one('.flag-video'))):
      continue
    
    if headline and 'href' in headline.attrs:
      url = headline['href']
      if not url.startswith('http'):
          url = f"https://www.cbc.ca{url}"
      if url not in links:
          links.append(url)
  
  for card in article_cards:
    if card.select_one('.flag-video'):
      continue
      
    link_element = card.select_one('a')
    if link_element and 'href' in link_element.attrs:
      url = link_element['href']
      if not url.startswith('http'):
          url = f"https://www.cbc.ca{url}"
      links.append(url)

  return links[:7]

def get_article_content(url):
  headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }
  data = requests.get(url, headers = headers, timeout = 360)
  soup = BeautifulSoup(data.text, 'html.parser')

  title_tag = soup.select_one("h1")
  title = "No title found"
  if (title_tag):
    title = title_tag.text.strip()

  article_div = soup.select(".story")
  article_text = ""

  for article in article_div:
    article_paragraphs = article.select('p')

    for paragraph in article_paragraphs:
      article_text += paragraph.text.strip()
  
  return {
    'title': title,
    'content': article_text
  }

def summarize_with_llm(article):
  query = "Can you help summarize this article? Please also state the title.\nThe title is: "
  query += article['title']
  query += "\nThe contents are below:\n"
  query += article['content']

  response = client.models.generate_content(model = "gemini-2.0-flash", contents = query)
  
  return response.text

def main():
  site_url = "https://www.cbc.ca/news"

  article_links = fetch_article_links(site_url)

  summaries = []
  
  response = summarize_with_llm(get_article_content(article_links[0]))

  summaries.append(response)

  print("Summary of Article #", 1)
  print(response)
  print("\n")

if __name__ == "__main__":
  main()