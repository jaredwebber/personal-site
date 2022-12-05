from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.service import Service as SafariService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import unittest

URL: str = "https://jaredwebber.dev"
SLEEP: bool = False
DEFAULT_SLEEP: int = 1


def try_sleep(duration: int = DEFAULT_SLEEP) -> None:
    if SLEEP:
        sleep(duration)


def enhance_errors(func):
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except AssertionError as e:
            e.args = (BrowserManager.browser_name, "".join(e.args))
            BrowserManager.failures = True
            raise
        try_sleep()

    return inner_function


class BrowserManager:
    browser_index: int = 0
    browser_name: str = ""
    failures: bool = False

    @classmethod
    def setup_chrome(cls) -> webdriver.Chrome:
        cls.browser_name = "Chrome"
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    @classmethod
    def setup_firefox(cls) -> webdriver.Firefox:
        cls.browser_name = "Firefox"
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

    @classmethod
    def setup_safari(cls) -> webdriver.Safari:
        cls.browser_name = "Safari"
        return webdriver.Safari(service=SafariService())

    @classmethod
    def get_next_browser(cls) -> list:
        browsers = [cls.setup_safari, cls.setup_chrome, cls.setup_firefox]
        browser: webdriver = browsers[cls.browser_index]()
        print("\nSetting Up " + cls.browser_name + "...")
        browser.implicitly_wait(12)
        browser.get(URL)
        cls.browser_index += 1
        return [browser, cls.browser_name]


class TestBrowser(unittest.TestCase):
    browser: webdriver = None
    browser_name: str = ""

    @classmethod
    def setUpClass(cls) -> None:
        cls.browser, cls.browser_name = BrowserManager.get_next_browser()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.browser:
            cls.browser.quit()

    @enhance_errors
    def test__validate_page_title(self) -> None:
        self.assertEqual("Jared Webber", self.browser.title)

    @enhance_errors
    def test__validate_card_title(self) -> None:
        # ensure card title is correct
        self.assertEqual(0, 1)

    @enhance_errors
    def test__validate_github_link(self) -> None:
        # ensure gh link is correct
        self.assertEqual(0, 1)

    @enhance_errors
    def test__validate_linkedin_link(self) -> None:
        # ensure linkedin link is correct
        self.assertEqual(0, 1)

    @enhance_errors
    def test__validate_email_link(self) -> None:
        # ensure email link is correct
        self.assertEqual(0, 1)

    @enhance_errors
    def test__validate_website_link(self) -> None:
        # ensure web link is correct
        self.assertEqual(0, 1)

    @enhance_errors
    def test__regenerate_button(self) -> None:
        # button is visible, and doesnt break anything?
        self.assertEqual(0, 1)

    @enhance_errors
    def test__toggle_palette_button(self) -> None:
        # button is visible, and doesnt break anything?
        self.assertEqual(0, 1)

    @enhance_errors
    def test__mobile_formatting(self) -> None:
        # look at css tags?
        self.assertEqual(0, 1)


# Placeholder which forces TestBrowser to tearDown
# Cycles the browser being tested
class NextBrowser(unittest.TestCase):
    def test__bump(self) -> None:
        print("\nNext Browser...")


def suite() -> unittest.TestSuite:
    test_suite = unittest.TestSuite()
    test_suite.addTests(unittest.makeSuite(TestBrowser))  # Safari
    test_suite.addTests(unittest.makeSuite(NextBrowser))
    test_suite.addTests(unittest.makeSuite(TestBrowser))  # Chrome
    test_suite.addTests(unittest.makeSuite(NextBrowser))
    test_suite.addTests(unittest.makeSuite(TestBrowser))  # Firefox
    return test_suite


mySuit = suite()
runner = unittest.TextTestRunner()
runner.run(mySuit)

if BrowserManager.failures:
    raise SystemExit(1)
