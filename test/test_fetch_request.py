import unittest
import requests
from unittest.mock import patch, Mock, call
from fetch_request import fetch_request

class Test_get_crew_ids(unittest.TestCase):
    def setUp(self):
        """
        Setting up mock env and mock response data
        """
        self.env = {
            "complete":{
                "BASE_URL": "https://jellyfin.example.com",
                "API_KEY": "test_api_key_123",
                "USERID": "test_user_id_123",
                "TIMEOUT": 30
            },
            "incomplete": {
                "BASE_URL": "https://jellyfin.example.com"
            }
        }

        # This is what requests.get will return when mocking with real function
        self.mock_response_data = {
            "valid_data":{
                "Items": [
                    {"Id": "crew_001", "Name": "John Doe"},
                    {"Id": "crew_002", "Name": "Jane Smith"},
                    {"Id": "crew_003", "Name": "Bob Johnson"}
                ]
            },
            "empty_items": {
                "Items": []
            },
            "no_valid_key": {
                "metadata": []
            },
            "missing_id":{
                "Items": [
                    {"Id": "crew_001", "Name": "John Doe"},
                    {"Name": "Jane Smith"},
                    {"Id": "crew_003", "Name": "Bob Johnson"},
                    {}
                ]
            },
            "duplicate_id":{
                "Items": [
                    {"Id": "crew_001", "Name": "John Doe"},
                    {"Name": "Jane Smith"},
                    {"Id": "crew_001", "Name": "Bob Johnson"},
                    {}
                ]
            }
        }

        self.person_id = "crew_001"


    # Mocking requests.get function
    @patch("requests.get")
    def test_return_crew_ids_structure(self, mock_get):
        mock_response = Mock()
        # mock raise_for_status() function
        mock_response.raise_for_status.return_value = None
        # mock json() function
        mock_response.json.return_value = self.mock_response_data.get("valid_data")

        mock_get.return_value = mock_response

        # Need to fetch first then test for structure
        result = fetch_request.get_all_crew_ids(self.env["complete"])

        # Make sure the structure is intact
        mock_get.assert_called_once_with(
            self.env["complete"]["BASE_URL"]+"/emby/Persons",
            params={"api_key": self.env["complete"]["API_KEY"]},
            timeout=self.env["complete"]["TIMEOUT"]
        )


    # Mocking requests.get function
    @patch("requests.get")
    def test_successful_return_crew_ids(self, mock_get):
        """
        Test successful API call returns correct set of crew IDs.
        """
        mock_response = Mock()
        # mock raise_for_status() function
        mock_response.raise_for_status.return_value = None
        # mock json() function
        mock_response.json.return_value = self.mock_response_data.get("valid_data")

        mock_get.return_value = mock_response

        result = fetch_request.get_all_crew_ids(self.env["complete"])

        # Verify the result
        expected_result = { "crew_001", "crew_002", "crew_003" }
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, set)


    @patch('requests.get')
    def test_empty_items_list_returns_empty_set(self, mock_get):
        """
        Test API response with empty Items list returns empty set.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_response_data.get("empty_items")
        mock_get.return_value = mock_response

        result = fetch_request.get_all_crew_ids(self.env["complete"])

        # Verify the result
        expected_result = set()
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, set)


    @patch('requests.get')
    def test_missing_items_key_returns_empty_set(self, mock_get):
        """
        Test API response with empty Items list returns empty set.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_response_data.get("no_valid_key")
        mock_get.return_value = mock_response

        result = fetch_request.get_all_crew_ids(self.env["complete"])

        # Verify the result
        expected_result = set()
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, set)


    @patch('requests.get')
    def test_some_missing_id_key_returns_valid_set(self, mock_get):
        """
        Test API response with empty Items list returns empty set.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_response_data.get("missing_id")
        mock_get.return_value = mock_response

        result = fetch_request.get_all_crew_ids(self.env["complete"])

        # Verify the result
        expected_result = { "crew_001", "crew_003" }
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, set)


    @patch('requests.get')
    def test_duplicate_id_keys_returns_unique_set(self, mock_get):
        """
        Test API response with empty Items list returns empty set.
        """
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_response_data["duplicate_id"]
        mock_get.return_value = mock_response

        result = fetch_request.get_all_crew_ids(self.env["complete"])

        # Verify the result
        expected_result = { "crew_001" }
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, set)


    @patch('builtins.exit') # Mock system buildtin functions
    @patch('builtins.print')
    @patch("requests.get")
    def test_request_timeout_exception_handling(self, mock_get, mock_print, mock_exit):
        mock_response = Mock()
        # Raising an exception in raise_for_status() function
        mock_response.raise_for_status.side_effect = requests.exceptions.Timeout
        mock_get.return_value = mock_response

        # The mock should terminate the program
        mock_exit.side_effect = SystemExit(0)

        # Call the function with anticipation of exception raising
        with self.assertRaises(SystemExit):
            fetch_request.get_all_crew_ids(self.env["complete"])

        # Verify the exception was handled correctly
        mock_print.assert_called_once_with("Error fetching all crew and casts: . Exiting...")
        mock_exit.assert_called_once_with(0)


    @patch('requests.get')
    @patch('builtins.print')
    @patch('builtins.exit')
    def test_request_http_error_handling(self, mock_exit, mock_print, mock_get):
        """Test that HTTP errors (like 404, 500) cause error message and exit."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        mock_exit.side_effect = SystemExit(0)

        with self.assertRaises(SystemExit):
            fetch_request.get_all_crew_ids(self.env["complete"])

        mock_print.assert_called_once_with("Error fetching all crew and casts: 404 Not Found. Exiting...")
        mock_exit.assert_called_once_with(0)


    @patch('requests.get')
    @patch('builtins.print')
    @patch('builtins.exit')
    def test_json_decode_error_is_caught(self, mock_exit, mock_print, mock_get):
        """Test that JSON decode errors are caught as RequestException."""
        mock_response = Mock()
        mock_response.json.side_effect = requests.JSONDecodeError("Invalid JSON", "HTTP Response returned Invalid JSON", 0)
        mock_get.return_value = mock_response

        mock_exit.side_effect = SystemExit(0)

        with self.assertRaises(SystemExit):
            fetch_request.get_all_crew_ids(self.env["complete"])

        mock_print.assert_called_once_with("Error fetching all crew and casts: Invalid JSON: line 1 column 1 (char 0). Exiting...")
        mock_exit.assert_called_once_with(0)


    @patch("requests.get")
    def test_get_cast_and_crew_structure(self, mock_get):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_response_data.get("valid_data")

        mock_get.return_value = mock_response

        # Need to fetch first then test for structure
        result = fetch_request.get_cast_and_crew(self.env["complete"], self.person_id)

        # Make sure the structure is intact
        mock_get.assert_called_once_with(
            f"{self.env['complete']['BASE_URL']}/Users/{self.env['complete']['USERID']}/Items/{self.person_id}",
            params={"api_key": self.env["complete"]["API_KEY"]},
            timeout=self.env["complete"]["TIMEOUT"]
        )


    @patch('requests.get')
    def test_successful_request_first_attempt(self, mock_get):
        """Test successful API call on first attempt."""
        # Mock successful response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = fetch_request.get_cast_and_crew(self.env["complete"], self.person_id)

        # Verify function returns None
        self.assertIsNone(result)

        # Verify only one attempt was made
        self.assertEqual(mock_get.call_count, 1)


    @patch('time.sleep')
    @patch('builtins.print')
    @patch('requests.get')
    def test_successful_request_second_attempt(self, mock_get, mock_print, mock_sleep):
        """Test successful API call on second attempt."""
        # Mock successful response
        mock_response = Mock()
        # List of side effects meaning 1st time & 2nd time calling raise_for_status() function
        mock_response.raise_for_status.side_effect = [
            requests.exceptions.Timeout, # 1st time calling will return timeout exception
            mock_response # 2nd time calling will return proper result
        ]
        mock_get.return_value = mock_response

        result = fetch_request.get_cast_and_crew(self.env["complete"], self.person_id)

        # Verify print is called once
        mock_print.assert_called_once_with(f"Retry attempt #1 for person {self.person_id}")
        # Verify sleep was called once (after first failure)
        mock_sleep.assert_called_once_with(1)

        # Verify function returns None
        self.assertIsNone(result)

        # Verify only one attempt was made
        self.assertEqual(mock_get.call_count, 2)


    @patch('time.sleep')
    @patch('builtins.print')
    @patch('requests.get')
    def test_successful_request_third_attempt(self, mock_get, mock_print, mock_sleep):
        """Test successful API call on second attempt."""
        # Mock successful response
        mock_response = Mock()
        # List of side effects meaning 1st time & 2nd time calling raise_for_status() function
        mock_response.raise_for_status.side_effect = [
            requests.exceptions.Timeout, # 1st time calling
            requests.RequestException, # 2st time calling
            mock_response # 3nd time calling
        ]
        mock_get.return_value = mock_response

        result = fetch_request.get_cast_and_crew(self.env["complete"], self.person_id)

        # Verify print is called once
        # mock_print.assert_called_once_with(f"Retry attempt #1 for person {self.person_id}")
        mock_print.assert_has_calls([
            call(f"Retry attempt #1 for person {self.person_id}"),
            call(f"Retry attempt #2 for person {self.person_id}"),
        ])
        # Verify sleep was called once (after first failure)
        mock_sleep.assert_has_calls([
            call(1),
            call(1)
        ])

        # Verify function returns None
        self.assertIsNone(result)

        # Verify only one attempt was made
        self.assertEqual(mock_get.call_count, 3)


    @patch('time.sleep')
    @patch('builtins.print')
    @patch('requests.get')
    def test_fail_request_exhausted_attempt(self, mock_get, mock_print, mock_sleep):
        """Test successful API call on second attempt."""
        # Mock successful response
        mock_response = Mock()
        # List of side effects meaning 1st time & 2nd time calling raise_for_status() function
        mock_response.raise_for_status.side_effect = [
            requests.exceptions.Timeout, # 1st time calling
            requests.RequestException, # 2st time calling
            requests.exceptions.Timeout, # 3st time calling
        ]
        mock_get.return_value = mock_response

        result = fetch_request.get_cast_and_crew(self.env["complete"], self.person_id)

        # Verify print is called once
        mock_print.assert_has_calls([
            call(f"Retry attempt #1 for person {self.person_id}"),
            call(f"Retry attempt #2 for person {self.person_id}"),
            call(f"Error fetching details for person {self.person_id}: "),
        ])
        # Verify sleep was called once (after first failure)
        mock_sleep.assert_has_calls([
            call(1),
            call(1)
            # 3rd call does not sleep, printing error immediately and return
        ])

        # Verify function returns None
        self.assertIsNone(result)

        # Verify only one attempt was made
        self.assertEqual(mock_get.call_count, 3)