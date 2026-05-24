"""
Goes through each season:
https://www.formula1.com/en/results/{fyear}/races (format(fyear = year))
given a start year, end year (default start = 1950, default end = this year)

Gets:
- html page prettified by beautifulsoup.prettify()

Outputs html page into:
data/sessions/raw/<year>/<year>.html
"""