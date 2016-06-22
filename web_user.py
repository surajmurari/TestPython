from base_web_user import BaseWebUser


class WebUser(BaseWebUser):

    def __init__(self):
        self.browser_type = 'phantomjs'
        super(WebUser, self).__init__(self.browser_type)

    def launch_url(self, url):
        self.browser.get(url)
