import math
import os
import re
import tempfile
import time
from datetime import datetime, timedelta
from functools import reduce

import numpy as np
import pandas as pd
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Name of the download file created by Google Trends
NAME_DOWNLOAD_FILE = "multiTimeline.csv"


class GoogleTrendsScraper:
    def __init__(self, sleep=1, path_driver=None):
        """
        Constructor of the Google-Scraper-Class
        Args:
            sleep: integer number of seconds where the scraping waits (avoids getting blocked and gives the code time
                    to download the data
            path_driver: path as string to where the chrome driver is located
        """
        # Current directory
        self.dir = os.getcwd()
        # Define download folder for browser:
        self.download_path = tempfile.TemporaryDirectory()
        # Define the path to the downloaded csv-files (this is where the trends are saved)
        self.filename = os.path.join(self.download_path.name, NAME_DOWNLOAD_FILE)
        # Whether the browser should be opened in headless mode
        self.headless = True
        # Path to the driver of Google Chrome
        self.path_driver = path_driver
        # Initialize the browser variable
        self.browser = None
        # Sleep time used during the scraping procedure
        self.sleep = sleep
        # Format of dates used by google
        self._google_date_format = "%Y-%m-%d"
        # Lunch the browser
        self.start_browser()

    def start_browser(self):
        """
        Method that initializes a selenium browser using the chrome driver

        """
        # If the browser is already running, do not start a new one
        if self.browser is not None:
            print("Browser already running")
            pass
        # Options for the browser
        chrome_options = webdriver.ChromeOptions()
        # Define browser language
        chrome_options.add_experimental_option(
            "prefs", {"intl.accept_languages": "en,en_US"}
        )
        # If the browser should be run in headless mode
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("window-size=1920x1080")
        # If no path for the chrome drive is defined, the default is used, i.e. path variables are checked
        if self.path_driver is None:
            self.path_driver = "chromedriver"
        # Start the browser
        service = Service(service=ChromeDriverManager().install())
        self.browser = webdriver.Chrome(service=service, chrome_options=chrome_options)
        # Define the download behaviour of chrome
        # noinspection PyProtectedMember
        self.browser.command_executor._commands["send_command"] = (
            "POST",
            "/session/$sessionId/chromium/send_command",
        )
        self.browser.execute(
            "send_command",
            {
                "cmd": "Page.setDownloadBehavior",
                "params": {
                    "behavior": "allow",
                    "downloadPath": self.download_path.name,
                },
            },
        )

    def quit_browser(self):
        """
        Method that closes the existing browser

        """
        if self.browser is not None:
            self.browser.quit()
            self.browser = None

    def get_trends(
        self,
        keywords,
        start,
        end,
        region=None,
        category=None,
    ):
        """
        Function that starts the scraping procedure and returns the Google Trend data.
        Args:
            keywords: list of strings of keywords
            region: string indicating the region for which the trends are computed, default is None (Worldwide trends)
            start: start date as a string
            end: end date as a string
            category: integer indicating the category (e.g. 7 is the category "Finance")

        Returns: pandas DataFrame

        """
        for keyword in keywords:
            print(f"Scraping keyword: {keyword}")
            url = self.create_url(keyword, start, end, region, category)
            try:
                data = self.get_data(url)
                return data
            except Exception as e:
                print(f"No data found for keyword: {keyword}.")
                return None

    def create_url(self, keyword, start, end, region=None, category=None):
        """
        Creates a URL for Google Trends
        Args:
            keyword: string of keyword
            start: start date as a string
            end: end date as a string
            region: string indicating the region for which the trends are computed, default is None (Worldwide trends)
            category: integer indicating the category (e.g. 7 is the category "Finance")

        Returns: string of the URL for Google Trends of the given keywords over the time period from 'start' to 'end'

        """
        # Replace the '+' symbol in a keyword with '%2B'
        keyword = re.sub(r"[+]", "%2B", keyword)
        # Replace white spaces in a keyword with '%20'
        keyword = re.sub(r"\s", "%20", keyword)
        # Define main components of the URL
        base = "https://trends.google.com/trends/explore"
        geo = f"geo={region}&" if region is not None else ""
        query = f"q={keyword}"
        cat = f"cat={category}&" if category is not None else ""
        # Define the date-range component for the URL
        date = f"date={start}%20{end}"
        # Construct the URL
        url = f"{base}?{cat}{date}&{geo}{query}"
        return url

    def get_data(self, url):
        """
        Method that retrieves for a specific URL the Google Trend data. Note that this is done by downloading a csv-file
        which is then loaded and stored as a pandas.DataFrame object
        Args:
            url: URL for the trend to be scraped as a string

        Returns: a pandas.DataFrame object containing the trends for the given URL

        """
        # Initialize the button that needs to be pressed to get download the data
        button = None
        # While this button is of type 'None' we reload the browser
        while button is None:
            try:
                # Navigate to the URL
                self.go_to_url(url)
                # Sleep the code by the defined time plus a random number of seconds between 0s and 2s. This should
                # reduce the likelihood that Google detects us as a scraper
                time.sleep(self.sleep * (1 + np.random.rand()))
                # Try to find the button and click it
                line_chart = self.browser.find_element(
                    By.CSS_SELECTOR, "widget[type='fe_line_chart']"
                )
                button = line_chart.find_element(
                    By.CSS_SELECTOR, ".widget-actions-item.export"
                )
                button.click()
            except exceptions.NoSuchElementException:
                # If the button cannot be found, try again (load page, ...)
                pass
        # After downloading, wait again to allow the file to be downloaded
        time.sleep(self.sleep * (1 + np.random.rand()))
        # Load the data from the csv-file as pandas.DataFrame object
        data = pd.read_csv(self.filename, skiprows=2)
        # Rename columns for clarity
        data.columns = ["date", "value"]
        # Convert 'date' column to datetime type
        data["date"] = pd.to_datetime(data["date"])

        # Set 'date' as the index
        data.set_index("date", inplace=True)

        # Sleep again
        time.sleep(self.sleep * (1 + np.random.rand()))
        # Delete the file
        while os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except:
                pass
        return data

    def go_to_url(self, url):
        """
        Method that navigates in the browser to the given URL
        Args:
            url: URL to which we want to navigate as a string

        """
        if self.browser is not None:
            self.browser.get(url)
        else:
            print("Browser is not running")

    def __del__(self):
        """
        When deleting an instance of this class, delete the temporary file folder and close the browser

        """
        self.download_path.cleanup()
        self.quit_browser()
