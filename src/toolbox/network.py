"""
does a ping to google.com.

If that fails, there's something up with the network
"""
import requests
from requests.exceptions import RequestException
import datetime # potentially some method to calculate time to ping.
from pprint import pprint

def test_outbound_connection(url: str = "https://www.google.com") -> tuple[bool, None | RequestException]:
    """A quick function that pings a URL (default google.com) using the requests module.

    Args:
        url (str, optional): The URL to be pinged, defaults to "https://www.google.com".

    Returns:
        tuple[bool, None | RequestException]: Returns True/False and an error if False (None if True)
    """
    try:
        r = requests.get(url)
        return True, None
    except RequestException as e:
        return False, e
    
import time
import requests

def measure_download_speed(
        test_url: str = "https://speed.cloudflare.com/__down?bytes=10000000" # 10MB stream
        ) -> dict[str, float | int | bool | str | None]:
    """Measures the network download speed to a specific target URL.

    Returns:
        dict: A dictionary of results e.g.:
            {
                "success": True,
                "duration_seconds": 1.042,
                "bytes_downloaded": 102340,
                "mbps": 10.43,       
                "mb_per_sec": 80.12 
                "error": None
            }
    """    
    try:
        start_time = time.perf_counter()
        
        # Stream=True ensures we don't load the entire file into memory at once
        response = requests.get(test_url, stream=True, timeout=10)
        response.raise_for_status()
        
        total_bytes = 0
        # Read the stream in 64KB blocks to track raw data arrival
        for chunk in response.iter_content(chunk_size=65536):
            if chunk:
                total_bytes += len(chunk)
                
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        # Calculate raw speeds
        bytes_per_second = total_bytes / duration if duration > 0 else 0
        megabits_per_second = (bytes_per_second * 8) / 1_000_000  # Mbps
        megabytes_per_second = bytes_per_second / 1_048_576       # MB/s
        
        return {
            "success": True,
            "duration_seconds": round(duration, 3),
            "bytes_downloaded": total_bytes,
            "mbps": round(megabits_per_second, 2),       # Standard network speed unit
            "mb_per_sec": round(megabytes_per_second, 2), # Real-world disk/file speed unit
            "error": None
        }
        
    except requests.RequestException as e:
        return {
            "success": False,
            "duration_seconds": 0.0,
            "bytes_downloaded": 0,
            "mbps": 0.0,
            "mb_per_sec": 0.0,
            "error": str(e)
        }
    
def avg_download_speed(url: str = "https://speed.cloudflare.com/__down?bytes=10000000", 
                       attempts: int = 2) -> dict[str, float | int | bool | str | None]:
    """
    Runs 'attempts' number of the 'measure_download_speed()' function and
    calculates the average.

    Input: 
      url: str, attempts: int = 2

    Returns:
      Returns the same format as measure_download_speed(), but as an average
      e.g.:
            {
                "success": True,
                "duration_seconds": 1.042,
                "bytes_downloaded": 102340,
                "mbps": 10.43,       
                "mb_per_sec": 80.12 
                "error": None
            }
    """
    results = []
    for i in range(attempts):
        speedtest = measure_download_speed(test_url=url)
        if speedtest["error"] is None:
            results.append(measure_download_speed(test_url=url))
        else:
            return speedtest
    
    duration_seconds = 0
    total_bytes = 0
    mbps = 0
    mb_per_sec = 0

    for result in results:
        duration_seconds += result["duration_seconds"]
        total_bytes += result["bytes_downloaded"]
        mbps += result["mbps"]
        mb_per_sec += result["mb_per_sec"]
    try:
        mbps = round(mbps / duration_seconds, 2)
        mb_per_sec = round(mb_per_sec / duration_seconds, 2)
    except:
        mbps = 0
        mb_per_sec = 0
            
    return {
        "success": True,
        "duration_seconds": duration_seconds,
        "bytes_downloaded": total_bytes,
        "mbps": total_bytes,
        "mb_per_sec": 0.0,
        "error": None
    }

import speedtest
import time
def run_speedtest() -> dict[str, float | int | bool | str | None]:
    """Another way of checking speedtest if the other fails after too many runs.

    Returns:
        dict: A summary of the speedtest results e.g.:
            {
                "success": True,
                "duration_seconds": 1.042,
                "bytes_downloaded": 102340,
                "mbps": 10.43,       
                "mb_per_sec": 80.12 
                "error": None
            }
    """
    try:
        # Initialize the Speedtest client
        st = speedtest.Speedtest()
        
        # Get the best server based on ping
        st.get_best_server()
        
        # Record start time to measure duration
        start_time = time.time()
        
        # Run the download test
        # threads=None uses the default allocation
        download_speed_bps = st.download(threads=None)
        
        end_time = time.time()
        duration_seconds = round(end_time - start_time, 2)
        
        # speedtest-cli calculates total bytes implicitly, 
        # but we can derive bytes downloaded during the test duration:
        # download_speed_bps is bits per second. Total bits = speed * duration.
        total_bytes = int((download_speed_bps * duration_seconds) / 8)
        
        # Conversions
        mbps = round(download_speed_bps / 1_000_000, 2)
        mb_per_sec = round(mbps / 8, 2)
        
        return {
            "success": True,
            "duration_seconds": duration_seconds,
            "bytes_downloaded": total_bytes,
            "mbps": mbps,
            "mb_per_sec": mb_per_sec,
            "error": None
        }
        
    except Exception as e:
        return {
            "success": False,
            "duration_seconds": 0.0,
            "bytes_downloaded": 0,
            "mbps": 0.0,
            "mb_per_sec": 0.0,
            "error": str(e)
        }