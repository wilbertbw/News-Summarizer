'''
Write a Python program that visits cbc.ca/news

The program should “read” the first 7 news articles and then use an LLM to create a short summary of each article.

The program will output the article headline and the summary produced by AI

Tip:  use any LLM you want for this task.  For example:  https://console.groq.com/home

Note: You will not be judged on the quality of the LLM’s output.
'''
import requests
from bs4 import BeautifulSoup
import openai

openai.api_key = ""

def fetch_article_links(site_url):
  data = requests.get(site_url)
  soup = BeautifulSoup(data.text)
  a_tags = soup.find_all('a')
  links = []

  for i in range(7):
    links.append(a_tags[i].get("href"))
  
  return links

def get_article_content(url):
  data = requests.get(url)
  soup = BeautifulSoup(data.text)

  title_tag = soup.select_one("h1")
  title = "No title found"
  if (title_tag):
    title = title_tag.text.strip()
  
  # article is in the <p> in the <div> with class="story"

  article_div = data.select_one(".story")
  article_text = "Could not extract article."

  if (article_div):
    article_paragraphs = article_div.select('p')

    for paragraph in article_paragraphs:
      article_text = " ".join(paragraph.text.strip())
  
  return {
    'title': title,
    'content': article_text
  }

def summarize_with_llm(article):
  query = "Can you help summarize this article?\nThe title is: "
  query += article['title']
  query += "\nThe contents are below:\n"
  query += article['content']

  messages = [{"role": "system", "content": "You are a intelligent assistant."}]

  messages.append({"role": "user", "content": query})
  
  chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)

  reply = chat.choices[0].message.content
  
  return reply