from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.safari.service import Service as SafariService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import unittest

URL: str = "https://jaredwebber.dev"
SLEEP: bool = False
DEFAULT_SLEEP: int = 1

# safari does not support headless
chrome_options = ChromeOptions()
chrome_options.headless = True
firefox_options = FirefoxOptions()
firefox_options.headless = True


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
        return webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

    @classmethod
    def setup_firefox(cls) -> webdriver.Firefox:
        cls.browser_name = "Firefox"
        return webdriver.Firefox(
            service=FirefoxService(GeckoDriverManager().install()),
            options=firefox_options,
        )

    @classmethod
    def setup_safari(cls) -> webdriver.Safari:
        cls.browser_name = "Safari"
        return webdriver.Safari(service=SafariService())

    @classmethod
    def get_next_browser(cls) -> list:
        browsers = [cls.setup_safari, cls.setup_chrome, cls.setup_firefox]
        browser: webdriver = browsers[cls.browser_index]()
        print("\nSetting Up " + cls.browser_name + "...")
        try_sleep()
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
        self.assertEqual(
            "Jared Webber", self.browser.find_element(By.TAG_NAME, "h2").text
        )

    @enhance_errors
    def test__validate_github_link(self) -> None:
        self.assertEqual(
            "https://github.com/jaredwebber",
            self.browser.find_element(
                By.LINK_TEXT, "github.com/jaredwebber"
            ).get_attribute("href"),
        )

    @enhance_errors
    def test__validate_linkedin_link(self) -> None:
        self.assertEqual(
            "https://www.linkedin.com/in/jaredwebber/",
            self.browser.find_element(
                By.LINK_TEXT, "linkedin.com/in/jaredwebber"
            ).get_attribute("href"),
        )

    @enhance_errors
    def test__validate_email_link(self) -> None:
        self.assertEqual(
            "mailto:jaredwebberdev@gmail.com",
            self.browser.find_element(
                By.LINK_TEXT, "jaredwebberdev@gmail.com"
            ).get_attribute("href"),
        )

    @enhance_errors
    def test__validate_website_link(self) -> None:
        link = self.browser.find_element(
            By.LINK_TEXT, "jaredwebber.dev - you're here"
        ).get_attribute("href")
        self.assertTrue(
            link == "https://jaredwebber.dev/index.html" or link == "index.html"
        )

    @enhance_errors
    def test__validate_number_of_elements(self) -> None:
        count = len(
            self.browser.find_element(By.TAG_NAME, "html").find_elements(
                By.XPATH, ".//*"
            )
        )
        # varies slightly by browser / load order
        self.assertTrue(count == 44 or count == 45)

    @enhance_errors
    def test__regenerate_button(self) -> None:
        button = self.browser.find_element(
            By.ID, "regenerate-background"
        ).get_attribute("onclick")

        self.assertEqual("regenerateBackground()", button)

    @enhance_errors
    def test__toggle_palette_button(self) -> None:
        button = self.browser.find_element(By.ID, "toggle-colours").get_attribute(
            "onclick"
        )

        self.assertEqual("toggleColours()", button)


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
