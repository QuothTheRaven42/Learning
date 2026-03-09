import requests
from bs4 import BeautifulSoup
import certifi

base_url = "http://quotes.toscrape.com"
next_page = "/"                                           # start at the first page

while next_page:                                          # loop until no next page found
    response = requests.get(base_url + next_page, verify=certifi.where())
    soup = BeautifulSoup(response.text, "html.parser")

    # Scrape all quotes, authors, and author bio paths into lists for this page
    quotes = [quote.get_text() for quote in soup.find_all("span", class_="text")]
    authors = [author.get_text() for author in soup.find_all("small", class_="author")]
    bios = [a["href"] for a in soup.find_all("a") if a["href"].startswith("/author/")]

    # Loop through each quote/author/bio path as a synced group
    for quote, author, bio in zip(quotes, authors, bios):

        # Make a new request to the author's bio page and scrape birth details
        bio_response = requests.get(base_url + bio, verify=certifi.where())
        bio_soup = BeautifulSoup(bio_response.text, "html.parser")
        born_date = bio_soup.find("span", class_="author-born-date").get_text().strip()
        born_location = bio_soup.find("span", class_="author-born-location").get_text().strip()
        bio_hint = bio_soup.find("div", class_="author-description").get_text().strip()
        bio_hint = bio_hint.replace(author, "they")  # swap author name for "they"
        hint = f"Born {born_date} {born_location}"

        print("\nHere's a quote:")
        print(quote)

        # Give the player 4 attempts to guess the author
        for attempt in range(1, 5):
            guess = input(f"Guess {attempt}/4: Who said this? ").lower()
            if author.lower() == guess:
                print("Right!")
                break  # correct - move to next quote
            elif attempt == 1:
                print(f"Wrong! Hint: They were born on {born_date}.")
            elif attempt == 2:
                print(f"Wrong! Hint: They were born in {born_location}.")
            elif attempt == 3:
                print(f"Wrong! Last hint: {bio_hint}")
            else:
                print(f"Wrong four times! It was {author}.")

    # Check for a next page link - returns None if not found, ending the while loop
    next_button = soup.find("li", class_="next")
    next_page = next_button.find("a")["href"] if next_button else None