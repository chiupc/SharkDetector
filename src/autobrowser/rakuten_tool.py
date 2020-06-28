from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from logging.config import fileConfig
import time
import pandas as pd
import sys
import os

fileConfig('logging.ini')
logger = logging.getLogger()


class RakutenTool:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        if sys.platform == 'win32' or sys.platform == 'win64':
            self.browser = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver83.exe'))
        elif sys.platform == 'linux':
            #init headless chrome
            self.browser = webdriver.Chrome("chromedriver83.exe")
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            self.browser = webdriver.Chrome(os.path.join(os.getcwd(), 'chromedriver'), options=chrome_options)

    def login(self):
        self.browser.get('https://www.rakutentrade.my/login/')
        self.browser.maximize_window()
        try:
            loginNameField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "loginName")))
            passwordField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "password")))
            loginNameField.send_keys(self.username)
            passwordField.send_keys(self.password)
            loginBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "login-btn")))
            loginBtn.click()
        except Exception as e:
            logger.error(e)

    def navigate_to_stock_page(self,code,symbol):
        searchStockField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//input[@class='search-input scene-input ui-input-text ui-body-a']")))
        searchStockField.send_keys(code)
        time.sleep(1)
        stockListItem = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//li[@data-symbol='" + symbol + "']")))
        stockListItem.click()

    def get_cash_balance(self):
        myAccountBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//li[@title='MY ACCOUNT']")))
        myAccountBtn.click()
        cashBalanceTextField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//td[@class='cash-value right']")))
        cashbalance = float(cashBalanceTextField.text.replace(',',''))
        return cashbalance

    #return data frame of order status
    def get_orders(self):
        orderStatusBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//li[@title='ORDER STATUS']")))
        orderStatusBtn.click()
        orderStatusTable = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.ID, "order_status_table")))
        orderStatusTableHTML=orderStatusTable.get_attribute('outerHTML')
        df = pd.read_html(orderStatusTableHTML)
        return df

    #return data rame of trade history
    def get_trade_history(self):
        orderStatusBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//li[@title='ORDER STATUS']")))
        orderStatusBtn.click()
        tradeHistBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.ID, "trade")))
        tradeHistBtn.click()
        tableHeader=WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//thead[@class='header-table']")))
        tradeHistTable = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.ID, "trade_status_table")))
        tradeHistTableHTML=tradeHistTable.get_attribute('outerHTML')
        df = pd.read_html(tradeHistTableHTML)
        return df

    def buy_order(self,lot_qty,buy_price,trading_pin):
        time.sleep(3)
        buyBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//button[@class='trade-buy trade-btn']")))
        buyBtn.click()
        buyPriceField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.ID, "price_idx")))
        buyPriceField.send_keys(str(buy_price))
        lotQtyField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//input[@class='order-input order-val Qty']")))
        lotQtyField.send_keys(str(lot_qty))
        tradingPinField = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//input[@class='order-input tpin-val tpin-pswd-txt']")))
        tradingPinField.send_keys(str(trading_pin))
        skipConfirmationBox = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='skip-confirmation']")))
        skipConfirmationBox.click()
        submitOrderBtn = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//button[@name='order_det_confirm']")))
        submitOrderBtn.click()
        time.sleep(3)
        orderMessageTextField=WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
            (By.XPATH, "//div[@class='order-msg']")))
        orderMessage = orderMessageTextField.text
        if 'submitted successfully' in orderMessage:
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//div[@class='order_list']")))
            orderListTextField = self.browser.find_element_by_xpath("//div[@class='order_list']")
            orderNumbers = orderListTextField.text
            logger.info(orderMessage + '' + orderNumbers)
            return orderNumbers
        else:
            logger.info(orderMessage)

