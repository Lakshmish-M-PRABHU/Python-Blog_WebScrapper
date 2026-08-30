import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from database import get_db_connection


BASE_URL = "https://blog.python.org"


def get_post_urls():
    urls = []
    page = 1

    while True:
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}/page/{page}/"

        print(f"Checking page {page}: {url}")

        response = requests.get(url, timeout=30)

        # Stop when the page doesn't exist
        if response.status_code == 404:
            break

        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        posts = soup.select("article.post-card a")

        if not posts:
            break

        new_posts = 0

        for post in posts:
            href = post.get("href")

            if href:
                full_url = urljoin(BASE_URL, href)

                if full_url not in urls:
                    urls.append(full_url)
                    new_posts += 1

        print(f"Found {new_posts} new posts")

        page += 1

    return urls

def scrape_article(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    article = soup.find("article")

    if not article:
        return None

    # -------------------------
    # Title
    # -------------------------

    title = article.select_one("h1")

    # -------------------------
    # Author
    # -------------------------

    author = article.select_one("header a[href^='/authors/']")

    # -------------------------
    # Date
    # -------------------------

    date = article.select_one("time")

    # -------------------------
    # Content
    # -------------------------

    body = article.select_one(
        "div.animate-fade-up.stagger-1"
    )

    content = []

    if body:
        for element in body.find_all(["h2", "h3", "p"]):

            # Clean the text
            text = element.get_text(" ", strip=True)

            if text:
                content.append(text)

    # -------------------------
    # Clean date
    # -------------------------

    published_date = None

    if date:
        datetime_value = date.get("datetime")

        if datetime_value:
            published_date = datetime_value[:10]
        else:
            published_date = date.get_text(" ", strip=True)

    # -------------------------
    # Return article
    # -------------------------

    return {
        "title": title.get_text(" ", strip=True) if title else None,
        "author": author.get_text(" ", strip=True) if author else None,
        "date": published_date,
        "url": url,
        "content": "\n\n".join(content)
    }


def save_post(post):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO posts (
                title,
                author,
                published_date,
                url,
                content
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING
        """

        cursor.execute(
            query,
            (
                post["title"],
                post["author"],
                post["date"],
                post["url"],
                post["content"]
            )
        )

        connection.commit()

        if cursor.rowcount == 1:
            print(f"✓ Saved: {post['title']}")
        else:
            print(f"- Already exists: {post['title']}")

    except Exception as e:
        connection.rollback()
        print(f"✗ Database error for {post['url']}")
        print(e)

    finally:
        cursor.close()
        connection.close()


def main():

    print("Starting Python Blog scraper...\n")

    # -------------------------
    # Get all post URLs
    # -------------------------

    urls = get_post_urls()

    print(f"Posts found: {len(urls)}\n")

    # -------------------------
    # Scrape every article
    # -------------------------

    for index, url in enumerate(urls, start=1):

        print(f"[{index}/{len(urls)}] Scraping:")
        print(url)

        try:
            post = scrape_article(url)

            if not post:
                print("✗ Article not found\n")
                continue

            save_post(post)

        except requests.RequestException as e:
            print(f"✗ Request failed: {e}")

        except Exception as e:
            print(f"✗ Unexpected error: {e}")

        print()


if __name__ == "__main__":
    main()

