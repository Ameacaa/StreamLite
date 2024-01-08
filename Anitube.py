from Shared import get_random_str, get_chrome_browser, By, download_urlfile, check_element, chronofunc
from dataclasses import dataclass, field
from bs4 import BeautifulSoup
from slugify import slugify
from pathlib import Path
import requests
import json
import re
import os

AUTOCHECK_PATH = Path(os.getcwd(), 'anitube_autocheck.txt')


@dataclass
class Episode:
	fullname: str = field()  # The nam in the anitube page (For metadata file)
	filename: str = field()  # The filename with extention
	episode_url: str = field()  # The anitube download url of the episode


@dataclass
class Anime:
	url: str = field()  # The url of the download page in anitube
	title: str = field(init=False)  # Anime title and subfolder destination
	season: str = field(init=False)  # For the episode name
	status: str = field(init=False)  # Use for auto update anime
	episodes: list[Episode] = field(init=False)
	
	@staticmethod
	def __get_title(soup) -> str:
		title_soup = soup.find('div', class_='anime_container_titulo').text
		return get_random_str(8, 'ud') if title_soup is None \
			else slugify(' '.join(str(title_soup).split()[1:]), lowercase=False, word_boundary=True,
						 separator=' ').title()
	
	@staticmethod
	def __get_season(soup) -> str:
		infos_soup = soup.find('div', "anime_infos").find_all('div', 'anime_info')
		alt_title = str(infos_soup[0].text).split()
		for i, value in enumerate(alt_title):
			if value == 'Season':
				if alt_title[i + 1].isdigit():
					return alt_title[i + 1]
		return '1'
	
	@staticmethod
	def __get_status(soup) -> str:
		infos_soup = soup.find('div', "anime_infos").find_all('div', 'anime_info')
		
		status = str(infos_soup[6].text).strip()
		if status is None or not status: return ''
		if status == 'Status: Em Progresso':
			return 'Airing'
		elif status == 'Status: Completo':
			return 'Complete'
		else:
			return 'NEW'
	
	@staticmethod
	def __get_episode(soup) -> (str, str, str):
		name_soup = str(soup[0].text).split()[1:]
		name = ' '.join(name_soup)
		
		is_final_ep = False
		number = get_random_str(4, 'd')
		for i in range(1, 4):  # It [-1:] or [-3:] but can be different sometimes
			number_soup = str(name_soup[-i:][0])
			if number_soup == 'FINAL': is_final_ep = True  # Check if final season episode
			if number_soup.isdigit(): number = number_soup; break
		if is_final_ep: number += 'F'
		
		for i in range(3, 0, -1):  # 3, 2, 1
			try:
				url = soup[i].a['href']
				if url is not None: return name, number, url
			except:
				pass
		return name, number, ''
	
	def __get_episodes(self, soup) -> list[Episode]:
		episodes_table_soup = soup.find('table', 'downloadpag_episodios').find_all('tr')
		episodes_table_soup = episodes_table_soup[1:]  # [0] is for table's header
		
		episodes = []
		for episode_row_soup in episodes_table_soup:
			ep_name, ep_number, ep_url = self.__get_episode(episode_row_soup.find_all('td'))
			filename = f's{str(self.season).zfill(2)}e{str(ep_number).zfill(2)}.mp4'  # s01e08 or s01e12F
			episodes.append(Episode(fullname=ep_name, filename=filename, episode_url=ep_url))
		return episodes
	
	def __post_init__(self):
		soup = BeautifulSoup(requests.get(self.url).text, 'lxml')
		self.title = self.__get_title(soup)
		self.season = self.__get_season(soup)
		self.status = self.__get_status(soup)
		self.episodes = self.__get_episodes(soup)
	
	def __str__(self):
		ep_str = ''
		for ep in self.episodes: ep_str += f'\n\tFullName: {ep.fullname:40} | Filename: {ep.filename:16} | Url: {ep.episode_url}'
		# Show Episodes too => return f"Anime( URL='{self.url}' | Title='{self.title}' | Season='{self.season}' | Status='{self.status}' )\nEpisodes:{ep_str}"
		return f"Anime( URL='{self.url}' | Title='{self.title}' | Season='{self.season}' | Status='{self.status}' )"
	
	def set_self(self, anime_dict: dict):
		self.url = anime_dict['url']
		self.title = anime_dict['title']
		self.season = anime_dict['season']
		self.status = anime_dict['status']
		self.episodes = anime_dict['episodes']
	
	def to_dict(self):
		return {
			'url': self.url,
			'title': self.title,
			'season': self.season,
			'status': self.status,
			'episodes': [episode.__dict__ for episode in self.episodes]
		}


