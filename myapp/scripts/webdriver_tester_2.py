import subprocess
import time

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def setup(user_agent):
    browser_process = subprocess.Popen(
        [
            "google-chrome",
            "--disable-gpu",
            "--disable-software-rasterizer",
            "--disable-extensions",
            "--no-proxy-server",
            "--remote-debugging-port=9222",
            "https://adengbao.com",
        ]
    )
    options = webdriver.ChromeOptions()
    options.debugger_address = "localhost:9222"
    options.add_argument(f"user-agent={user_agent}")
    driver = webdriver.Chrome(options=options)
    print(f"Successfully opened web page: {driver.current_url}")
    return driver, browser_process


def wait_for_page_load(max_attempts=5):
    for attempt in range(max_attempts):
        if driver.execute_script("return document.readyState === 'complete';"):
            print("Page is fully loaded.")
            time.sleep(5)
            return
        print(f"Page not ready, retrying... (Attempt {attempt + 1}/{max_attempts})")
        time.sleep(1)
    print("Failed to load the page after multiple attempts.")


def close_all_ad_tabs():
    main_handle = driver.window_handles[0]
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(main_handle)
    print("Closed all other tabs.")


def close_ads():
    """Attempt to close ads within an iframe."""
    try:
        iframe = driver.find_element(By.XPATH, "//iframe")
        driver.switch_to.frame(iframe)
        close_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='Close']/ancestor::div")
            )
        )
        actions.click(close_div).perform()
        print("Closed the iframe ad.")
    except Exception as e:
        print(f"Failed to close iframe ad: {e}")
    finally:
        driver.switch_to.default_content()


def scroll_to_element(css_selector):
    """Scroll to an element using its CSS selector."""
    try:
        element = driver.find_element(By.CSS_SELECTOR, css_selector)
        driver.execute_script("arguments[0].scrollIntoView();", element)
        print(f"Scrolled to element: {css_selector}")
        return element
    except Exception as e:
        print(f"Failed to scroll to element {css_selector}: {e}")
        return None


user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
driver, browser_process = setup(user_agent)
actions = ActionChains(driver)
wait_for_page_load()

# Scroll to 'About' section
driver.execute_script(
    "window.scrollTo(0, document.querySelector('section#about').offsetTop);"
)
print("Scrolled to 'About' section.")
time.sleep(2)

# Scroll to 'About' image
about_image = scroll_to_element(".about img")

# Click the second listing image
try:
    close_ads()
    close_all_ad_tabs()
    second_listing_image = scroll_to_element(
        ".listing-grid .listing-item:nth-child(2) img"
    )
    time.sleep(5)
    if second_listing_image:
        actions.click(second_listing_image).perform()
        print("Clicked the second listing image.")
except Exception as e:
    print(f"Failed to interact with the second listing image: {e}")

driver.quit()
browser_process.kill()
