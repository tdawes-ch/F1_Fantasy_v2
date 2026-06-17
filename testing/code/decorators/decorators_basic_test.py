def log_activity(func):
    def wrapper():
        print(func.__name__, "is starting...")
        func()
        print(func.__name__, "has finished!")
    return wrapper

@log_activity
def download_file():
    print("Downloading a large file...")

@log_activity
def clear_cache():
    print("Clearing the system cache...")

# Test them out
download_file()
print("---")
clear_cache()