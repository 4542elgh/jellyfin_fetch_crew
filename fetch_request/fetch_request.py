import time
import requests

def get_all_crew_ids(request_env: dict) -> set:
    """
    Fetch all crew IDs from the Jellyfin API.
    Returns:
        set: A set of all crew IDs.
    """
    # Fetch all Cast and Crew persons, TIL try/except does not count as a scope
    try:
        response = requests.get(
            f"{request_env.get('BASE_URL')}/emby/Persons",
            params = {"api_key": request_env.get("API_KEY")},
            timeout = request_env.get("TIMEOUT")
        )
        response.raise_for_status()
        data = response.json() # Setting data here can be use later
    except (requests.HTTPError, requests.exceptions.Timeout, requests.JSONDecodeError) as e:
        print(f"Error fetching all crew and casts: {e}. Exiting...")
        exit(0)


    # Get every cast and crew id, doesnt matter if they have a picture or not. Sometimes the person have a picture hash but still display blank
    ids = set()
    for item in data.get('Items', []):
        if item.get('Id'):
            ids.add(item.get('Id'))
    return ids


def get_cast_and_crew(request_env: dict, person_id: str) -> None:
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
                f"{request_env.get('BASE_URL')}/Users/{request_env.get('USERID')}/Items/{person_id}",
                params = {"api_key": request_env.get("API_KEY")},
                timeout = request_env.get("TIMEOUT") # This needs to be high, multithread request basically is a mini ddos your Jellyfin server
            )
            detail_response.raise_for_status()
            break # If not raise for status, break out (this was caught in testing, unit testing does its work)
        except (requests.exceptions.Timeout, requests.RequestException) as e:
            if attempt == max_retries - 1:
                print(f"Error fetching details for person {person_id}: {e}")
                break
            else:
                print(f"Retry attempt #{attempt + 1} for person {person_id}")
                time.sleep(1)
                continue
