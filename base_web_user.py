import time
import logging
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

logger = logging.getLogger('MTMTestLogger')
formatter = logging.Formatter('%(asctime)s.%(msecs).03d|%(levelname)-3.3s|%(message)s',
                              datefmt='%m-%d-%Y_%I:%M:%S')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


class BaseWebUser(object):
    """ Base class to provide common functionality for selenium based web test users. """

    def __init__(self, browser, encoding='utf-8', truncate_log=False, log_level='DEBUG'):

        self.encoding = encoding
        self.truncate_log = truncate_log
        self.set_log_level(log_level)

        if browser.lower() == 'chrome':
            self.browser = webdriver.Chrome()
        elif browser.lower() == 'firefox':
            self.browser = webdriver.Firefox()
        elif browser.lower() == 'ie':
            caps = webdriver.DesiredCapabilities.INTERNETEXPLORER
            caps['ignoreProtectedModeSettings'] = True
            self.browser = webdriver.Ie(capabilities=caps)
        elif browser.lower() == 'phantomjs':
            self.browser = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'])

        self.browser.implicitly_wait(30)

        self.browser.maximize_window()

    def log_debug(self,  text):
        message = '{s} {t}'.format(s=self, t=text)
        logger.debug(message)

    def log_info(self,  text):
        message = '{s} {t}'.format(s=self, t=text)
        logger.info(message)

    def set_log_level(self, log_level):
        logger.setLevel(log_level)

    def _set_text_box(self, text_box, value):
        """ Set the value of the text box identified by text_box to value. """

        self._clear_text_box(text_box)

        text_box.send_keys(value)

    def _set_text_box_by_xpath(self, xpath, value):
        """ Set the value of the text box identified by xpath to value """
        self._set_text_box(self.browser.find_element_by_xpath(xpath), value)

    def _clear_text_box(self, text_box):
        """ Clear the value of the text box identified by text_box. """

        text_box.send_keys(Keys.HOME)
        text_box.send_keys(Keys.SHIFT, Keys.END)
        text_box.send_keys(Keys.DELETE)

    def _click_element_by_xpath(self, xpath):
        """ Click the element identified by xpath. """

        self._click(self.browser.find_element_by_xpath(xpath))

    def _click_element_by_css_selector(self, css_selector):
        """ Click the element identified by css_selector. """

        self._click(self.browser.find_element_by_css_selector(css_selector))

    def _click_element_by_id(self, identifier):
        """ Click the element identified by identifier. """

        self._click(self.browser.find_element_by_id(identifier))

    def _click(self, element):
        """ Click the element. """

        self._retry_action(element, 'click')

    def _retry_action(self, element, action, *args):
        """ Perform action on element.  Pass *args to the action function.

            In exception conditions, keep retrying the action until either no exception occurs or the timeout expires.
        """

        start = time.time()

        exception = None
        while time.time() - start < 30:
            try:
                self._move_to_element(element)
                return getattr(element, action)(*args)
            except WebDriverException as e:
                self.log_info('Retrying due to exception {msg}'.format(msg=e.msg))
                time.sleep(0.5)
                exception = e

        raise exception

    def _move_to_element(self, element):
        """ Scroll the web browser so that element is in view. """

        webdriver.ActionChains(self.browser).move_to_element(element)

    def _click_submenu_item_with_mouse_hover(self, menu, sub_menu):
        """ Mouse hover the menu to get the sub menu item and performs click on it"""

        menu = self.browser.find_element_by_xpath(menu)
        action = webdriver.ActionChains(self.browser)

        action.move_to_element(menu).perform()

        sub_menu = self.browser.find_element_by_xpath(sub_menu)

        action.move_to_element(sub_menu).click().perform()

    def _find_elements_by_xpath(self, xpath):

        return self.browser.find_elements_by_xpath(xpath)

    def _find_element_by_xpath(self, xpath):

        return self.browser.find_element_by_xpath(xpath)

    def _save_screenshot(self, filename):
        """ Save a screenshot of the web browser. """

        self.log_info('Saved screenshot at {filename}'.format(filename=filename))

        self.browser.save_screenshot(filename)

    def switch_to_frame(self, name):
        """ Switch to the frame by frame name"""
        self.browser.switch_to.frame(name)

    def switch_to_parent_frame(self):
        """Switch to the parent from any frame"""
        self.browser.switch_to.parent_frame()

    def _get_text_of_control_by_xpath(self, xpath):
        """ Returns the value of the text property of the control identified by xpath """
        return self.browser.find_element_by_xpath(xpath).text

    def _get_browser_title(self):
        """ Returns the value of the title property of the current browser instance """
        return self.browser.title

    def _get_webelement_color(self, xpath):
        """
        Extract the color of the web element present in the UI
        """
        return self.browser.find_element_by_xpath(xpath).value_of_css_property('Color')

    def _perform_rt_mouse_click(self, select_trade):
        """
        Perform right click mouse operation
        """
        return webdriver.ActionChains(self.browser).context_click(select_trade).perform()

    def _wait_for_element(self, xpath):
        delay = 20 # seconds
        try:
            WebDriverWait(self.browser, delay).until(EC.presence_of_element_located((By.XPATH, xpath)))
        except TimeoutException:
            raise Exception(TimeoutException)

    def _wait_for_element_to_be_clickable(self, xpath):
        delay = 20 # seconds
        try:
            WebDriverWait(self.browser, delay).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        except TimeoutException:
            raise Exception(TimeoutException)

    def _page_has_loaded(self):
        page_state = self.browser.execute_script(
            'return document.readyState;'
        )
        return page_state == 'complete'

    def wait_for_page(self):
        start_time = time.time()
        while time.time() < start_time + 3:
            if self._page_has_loaded():
                return True
            else:
                time.sleep(0.1)
        raise Exception('Timeout waiting for page to load')