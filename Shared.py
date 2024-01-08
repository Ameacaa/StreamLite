from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from pathlib import Path
import urllib3
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image, ImageDraw, ImageFont
from selenium.webdriver.common.by import By
from selenium import webdriver
from haralyzer import HarParser
from browsermobproxy import Server
from random import choice
from shutil import rmtree
from pathlib import Path
from colorama import Fore, Back
import urllib3
import requests
import string
import time
import sys
import os


# CLASSES -----------------------------

@dataclass
class DownloadInfos:
	download_date: datetime
	download_result: str


class ProxyManager:
	__BMP = r'B:\Projects\_new_\StreamLite\Addicionals\proxy\bin\BrowserMobProxy.bat'  # TODO Make relative
	
	def __init__(self):
		self.__server = Server(ProxyManager.__BMP)
		self.__client = None
	
	def start_server(self):
		self.__server.start()
		return self.__server
	
	def start_client(self):
		self.__client = self.__server.create_proxy(params={"trustAllServers": "true"})
		return self.__client
	
	@property
	def client(self):
		return self.__client
	
	@property
	def server(self):
		return self.__server


# DECORATORS --------------------------

def chronofunc(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		begin = time.monotonic_ns()
		result = func(*args, **kwargs)
		timetake = (time.monotonic_ns() - begin) / 1_000_000_000
		print(f'{Back.BLUE}{Fore.RED}Time taken ({func.__name__}): {timetake:.3f} seconds{Fore.RESET}{Back.RESET}')
		return result
	
	return wrapper


# FUNCTIONS ---------------------------


def persistent_hash(s: str):
	"""
	Return a hash from a string that is persistent (always the same)
	"""
	ord3 = lambda x: '%.3d' % ord(x)
	return int(''.join(map(ord3, s)))


def persistent_dehash(_hash):
	"""
	Return a string from a hash that is persistent (always the same)
	"""
	s = str(_hash)
	return ''.join([chr(int(s[i:i + 3])) for i in range(0, len(s), 3)])


def get_random_str(string_length: int, keep: str = 'lud', adicional_chars: str = '') -> str:
	"""
	Return a random string
	@param string_length: The length of the returned string
	@param keep: Lower, Upper, Digits, Ponctuation, Windows ponctuation, Space(' '), Xspaces('\t\n\r\v\f')
	@param adicional_chars: Char wanted in random string, can be anything
	@return: A string with random characters
	"""
	from random import choice
	import string as s
	char_sets = {
		'l': s.ascii_lowercase,
		'u': s.ascii_uppercase,
		'd': s.digits,
		'p': s.punctuation,
		'x': s.whitespace,
		's': ' ',
		'w': r"""!#$%&'()_+,-.;=@[]^_`{}~"""
	}
	valid_chars = adicional_chars.join(char_sets[char] for char in keep if char in char_sets)
	return ''.join(choice(valid_chars) for i in range(string_length))


def download_urlfile(url: str, filepath: str, chunk_size: int = 1073741824):
	"""
	Download a file from url
	@param url: The url of the file to download
	@param filepath: The absolute path of the file download (path, name, extention)
	@param chunk_size: The size of the chunk default 1Gb
	"""
	urllib = urllib3.PoolManager()
	
	response = urllib.request('GET', url, preload_content=False)
	
	with open(filepath, 'wb') as output:
		data = response.read(chunk_size)
		if not data: pass
		output.write(data)
	response.release_conn()


def get_total_video_parts(base_url: str, end_url: str) -> int:
	"""
	Get the total number of parts for a video on the web using a binary search approach.
	In case of an exception during the process, the function returns a default value of 4096.
	@param base_url: The base URL of the video parts.
	@param end_url: The endpoint that represents the video parts.
	@return: The total number of parts for the video.
	"""
	import requests
	
	try:
		# Initialize the search range parameters
		current_part = next_part = 2048
		
		# Perform a binary search for the correct part number
		while next_part != 1:
			status = requests.get(f'{base_url}{int(current_part)}{end_url}').status_code
			next_part = int(next_part / 2)
			
			# Adjust the current part based on the HTTP status code
			current_part = int(current_part - next_part) if status in {403, 404} and next_part != 1 \
				else int(current_part + next_part)
		
		return current_part
	except Exception as e:
		# Print an error message in case of an exception
		print(f"An error occurred: {e}")
		return 4096  # Return a maximum value


def get_chrome_browser(headless=True, mute=True, download_path=None, proxy=False, ignore_errors=True,  driver_logging=False, extention=False):
	"""
	Create a automated chrome browser
	Proxy Server stop -> server.stop()
	Webdriver stop -> driver.quit()
	@param headless: If True, the browser will be invisible
	@param mute: If True, the entire browser is muted
	@param download_path: The destination where Chrome will download files
	@param proxy: If True, add a proxy to the browser
	@param ignore_errors: If True, ignore SSL errors and certificate errors (usefull for Twitch download)
	@param driver_logging: If False, suppress unnecessary logging information in the console
	@param extention: TODO make it accept extention
	@return: Without Proxy (Webdriver) | With Proxy (Webdriver, Client, Server) | If error (None)
	"""
	
	options = webdriver.ChromeOptions()
	options.add_experimental_option('detach', True)
	service = Service(ChromeDriverManager().install())
	
	if headless: options.add_argument('--headless=new')
	if mute: options.add_argument('--mute-audio')
	if download_path is not None: options.add_experimental_option('prefs',
																  {'download.default_directory': str(download_path)})
	if not driver_logging: options.add_experimental_option("excludeSwitches", ["enable-logging"])
	if ignore_errors:
		options.add_argument('--ignore-ssl-errors=yes')
		options.add_argument('--ignore-certificate-errors')
	
	if proxy:
		try:
			proxy_manager = ProxyManager()
			server = proxy_manager.start_server()  # Need to be server.stop()
			client = proxy_manager.start_client()
			if client.proxy is None:
				print("ERROR: Proxy client is None")
				return None
			options.add_argument(f'--proxy-server={client.proxy}')
			return webdriver.Chrome(options=options, service=service), client, server
		except Exception as e:
			print("ERROR: Exception occurred when opening proxy\n", e)
			return None
	return webdriver.Chrome(options=options, service=service)


def wait_for_requests(client, find_in: str = '.ts', timeout: int = 5):
	"""
	Wait for getting requests with the extention wanted
	@param client: The proxy client
	@param find_in: The str to find in the requests to confirm it
	@param timeout: The time to wait until getting the request
	@return: A list of requests wanted
	"""
	start = time.monotonic()
	while time.monotonic() - start < timeout:
		requests_all: list[str] = [str(req.url) for req in HarParser(client.har).pages[0].get_requests]
		requests_wanted: list[str] = [request for request in requests_all if request.find(find_in) != -1]
		if len(requests_wanted) > 0: return requests_wanted


def wait_clickable_element(driver: webdriver, element_locator: str, by: str = By.XPATH, click: bool = True,
						   submit: bool = False, timeout: int = 5) -> bool:
	"""
	DONT WORK EVERY TIME
	Wait until the element exists and click/submit it
	@param driver: Webdriver
	@param by: By.XPATH, ID,
	@param element_locator: The value to find the element
	@param click: Click the element
	@param submit: Submit the element
	@param timeout: The max time to wait
	@return: return the success of the function, True Successed, False Error
	"""
	try:
		element = WebDriverWait(driver, timeout).until(ec.element_to_be_clickable((by, element_locator)))
		if click: element.click()
		if submit: element.submit()
		return True
	except Exception as e:
		print(f"Exception: {e}")
		return False


def check_element(driver: webdriver, by: str = By.XPATH, value: str = '', click: bool = False, submit: bool = False,
				  timeout: int = 5) -> bool | None:
	"""
	Find a element and click/submit if the element has been found
	@param driver: Webdriver
	@param by: Webdriver By
	@param value: Locator
	@param click: Click if find the element
	@param submit: Submit if find the element
	@param timeout: The max time to wait the element
	@return: True=Successed | False=Failed
	"""
	if value == '': print('No value in check_element()'); return False
	
	start = time.monotonic()
	while time.monotonic() - start <= timeout:
		try:
			element = driver.find_element(by, value)
			if click: element.click()
			if submit: element.submit()
			return True
		except:
			time.sleep(0.5)
	return False
