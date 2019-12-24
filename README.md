## Dependencies:
- scrapy
- pandas
- BeautifulSoup
- selenium
- requests

## Selenium setup:

In order for the driver to work, go to the ChromeDriver downloads page here: https://sites.google.com/a/chromium.org/chromedriver/home and download the correct driver for your OS and version of Chrome. Other browsers may work, but will require modifications to the code and also have not been tested. Place the driver into the same folder as the file the spider is located. There is currently a MacOS ChromeDriver for Chrome version 77 in the folder that can be replaced.

## Instructions

To start, run the script with python3 scraper.py located inside aids_scraper/aids_scraper/spiders. Make sure there is not a folder named "scrapes" already inside the spiders folder. The script will output 42 CSV files (as of 2019) of datasets (one for each year starting from 1978) into this folder.

## Notes

The script will open and close several Chrome windows during its run. Don't close these windows otherwise the script will not work. Overall runtime should not be too long (Should only be a few hours maximum depending on how fast the system is able to open chrome browsers and send POST requests).