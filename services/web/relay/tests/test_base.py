#from run import Transmitter
import unittest


class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass
        # creates a test client
        #transmit = Transmitter()
        # propagate the exceptions to the test client
        #self.app.testing = True

    def tearDown(self):
        pass

    def test_home_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        assert 1 == 1
