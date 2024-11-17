from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WikiCrawler:
    def __init__(self, user_agent="Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko"):
        self.user_agent = user_agent
        self.driver = self._set_driver()

    def _set_driver(self):
        """Sets up the Chrome WebDriver with the specified options."""

        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        return driver

    def bfs_crawl(self, url, document_title, max_depth=2):
        """
        Performs BFS-based crawling on the given wiki URL starting from the given title.

        Args:
            url (str): Starting URL for the crawl.
            document_title (str): Starting document title.
            max_depth (int): Maximum depth for BFS crawl.

        Returns:
            list: A list of tuples containing document title and content.
        """
        bfs_queue = []  # (title, url)
        res_list = []   # (title, content.text)

        bfs_queue.append((document_title, url))

        for depth in range(max_depth + 1):
            current_depth = depth

            if len(bfs_queue) == 0:
                break

            current_bfs_queue = list(set(bfs_queue))
            bfs_queue = []

            for title, url in current_bfs_queue:
                print(f"Current Depth: {current_depth}, Title: {title}, URL: {url}")

                self.driver.get(url)
                self.driver.implicitly_wait(5)

                document_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div[2]/div/div[4]/div'))
                )

                try:
                    self.driver.execute_script("""
                        var element = arguments[0];
                        var tables = element.getElementsByTagName('table');
                        while(tables.length > 0) {
                            tables[0].parentNode.removeChild(tables[0]);
                        }
                    """, document_element)
                except Exception:
                    pass

                try:
                    element_to_remove = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '/html/body/div/div[1]/div[2]/div/div[3]/div/div[5]'))
                    )
                    self.driver.execute_script("""
                        var element = arguments[0];
                        element.parentNode.removeChild(element);
                    """, element_to_remove)
                except Exception:
                    pass

                document_text = document_element.text.replace("/", "")
                res_list.append((title, document_text))

                a_tags = document_element.find_elements(By.XPATH, './/a')

                for element in a_tags:
                    a_title = element.get_attribute('title')
                    a_href = element.get_attribute('href')

                    title_filter = ["역사", "토론", "내 문서함에 추가", "토막글 규정", "크리에이티브 커먼즈 라이선스"]

                    if a_title and a_title != "":
                        if (a_title in title_filter or "https" in a_title) or a_title == title:
                            continue
                        if "namu.wiki" not in a_href:
                            continue

                        bfs_queue.append((a_title, a_href))

            print("search_finished")

        return res_list

    def close(self):
        """Closes the WebDriver."""

        self.driver.quit()
