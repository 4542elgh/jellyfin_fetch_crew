import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dotenv import load_dotenv

load_dotenv()
# Loading .env file
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
USER = os.getenv("USER")
USERID = os.getenv("USERID")
CORE_COUNT = os.cpu_count() if os.getenv("CORE_COUNT") == "MAX" else int(os.getenv("CORE_COUNT", 4))

def main():
    """
    Main function to fetch all cast and crew members from Jellyfin.
    """
    if not API_KEY or not BASE_URL or not USER or not USERID:
        print("Please set API_KEY, BASE_URL, USER, and USERID in your .env file.")
        exit(1)

    # Fetch all Cast and Crew persons, TIL try/except does not count as a scope
    try:
        response = requests.get(
            f"{BASE_URL}/emby/Persons",
            params={"api_key": API_KEY},
            timeout=30
        )
        response.raise_for_status()
        data = response.json() # Setting data here can be use later
    except requests.RequestException as e:
        print(f"Error fetching persons: {e}")
        return

    # Get every cast and crew id, doesnt matter if they have a picture or not. Sometimes the person have a picture hash but still display blank
    ids = set()
    for item in data.get('Items', []):
        ids.add(item.get('Id', ''))

    total_count = len(ids)
    completed_count = 0

    # multithreaded fetching of cast and crew details
    # Max threads on 12700K took about 9 minutes for 14TB media library to complete
    with ThreadPoolExecutor(max_workers=CORE_COUNT) as executor:
        print(f"Fetching details with {CORE_COUNT} threads")
        futures = { executor.submit(get_cast_and_crew, person_id) for person_id in ids }
        # Yield as they complete
        for future in as_completed(futures):
            completed_count += 1
            print(f"\rProgress: {completed_count}/{total_count} ({completed_count/total_count*100:.1f}%)", end="", flush=True)
            future.result()

def get_cast_and_crew(person_id: str) -> None:
    """
    GET request to the detail page of a cast or crew member by their ID.
    Args:
        person_id (str): The crew/cast ID of the person to fetch details for.
    Returns:
        None
    Raises:
        requests.RequestException: If the request to the Jellyfin API fails.
    """
    max_retries = 3

    for attempt in range(max_retries):
        try:
            detail_response = requests.get(
                f"{BASE_URL}/Users/{USERID}/Items/{person_id}",
                params={"api_key": API_KEY},
                timeout=30 # This needs to be high, multithread request basically is a mini ddos your Jellyfin server
            )
            detail_response.raise_for_status()
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                print(f"Error fetching details for person {person_id}: {e}")
            else:
                print(f"Retry attempt #{attempt + 1} for person {person_id}")
                time.sleep(1)
                continue

if __name__ == "__main__":
    main()
