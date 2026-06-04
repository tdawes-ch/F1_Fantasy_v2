"""
does a ping to google.com.

If that fails, there's something up with the network
"""
import requests
from requests.exceptions import RequestException

def test_outbound_connection(url: str = "https://www.google.com") -> tuple[bool, None | RequestException]:
    try:
        r = requests.get(url)
        return True, None
    except RequestException as e:
        return False, e