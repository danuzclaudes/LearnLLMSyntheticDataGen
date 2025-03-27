import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def setup_driver(user_agent, proxy=None):
    chrome_options = Options()
    chrome_options.add_argument(f"user-agent={user_agent}")
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def simulate_human_interactions(driver):
    # Scroll the page
    scrolls = random.randint(3, 7)
    for _ in range(scrolls):
        scroll_height = random.randint(200, 800)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(1, 3))

    # Randomly click on navigation or Listings
    elements = driver.find_elements(By.CSS_SELECTOR, "header nav ul li")
    nav_listings = driver.find_element(By.CSS_SELECTOR, "nav a[href='#listings']")
    click_options = []
    if elements:
        click_options.append("random_nav_li")
    if nav_listings:
        click_options.append("listings")
    if click_options:
        choice = random.choice(click_options)
        if choice == "random_nav_li":
            random_li = random.choice(elements)
            random_li.click()
            print("Clicked on a random <li> element on nav bar.")
        elif choice == "listings":
            nav_listings.click()
            print("Clicked on the 'Listings' link.")
        # Simulate human delay and navigate back
        time.sleep(random.uniform(2, 5))
        driver.back()


def simulate_traffic(urls, user_agents, proxies, rate_limit):
    for url in urls:
        # Select a random user agent and proxy
        user_agent = random.choice(user_agents)
        proxy = random.choice(proxies) if proxies else None

        # Set up the driver
        driver = setup_driver(user_agent, proxy)

        try:
            # Open the website
            driver.get(url)
            print(f"Opened {url} with User-Agent: {user_agent} and Proxy: {proxy}")

            # Simulate human behavior
            simulate_human_interactions(driver)

            # Find and click on ad elements (if available)
            # ad_elements = driver.find_elements(By.CSS_SELECTOR, "[data-ad]")
            # if ad_elements:
            #     random.choice(ad_elements).click()
            #     time.sleep(random.uniform(2, 5))
            #     driver.back()

        except Exception as e:
            print(f"Error: {e}")
        finally:
            driver.quit()

        # Rate limiting (input-controlled delay)
        delay = random.uniform(rate_limit[0], rate_limit[1])
        print(f"Rate limiting: Sleeping for {delay:.2f} seconds...")
        time.sleep(delay)


if __name__ == "__main__":
    # URLs to visit
    urls = ["https://adengbao.com"]

    # User agents for mobile and desktop
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    ]

    # Proxies for regional traffic
    proxies = [
        # "http://US_PROXY:PORT",
        # "http://EU_PROXY:PORT",
        # "http://CN_PROXY:PORT",
    ]

    # Rate limit input (min and max delay between requests)
    rate_limit = (3, 10)  # Adjust as needed

    # Simulate traffic
    simulate_traffic(urls, user_agents, proxies, rate_limit)
