import requests
from bs4 import BeautifulSoup

url = "https://blog.python.org/2026/08/the-python-documentation-is-now-available-in-russian"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

article = soup.find("article")

if article:
    print(article.prettify()[:5000])
else:
    print("Article not found")
