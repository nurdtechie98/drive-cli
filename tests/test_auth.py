import unittest
from drive_cli.auth import (login)


class TestAuth(unittest.TestCase):

    def test_auth_when_token_is_incorrect(self):
        '''
        Test when auth token in correct
        '''
        pass

    def test_auth_when_token_is_correct(self):
        '''
        Test when auth token in correct
            refresh current encoded token for auth to pass
        '''
        login(remote=False)
        print("DONE LOGIN")


if __name__ == "__main__":
    # Test path
    # dirpath = "/home/travis/build/nurdtechie98/drive-cli/drive_cli"
    unittest.main()
