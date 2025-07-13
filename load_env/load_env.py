"""
This module loads environment variables from a .env file and provides a dictionary with the necessary configuration for the application.
"""
import os
from dotenv import load_dotenv

def load_env() -> dict:
    """
    Load environment variables from a .env file and return a dictionary with the configuration.
    CORE COUNT is set to the maximum number of CPU cores if "MAX" is specified, otherwise it defaults to 4.
    Exit if required variables are missing.
    Returns:
        dict: A dictionary containing the environment variables.
    """
    load_dotenv()
    # Loading .env file
    env = {
        "API_KEY": os.getenv("API_KEY"),
        "BASE_URL": os.getenv("BASE_URL"),
        "USER": os.getenv("USER"),
        "USERID": os.getenv("USERID"),
        "CORE_COUNT": os.cpu_count() if os.getenv("CORE_COUNT") == "MAX" else int(os.getenv("CORE_COUNT", 4)),
        "TIMEOUT": 30
    }

    if not env.get("API_KEY") or not env.get("BASE_URL") or not env.get("USER") or not env.get("USERID"):
        print("Please set API_KEY, BASE_URL, USER, and USERID in your .env file.")
        exit(1)

    return env
