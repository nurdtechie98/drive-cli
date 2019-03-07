import os
import sys
import unittest


if __name__ == '__main__':

    test_suite = unittest.TestLoader().discover(os.path.join(os.path.dirname(os.path.abspath(__file__)), "."),
                                                pattern='test_*.py')
    result = unittest.TextTestRunner(buffer=True).run(test_suite)
    sys.exit(not result.wasSuccessful())
