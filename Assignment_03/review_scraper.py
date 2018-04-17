from selenium import webdriver
import pandas as pd
import json

# To simulate the delay
import random
import time
def delay(t):
    normal_delay = random.normalvariate(t, 0.5)
    time.sleep(normal_delay)

# Run the Chrome Driver and go to the review page
driver = webdriver.Chrome(executable_path=r'/Users/qinjiale/Downloads/chromedriver')
driver.get('https://www.amazon.com/RockBirds-Flashlights-Bright-Aluminum-Flashlight/product-reviews/B00X61AJYM')



# Rank the reviews from present to past
delay(4)
top_rated_reviews = driver.find_element_by_id('a-autoid-4-announce')
top_rated_reviews.click()
recent_reviews = driver.find_element_by_id('sort-order-dropdown_1')
recent_reviews.click()
# Find the reviews for a verified purchase
delay(3)
reviewer_button = driver.find_element_by_id('a-autoid-5-announce')
reviewer_button.click()
verified_reviews = driver.find_element_by_id('reviewer-type-dropdown_1')
verified_reviews.click()


"""
Reviews Scrape
Needed Information: 
customer name, review headline, review stars, review date, product pattern, review comment and review text
"""


# Set a dateset to store the data
data_set = []
# Set a flag for the while loop
flag = True

def scrape_reviews():
    global flag
    # locate the sorted reviews (exclude the recommend reviews on the top)
    review_page = driver.find_element_by_id('cm_cr-review_list')

    # Find the list for each part of the reviews on this page
    customer_names = review_page.find_elements_by_css_selector('.a-size-base.a-link-normal.author')
    headlines = review_page.find_elements_by_css_selector('.a-size-base.a-link-normal.review-title.a-color-base.a-text-bold')
    ratings = review_page.find_elements_by_xpath(".//a[contains(@title, 'out of 5 stars')]")
    dates = review_page.find_elements_by_css_selector(".a-size-base.a-color-secondary.review-date")
    patterns = review_page.find_elements_by_css_selector('.a-size-mini.a-link-normal.a-color-secondary')
    comments = review_page.find_elements_by_xpath("//*[contains(text(), 'Was this review helpful to you?')]")
    text_reviews = review_page.find_elements_by_css_selector(".a-size-base.review-text")

    # Then, find the needed information of each part
    customer_name = [customer_name.text for customer_name in customer_names]
    headline = [headline.text for headline in headlines]
    rating = [rating.get_attribute('title') for rating in ratings]
    date = [date.text for date in dates]
    year = list(date)
    pattern = [pattern.text for pattern in patterns]
    comment = [comment.text for comment in comments]
    text_review = [text_review.text for text_review in text_reviews]

    # Set the date requirement
    for i in range(len(year)):
        year[i] = year[i].split(', ')[1]
        if int(year[i]) > 2016:
            # Store the data into dataset
            data_set.append((customer_name[i], headline[i], rating[i], date[i], pattern[i], comment[i], text_review[i]))
        else:
            flag = False
            df = pd.DataFrame(data_set, columns=['CustomerName', 'Headline', 'Rating', 'Date', 'Pattern', 'Comment', 'TextRivew'])
            df.to_csv('firstpage.csv', index=False, header=False)
            data = df.to_json(orient='records')
            with open('reviews.json', 'w') as outfile:
                json.dump(data, outfile, sort_keys=True)
            break

delay(3)
scrape_reviews()

while(flag):
    delay(3)
    next = driver.find_element_by_class_name('a-last')
    next_page = next.find_elements_by_css_selector("*")[0]
    next_page.click()
    delay(3)
    scrape_reviews()


