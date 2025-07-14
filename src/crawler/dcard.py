# TODO: Dcard 登入使用 pyauto gui 比較方便，所以可能需要用 xvfb container 比較好，再想一下這邊的架構怎麼設計
# 目前想到是直接用一個 docker compose 來一次開，然後執行到這個腳本的時候利用那個 container 當作假的 Display
import time
import os


import undetected_chromedriver as uc
from selenium_stealth import stealth

# from fake_useragent import UserAgent
from dotenv import load_dotenv
from openai import OpenAI
from rich import print
from seleniumbase import SB


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

url_list = ["https://www.dcard.tw/f/ncku"]


# NOTE: SB test
def sb_get_raw_html(url: str):
    with SB(uc=True, test=True, locale="en", xvfb=True) as sb:
        sb.activate_cdp_mode(url)
        sb.uc_gui_click_captcha()  # 如果要這樣就不能用 headless 模式
        sb.sleep(2)
        sb.open(url)
        sb.wait_for_element("body", timeout=10)  # wait for the page to load
        result = sb.get_page_source()
        with open("dcard_content.html", "w", encoding="utf-8") as f:
            f.write(result)
        return result


def get_fake_user_agent():
    # This function can be used to generate a fake user agent using OpenAI's API
    client = OpenAI(
        api_key=OPENAI_API_KEY,
    )
    response = client.responses.create(
        model="gpt-4.1-mini",
        instructions="""Generate a random user agent string for a web browser. This user agent is used to crawl data from Dcard.Output something like:mozilla/5.0 (macintosh; intel mac os x 10_15_6) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36""",
        input="Generate a random user agent string for a web browser. As real as fuck",
    )

    user_agent = response.output_text
    print(f"Generated User-Agent: {user_agent}")
    return user_agent


def setup_driver():
    options = uc.ChromeOptions()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--use-subprocess")

    # NOTE: 目前只有使用第一種方法的前兩個 user agent 是有效的，如果要用 AI，那要給可以成功的 agent example

    ## 重點是要隨機化 User-Agent
    ## 這邊可能用 LLM 來隨機化 User-Agent
    # user_agents = [
    #     # "mozilla/5.0 (macintosh; intel mac os x 10_15_6) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36",
    #     # "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36 edg/122.0.0.0",
    #     # "mozilla/5.0 (macintosh; intel mac os x 10_15_1) applewebkit/605.1.15 (khtml, like gecko) version/17.0 safari/605.1.15", # this not work 因為他多寫了版本，其實可以不用寫！
    #     "mozilla/5.0 (macintosh; intel mac os x 10_15_1) applewebkit/605.1.15 (khtml, like gecko) safari/605.1.15", # this not work
    # ]
    #
    # options.add_argument(f"--user-agent={random.choice(user_agents)}")

    ## 用 AI 產生的
    user_agent = get_fake_user_agent()
    options.add_argument(f"--user-agent={user_agent}")

    # # 用 fake-useragent 套件
    # ua = UserAgent()
    # user_agent = ua.chrome
    # print(f"Using User-Agent from fake-useragent: {user_agent}")
    # options.add_argument(f"--user-agent={user_agent}")

    ### NOTE: 設定 proxy, 這邊目前還沒弄好，之所以會需要這個是因為要避免速率限制，而出現 cloudflare 的防護機制

    # # proxy = FreeProxy(country_id='TW', rand=True, timeout=1.0).get()
    # proxy = FreeProxy(country_id='CN').get()
    # proxy = FreeProxy().get()
    # print(f"Using Proxy: {proxy}")   ## get proxy ip
    # options.add_argument(f"--proxy-server={proxy}")

    driver = uc.Chrome(options=options)
    return driver


def apply_stealth(driver: uc.Chrome):
    stealth(
        driver,
        languages=["zh-TW", "en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        webgl_debug_renderer_info=True,
    )


def get_raw_html(url: str):
    driver = setup_driver()
    apply_stealth(driver)
    try:
        # wait for the page to load
        driver.get(url)
        time.sleep(20)  # wait for dynamic content to load
        driver.implicitly_wait(10)  # wait for elements to load
        content = driver.page_source
        return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


if __name__ == "__main__":
    # for url in url_list:
    #     content = get_raw_html(url)
    #     if content:
    #         print(f"Content from {url}:\n{content}\n")
    #         with open("dcard_content.html", "w", encoding="utf-8") as f:
    #             f.write(content)
    #     else:
    #         print(f"No content found for {url}.")
    result = sb_get_raw_html("https://www.dcard.tw/f/ncku")
    print("Done")
    # print(result)
