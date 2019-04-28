import unittest
<<<<<<< HEAD
from drive_cli.dcli import (login, refresh, dirpath)
=======
from drive_cli.auth import (login)
>>>>>>> ed6cab20d411bdb0b8ebf302278ba9660bae6357


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
<<<<<<< HEAD
        refresh()
=======
>>>>>>> ed6cab20d411bdb0b8ebf302278ba9660bae6357
        login(remote=False)
        print("DONE LOGIN")


if __name__ == "__main__":
    # Test path
<<<<<<< HEAD
    dirpath = "/home/travis/build/nurdtechie98/drive-cli/drive_cli"
=======
    # dirpath = "/home/travis/build/nurdtechie98/drive-cli/drive_cli"
>>>>>>> ed6cab20d411bdb0b8ebf302278ba9660bae6357
    unittest.main()