def __get_download_page_url(user_url: str) -> list[str]:
	re_download = r'https?:\/\/(www\.)?(anitube.vip\/)?(download)'
	re_anime = r'https?:\/\/(www\.)?(anitube.vip\/)?[-a-zA-Z0-9]{1,256}(\/)[-a-zA-Z0-9]{1,256}'
	re_search = r'https?:\/\/(www\.)?(anitube.vip\/)?(busca.php)'
	
	# Download page
	if re.search(re_download, user_url) is not None:
		return [user_url]
	else:
		soup = BeautifulSoup(requests.get(user_url).text, 'lxml')
		
		if re.search(re_anime, user_url) is not None:  # Anime Page
			a_tag = soup.find('a', 'anime_downloadBTN')
			return [str(a_tag['href']).strip()] if a_tag is not None else []
		
		elif re.search(re_search, user_url) is not None:  # Search Page
			for search_anime in soup.find_all('div', 'ani_loop_item_infos'):
				
				if str(search_anime.a.text).find('Dublado') != -1: continue  # If dublado continue
				
				downloadpage_urls = [str(a_tag['href']).strip() for a_tag in search_anime.find_all('a') if
									 re.search(re_download, a_tag['href']) is not None]
				return [download_url for download_url in downloadpage_urls if download_url is not None]
	return []


def get_anitube_urls(user_urls: list[str]) -> list[str]:
	anitube_urls = []
	for url in user_urls:
		new_annitube_urls = __get_download_page_url(url)
		
		if len(new_annitube_urls) == 0:
			print(f'The url insered had no anitube download page found in it: {url}')
			continue
		
		anitube_urls += new_annitube_urls
	return anitube_urls


@chronofunc
def scrape(anitube_urls: list[str]) -> list[Anime]:
	animes = []
	for url in anitube_urls:
		animes.append(Anime(url))
	return animes


def __get_download_url(driver, episode_download_url: str) -> str:
	driver.get(episode_download_url)
	
	if not check_element(driver, value='/html/body/div/div[2]/div[1]/div[3]/div/form/button', submit=True):
		print("ERROR 1: Can't get the download url to proceed, skipping this episode")
		return ''
	
	download_url = str(
		driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/div[3]/a').get_property('href'))
	
	return download_url


def download_anime(driver, anime: Anime, _destination: str, skip_existing: bool):
	for episode in anime.episodes:
		print(f'\t{episode}')
		
		destination = Path(_destination, anime.title, episode.filename)
		
		if destination.is_file() and skip_existing:
			print('Skipping this episode, it already exist')
			continue
		
		download_url = __get_download_url(driver, episode.episode_url)
		if download_url == '':
			print("ERROR 2: Can't get the download url to proceed, skipping this episode")
			continue
		
		download_urlfile(download_url, str(destination))


@chronofunc
def download(animes: list[Anime], destination: str, skip_existing: bool):
	driver = get_chrome_browser()
	for anime in animes:
		print(anime)
		Path(destination, anime.title).mkdir(exist_ok=True, parents=True)
		download_anime(driver, anime, destination, skip_existing)
	driver.quit()


# def save_to_autocheck_anime(animes: list[Anime]):
# 	try:
# 		# Read existing data from the JSON file if it exists
# 		with open(AUTOCHECK_PATH, 'r') as json_file:
# 			file_animes = json.load(json_file)
# 	except FileNotFoundError:
# 		# If the file doesn't exist, initialize with an empty list
# 		file_animes = []
#
# 	# Convert DataClass instances to dictionaries and append to existing data
# 	new_animes = [anime.__dict__ for anime in animes]
# 	file_animes.extend(new_animes)
#
# 	# Write the updated data back to the JSON file
# 	with open(AUTOCHECK_PATH, 'w') as json_file:
# 		json.dump(file_animes, json_file, indent=2)
#
#
# def __open_file_urls() -> list[str]:
# 	with open(AUTOCHECK_PATH, 'rt', encoding='utf-8') as file:  # Create new file if does not exist
# 		urls = file.read().split()
# 	return urls

#
# def __autodownload(animes: list[Anime]):
# 	print()


# for anime in animes:
# 	destination = Path(_destination, anime.title, episode.filename)

#
# def autodownload_anime():
# 	urls = __open_file_urls()


def main(user_urls: list[str], destination: str = r'E:\__new__\Medias\Animes', skip_existing: bool = True, autocheck_anime: bool = True):
	urls = get_anitube_urls(user_urls)
	
	animes = scrape(urls)
	
	download(animes, destination, skip_existing)
	
	# if autocheck_anime: save_to_autocheck_anime(animes)


if __name__ == '__main__':
	# print("It does not work like this, use 'main.py -help' to know how to use")
	main(['https://www.anitube.vip/anime/ao-no-exorcist-shimane-illuminati-hen'], r'E:\__new__\Medias\Animes\NEWTEMP')
