# #!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
import datetime

def timestamp():
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (ts + '\t')

URL_LOGIN = 'https://www.saucedemo.com/'
URL_INVENTORY = 'https://www.saucedemo.com/inventory.html'
URL_CART = 'https://www.saucedemo.com/cart.html'

# Start the browser and login with standard_user


def login(user, password):
    print(timestamp() + 'Starting the login test')
    # uncomment when running in Azure DevOps.
    options = ChromeOptions()
    options.add_argument("--no-sandbox") 
    options.add_argument("--disable-dev-shm-usage") 
    options.add_argument("--headless") 
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    # On Local
    # driver = webdriver.Chrome()

    print(timestamp() + 'Browser started successfully. Navigating to the demo page to login.')
    driver.get(URL_LOGIN)
    print(timestamp() + 'Navigating to the demo page to login.')

    # login
    driver.find_element(
        By.CSS_SELECTOR, "input[id='user-name']").send_keys(user)
    driver.find_element(
        By.CSS_SELECTOR, "input[id='password']").send_keys(password)
    driver.find_element(By.ID, "login-button").click()

    assert URL_INVENTORY in driver.current_url

    product_label = driver.find_element(
        By.CSS_SELECTOR, "div.header_secondary_container > span.title").text
    assert "Products" in product_label
    print(timestamp() + 'Login successfully as {:s} .'.format(user))

    return driver

# Test adding all products to cart


def addItem(driver):
    print(timestamp() + "Start test adding item to cart")
    items = driver.find_elements(By.CSS_SELECTOR, '.inventory_item')

    for i in range(0, len(items)):
        item = items[i]

        item_name = item.find_element(
            By.CLASS_NAME, 'inventory_item_name').text
        print(timestamp() + "Add item: {}".format(item_name))
        button = item.find_element(By.CSS_SELECTOR, '.pricebar > button')
        button.click()

    totalItemOnCartLabel = driver.find_element(
        By.CLASS_NAME, 'shopping_cart_badge').text
    testItemAdded = "6"

    print(timestamp() + "Total tested item added to cart: {}".format(testItemAdded))
    print(timestamp() + "Total item added to cart: {}".format(totalItemOnCartLabel))
    assert testItemAdded == totalItemOnCartLabel, "Total added item on cart not matched"

    print(timestamp() + "All item added to cart successfully")

# Test remove all products to cart

def removeItem(driver):
    print(timestamp() + "Start test remove item from the cart")

    items = driver.find_elements(By.CSS_SELECTOR, '.cart_item')

    for i in range(0, len(items)):
        item = items[i]

        item_name = item.find_element(
            By.CLASS_NAME, 'inventory_item_name').text
        print(timestamp() + "Remove item: {}".format(item_name))
        button = item.find_element(By.CSS_SELECTOR, '.item_pricebar > button')
        button.click()

    totalItemOnCartLabel = driver.find_element(
        By.CLASS_NAME, 'shopping_cart_link').text
    testItemRemove = "6"

    print(timestamp() + 
        "Total tested item remove from the to cart: {}".format(testItemRemove))
    assert "" == totalItemOnCartLabel, "Total added item on cart not matched"

    # Check on cart url
    print(timestamp() + "Test removed item on the cart page")
    driver.get(URL_CART)
    totalItemsOnCart = driver.find_elements(By.CLASS_NAME, 'cart_item')
    numberOfItemsInCart = 0

    assert numberOfItemsInCart == len(
        totalItemsOnCart), "Total added item on cart not matched"

    print(timestamp() +  "All item removed from cart successfully")


if __name__ == "__main__":
    driver = login('standard_user', 'secret_sauce')
    addItem(driver)
    removeItem(driver)

    print(timestamp() + "UI Tests are successfully completed")
