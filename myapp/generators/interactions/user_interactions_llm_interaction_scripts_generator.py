import time

from openai import OpenAI

from myapp.utils.file_utils import (save_llm_response_data_to_python,
                                    scripts_dir, data_dir, load_json_array_data, user_interactions_data_file)
from myapp.utils.prompt_utils import website, website_business


class UserInteractionsScriptGenerator:
    client = OpenAI()

    def generate_selenium_script(self, user_interaction_data: dict) -> str:
        setup_code = """
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
        """

        wait_for_page_code = """
        def wait_for_page_load(max_attempts=5):
            for attempt in range(max_attempts):
                if driver.execute_script("return document.readyState === 'complete';"):
                    print("Page is fully loaded.")
                    return
                print(f"Page not ready, retrying... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(1)
            print("Failed to load the page after multiple attempts.")
        """

        close_all_ad_tabs_code = """
        def close_all_ad_tabs():
            main_handle = driver.window_handles[0]
            for handle in driver.window_handles[1:]:
                driver.switch_to.window(handle)
                driver.close()
            driver.switch_to.window(main_handle)
            print("Closed all other tabs.")
            time.sleep(random.uniform(2, 10))
        """

        close_ads_code = """
        def close_ads():
            try:
                iframe = driver.find_element(By.XPATH, "//iframe")
                driver.switch_to.frame(iframe)
                close_div = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Close']/ancestor::div"))
                )
                actions.click(close_div).perform()
                print("Closed the iframe ad.")
            except Exception as e:
                print(f"Failed to close iframe ad: {e}")
            finally:
                driver.switch_to.default_content()
                time.sleep(random.uniform(2, 10))
        """

        teardown_code = """
        def teardown():
            time.sleep(random.uniform(2, 10))
            close_all_ad_tabs()
            close_ads()
            time.sleep(random.uniform(2, 10))
            driver.quit()
            browser_process.kill()
        """

        prompt = f"""
        You are a Python developer to implement some user interactions using Selenium.
        - The user is browsing a website {website} about {website_business}.
        
        You should remember the script should have following requirements:
        - The script must be compatible and working.
        - The script must be concise and no comments.
        - The script must define the setup_driver() function to setup Chrome driver and configure user_agent.
          ```python
          {setup_code}
          ```
        - The script must define the wait_for_page() function to wait webpage until fully loaded:
          ```python
          {wait_for_page_code}
          ```
        - The script must define the close_all_ad_tabs() function to close all other pages opened by ads:
          ```python
          {close_all_ad_tabs_code}
          ```
        - The script must define the close_ads() function to close ads on the web page, just like a human user would do:
          ```python
          {close_ads_code}
          ```
        - The script must define the teardown() function to clean up:
          ```
          {teardown_code}
          ```
        - The script must initialize driver and subprocess by calling setup().
        - The script must wait for page to fully load by calling wait_for_page_load().
        - The script must clean up at the very end, by calling teardown().    
        
        All user interactions are described in JSON: {user_interaction_data}.
        - Read the user_behavior_description to understand what the user interactions are.
        - Read the user_behavior_explanation to understand why you generate the interactions and what html tags and CSS selectors exist.
        - Read the user_profile_description to understand who the user is.
        - You must follow all interactions described in user_behavior_description.
        - You may add more sleep time between interactions, to behave more naturally like human browsing.
        - You may scroll up or down more often and more naturally, to behave more naturally like human browsing.
        - You may generate more mouse movements, to behave more naturally like human browsing.
        
        More technical requirements:
        - You must double check if the whole code compiles.
        - Only use CSS selectors exists in JSON.
        - As a normal user, you will close ad tabs and close ads before any click or scrolling the page.
        - All pause time must be random, as a human user would naturally do.
        - Use actions.click(...).perform().
        - You must call close_all_ad_tabs() and close_ads(), immediately before performing actions.click interaction.

        Please provide the response without enclosing it in any code blocks.
        """

        # print(prompt)

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )
        response_data = completion.choices[0].message.content.strip()
        print(response_data)
        return response_data

    def read_interactions_data_and_call_llm(self):
        user_interactions_data = load_json_array_data(data_dir=data_dir, data_file_name=user_interactions_data_file)
        print(f"Successfully read {len(user_interactions_data)} user interactions.")
        for index, user_interaction in enumerate(user_interactions_data):
            if index > 100:
                break
            response_data = self.generate_selenium_script(user_interaction_data=user_interaction)
            save_llm_response_data_to_python(
                response_data=response_data,
                filename=f"user_interactions_script_{index + 1}.py",
                scripts_dir=scripts_dir
            )
            print(f"Processed {index + 1}.")
            time.sleep(1)


if __name__ == "__main__":
    gen = UserInteractionsScriptGenerator()
    gen.read_interactions_data_and_call_llm()

    user_interaction_data = {
        "interaction_id": 99,
        "user_behavior_id": 10,
        "user_profile_id": 20,
        "user_behavior_description": "User opens the site, hovers over each navigation link for 2 seconds, ultimately clicking on 'Home'.",
        "user_behavior_explanation": "The user is exploring their options in navigation before making a choice. The clicked link's HTML element is <a href='#home'> in the navigation. The CSS selector is 'nav ul li:nth-child(1) a'.",
        "user_profile_description": "Luxury real estate agent with a focus on high-net-worth clients.",
        "region": "Bellevue",
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "user_interaction_explanation": "A luxury real estate agent would want to familiarize themselves with the website's structure to best serve their high-net-worth clients."
    }
    _response_data = gen.generate_selenium_script(user_interaction_data=user_interaction_data)
    save_llm_response_data_to_python(
        response_data=_response_data,
        filename=f"test_script.py",
        scripts_dir=scripts_dir
    )
