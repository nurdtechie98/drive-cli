import os
import unittest

from click.testing import CliRunner
from drive_cli.auth import (login, config_path)


class TestAuth(unittest.TestCase):
    runner = CliRunner()

    def test_auth_when_token_is_incorrect(self):
        '''
        Test when auth token in correct
        '''
        pass

    def test_login_remote(self):
        '''
        Test when auth token in correct
            refresh current encoded token for auth to pass
        '''
        result = self.runner.invoke(login, ["--remote"])
        assert "Running without local webserver auth." in result.output

    def test_login_no_remote(self):
        """
        Tests when the remote flag is off for login.
        """
        result = self.runner.invoke(login)
        assert "Running without local webserver auth." not in result.output

    def test_login_with_json_file(self):
        oauth_file = os.path.join(config_path, "oauth.json")
        result = self.runner.invoke(login, ["--json-file", oauth_file])
        assert oauth_file in result.output

if __name__ == "__main__":
    # Test path
    # dirpath = "/home/travis/build/nurdtechie98/drive-cli/drive_cli"
    unittest.main()
