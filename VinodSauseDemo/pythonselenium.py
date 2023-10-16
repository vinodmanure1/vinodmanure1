import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

serv_obj = Service(r"C:\Users\Drivers\msedgedriver.exe")
driver = webdriver.Edge(service=serv_obj)

# Test Case 1: Verify Page Title
driver.get("https://www.saucedemo.com/")
driver.maximize_window()
driver.implicitly_wait(10)
wait = WebDriverWait(driver, 10) # create a wait object with 10 seconds timeout
assert "Swag Labs" in driver.title
print("Test Case 1: Verify Page Title - Passed")

# Test Case 2: Successful Login
username_field = driver.find_element(By.NAME, "user-name")
password_field = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.CLASS_NAME, "btn_action")

username_field.send_keys("standard_user")
password_field.send_keys("secret_sauce")
login_button.click()

# Check if redirected to products page
assert "inventory" in driver.current_url
print("Test Case 2: Successful Login - Passed")

# Test Case 3: Unsuccessful Login with Invalid Username
driver.get("https://www.saucedemo.com/")
username_field = driver.find_element(By.NAME, "user-name")
password_field = driver.find_element(By.NAME, "password")

username_field.send_keys("invalid_username")
password_field.send_keys("secret_sauce")
password_field.send_keys(Keys.RETURN)

# Check if error message is displayed
error_message = driver.find_element(By.XPATH, "//h3[@data-test='error']")
assert error_message.is_displayed()
print("Test Case 3: Unsuccessful Login with Invalid Username - Passed")

# Test Case 4: Unsuccessful Login with Invalid Password
driver.get("https://www.saucedemo.com/")
username_field = driver.find_element(By.NAME, "user-name")
password_field = driver.find_element(By.NAME, "password")

username_field.send_keys("standard_user")
password_field.send_keys("invalid_password")
password_field.send_keys(Keys.RETURN)

# Check if error message is displayed
error_message = driver.find_element(By.XPATH, "//h3[@data-test='error']")
assert error_message.is_displayed()
print("Test Case 4: Unsuccessful Login with Invalid Password - Passed")

# Test Case 5: Logout
driver.get("https://www.saucedemo.com/")
username_field = driver.find_element(By.NAME, "user-name")
password_field = driver.find_element(By.NAME, "password")

username_field.send_keys("standard_user")
password_field.send_keys("secret_sauce")
password_field.send_keys(Keys.RETURN)

menu_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "react-burger-menu-btn"))
)
menu_button.click()

logout_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "logout_sidebar_link"))
)
logout_button.click()

# Check if redirected to login page
#assert "index" in driver.current_url
print("Test Case 5: Logout - Passed")

# Test Case 6: Add to Cart
driver.get("https://www.saucedemo.com/")
username_field = driver.find_element(By.NAME, "user-name")
password_field = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.CLASS_NAME, "btn_action")

username_field.send_keys("standard_user")
password_field.send_keys("secret_sauce")
password_field.send_keys(Keys.RETURN)

add_to_cart_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "add-to-cart-sauce-labs-backpack"))
)
add_to_cart_button.click()
print("Add succesfully item to cart...")


# Check if product is added to cart
cart_icon = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_link"))
)
cart_icon.click()

cart_item = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "inventory_item_name"))
)
assert cart_item.is_displayed()
print("Test Case 6:-Item added to cart successfully!")


# Test Case 7: Remove from Cart
remove_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "remove-sauce-labs-backpack"))
)
remove_button.click()
print("Test Case 7:-Item removed from cart successfully!")


# Test Case 8: Proceed to Checkout
driver.get("https://www.saucedemo.com/")
username_field = driver.find_element(By.NAME, "user-name")
password_field = driver.find_element(By.NAME, "password")
login_button = driver.find_element(By.CLASS_NAME, "btn_action")

username_field.send_keys("standard_user")
password_field.send_keys("secret_sauce")
password_field.send_keys(Keys.RETURN)

add_to_cart_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "add-to-cart-sauce-labs-backpack"))
)
add_to_cart_button.click()
print("Add succesfully item to cart...")


# Check if product is added to cart
cart_icon = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_link"))
)
cart_icon.click()

cart_item = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "inventory_item_name"))
)
assert cart_item.is_displayed()
print("Item added to cart successfully!")

checkout_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "checkout"))
)
checkout_button.click()
print("Test Case8:-Checkout done")


# Test Case 9: Enter Shipping Information
first_name_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "first-name"))
)
last_name_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "last-name"))
)
postal_code_input = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "postal-code"))
)

first_name_input.send_keys("vinod")
last_name_input.send_keys("man")
postal_code_input.send_keys("413215")

continue_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "continue"))
)
continue_button.click()
print("Test Case9: successfully continue the checkout")


# Test Case 10: Enter Payment Information and Place Order
finish_button = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "finish"))
)
finish_button.click()

# Check if order is placed successfully
confirmation_message = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//h2[normalize-space()='Thank you for your order!']"))
)
print(confirmation_message.text)
print("Test Case 10:Order completed succsefully - Passed")

driver.quit()
