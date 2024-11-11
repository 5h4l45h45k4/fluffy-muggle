import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import os

def scrape_urls():
    # Initialize variables
    page_number = 1
    origin_url = "https://www.tasnimnews.com/fa/service/11/%D9%86%D8%B8%D8%A7%D9%85%DB%8C-%D8%AF%D9%81%D8%A7%D8%B9%DB%8C-%D8%A7%D9%85%D9%86%DB%8C%D8%AA%DB%8C?page={}"
    base_url = "https://www.tasnimnews.com"  # Base URL to prepend
    csv_file = 'articles_urls.csv'
    
    # Initialize a set to keep track of scraped IDs
    scraped_ids = set()

    # Load existing IDs from the CSV if the file exists
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                scraped_ids.add(row["ID"])

    # Open CSV file and write header if it doesn't exist
    write_header = not os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["ID", "Year", "Month", "Day", "Title", "URL"])  # Write header

    # Regex pattern to extract the ID, year, month, day, and title from the URL
    url_pattern = re.compile(r"/fa/news/(\d{4})/(\d{2})/(\d{2})/(\d+)/(.+)$")

    # Scrape URLs from each page
    while True:
        # Fetch the page content
        response = requests.get(origin_url.format(page_number))
        if response.status_code != 200:
            print(f"Failed to retrieve page {page_number}. Status code: {response.status_code}")
            break

        # Parse the page content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all <article class="list-item"> elements and their <a href> links
        articles = soup.find_all('article', class_='list-item')
        if not articles:
            print(f"No articles found on page {page_number}. Ending scrape.")
            break

        # Extract and write URLs and additional details to CSV
        new_entries = []
        for article in articles:
            link = article.find('a', href=True)
            if link:
                # Construct full URL and extract details using regex
                full_url = base_url + link['href']
                match = url_pattern.search(link['href'])
                if match:
                    year, month, day, article_id, title = match.groups()
                    title = title.replace("-", " ")  # Replace hyphens in title with spaces

                    # Skip if ID is already scraped
                    if article_id in scraped_ids:
                        continue

                    # Add new entry to list and mark ID as scraped
                    new_entries.append([article_id, year, month, day, title, full_url])
                    scraped_ids.add(article_id)

        # Append new entries to CSV
        if new_entries:
            with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(new_entries)
            print(f"Scraped page {page_number} and saved {len(new_entries)} new URLs to {csv_file}")
        else:
            print(f"No new entries on page {page_number}.")

        # Increment page number and move to the next page
        page_number += 1
        time.sleep(1)  # Pause briefly to avoid overwhelming the server

# Run the scraping function
scrape_urls()
