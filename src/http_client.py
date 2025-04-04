import http.client
import json
import socket
import ssl
import time


class Client:
    def __init__(self, host, timeout=30, max_retries=3, retry_delay=2, headers=None):
        """
        Host should be passed without protocol.
        """
        self.host = host
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.headers = headers
        self.context = ssl.create_default_context()
        self.conn = None

    def __enter__(self):
        """Called when entering the 'with' block. Creates reusable connection."""
        self._create_connection()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Called when exiting the 'with' block. Closes the connection."""
        if self.conn:
            self.close_connection()

    def get_connection(self):
        """Ensure a valid connection before making a request."""
        if self.conn is None:
            self._create_connection()
            return self.conn

    def _create_connection(self):
        self.conn = http.client.HTTPSConnection(
            host=self.host, timeout=self.timeout, context=self.context
        )

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def request(self, url, method="GET", headers={}):
        headers = self.headers or {}

        for attempt in range(1, self.max_retries + 1):
            try:
                if self.conn is None:
                    self.get_connection()

                print(f"making {method} request to {url}")
                self.conn.request(method, url, headers=headers)
                response = self.conn.getresponse()

                if response.status == 200:
                    return response

                print(f"Attempt {attempt}: Received status {response.status}")

                if response.status == 404:
                    return response

            except (http.client.HTTPException, socket.timeout) as e:
                print(f"Attempt {attempt}: Error - {e}")

            if attempt < self.max_retries:
                time.sleep(self.retry_delay)

        print("Failed to fetch data after retries.")
        return None

    def get_response_data(self, response):
        return response.read().decode("utf-8")

    def get_json_dict_from_response(self, response_str: str) -> dict | str:
        """
        This will take the result from get_response_data
        and convert into dict
        """
        try:
            return json.loads(response_str)
        except Exception as err:
            err = f"ERROR reading json from {response_str}, {err}"
            return err
