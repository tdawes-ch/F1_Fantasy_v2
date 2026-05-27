class ScraperError(Exception):
    # Base exception for scraper errors
    pass


def scrape(url):
    raise ScraperError("Invalid URL")


def main():
    scrape("bad_url")


main()