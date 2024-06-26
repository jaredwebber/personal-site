import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from time import sleep
import unittest

URL: str = "https://jaredwebber.dev"
SLEEP: bool = False
DEFAULT_SLEEP: int = 1

# safari doesnt support headless mode
chrome_options = ChromeOptions()
chrome_options.add_argument("--headless")


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
    def setup_safari(cls) -> webdriver.Safari:
        cls.browser_name = "Safari"
        return webdriver.Safari()

    @classmethod
    def get_next_browser(cls) -> list:
        browsers = [cls.setup_safari, cls.setup_chrome]
        browser: webdriver = browsers[cls.browser_index]()
        print("\nSetting Up " + cls.browser_name + "...")
        try_sleep()
        browser.implicitly_wait(12)
        cls.browser_index += 1
        return [browser, cls.browser_name]


class TestBrowser(unittest.TestCase):
    browser: webdriver = None
    browser_name: str = ""
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.browser, cls.browser_name = BrowserManager.get_next_browser()

    @classmethod
    def tearDownClass(cls) -> None:
        if cls.browser:
            cls.browser.quit()

    @enhance_errors
    def test__validate_page_title(self) -> None:
        self.browser.get(URL)
        self.assertEqual("Jared Webber", self.browser.title)

    @enhance_errors
    def test__validate_card_title(self) -> None:
        self.browser.get(URL)
        self.assertEqual("Jared Webber", self.browser.find_element(By.TAG_NAME, "h2").text)

    @enhance_errors
    def test__validate_github_link(self) -> None:
        self.browser.get(URL)
        self.assertEqual(
            "https://github.com/jaredwebber",
            self.browser.find_element(By.LINK_TEXT, "github.com/jaredwebber").get_attribute("href"),
        )

    @enhance_errors
    def test__validate_linkedin_link(self) -> None:
        self.browser.get(URL)
        self.assertEqual(
            "https://www.linkedin.com/in/jaredwebber/",
            self.browser.find_element(By.LINK_TEXT, "linkedin.com/in/jaredwebber").get_attribute("href"),
        )

    @enhance_errors
    def test__validate_email_link(self) -> None:
        self.browser.get(URL)
        self.assertEqual(
            "mailto:jaredwebberdev@gmail.com",
            self.browser.find_element(By.LINK_TEXT, "jaredwebberdev@gmail.com").get_attribute("href"),
        )

    @enhance_errors
    def test__validate_website_link(self) -> None:
        self.browser.get(URL)
        link = self.browser.find_element(By.LINK_TEXT, "jaredwebber.dev - you're here").get_attribute("href")
        self.assertTrue(link == "https://jaredwebber.dev/index.html" or link == "index.html")

    @enhance_errors
    def test__validate_number_of_elements(self) -> None:
        self.browser.get(URL)
        count = len(self.browser.find_element(By.TAG_NAME, "html").find_elements(By.XPATH, ".//*"))
        # varies slightly by browser / load order
        self.assertTrue(count >= 44 and count <= 47)

    @enhance_errors
    def test__regenerate_button(self) -> None:
        self.browser.get(URL)
        button = self.browser.find_element(By.ID, "regenerate-background").get_attribute("onclick")

        self.assertEqual("regenerateBackground()", button)

    @enhance_errors
    def test__toggle_palette_button(self) -> None:
        self.browser.get(URL)
        button = self.browser.find_element(By.ID, "toggle-colours").get_attribute("onclick")

        self.assertEqual("toggleColours()", button)

    @enhance_errors
    def test__validate_everyday_privacy_policy(self) -> None:
        privacy_policy: str = """
            Every Day Privacy Policy

            Overview
            
            We Collect No Personal Information Using Our Application 
            We do not collect, use, save, or have access to any of your personal data
            recorded. Data recorded in Every Day is stored on your device, and is not
            transferred.
            
            

            Contact Us
            
            If you have any questions about this Privacy Policy, feel free to get in
            touch at jaredwebberdev@gmail.com.
            """  # noqa: E501, W291, W293
        self.browser.get(URL + "/everyday-privacy-policy")
        no_whitespace_expected_string = re.sub(r"\s+", "", privacy_policy)
        self.assertEqual(
            no_whitespace_expected_string,
            re.sub(r"\s+", "", self.browser.find_element(By.ID, "body").text),
        )


# Placeholder which forces TestBrowser to tearDown
# Cycles the browser being tested
class NextBrowser(unittest.TestCase):
    def test__bump(self) -> None:
        print("\nNext Browser...")


def suite() -> unittest.TestSuite:
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTests(loader.loadTestsFromTestCase(TestBrowser))  # Safari
    test_suite.addTests(loader.loadTestsFromTestCase(NextBrowser))
    test_suite.addTests(loader.loadTestsFromTestCase(TestBrowser))  # Chrome
    return test_suite


mySuite = suite()
runner = unittest.TextTestRunner()
runner.run(mySuite)

if BrowserManager.failures:
    raise SystemExit(1)
