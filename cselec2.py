import requests
import re
import time
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')

def fetch_html(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            # Detect if page is a CAPTCHA block
            if "captcha" in response.text.lower():
                print("⚠️ Amazon returned a CAPTCHA page. Try again later or use VPN.")
                return None
            return response.text
        else:
            print(f"HTTP error: {response.status_code}")
            return None
    except requests.RequestException as err:
        print(f"Request failed: {err}")
        return None

def extract_reviews_and_stars(html_content):
    # Main regex patterns
    review_pattern_1 = r'<span[^>]*data-hook="review-body"[^>]*>(.*?)</span>'
    star_pattern_1 = r'<i[^>]*data-hook="review-star-rating"[^>]*><span[^>]*>([\d.]+) out of 5 stars</span>'

    # Fallback regex patterns (Amazon sometimes changes HTML)
    review_pattern_2 = r'<span[^>]*class="a-size-base review-text[^"]*"[^>]*>(.*?)</span>'
    star_pattern_2 = r'<span[^>]*class="a-icon-alt"[^>]*>([\d.]+) out of 5 stars</span>'

    reviews = re.findall(review_pattern_1, html_content, re.DOTALL)
    stars = re.findall(star_pattern_1, html_content)

    if not reviews:  # fallback check
        reviews = re.findall(review_pattern_2, html_content, re.DOTALL)
    if not stars:  # fallback check
        stars = re.findall(star_pattern_2, html_content)

    return reviews, stars

def clean_html(raw_html):
    return re.sub(r'<[^>]+>', '', raw_html).strip()

def map_sentiment_to_stars(score):
    if score >= 0.75:
        return "★  ★  ★  ★  ★"
    elif score >= 0.5:
        return "★  ★  ★  ★  ☆"
    elif -0.5 < score < 0.5:
        return "★  ★  ★  ☆  ☆"
    elif score <= -0.5:
        return "★  ★  ☆  ☆  ☆"
    return "★  ☆  ☆  ☆  ☆"

def analyze_reviews(reviews, stars):
    sia = SentimentIntensityAnalyzer()

    for idx, (raw_review, star) in enumerate(zip(reviews, stars), 1):
        text = clean_html(raw_review)
        sentiment = sia.polarity_scores(text)
        compound = sentiment['compound']

        if compound >= 0.5:
            label = "Positive"
        elif compound <= -0.5:
            label = "Negative"
        else:
            label = "Neutral"

        expected = map_sentiment_to_stars(compound)

        try:
            actual = float(star)
            actual_visual = "★  " * int(actual) + "☆  " * (5 - int(actual))

            print(f"\nReview {idx}: {text}")
            print(f"Star Rating: {star}")
            print(f"Sentiment Scores: {sentiment}")
            print(f"Sentiment Label: {label}")
            print(f"Expected Star Rating: {expected}")
            print(f"Actual Star Representation: {actual_visual.strip()}")

            if expected.strip() == actual_visual.strip():
                print("✅ Sentiment matches star rating.\n")
            else:
                print("❗ Mismatch between sentiment and rating.\n")

        except ValueError:
            print(f"⚠️ Invalid rating format in review {idx}\n")

def main():
    url = input("Enter product URL: ").strip()

    headers = {
        'Sec-Ch-Ua': '"Chromium";v="118", "Brave";v="118", "Not:A-Brand";v="99"',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Ch-Ua-Platform-Version': '"15.0.0"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Sec-Gpc': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/118.0.5993.90 Safari/537.36'
    }

    max_attempts = 3
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1} of {max_attempts}...")
        html = fetch_html(url, headers)
        if not html:
            print("Failed to fetch the page.")
            time.sleep(3)  # wait before retry
            continue

        reviews, stars = extract_reviews_and_stars(html)

        if reviews and stars:
            print(f"\nFound {len(reviews)} reviews and {len(stars)} star ratings.")
            analyze_reviews(reviews, stars)
            break
        else:
            print("Reviews or ratings not found.")
            if attempt < max_attempts - 1:
                print("Retrying...\n")
                time.sleep(3)
            else:
                print("No more retries left.")

    else:
        print("Failed to retrieve reviews and ratings after multiple attempts.")

if __name__ == "__main__":
    main()