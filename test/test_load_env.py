"""
# test/test_load_env.py
Unit tests for the load_env.load_env() function.
It includes tests for: ensuring the correct number of CPU cores is set, handling missing environment variables, and ensuring the function exits with an error message when required variables are not set.
"""
import unittest
from unittest.mock import patch
from load_env import load_env

class TestLoadEnv(unittest.TestCase):
    """
    Unit tests for the load_env.load_env() function.
    """

    def setUp(self):
        self.env = {
            "complete":{
                "BASE_URL": "https://jellyfin.example.com",
                "API_KEY": "test_api_key_123",
                "USER": "john",
                "USERID": "test_user_id_123",
                "CORE_COUNT": "MAX",
                "TIMEOUT": 30
            },
            "complete_no_core_count":{
                "BASE_URL": "https://jellyfin.example.com",
                "API_KEY": "test_api_key_123",
                "USER": "john",
                "USERID": "test_user_id_123",
                "TIMEOUT": 30
            },
            "incomplete": {
                "BASE_URL": "https://jellyfin.example.com"
            }
        }

    @patch("os.getenv")
    @patch("os.cpu_count")
    def test_max_core(self, mock_cpu_count, mock_getenv):
        """
        Test that when 'CORE_COUNT' is set to 'MAX', the function uses the maximum number of CPU cores.
        """
        # Always mock first, then execute. This way execute can take mock values
        mock_cpu_count.side_effect = [8] # This need to be an iterator

        # os.getenv will return base on dict
        def getenv_side_effect(key, default=None):
            values = self.env["complete"]
            return values.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        result = load_env.load_env()

        # Assertion iterating with keys
        for key in self.env["complete"]:
            if key != "CORE_COUNT":
                self.assertEqual(result[key], self.env["complete"][key])
            else:
                # Mock max core is 8 cores
                self.assertEqual(result["CORE_COUNT"], 8)


    @patch("os.getenv")
    @patch("os.cpu_count")
    def test_default_core(self, mock_cpu_count, mock_getenv):
        """
        Test that when 'CORE_COUNT' is not provided, the function defaults to 4 cores.
        """
        mock_cpu_count.side_effect = [8]

        def getenv_side_effect(key, default=None):
            values = self.env["complete_no_core_count"]
            return values.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        result = load_env.load_env()

        for key in self.env["complete"]:
            if key != "CORE_COUNT":
                self.assertEqual(result[key], self.env["complete"][key])
            else:
                # Default 4 cores
                self.assertEqual(result["CORE_COUNT"], 4)


    @patch("builtins.exit")
    @patch("builtins.print")
    @patch("os.getenv")
    @patch("os.cpu_count")
    def test_missing_fields(self, mock_cpu_count, mock_getenv, mock_print, mock_exit):
        """
        Test that if required environment variables are missing, the function prints an error message and exits with code 1.
        """
        mock_cpu_count.side_effect = [8]

        def getenv_side_effect(key, default=None):
            values = self.env["incomplete"]
            return values.get(key, default)
        mock_getenv.side_effect = getenv_side_effect
        mock_exit.side_effect = SystemExit

        with self.assertRaises(SystemExit):
            load_env.load_env()

        # Verify the exception was handled correctly
        mock_print.assert_called_once_with("Please set API_KEY, BASE_URL, USER, and USERID in your .env file.")
        mock_exit.assert_called_once_with(1)
