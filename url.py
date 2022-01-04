from datetime import datetime, timedelta
import time
from pandas.core.frame import DataFrame
from pandas import concat

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pandas import read_csv


SCROLL_TIME = 1
LIMIT_REVIEWS = 12000
LIMIT_SCORE_5 = 4000
LIMIT_SCORE_4 = 4000
LIMIT_SCORE_3 = 2000
LIMIT_SCORE_2 = 1000
LIMIT_SCORE_1 = 1000
LIMIT_PRODUCT_PAGES = 1000
LIMIT_PAGES_OF_REVIEW = 1000
LIMIT_HOURS = 1

checkpoint = read_csv("checkpoint")
checkpoint_page = int(checkpoint['page'])
checkpoint_product = int(checkpoint['products'])
checkpoint_score5 = int(checkpoint['score_5'])
checkpoint_score4 = int(checkpoint['score_4'])
checkpoint_score3 = int(checkpoint['score_3'])
checkpoint_score2 = int(checkpoint['score_2'])
checkpoint_score1 = int(checkpoint['score_1'])

current_count = {5: checkpoint_score5, 4: checkpoint_score4, 3: checkpoint_score3, 2: checkpoint_score2, 1:checkpoint_score1}

url = ""
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('disable-infobars')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='language-selection__list-item']//button[text()='ไทย']"))).click()
page_id = 1


def save_checkpoint(page: int, products: int):
    checkpoint_df = DataFrame({
        "page": [page], 
        "products": [products + 1], 
        "score_5": [current_count[5]],
        "score_4": [current_count[4]],
        "score_3": [current_count[3]],
        "score_2": [current_count[2]],
        "score_1": [current_count[1]]}
        )
    if int(checkpoint_df['page']) < checkpoint_page or int(checkpoint_df['products']) < checkpoint_product:
        return
    print(checkpoint_df)
    checkpoint_df.to_csv("checkpoint", index=False)


def click_next_page(driver: webdriver) -> bool:
    """
    Return True if next_button can be clicked, False otherwise
    """
    current_page = driver.find_elements_by_css_selector("button.shopee-button-solid.shopee-button-solid--primary")[2]
    # next_button = driver.find_elements_by_css_selector("button.shopee-button-no-outline")[i]
    next_button = driver.find_elements_by_css_selector("button.shopee-icon-button.shopee-icon-button--right")[0]
    
    print(f"before click: previous = {int(current_page.text)}")
    previous_page = int(current_page.text)
    next_button.click()
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight*1/4)")
    time.sleep(SCROLL_TIME/2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight*2/4)")
    time.sleep(SCROLL_TIME/2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4)")
    time.sleep(SCROLL_TIME/2)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(SCROLL_TIME/2)
    current_page = int(driver.find_elements_by_css_selector("button.shopee-button-solid.shopee-button-solid--primary")[2].text)
    print(f"after click: previous = {previous_page}, current = {current_page}")
    
    if current_page > previous_page:
        return True
    # if int(next_button.text) > int(current_page.text):
    #     next_button.click()
    #     return True
    return False


def is_rating_valid(rating: int, current_count: dict):
    """
    Return True if rating is not more than limit
    """
    # if rating == 5 and current_count[5] <= LIMIT_SCORE_5:
    #     return True
    # elif rating == 4 and current_count[4] <= LIMIT_SCORE_4:
    #     return True
    if rating == 3 and current_count[3] <= LIMIT_SCORE_3:
        return True
    elif rating == 2 and current_count[2] <= LIMIT_SCORE_2:
        return True
    elif rating == 1 and current_count[1] <= LIMIT_SCORE_1:
        return True
    return False


def is_review_valid(review: str) -> bool:
    """
    Return True if review is length between 50 and 1000
    """
    if len(review) >= 50 and len(review) <= 1000:
        return True
    return False

    
def scrap_comments_from_url(url: str):
    ratings, reviews = [], []
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='language-selection__list-item']//button[text()='ไทย']"))).click()
    page_of_review = 1
    while page_of_review < LIMIT_REVIEWS + 1:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*1/4)")
        time.sleep(SCROLL_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*2/4)")
        time.sleep(SCROLL_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4)")
        time.sleep(SCROLL_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(SCROLL_TIME)
        product_ratings = driver.find_elements_by_css_selector("div.shopee-product-rating__rating")
        product_reviews = driver.find_elements_by_css_selector("div._3NrdYc")
        # product_reviews = driver.find_elements_by_css_selector("div.shopee-product-rating__main")
        
        for rating, review in zip(product_ratings, product_reviews):
            rating = rating.find_elements_by_css_selector("svg.icon-rating-solid--active")
            review = review.text.strip()
            review = review.replace("\n", " ")
            print("rating: ", len(rating))
            if is_rating_valid(len(rating), current_count) and is_review_valid(review):
                current_count[len(rating)] += 1
                ratings.append(int(len(rating)))
                reviews.append(review)
                print(len(rating), review)
        current_page = int(driver.find_elements_by_css_selector("button.shopee-button-solid.shopee-button-solid--primary")[0].text)
        next_button = driver.find_element_by_css_selector("button.shopee-icon-button.shopee-icon-button--right")
        next_button.click()
        time.sleep(SCROLL_TIME)
        next_page = int(driver.find_elements_by_css_selector("button.shopee-button-solid.shopee-button-solid--primary")[0].text)
        print(current_page, next_page)
        if current_page >= next_page or current_page >= LIMIT_PAGES_OF_REVIEW:
            break
        page_of_review += 1
    driver.close()
    return ratings, reviews


all_df = DataFrame()
save_checkpoint_product = 0
start_time = datetime.now()
while page_id < LIMIT_PRODUCT_PAGES:
    current_time = datetime.now()
    if current_time - start_time > timedelta(hours=LIMIT_HOURS):
        break

    try:
        print("page: ", page_id, checkpoint_page)
        if page_id < checkpoint_page:
            if click_next_page(driver):
                print("CLICK!")
                page_id += 1
                continue
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*1/4)")
        time.sleep(SCROLL_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*2/4)")
        time.sleep(SCROLL_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight*3/4)")
        time.sleep(SCROLL_TIME)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(SCROLL_TIME)
        products = driver.find_elements_by_xpath("//div[@class='col-xs-2-4 shopee-search-item-result__item']//a[@href]")

        for product_id, product in enumerate(products):
            if product_id > 49:
                break
            print(f"product id: {product_id}")
            current_time = datetime.now()
            if current_time - start_time > timedelta(hours=LIMIT_HOURS):
                break
            if product_id < checkpoint_product:
                continue
            save_checkpoint_product = product_id + 1
            ratings, reviews = scrap_comments_from_url(product.get_attribute('href'))
            product_df = DataFrame({"review": reviews, "rating": ratings})
            all_df = concat([all_df, product_df], ignore_index=False)
        if click_next_page(driver):
            page_id += 1
        else:
            break
    except Exception as e:
        page_id += 1
        save_checkpoint(page=page_id, products=save_checkpoint_product)

print(all_df)
save_checkpoint(page=page_id, products=save_checkpoint_product)
date_now = datetime.now().strftime("%d_%m_%y_%H%M%S")
all_df.to_csv(f"fasion_male_{date_now}.csv", index=False)
driver.close()