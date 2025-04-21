import requests
from bs4 import BeautifulSoup
import time
from google import genai

client = genai.Client(api_key = "API_key_here")

def fetch_article_links(site_url):
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
  }
  data = requests.get(site_url, headers = headers, timeout = 360)

  soup = BeautifulSoup(data.text, 'html.parser')

  links = []

  video_cards = soup.select('.flag-video')
  for video_card in video_cards:
      video_card.decompose()
  
  live_cards = soup.select('.flag-live')
  for live_card in live_cards:
      live_card.decompose()

  article_cards = soup.select('.cardText')
  headline_cards = soup.select('.primaryHeadlineLink')

  if not headline_cards[0].select_one('.flag-video'):
    url = headline_cards[0].get("href")
    if not url.startswith('http'):
      url = f"https://www.cbc.ca{url}"
    links.append(url)

  
  
  for card in article_cards:
    if card.select_one('.flag-video'):
      continue
      
    url = card.get("href")
    if url.startswith("https://newsinteractives.cbc.ca/"):
      continue
    
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
      article_text += " "
  
  # print("Article Title: ", title)
  # print("Article Content: ", article_text)
  
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
  for i in range(len(article_links)):
    response = summarize_with_llm(get_article_content(article_links[i]))

    summaries.append(response)

    print("Summary of Article #", i + 1)
    print(response)
    print("\n")

if __name__ == "__main__":
  main()