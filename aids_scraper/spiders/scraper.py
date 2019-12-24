import scrapy
import csv
import os
import pandas as pd
import requests
import datetime
from bs4 import BeautifulSoup as bs
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

data = {
			"p_flow_id": "100",
			"p_flow_step_id": "11",
			"p_instance": "10627854411936",
			"p_request": "APXWGT",
			"p_widget_action": "paginate",
			"p_pg_min_row": "1",
			"p_pg_max_rows": "50",
			"p_pg_rows_fetched": "50",
			"x01": "31839809323498316",
			"p_widget_name": "classic_report",
			"p_json": '{"salt":"328080557190964301516645871009597313174"}'
		}
fields = [
	"aids_report_number",
	"local_event_date",
	"event_city",
	"event_state",
	"event_airport",
	"event_type",
	"aircraft_damage",
	"flight_phase",
	"aircraft_make",
	"aircraft_model",
	"aircraft_series",
	"operator",
	"primary_flight_type",
	"flight_conduct_code",
	"flight_plan_filed_code",
	"aircraft_registration_nbr",
	"total_fatalities",
	"total_injuries",
	"aircraft_engine_make",
	"aircraft_engine_model",
	"engine_group_code",
	"nbr_of_engines",
	"pic_certificate_type",
	"pic_flight_time_total_hrs",
	"pic_flight_time_total_make-model",
	"NULL",
	"NULL"
]
finished_scraping = {}
today = str(datetime.date.today());
curr_year = int(today[:4]);
year = 1978
dates = [[] for i in range(curr_year - (year - 1))]

if not os.path.exists('scrapes'):
	os.makedirs('scrapes')

