import os
import unittest
from unittest.mock import patch, Mock, call
from load_env import load_env

class Test_load_env(unittest.TestCase):

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
        # Always mock first, then execute. This way execute can take mock values
        mock_cpu_count.side_effect = [8] # This need to be an iterator

        # os.getenv will return base on dict
        def getenv_side_effect(key, default=None):
            values = self.env["complete"]
            return values.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        result = load_env.load_env()

        # Assertion iterating with keys
        for key in self.env["complete"].keys():
            if key != "CORE_COUNT":
                self.assertEqual(result[key], self.env["complete"][key])
            else:
                # Mock max core is 8 cores
                self.assertEqual(result["CORE_COUNT"], 8)


    @patch("os.getenv")
    @patch("os.cpu_count")
    def test_default_core(self, mock_cpu_count, mock_getenv):
        mock_cpu_count.side_effect = [8]

        def getenv_side_effect(key, default=None):
            values = self.env["complete_no_core_count"]
            return values.get(key, default)
        mock_getenv.side_effect = getenv_side_effect

        result = load_env.load_env()

        for key in self.env["complete"].keys():
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