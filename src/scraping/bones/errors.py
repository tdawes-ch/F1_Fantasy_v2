class ScraperError(Exception):
    # Base exception for scraper errors
    pass

class InvalidUrlError(ScraperError):
    # something up with the url
    pass

class FetchError(ScraperError):
    # url is okay, but something wrong with website. Not code 200 OK
    pass

class FileWriteError(ScraperError):
    # something up when writing the file
    pass

class FilepathError(Exception):
    pass