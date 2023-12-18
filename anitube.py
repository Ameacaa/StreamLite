from shared.chromium import By, getChromeBrowser, getFirefoxBrowser
from shared.download import DownloadFile
from shared.funcs import error
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import requests, re, time

from time import monotonic

import json


class Anitube:
	def __init__(self, user_urls: list):
		if type(user_urls) is str: user_urls = [user_urls]
		self.user_urls: list[str] = user_urls
		self.download_urls: list[str] = self.__getValidsUrls__(user_urls)
		self.animes: list[Anime] = []
		self.last_modification: datetime | None = None
		self.json_path: str = 'json/anitube.json'

	def __str__(self):
		user_urls = "\n\t- ".join(self.user_urls)
		anitube_urls = "\n\t- ".join(self.download_urls)
		animes = ''
		for anime in self.animes:
			episodes = ''
			for ep in anime.episodes:
				episodes += f'\n\t\t{ep.name}\n\t\t{ep.download_url}\n\t\t{ep.download_date}'
			animes += f'\n{anime.name}\n\tUrl: {anime.download_page_url}\nEpisodes:{episodes}'
		
		return (f'Last Modification Date: {self.last_modification}\n\nUrls from user:{user_urls}\n'
				f'\nUrls in Anitube:{anitube_urls}\n\nAnimes: {animes}')
	
	def __dict__(self):
		return dict(
			user_urls=self.user_urls,
			anitube_urls=self.download_urls,
			last_modification=self.last_modification,
			animes=[
				{'download_page_url': anime.download_page_url,
				 'name': anime.name,
				 'scrape_date': anime.scrape_date,
				 'episodes': [
					 {'name': episode.name,
					  'number': episode.number,
					  'download_url': episode.download_url}
					 for episode in anime.episodes]}
				for anime in self.animes])
	
	@staticmethod
	def init(self) -> None:
		# TODO init from file
		# self.user_urls: list = user_urls
		# self.anitube_urls: list = anitube_urls
		# self.animes: list = animes
		# self.last_modification: datetime = last_modification
		print()
	
	@staticmethod
	def __getValidsUrls__(user_urls: list) -> list[str]:
		valids_urls = []
		pages = {'anime': r'https?:\/\/(www\.)?(anitube.vip\/)?[-a-zA-Z0-9]{1,256}(\/)[-a-zA-Z0-9]{1,256}',
				 'search': r'https?:\/\/(www\.)?(anitube.vip\/)?(busca.php)',
				 'download': r'https?:\/\/(www\.)?(anitube.vip\/)?(download)'}
		
		for url in user_urls:
			if re.search(pages['download'], url) is not None:
				valids_urls.append(url)
				continue
			
			soup = BeautifulSoup(requests.get(url).text, 'lxml')
			if re.search(pages['anime'], url) is not None:
				a_tag = soup.find('a', 'anime_downloadBTN')
				if a_tag is None: error(213); continue
				valids_urls.append(str(a_tag['href']).strip())
			
			elif re.search(pages['search'], url) is not None:
				search = soup.find_all('div', 'ani_loop_item_infos')
				if len(search) == 0: error(213); continue
				for anime in search:
					if str(anime.a.text).find('Dublado') != -1: continue
					a_tags = anime.find_all('a')
					if len(a_tags) == 0: error(213); continue
					for a_tag in a_tags:
						if re.search(pages['download'], a_tag['href']) is not None:
							valids_urls.append(str(a_tag['href']).strip())
			
			else:
				error(213)
		return valids_urls
	
	def check(self) -> bool:
		if len(self.download_urls) == 0 or len(self.user_urls) == 0 or len(self.animes) == 0: return False
		return True
	
	def scrape(self, show=True):
		self.last_modification = datetime.now()
		start = monotonic()
		self.animes = [anime for url in self.download_urls if (anime := Anime(url)).name is not None]
		if show: print(f"Time taken for Scrape {len(self.animes)} animes: {(monotonic() - start):.2f}")
	
	def save(self):
		# TODO
		# with open(path, "w") as file:
		# 	json.dump(to_save, file)
		print('TODO')
	
	def open(self):
		# TODO
		print()
	
	def download(self):
		# TODO
		driver = getChromeBrowser(simple=True)
		
		for anime in self.animes:
			print(anime.name)
			for episode in anime.episodes:
				driver.get(episode.download_url)
				time.sleep(3)
				try:
					blocker_button = driver.find_element(By.CLASS_NAME, 'download')
					driver.implicitly_wait(1)
					blocker_button.submit()
					driver.implicitly_wait(1)
					download_url = driver.find_element(By.CLASS_NAME, 'download').get_property('href')
					print(download_url)
				except:
					print(episode.name)
					continue


class Anime:
	def __init__(self, url: str):
		self.download_page_url: str = url
		self.name: str = ''
		self.episodes: list[Episode] = []
		self.state: str = ''
		self.scrape_date: datetime = datetime.now()
		
		# Scrape the download page anime
		soup = BeautifulSoup(requests.get(self.download_page_url).text, 'lxml')
		if soup is None: error(213); return
		
		# Get the name of the anime
		name_soup = soup.find('div', class_='anime_container_titulo').text
		if name_soup is None: error(213); return
		name = str(name_soup).split()[1:]
		self.name = ' '.join(name)
		
		# Get the status of the anime
		infos_soup = soup.find('div', "anime_infos").find_all('div', 'anime_info')
		if len(infos_soup) == 0: error(213); return
		state = str(infos_soup[6].text).strip()
		self.state = 'Airing' if state == 'Status: Em Progresso' else 'Complete' \
			if state == 'Status: Completo' else 'GO CHECK IN THE WEBSITE'
		
		# Get the episodes infos
		episodes_table_soup = soup.find('table', 'downloadpag_episodios').find_all('tr')
		if len(episodes_table_soup) == 0: error(213); return
		else: episodes_table_soup = episodes_table_soup[1:]
		self.episodes = [Episode(episode_row_soup) for episode_row_soup in episodes_table_soup]
	
	def __str__(self):
		episodes = ''
		for ep in self.episodes: episodes += f'\n\t\t{ep.name}\n\t\t{ep.download_url}\n\t\t{ep.download_date}'
		return f'\n{self.name}\n\tUrl: {self.download_page_url}\nEpisodes:{episodes}'
	
	def __dict__(self):
		return dict(
			download_page_url=self.download_page_url,
			name=self.name,
			scrape_date=self.scrape_date,
			episodes=[
				{'name': episode.name,
				 'number': episode.number,
				 'download_url': episode.download_url}
				for episode in self.episodes])


class Episode:
	def __init__(self, episode_row_soup):
		self.name: str = ''
		self.number: int = -1
		self.download_url: str = ''
		self.download_date: datetime | None = None
		
		episode = episode_row_soup.find_all('td')
		if len(episode) == 0: error(213); return
		
		name = str(episode[0].text).split()[1:]
		self.name = ' '.join(name)

		number = str(name[-1:][0])
		self.number = int(number) if number.isdigit() else -1

		try: self.download_url = episode[3].a['href']; return
		except: pass
		try: self.download_url = episode[2].a['href']; return
		except: pass
		try: self.download_url = episode[1].a['href']; return
		except: pass
	
	def __str__(self):
		return f'{self.name:36} [DL: {self.download_date}] - {self.download_url}'


anitube = Anitube(['https://www.anitube.vip/anime/goblin-slayer-ii'])
anitube.scrape()
print(anitube.__str__())
# anitube.download()
