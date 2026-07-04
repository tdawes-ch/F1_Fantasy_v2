from unidecode import unidecode

def time_to_seconds(time_str: str) -> float | None:
    """Converts time data stored in a string to a float (or none, if unconvertable)

    Args:
        time_str (str): The time, int the format HH:MM:SS.mmm or MM:SS.mmm

    Returns:
        float | None: The time, but in seconds.milliseconds
    """
    if not time_str:
        return None
    
    try:
        parts = time_str.split(':')
        
        # Reverse parts so we always have seconds at index 0, minutes at 1, hours at 2
        # This handles both "1:23:06.801" and "23:06.801" cases
        parts.reverse()
        
        seconds = float(parts[0]) # Seconds and milliseconds
        
        if len(parts) > 1:
            seconds += float(parts[1]) * 60 # Add minutes
            
        if len(parts) > 2:
            seconds += float(parts[2]) * 3600 # Add hours
            
        return round(seconds,3)
    except:
        return None

def create_driver_id(fname: str, lname: str) -> str:
    """Generates the driver ID from a given first name and last name

    Args:
        fname (str): Driver's first name
        lname (str): Driver's last name

    Returns:
        str: Generated driver ID
    """
    return f"{unidecode("_".join(fname.split()))}_{unidecode("_".join(lname.split()))}".lower()

#print(create_driver_id(fname="José l  hamilton",lname="Hamilton"))