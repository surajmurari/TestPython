import unittest
from web_user import WebUser

class TestClass(unittest.TestCase):

    def setUp(self):
        self.user = WebUser()

    def tearDown(self):
        self.user.browser.quit()

    def test_browser(self):
        url = "http://amazon.com"
        self.user.launch_url(url)



if __name__ == '__main__':
    unittest.main()

