import requests
from bs4 import BeautifulSoup
import csv
import os

def scrape_article_data():
    # Input and output CSV files
    input_csv = 'articles_urls.csv'
    output_csv = 'articles_data.csv'
    
    # Load existing IDs from the output CSV to prevent duplicates
    scraped_ids = set()
    if os.path.exists(output_csv):
        with open(output_csv, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                scraped_ids.add(row["ID"])

    # Open the output CSV and write header if it doesn't exist
    write_header = not os.path.exists(output_csv)
    with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header:
            writer.writerow(["ID", "Title", "Date", "Image", "Text"])  # Write header

    # Read URLs and IDs from the input CSV
    with open(input_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            article_id = row['ID']
            url = row['URL']
            
            # Skip if article has already been scraped
            if article_id in scraped_ids:
                print(f"Article {article_id} already scraped, skipping.")
                continue

            try:
                # Fetch the page content
                response = requests.get(url)
                if response.status_code != 200:
                    print(f"Failed to retrieve {url}. Status code: {response.status_code}")
                    continue

                # Parse the page content with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract Title
                title = soup.find('h1', class_='title').get_text(strip=True) if soup.find('h1', class_='title') else "N/A"

                # Extract Date
                date = soup.find('li', class_='time').get_text(strip=True) if soup.find('li', class_='time') else "N/A"

                # Extract Image URL
                image_tag = soup.find('img', class_='img-responsive center_position')
                image = image_tag['src'] if image_tag else "N/A"

                # Extract Text
                text_content = []
                story_div = soup.find('div', class_='story')
                if story_div:
                    paragraphs = story_div.find_all('p')
                    for p in paragraphs:
                        text_content.append(p.get_text(strip=True))
                text = " ".join(text_content) if text_content else "N/A"

                # Write the scraped data to the output CSV immediately
                with open(output_csv, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([article_id, title, date, image, text])

                # Add the article ID to scraped_ids set to avoid future duplicates
                scraped_ids.add(article_id)

                print(f"Scraped data from {url}")

            except Exception as e:
                print(f"Error processing {url}: {e}")

# Run the scraping function
scrape_article_data()
