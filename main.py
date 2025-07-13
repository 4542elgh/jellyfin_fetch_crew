"""
This script fetches all cast and crew members from a Jellyfin server using multithreading.
"""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from fetch_request import fetch_request
from load_env import load_env

env = load_env.load_env()

def main():
    """
    Main function to fetch all cast and crew members from Jellyfin.
    """
    start_time = time.time()
    ids = fetch_request.get_all_crew_ids(env)
    if len(ids) == 0:
        print("Did not find any cast and crew. Exiting...")
        exit(0)
    execute_requests(env, ids)
    end_time = time.time()
    print(f"\nProcessed {len(ids)} crew & cast in {end_time - start_time:.2f} seconds.")


def execute_requests(request_env: dict, ids: set) -> None:
    """
    Execute the requests to fetch cast and crew details using multithreading.
    Args:
        ids (set): A set of crew/cast IDs to fetch details for.
    Returns:
        None
    """
    total_count = len(ids)
    completed_count = 0

    # multithreaded fetching of cast and crew details
    # Max threads on 12700K took about 9 minutes for 14TB media library to complete
    with ThreadPoolExecutor(max_workers = request_env.get("CORE_COUNT")) as executor:
        print(f"Fetching details with {request_env.get('CORE_COUNT')} threads and max timeout of {request_env.get('TIMEOUT')} seconds per request...")
        futures = { executor.submit(fetch_request.get_cast_and_crew, env, person_id) for person_id in ids }
        # Yield as they complete
        for future in as_completed(futures):
            completed_count += 1
            print(f"\rProgress: {completed_count}/{total_count} ({completed_count/total_count*100:.1f}%)", end="", flush=True)
            future.result()


if __name__ == "__main__":
    main()