for date in dates:
	with open('scrapes/scrape' + str(year) + '.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(fields)
	shortYear = str(year % 100)
	if len(shortYear) == 1:
		shortYear = "0" + shortYear
	date.append(year) # Index 0 is the year
	date.append("01-Jan-" + shortYear) # Index 1 is the starting day
	date.append("31-Dec-" + shortYear) # Index 2 is the end day
	finished_scraping[date[0]] = {}
	year += 1

class scraper(scrapy.Spider):
	def __init__(self):
		self.name = 'scraper'
		self.allowed_domains = ['www.asias.faa.gov']
		self.api_url = "https://www.asias.faa.gov/apex/wwv_flow.ajax"
		self.finished_scraping = finished_scraping
		self.data = data

	def start_requests(self):
		for date in dates:
			d = webdriver.Chrome('./chromedriver') 
			d.get('https://www.asias.faa.gov/apex/f?p=100:12:::NO:::')
			try:  #attempt to dismiss banners that could block later clicks
				WebDriverWait(d, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".closer"))).click()
				d.find_element_by_css_selector('.closer').click()
			except:
				pass
			sDate = d.find_element_by_id('P12_EVENT_STRT_DATE')
			sDate.clear()
			sDate.send_keys(date[1])
			d.find_element_by_id("P12_EVENT_STRT_DATE").send_keys(Keys.RETURN)
			eDate = d.find_element_by_id('P12_EVENT_END_DATE')
			eDate.clear()
			eDate.send_keys(date[2])
			d.find_element_by_id("P12_EVENT_END_DATE").send_keys(Keys.RETURN)
			d.find_element_by_id("B14245265123184264").click()
			driverCookies = d.get_cookies()
			d.close()
			cookie = driverCookies[0]['value']
			cookie = 'ORA_WWV_APP_100=' + cookie
			headers = {
				"Accept": "text/html, */*; q=0.01",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "en-US,en;q=0.9,und;q=0.8",
				"Connection": "keep-alive",
				# "Content-Length": "285",
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"Cookie": cookie,
				"Host": "www.asias.faa.gov",
				"Origin": "https://www.asias.faa.gov",
				"Referer": "https://www.asias.faa.gov/apex/f?p=100:11:::NO:::",
				"Sec-Fetch-Mode": "cors",
				"Sec-Fetch-Site": "same-origin",
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
				"X-Requested-With": "XMLHttpRequest"
			}
			yield scrapy.FormRequest(url=self.api_url,
								formdata=self.data,
								headers=headers,
								callback=self.parse, 
								meta={'p_pg_min_row': 1, 'date': date[0], 'cookie': cookie}, 
								dont_filter=True, 
								errback=self.handle_failure)

	def handle_failure(self, failure):
		self.data['p_pg_min_row'] = str(failure.request.meta['p_pg_min_row'])
		index = 0
		for date in dates:
			if date[0] == failure.request.meta['date']:
				break 
			index += 1
		date = dates[index]
		d = webdriver.Chrome('./chromedriver') 
		d.get('https://www.asias.faa.gov/apex/f?p=100:12:::NO:::')
		try:  #attempt to dismiss banners that could block later clicks
			WebDriverWait(d, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".closer"))).click()
			d.find_element_by_css_selector('.closer').click()
		except:
			pass
		sDate = d.find_element_by_id('P12_EVENT_STRT_DATE')
		sDate.clear()
		sDate.send_keys(date[1])
		d.find_element_by_id("P12_EVENT_STRT_DATE").send_keys(Keys.RETURN)
		eDate = d.find_element_by_id('P12_EVENT_END_DATE')
		eDate.clear()
		eDate.send_keys(date[2])
		d.find_element_by_id("P12_EVENT_END_DATE").send_keys(Keys.RETURN)
		d.find_element_by_id("B14245265123184264").click()
		driverCookies = d.get_cookies()
		d.close()
		cookie = driverCookies[0]['value']
		cookie = 'ORA_WWV_APP_100=' + cookie
		headers = {
			"Accept": "text/html, */*; q=0.01",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "en-US,en;q=0.9,und;q=0.8",
			"Connection": "keep-alive",
			# "Content-Length": "285",
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			"Cookie": cookie,
			"Host": "www.asias.faa.gov",
			"Origin": "https://www.asias.faa.gov",
			"Referer": "https://www.asias.faa.gov/apex/f?p=100:11:::NO:::",
			"Sec-Fetch-Mode": "cors",
			"Sec-Fetch-Site": "same-origin",
			"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
			"X-Requested-With": "XMLHttpRequest"
		}
		yield scrapy.FormRequest(url=self.api_url,
							formdata=self.data,
							headers=headers,
							callback=self.parse,
							meta={'p_pg_min_row': failure.request.meta['p_pg_min_row'],
								'date': failure.request.meta['date'],
								'cookie': cookie},
							dont_filter=True,
							errback=self.handle_failure)
		
	def parse(self, response):
		if "Your session has expired" in response.text and "to create a new session." in response.text:
			index = 0
			for date in dates:
				if date[0] == response.meta['date']:
					break 
				index += 1
			date = dates[index]
			d = webdriver.Chrome('./chromedriver') 
			d.get('https://www.asias.faa.gov/apex/f?p=100:12:::NO:::')
			try:  #attempt to dismiss banners that could block later clicks
				WebDriverWait(d, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".closer"))).click()
				d.find_element_by_css_selector('.closer').click()
			except:
				pass
			sDate = d.find_element_by_id('P12_EVENT_STRT_DATE')
			sDate.clear()
			sDate.send_keys(date[1])
			d.find_element_by_id("P12_EVENT_STRT_DATE").send_keys(Keys.RETURN)
			eDate = d.find_element_by_id('P12_EVENT_END_DATE')
			eDate.clear()
			eDate.send_keys(date[2])
			d.find_element_by_id("P12_EVENT_END_DATE").send_keys(Keys.RETURN)
			d.find_element_by_id("B14245265123184264").click()
			driverCookies = d.get_cookies()
			d.close()
			cookie = driverCookies[0]['value']
			cookie = 'ORA_WWV_APP_100=' + cookie
			headers = {
				"Accept": "text/html, */*; q=0.01",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "en-US,en;q=0.9,und;q=0.8",
				"Connection": "keep-alive",
				# "Content-Length": "285",
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"Cookie": cookie,
				"Host": "www.asias.faa.gov",
				"Origin": "https://www.asias.faa.gov",
				"Referer": "https://www.asias.faa.gov/apex/f?p=100:11:::NO:::",
				"Sec-Fetch-Mode": "cors",
				"Sec-Fetch-Site": "same-origin",
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
				"X-Requested-With": "XMLHttpRequest"
			}
			yield scrapy.FormRequest(url=self.api_url,
								formdata=self.data,
								headers=headers,
								callback=self.parse,
								meta={'p_pg_min_row': response.meta['p_pg_min_row'],
									'date': response.meta['date'],
									'cookie': cookie},
								dont_filter=True,
								errback=self.handle_failure)
		else:
			if "Error processing request."in response.text or "Invalid set of rows requested, the source data of the report has been modified." in response.text:
				return
			try:
				self.finished_scraping[response.meta['date']][response.meta['p_pg_min_row']]
				return
			except:
				pass
			soup = bs(response.text, 'html.parser')
			data = [[] for i in range(29)]
			for i in range(2, 29):
				if i >= 0 and i <= 9:
					header = 'COL0' + str(i)
				else:
					header = 'COL' + str(i)
				results = soup.findAll(attrs={'headers': header})
				for tag in results:
					data[i].append(tag.text)
			df = pd.DataFrame(columns=fields)
			for i in range(2, 29):
				df[fields[i - 2]] = data[i]
			try:
				self.finished_scraping[response.meta['date']][response.meta['p_pg_min_row']]
			except:
				self.finished_scraping[response.meta['date']][response.meta['p_pg_min_row']] = True
				with open('scrapes/scrape' + str(response.meta['date']) + '.csv', 'a') as f:
					df.to_csv(f, header=None, index=False)
				print("Finished scraping rows: " + str(response.meta['p_pg_min_row']) + "-" + str(response.meta['p_pg_min_row'] + 49)
					+ " for " + str(response.meta['date']))
			next_rows_index = response.meta['p_pg_min_row'] + 50
			self.data['p_pg_min_row'] = str(next_rows_index)
			headers = {
				"Accept": "text/html, */*; q=0.01",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "en-US,en;q=0.9,und;q=0.8",
				"Connection": "keep-alive",
				# "Content-Length": "285",
				"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
				"Cookie": response.meta['cookie'],
				"Host": "www.asias.faa.gov",
				"Origin": "https://www.asias.faa.gov",
				"Referer": "https://www.asias.faa.gov/apex/f?p=100:11:::NO:::",
				"Sec-Fetch-Mode": "cors",
				"Sec-Fetch-Site": "same-origin",
				"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
				"X-Requested-With": "XMLHttpRequest"
			}
			yield scrapy.FormRequest(url=self.api_url,
								formdata=self.data,
								headers=headers,
								callback=self.parse,
								meta={'p_pg_min_row': next_rows_index,
									'date': response.meta['date'],
									'cookie': response.meta['cookie']},
								dont_filter=True,
								errback=self.handle_failure)




def start_scraping():
	process = CrawlerProcess(get_project_settings())
	process.crawl(scraper)
	process.start()

start_scraping()
