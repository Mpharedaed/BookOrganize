import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urljoin
import logging
import re

def clean_title(title):
    title = title.replace('_', ' ')
    title = re.sub(r'[^\w\s]', '', title)
    title = title.lower()
    title = re.split(r'[:-]', title)[0].strip()
    
    abbreviations = {
        'ave.': 'avenue',
        'st.': 'street',
    }
    for abbr, full_word in abbreviations.items():
        title = title.replace(abbr, full_word)
    
    title = title.replace('’', "'").replace('–', '-')
    title = re.sub(r'\(.*?\)', '', title)
    title = title.strip()
    
    return title

def process_title(title):
    base_search_url = "https://www.goodreads.com/search?q="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    cleaned_title = clean_title(title)
    search_query = quote_plus(cleaned_title)
    search_url = f"{base_search_url}{search_query}"
    
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        first_book_link = soup.find('a', class_='bookTitle')
        
        if first_book_link:
            book_url = urljoin("https://www.goodreads.com/", first_book_link.get('href'))
            logging.info(f"First Book URL for '{title}': {book_url}")

            book_response = requests.get(book_url, headers=headers)
            book_response.raise_for_status()
            book_soup = BeautifulSoup(book_response.content, 'html.parser')

            genre_container = book_soup.find('span', class_='BookPageMetadataSection__genrePlainText')
            genres = []
            if genre_container:
                genre_buttons = genre_container.find_all_next('a', class_='Button--tag-inline')
                for i, genre in enumerate(genre_buttons):
                    if i < 6:
                        genre_text = genre.text.strip()
                        genres.append(genre_text)
                    else:
                        break

            rating_span = book_soup.find('div', class_='RatingStatistics__rating')
            rating = rating_span.text.strip() if rating_span else None

            ratings_container = book_soup.find('div', class_='RatingStatistics')
            if ratings_container:
                total_raters_span = ratings_container.find('span', attrs={'data-testid': 'ratingsCount'})
                total_raters = total_raters_span.text.strip() if total_raters_span else None

            ratings_histogram = book_soup.find('div', class_='RatingsHistogram')
            if ratings_histogram:
                rating_bars = ratings_histogram.find_all('div', class_='RatingsHistogram__bar')
                ratings = {}
                for bar in rating_bars:
                    star_rating = bar.find('div', class_='RatingsHistogram__labelTitle').text.strip()
                    total_ratings = bar.find('div', class_='RatingsHistogram__labelTotal').text.strip()
                    ratings[star_rating] = total_ratings

            publish_date_p = book_soup.find('p', attrs={'data-testid': 'publicationInfo'})
            if publish_date_p:
                publish_date_text = publish_date_p.text.strip()
                publish_date_match = re.search(r'\b(\w+ \d{1,2}, \d{4})\b', publish_date_text)
                publish_date = publish_date_match.group(1) if publish_date_match else None
            else:
                publish_date = None

            pages_p = book_soup.find('p', attrs={'data-testid': 'pagesFormat'})
            pages_info = None
            if pages_p:
                pages_text = pages_p.text.strip()
                pages_info = re.search(r'(\d+)\s+pages', pages_text)
                if pages_info:
                    pages_info = pages_info.group(1)

            description_span = book_soup.find('span', class_='Formatted')
            description = description_span.text.strip() if description_span else None
            
            image_container = book_soup.find('img', class_='ResponsiveImage')
            image_url = image_container.get('src') if image_container else None

            author_name = None
            author_description = None

            about_author_section = book_soup.find('div', class_='PageSection__title', text='About the author')
            if about_author_section:
                author_name_container = about_author_section.find_next('span', class_='ContributorLink__name')
                author_name = author_name_container.text.strip() if author_name_container else None
                
                author_description_container = about_author_section.find_next('div', class_='DetailsLayoutRightParagraph')
                if author_description_container:
                    author_description = author_description_container.text.strip()

            return {
                'Title': title,
                'Book_URL': book_url,
                'Genres': genres,
                'Rating': rating,
                'Total_Raters': total_raters,
                'Ratings': ratings,
                'Publish_Date': publish_date,
                'Pages': pages_info,
                'Description': description,
                'Image_URL': image_url,
                'Author_Name': author_name,
                'Author_Description': author_description
            }
        else:
            logging.warning(f"No results found for: {title}")
            return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error processing title '{title}': {e}")
        return None
    except Exception as e:
        logging.error(f"An error occurred while processing title '{title}': {e}")
        return None
