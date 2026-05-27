class ScraperError(Exception):
    # Base exception for scraper errors
    pass

def scrape(url):
    raise ScraperError("Invalid URL")


def main():
    try:
        scrape("bad_url")
    except ScraperError as e:
        print("ScraperError:", e)
        print("Try again")


main()