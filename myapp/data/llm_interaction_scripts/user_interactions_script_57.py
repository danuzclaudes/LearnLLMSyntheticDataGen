import sys
import subprocess
import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def setup_driver():
    args = [
        "google-chrome",
        "--disable-gpu",
        "--disable-software-rasterizer",
        "--disable-extensions",
        "--no-proxy-server",
        "--remote-debugging-port=9222",
        "https://adengbao.com",
    ]
    if len(sys.argv) > 1:
        args.insert(4, f"--user-agent={sys.argv[1]}")
    browser_process = subprocess.Popen(args)
    options = webdriver.ChromeOptions()
    options.debugger_address = "localhost:9222"
    driver = webdriver.Chrome(options=options)
    return driver, browser_process

def wait_for_page_load(max_attempts=5):
    for attempt in range(max_attempts):
        if driver.execute_script("return document.readyState === 'complete';"):
            return
        time.sleep(1)
    print("Failed to load the page after multiple attempts.")

def close_all_ad_tabs():
    main_handle = driver.window_handles[0]
    for handle in driver.window_handles[1:]:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(main_handle)
    time.sleep(random.uniform(2, 10))

def close_ads():
    try:
        iframe = driver.find_element(By.XPATH, "//iframe")
        driver.switch_to.frame(iframe)
        close_div = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Close']/ancestor::div"))
        )
        actions.click(close_div).perform()
    except Exception as e:
        print(f"Failed to close iframe ad: {e}")
    finally:
        driver.switch_to.default_content()
        time.sleep(random.uniform(2, 10))

def teardown():
    time.sleep(random.uniform(2, 10))
    close_all_ad_tabs()
    close_ads()
    time.sleep(random.uniform(2, 10))
    driver.quit()
    browser_process.kill()

driver, browser_process = setup_driver()
wait_for_page_load()
actions = ActionChains(driver)

close_all_ad_tabs()
close_ads()

scroll_pause_time = random.uniform(1, 3)
actions.move_to_element(driver.find_element(By.CSS_SELECTOR, '.contact form')).perform()
time.sleep(scroll_pause_time)

driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(scroll_pause_time)

contact_form = driver.find_element(By.CSS_SELECTOR, '.contact form')
actions.click(contact_form).perform()

time.sleep(random.uniform(1, 3))
# Assuming the form has input fields with specific selectors
name_input = driver.find_element(By.CSS_SELECTOR, '.contact form input[name="name"]')
email_input = driver.find_element(By.CSS_SELECTOR, '.contact form input[name="email"]')
message_input = driver.find_element(By.CSS_SELECTOR, '.contact form textarea[name="message"]')

actions.click(name_input).send_keys("Luxury Traveler").perform()
time.sleep(random.uniform(1, 2))
actions.click(email_input).send_keys("luxurytraveler@example.com").perform()
time.sleep(random.uniform(1, 2))
actions.click(message_input).send_keys("I'm interested in luxury rental properties.").perform()
time.sleep(random.uniform(1, 2))

submit_button = driver.find_element(By.CSS_SELECTOR, '.contact form button[type="submit"]')
actions.click(submit_button).perform()

time.sleep(random.uniform(2, 5))
teardown()