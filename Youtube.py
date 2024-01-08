import pytube.exceptions

from Shared import get_random_str, download_urlfile
from dataclasses import dataclass, field
from pytube import YouTube, Playlist, Stream
from mutagen.mp4 import MP4
from slugify import slugify
from colorama import Fore
from pathlib import Path
import logging
import shutil
import os
import re

LOGFILE = r'B:\Projects\_new_\StreamLite\logs\yt_debug.log'
LOGGINGLEVEL = logging.DEBUG

AUTHORS = {
	"ALTER": ("", ["Horror", "Movie"]),
	"12 Parsecs": ("", ["Entertainment", "Learn", "Astronomy"]),
	"0612 TV w/ NERDfirst": ("", ["Learn", "Programming"]),
	"Abrège": ("", ["DIY"]),
	"ACIDRAMA": ("", ["Stories", "Mystery", "Favorite"]),
	"Ad Immensum": ("", ["Learn", "Stories", "Mythology"]),
	"Adam Bros": ("", ["Learn"]),
	"Alex Kister": ("", ["Favorite", "Movie"]),
	"ALT 236": ("", ["Favorite", "Stories"]),
	"AlterHis": ("", ["Stories"]),
	"Amenoz Cotcot": ("", ["Entertainment"]),
	"Ami des lobbies": ("", ["Learn", "World", "Favorite"]),
	"Aminematue": ("", ["Entertainment"]),
	"Andy Math": ("", ["Learn", "Maths"]),
	"ANIMAUX : MODE D'EMPLOI ": ("Yvan Animaux", ["Animals"]),
	"anna dreamy ASMR": ("Anna Dreamy", ["ASMR"]),
	"Anthox Colaboy": ("Anthox", ["Entertainment", "Favorite"]),
	"Anthox Colaboy VOD twitch (Officiel) ": ("Anthox VOD", ["Favorite", "VOD"]),
	"Artu": ("", ["Stories", "Movie"]),
	"ATOM": ("", ["Learn", "Design"]),
	"Axolot": ("", ["Learn"]),
	"BABOR LELEFAN": ("", ["Entertainment"]),
	"BADNEWS": ("", ["Entertainment"]),
	"Balkan Gains": ("", ["Motivation"]),
	"Basti Ui": ("", ["Learn", "Design"]),
	"Benjamin Code": ("", ["Learn", "Programming"]),
	"Benjamin Workshop": ("", ["Entertainment", "Learn", "Mechanics"]),
	"Best Of du Grenier": ("", ["Entertainment", "VOD"]),
	"BPS.space": ("", ["Learn", "DIY", "Astronomy"]),
	"Branch Education": ("", ["Learn"]),
	"Brick Experiment Channel": ("", ["Learn", "Entertainment"]),
	"Brick Technology": ("", ["Entertainment", "Learn"]),
	"Bricolage c'est cool": ("", ["Learn", "DIY"]),
	"Bruno Le Salé": ("", ["World"]),
	"CacaboxTV": ("CCB", ["Favorite", "VOD"]),
	"Charles Villa": ("", ["Reportage", "World", "Favorite"]),
	"Chat Sceptique": ("", ["Favorite", "Learn"]),
	"Chronik Fiction": ("", ["Favorite", "Movie", "Stories"]),
	"clararunaway": ("", ["Movie", "Stories"]),
	"Cleo Abram": ("", ["Learn"]),
	"Clément Freze": ("", ["Favorite", "Learn", "Entertainment"]),
	"Cnawak": ("", ["Stories"]),
	"cocadmin": ("", ["Favorite", "Programming"]),
	"Code BH": ("", ["Favorite", "Gamedev"]),
	"Code Pointers": ("", ["Programming"]),
	"Codeur de Nuit": ("", ["Programming"]),
	"colinfurze": ("", ["DIY"]),
	"Compilations Virgule Animale": ("", ["Animals"]),
	"Confessions d'Histoire": ("", ["History"]),
	"Consul Pazen ": ("", ["World"]),
	"Consulo Pazeno": ("", ["World"]),
	"CULTUR3D": ("", ["Learn", "Favorite"]),
	"CurieuxLive": ("", ["Learn", "Favorite"]),
	"Cédrik JURASSIK": ("", ["Learn", "Favorite", "Entertainment"]),
	"Daenys Horror Story": ("", ["Stories", "Horror"]),
	"Dans Ton Corps": ("", ["Learn"]),
	"Decode - Explore Media": ("", ["Stories"]),
	"Defakator Vite Fait": ("", ["Favorite", "Learn"]),
	"Defend Intelligence": ("", ["Favorite", "Programming", "Learn"]),
	"DEO TOONS": ("", ["Favorite", "Entertainment"]),
	"Diable Positif": ("", ["Favorite"]),
	"Didi": ("", ["Stories"]),
	"Dimby Rakotomalala": ("", ["Excel"]),
	"diorama111": ("", ["Favorite"]),
	"DirtyBiology": ("", ["Favorite", "Learn"]),
	"DIY Perks": ("", ["Favorite", "Learn"]),
	"Dr Nozman": ("", ["Learn"]),
	"Eddie Woo": ("", ["Maths"]),
	"Edward": ("", ["Favorite", "Stories"]),
	"EGO": ("", ["Favorite", "Stories"]),
	"ElectroBOOM": ("", ["Learn"]),
	"Electronoobs": ("", ["DIY"]),
	"Elie Lou": ("", ["Stories"]),
	"Envato Tuts+": ("", ["Programming"]),
	"Epic Teaching of History": ("", ["Favorite", "Learn", "Entertainment"]),
	"Et tout le monde s'en fout": ("", ["Learn"]),
	"Explore Media": ("", ["Learn"]),
	"FabienOlicard": ("", ["Learn", "Psychology"]),
	"Fabio Musanni - Programming Channel": ("", ["Programming"]),
	"Feldup": ("", ["Favorite", "Stories"]),
	"Fouloscopie": ("", ["Favorite", "Psychology"]),
	"Fourmi des plaines": ("", ["Favorite"]),
	"freeCodeCamp.org": ("", ["Favorite", "Programming"]),
	"FRENCH DREAM TV": ("", ["Favorite", "Cringe"]),
	"FRENCH DREAM TV RE": ("", ["Favorite", "Cringe"]),
	"Frère Castor": ("", ["Favorite", "Stories"]),
	"G Milgram": ("", ["Favorite", "World"]),
	"G un kilo": ("", ["Favorite", "World"]),
	"Gamedev Teacher": ("", ["Gamedev"]),
	"Gaspard G": ("", ["Favorite", "Reportage"]),
	"Gotabor": ("", ["Favorite", "Learn"]),
	"Grafikart.fr": ("", ["Programming"]),
	"Guillaume Cassar": ("", ["Favorite", "Movie", "Stories"]),
	"Hackintux": ("", ["Cybersecurity", "Learn"]),
	"Harley Guio Guitar": ("", ["Guitar"]),
	"Hasheur": ("", ["Favorite", "Crypto"]),
	"Hedacademy": ("", ["Maths"]),
	"Heliox": ("", ["DIY"]),
	"Henri Hihacks": ("", ["DIY"]),
	"HighGame_Def": ("", ["Learn", "Gamedev"]),
	"Hinfiney": ("", ["Mythology", "History"]),
	"Horizon_Universe": ("", ["Stories"]),
	"Horreur 404": ("", ["Stories", "Movie", "Horror"]),
	"Hugo Délire": ("", ["Favorite"]),
	"Hugo Délire - Les VOD": ("", ["Favorite", "VOD"]),
	"Hugo Lisoir": ("", ["Favorite", "Astronomy"]),
	"Hugo Roth Raza": ("", ["Entertainment"]),
	"Hygiène Mentale": ("", ["Favorite", "Learn", "Psychology"]),
	"I did a thing": ("", ["DIY"]),
	"Iconoclaste": ("", ["Stories"]),
	"Illustre Connu": ("", ["Movies", "Story"]),
	"INA Société": ("", ["History"]),
	"Incroyables Expériences": ("", ["Favorite", "DIY"]),
	"Integza": ("", ["Favorite", "Learn"]),
	"Jaihno": ("", ["Favorite", "Stories"]),
	"JBV Creative": ("", ["Favorite", "DIY"]),
	"Joey Carlino": ("", ["Blender"]),
	"Josh Gambrell": ("", ["Blender"]),
	"Joueur Du Grenier": ("", ["Favorite", "Entertainment"]),
	"Julien Bobroff": ("", ["Favorite", "Learn"]),
	"Kaizen": ("", ["Blender"]),
	"Kane Pixels": ("", ["Favorite", "Movie"]),
	"Kayomil": ("", ["Gamedev"]),
	"Kombo": ("", ["Favorite", "Stories"]),
	"KT TechHD": ("", ["Favorite", "Learn"]),
	"L'Effet Papillon": ("", ["World"]),
	"La Psy Qui Parle": ("", ["Learn", "Psychology"]),
	"La statistique expliquée à mon chat": ("", ["Favorite", "Maths"]),
	"LaGrandeRevue": ("", ["Favorite", "Stories"]),
	"LaPatience": ("", ["Favorite", "World"]),
	"LAPIN DU FUTUR": ("", ["Favorite", "World"]),
	"Le Clap": ("", ["Movie", "Stories"]),
	"Le Designer Auto": ("", ["Favorite", "Design", "Learn"]),
	"LE GRAND JD": ("", ["Favorite", "Horror", "Stories"]),
	"Le Muséum des ‽ourquois": ("", ["Learn"]),
	"Le Point Genius": ("", ["Favorite", "Learn"]),
	"Le Radis Irradié": ("", ["Favorite", "World", "Entertainment"]),
	"Le Raptor": ("", ["World"]),
	"LE ROI DES RATS": ("", ["Favorite", "World"]),
	"Le Règlement": ("", ["Music", "Stories"]),
	"Leffy62z": ("", ["Entertainment"]),
	"Les Freres Poulain": ("", ["Favorite", "DIY"]),
	"Les génies des sciences": ("", ["Favorite", "Learn"]),
	"Les Kassos": ("", ["Favorite", "Entertainment"]),
	"Les Revues du Monde": ("", ["Favorite", "Learn", "History"]),
	"Lesics": ("", ["Learn"]),
	"Liu Zuo Lin": ("", ["Programming"]),
	"LiveOverflow": ("", ["Cybersecurity"]),
	"Livre Noir": ("", ["World"]),
	"LORIS GIULIANO": ("", ["Favorite", "Entertainment"]),
	"LOUP GAROU": ("", ["Entertainment"]),
	"Léa Ricci": ("", ["Learn"]),
	"Léo - TechMaker": ("", ["Learn"]),
	"Léo-Paul ": ("", ["Favorite", "Entertainment"]),
	"Maskey": ("", ["Favorite", "Entertainment", "Music"]),
	"MasterSnakou": ("", ["Favorite"]),
	"MATH": ("", ["Movie", "Entertainment"]),
	"MATHIEU": ("", ["Gamedev"]),
	"Mathieu Tutos Unreal Engine 5": ("", ["Gamedev"]),
	"Maudin Malin": ("", ["Favorite", "World", "Psychology"]),
	"MaxEst ToujoursLa": ("", ["World"]),
	"MaxEstLa": ("", ["Favorite", "World"]),
	"Megan Morgan": ("", ["Stories", "World"]),
	"Merci la physique": ("", ["Learn"]),
	"Micode": ("", ["Favorite", "Programming"]),
	"Millomaker": ("", ["Favorite", "DIY"]),
	"Ming Jin": ("", ["Learn"]),
	"Mister V": ("", ["Favorite", "Entertainment"]),
	"MisterFlech": ("", [""]),
	"Monsieur Bidouille": ("", ["Favorite", "Learn"]),
	"Monsieur Phi": ("", ["Favorite", "Psychology"]),
	"Montreux Comedy": ("", ["Favorite", "Entertainment"]),
	"MyFuckinMess": ("", ["Favorite", "Entertainment"]),
	"Mythos Realis": ("", ["Mythology", "Stories"]),
	"Naj B Fit": ("", ["Favorite", "Psychology"]),
	"NetworkChuck": ("", ["Favorite", "Programming"]),
	"NeuralNine": ("", ["Favorite", "Programming"]),
	"Nico71's Lego Technic Creations": ("", ["Learn"]),
	"Nota Bene": ("", ["History"]),
	"Notseriou's": ("", ["Favorite", "Movie", "Entertainment"]),
	"Officiel DEFAKATOR": ("Defakator", ["Favorite", "Learn"]),
	"Olivier - Coach Webmarketing": ("", ["Learn"]),
	"Palmashow": ("", ["Favorite", "Entertainment"]),
	"PARADOX": ("", ["Horror", "Stories"]),
	"Parfaitement Web": ("", ["Favorite", "Programming"]),
	"Pas Végan": ("", ["Favorite", "Learn"]),
	"Plot Time": ("", ["Favorite", "Movie", "Stories"]),
	"Polokus": ("", ["Favorite", "Music", "Stories"]),
	"PortugueseFacts par Tiago": ("", ["Learn", "History"]),
	"POTATOZ": ("", ["Favorite", "Entertainment"]),
	"POTATOZ - LIVE & BEST-OF": ("", ["Favorite", "VOD", "Entertainment"]),
	"POTATOZ Clips": ("", ["Favorite", "Entertainment"]),
	"Primer": ("", ["Favorite", "Learn", "Programming"]),
	"Programiz": ("", ["Programming"]),
	"Programming with Mosh": ("", ["Programming"]),
	"ProjectAir": ("", ["DIY"]),
	"Psyhodelik": ("", ["World"]),
	"pwnisher": ("", ["Design"]),
	"RaAaK": ("", ["Favorite"]),
	"RIAN": ("", ["Learn"]),
	"Romy Victory": ("", ["TrueCrime"]),
	"Rui Santos": ("", ["DIY"]),
	"Sabine": ("", ["Learn", "World"]),
	"salut c'est cringe": ("", ["Favorite", "Cringe"]),
	"Sandoz": ("", ["Cybersecurity", "Entertainment"]),
	"Savage Games": ("", ["Gamedev"]),
	"Scarabête": ("", ["Animals"]),
	"Science de comptoir": ("", ["Learn"]),
	"Science4All": ("", ["Learn"]),
	"Scilabus": ("", ["Favorite", "Learn"]),
	"SCP Foundation": ("", ["Horror"]),
	"Scrotumdepoulpe": ("", []),
	"SEB": ("", ["Favorite", "Stories"]),
	"Sebastian Lague": ("", ["Favorite", "Programming"]),
	"SeriActu": ("", ["World"]),
	"SEROTHS": ("", ["Favorite", "Horror"]),
	"Servet Gulnaroglu": ("", ["Programming"]),
	"Sheshounet": ("", ["Favorite", "Entertainment"]),
	"Simon Puech": ("", ["Favorite", "Stories", "World"]),
	"Sir_Thomas_ Gaming": ("", ["Entertainment"]),
	"Sky Guitar": ("", ["Guitar"]),
	"Slexno": ("", ["Favorite", "Movie", "Learn"]),
	"SmarterEveryDay": ("", ["Favorite", "Learn"]),
	"SQUEEZIE": ("", ["Favorite", "Stories"]),
	"Steve Mould": ("", ["Favorite", "Learn", "DIY"]),
	"Stream Theory": ("", ["Favorite", "Learn"]),
	"Stupid Economics": ("", ["Favorite", "Learn"]),
	"Stéphane Edouard": ("", ["World"]),
	"Superconeri": ("", ["Favorite", "Entertainment"]),
	"Sylartichot": ("", ["Horror", "Mythology", "Stories"]),
	"Sylvdeux": ("", ["Stories", "Programming"]),
	"Sylvqin": ("", ["Favorite", "Stories", "Programming"]),
	"tableuh": ("", ["Stories"]),
	"TAOQAN": ("", ["Favorite", "Learn"]),
	"TechWorld with Nana": ("", ["Programming"]),
	"Terrapodia": ("", ["Favorite", "Animals", "Learn"]),
	"The Action Lab": ("", ["Learn"]),
	"the roadmap": ("", ["Programming"]),
	"The Sciencoder": ("", ["Favorite", "Entertainment"]),
	"TheoBabac": ("", ["Entertainment"]),
	"TheoBabac2": ("", ["Entertainment"]),
	"Thomi et Skadi": ("", ["Learn", "Animals", "Dogs"]),
	"Thoz": ("", ["Entertainment"]),
	"Théorus": ("", ["Favorite", "Entertainment"]),
	"tn DNA": ("", ["Favorite", "Psychology"]),
	"TOM ASMR": ("Tom", ["ASMR"]),
	"Tom Stanton": ("", ["Favorite", "DIY"]),
	"TOUNY": ("", ["Stories"]),
	"Tout Simplement – Kurzgesagt": ("", ["Learn"]),
	"Underscore_": ("", ["Favorite", "Stories", "Programming"]),
	"UNF Games": ("", ["Gamedev"]),
	"Useless Game Dev": ("", ["Gamedev"]),
	"Valek": ("", ["World"]),
	"Veritasium": ("", ["Favorite", "Learn"]),
	"Victor Ferry": ("", ["Favorite", "Psychology"]),
	"Vilebrequin": ("", ["Favorite"]),
	"Virgule Animale": ("", ["Favorite", "Animals"]),
	"VLRN | Valerian": ("", ["Gamedev"]),
	"Vous Avez Le Droit": ("", ["Favorite", "Learn"]),
	"Waked XY": ("", ["Favorite", "Cybersecurity"]),
	"Wankil Studio - Laink et Terracid": ("", ["Favorite", "Entertainment"]),
	"Wankil Studio - Les VOD": ("", ["Favorite", "VOD"]),
	"White Box Dev": ("", ["Favorite", "Programming"]),
	"Wildeye Demon": ("", ["Favorite", "Reportage"]),
	"Yann Bouvier | YannToutCourt": ("", ["History"]),
	"Yann Piette": ("", ["Psychology"]),
	"Zyger": ("", ["Gamedev"])
	
}
errors = list()


@dataclass
class Video:
	youtube: YouTube = field()
	destination: str = field()
	url: str = field()
	can_download_codes: list[int] = field(init=False)
	filename: str = field(init=False, default='')  # Error Code 10
	thumbnail_url: str = field(init=False, default='')  # Error Code 11
	audio_stream: Stream | None = field(init=False, default=None)  # Error Code 1 - Can't download
	video_stream: Stream | None = field(init=False, default=None)  # Error Code 2 - Can't download
	author: str = field(init=False, default='')  # Error Code 12
	duration: str = field(init=False, default='')
	tags: list[str] = field(init=False, default=list)  # Error Code 13
	filesize_mb: float = field(init=False, default=-1)  # Error Code 14
	
	def __get_filename(self) -> str:
		return slugify(self.youtube.title, max_length=128, word_boundary=True, separator=" ", lowercase=False,
					   replacements=[['Asmr', ''], ['\'', '']]).title() + '.mp4'
	
	def __get_author(self) -> str:
		author = AUTHORS.get(self.youtube.author, ('', ''))[0]
		return author or slugify(self.youtube.author, max_length=24, word_boundary=True, separator=" ", lowercase=False,
								 replacements=[['Asmr', ''], ['\'', '']]).title()
	
	def __get_tags(self) -> list[str]:
		try:
			author_tags = AUTHORS.get(self.youtube.author, ['Other'])[1]
		except IndexError:
			author_tags = []
		video_length = 'TitTok' if self.youtube.length < 2 * 60 else 'Short' if self.youtube.length < 45 * 60 else 'Long'
		return author_tags + [video_length] if author_tags is not None else [video_length]
	
	def __get_duration(self) -> str:
		"""
		Get the video duration in hour:minutes:seconds, if hour or minutes is zero, it's not represented
		@return: String that represent time in hh:mm:ss
		"""
		hours, remainder = divmod(self.youtube.length, 3600)
		minutes, seconds = divmod(remainder, 60)
		return f'{hours:2d}h{minutes:2d}m{seconds:2d}' if hours > 0 else f'{minutes:2d}m{seconds:2d}' if minutes > 0 else f'{seconds:2d}s'
	
	def __get_audio_stream(self) -> Stream | None:
		try:
			audio = self.youtube.streams.filter(type='audio').order_by('abr').desc().first()
			logging.info(f"Audio Stream Found: {self.audio_stream}")
		except pytube.exceptions.AgeRestrictedError:
			print(f'{Fore.RED}This Video is Age Restricted: Can\'t Download it{self.filename} {Fore.RESET}')
			self.can_download_codes.append(2)
			return None
		except (AttributeError, TypeError, ValueError):
			logging.error(f"Error getting streams audio or video (Streams): ", self.youtube.streams.filter(type='audio'))
			self.can_download_codes.append(2)
			return None
		
		return audio
	
	def __get_video_stream(self) -> Stream | None:
		try:
			video = self.youtube.streams.filter(subtype='webm', type='video').order_by('resolution').desc().first()
			logging.info(f"Audio Stream Found: {self.audio_stream}")
		except pytube.exceptions.AgeRestrictedError:
			print(f'{Fore.RED}This Video is Age Restricted: Can\'t Download it{self.filename}{Fore.RESET}')
			self.can_download_codes.append(2)
			return None
		except (TypeError, ValueError):
			logging.error(f"Error getting streams audio or video (Streams): ", self.youtube.streams.filter(type='video'))
			self.can_download_codes.append(2)
			return None
		return video
	
	def __verify(self):
		logging.info("Verifying class values")
		
		if self.filename == "":
			self.filename = get_random_str(16, 'ud')
			logging.error(f"New Filename={self.filename}")
			self.can_download_codes.append(10)
		
		if self.author == "":
			self.author = get_random_str(16, 'ud')
			logging.error(f"New Author={self.author}")
			self.can_download_codes.append(12)
		
		if self.thumbnail_url == "":
			logging.error(f"No thumbnail url found")
			self.can_download_codes.append(11)
		
		if len(self.tags) == 0:
			logging.error(f"No tags found, even video length tags")
			self.can_download_codes.append(13)
		
		if self.audio_stream is None:
			logging.error(f"Audio Stream is None")
			self.can_download_codes.append(1)
		
		if self.video_stream is None:
			logging.error(f"Video Stream is None")
			self.can_download_codes.append(2)
		
		if self.filesize_mb == -1:
			logging.error(f"No filesize found, video or audio stream is None")
			self.can_download_codes.append(14)
		
		logging.info(f"Error download codes= {self.can_download_codes}")
	
	def __post_init__(self):
		self.can_download_codes = []
		logging.info(f"Video Class Values")
		self.thumbnail_url = self.youtube.thumbnail_url
		self.filename = self.__get_filename()
		self.author = self.__get_author()
		self.tags = self.__get_tags()
		self.duration = self.__get_duration()
		self.filesize_mb = -1
		logging.info(f"name={self.filename}\nauthor={self.author}\ntags={self.tags}\nduration={self.duration}\nwatch_url={self.url}\nthumbnail_url={self.thumbnail_url}")
		
		self.audio_stream = self.__get_audio_stream()
		self.video_stream = self.__get_video_stream()
		if self.audio_stream is None or self.video_stream is None:
			logging.error(f"audio_stream={self.audio_stream}\nvideo_stream={self.video_stream}\nfilesize={self.filesize_mb}")
			self.__verify()
			return
		
		self.filesize_mb = self.audio_stream.filesize_mb + self.video_stream.filesize_mb
		logging.info(f"audio_stream={self.audio_stream}\nvideo_stream={self.video_stream}\nfilesize={self.filesize_mb}")
		self.__verify()
	
	def __str__(self):
		return (f'{Fore.MAGENTA}{self.author}{Fore.RESET} | {Fore.CYAN}{self.filename}{Fore.RESET}\n'
				f'\t{Fore.BLUE}{self.duration} | {self.filesize_mb:.1f}Mb | {self.tags}\n'
				f'\tDestination: {self.destination}\n'
				f'\tVideo: {self.video_stream}\n'
				f'\tAudio: {self.audio_stream}{Fore.RESET}')


def __transform_playlist_url(url: str) -> str:
	"""
	Transform a playlist watch url to a playlist list url and return it
	"""
	
	pattern_pl = r"https://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)(?:&list=([a-zA-Z0-9_-]+)(?:&index=\d+)?)?"
	match = re.compile(pattern_pl).match(url)
	if match is None: return ''
	
	playlist_id = match.group(2)
	return f'https://www.youtube.com/playlist?list={playlist_id}' if playlist_id else ''


def __get_url_and_is_playlist(url: str) -> (str, bool):
	"""
	Get a valid url (YouTube -> Watch video url; Playlist -> Playlist list url) and return if is playlist or not,
	other urls can work but not sure for all
	"""
	re_watch = r"(?:https://www.youtube.com/watch[?]v=)[a-zA-Z0-9_-]{11}($|&t=[0-9]{1,}s)"
	re_pl_list = r"(?:https://www.youtube.com/playlist[?]list=)[a-zA-Z0-9_-]{34}$"
	re_pl_watch = r"(?:https://www.youtube.com/watch[?]v=)[a-zA-Z0-9_-]{11}(?:&list=)[a-zA-Z0-9_-]{34}"
	
	if re.search(re_watch, url) is not None:
		return url, False
	
	elif re.search(re_pl_list, url) is not None:
		return url, True
	
	elif re.search(re_pl_watch, url) is not None:
		url = __transform_playlist_url(url)
		if url != '' and re.search(re_pl_list, url) is not None:
			return url, True
	
	return '', False


def separate_urls(user_urls: list[str]) -> (list[str], list[str]):
	"""
	Return (youtube_urls, playlist_urls) removing duplicates and checking if the url is a valid youtube url
	"""
	youtube_urls = []
	playlist_urls = []
	
	for user_url in user_urls:
		url, is_playlist = __get_url_and_is_playlist(user_url)
		if url == '':
			logging.error(f"Not valid url => {url}")
			print(f"ERROR: Not valid url => {url}")
			continue
		playlist_urls.append(url) if is_playlist else youtube_urls.append(url)
	
	return list(set(youtube_urls)), list(set(playlist_urls))


def __download_files(video: Video, _folder: str, _audioname: str, _videoname: str, _thumbnailname: str) -> int:
	# Streams
	try:
		video.audio_stream.download(output_path=_folder, filename=_audioname, max_retries=2)
		video.video_stream.download(output_path=_folder, filename=_videoname, max_retries=2)
	except:
		logging.error("Error Download: a problem occured while downloading streams", video)
		print('Error Download: a problem occured while downloading files')
		errors.append(video)
		return 0  # Can't download
	# Thumbnail
	try:
		if 11 in video.can_download_codes:
			logging.error("Error Download Thumbnail: The video will put a random thumbnail because no thumbnail found",video)
			print('Error Download Thumbnail: The video will put a random thumbnail because no thumbnail found')
			return 1  # No thumbnail
		download_urlfile(video.thumbnail_url, str(Path(_folder, _thumbnailname)))
	except:
		logging.error("Error Download Thumbnail: The video will put a random thumbnail because no thumbnail found", video)
		print('Error Download Thumbnail: The video will put a random thumbnail because no thumbnail found')
		return 1  # No thumbnail
	return -1  # good - useless


def __combine_files(video: Video, _audio: str, _video: str, _thumbnail: str | None, _ffmpeg: str) -> int:
	command = f"ffmpeg -hide_banner -loglevel error -i {_video} -i {_audio} -c copy -y {_ffmpeg}" if _thumbnail is None \
		else f'ffmpeg -hide_banner -loglevel error -i {_video} -i {_audio} -i {_thumbnail} -map 0 -map 1 -c copy -map_metadata 0 -disposition:2 attached_pic -y {_ffmpeg}'
	try:
		os.system(command)
		return -1  # Good
	except:
		logging.error("Error combining files: ", video)
		print('Error Combine: a problem occured while combining files')
		errors.append(video)
		return 0  # Error


def __rename_file(old_filepath: str, new_filepath: str):
	try:
		os.rename(Path(old_filepath), Path(new_filepath))
	except:
		logging.error(f'Error Renaming file: The file will keep the temporary name(old={old_filepath}; new={new_filepath})')
		print(f'Error Renaming file: The file will keep the temporary name; filename={old_filepath}')


def __add_file_metadata(video: Video, filepath: str):
	try:
		mp4 = MP4(filepath)
		mp4["\xa9gen"] = "; ".join(video.tags)
		mp4["\xa9ART"] = video.author
		mp4["\xa9cmt"] = video.youtube.publish_date.strftime('%d-%m-%Y')
		mp4.save()
	except:
		logging.error(
			f'Error Metadata: can\'t insert metadata in file(genre={"; ".join(video.tags)}, artist={video.author}, comment={video.youtube.publish_date.strftime("%d-%m-%Y")})')
		print(
			f'Error Metadata: can\'t insert metadata in file\n\tgenre={"; ".join(video.tags)}\n\tartist={video.author}\n\tcomment={video.youtube.publish_date.strftime("%d-%m-%Y")})')


def download(video: Video, skip_existing: bool) -> None:
	print(video)
	
	# Check if error code
	if 1 in video.can_download_codes or 2 in video.can_download_codes:
		logging.error("This video class have stream missing: ", video)
		print(f'{Fore.RED}This video have streams missing and can\'t be downloaded{Fore.RESET}')
		return
	
	# Skip if already exist file
	if skip_existing:
		if Path(video.destination, video.filename).is_file():
			print(f'{Fore.YELLOW}Already exist. Passing{Fore.RESET}')
			return
	
	# temp filename - Easy to change
	_audioname = 'audio.webm'
	_videoname = 'video.webm'
	_thumbnailname = 'thumbnail.jpg'
	_name = slugify(f'{video.author}{video.filename}', max_length=64)
	
	_folder = Path(video.destination, _name)
	_folder.mkdir(parents=True, exist_ok=True)
	
	_folder = str(_folder)
	_audio = str(Path(_folder, _audioname))
	_video = str(Path(_folder, _videoname))
	_thumbnail = str(Path(_folder, _thumbnailname))
	_ffmpeg = str(Path(video.destination, f'{_name}.mp4'))
	destination = str(Path(video.destination, video.filename))
	
	# Download
	_code = __download_files(video, _folder, _audioname, _videoname, _thumbnailname)
	if _code == 0: return
	
	# Combine
	_code = __combine_files(video, _audio, _video, _thumbnail if _code != 1 else None, _ffmpeg)
	if _code == 0: return
	
	# Remove temp folder
	shutil.rmtree(_folder)
	
	# Rename
	__rename_file(_ffmpeg, destination)
	
	# Add Metadata
	__add_file_metadata(video, destination)


def main(user_urls: list[str], destination: str, skip_existing: bool) -> None:
	logging.basicConfig(filename=LOGFILE, encoding='utf-8', level=LOGGINGLEVEL)
	
	youtube_urls, playlist_urls = separate_urls(user_urls)
	
	for url in youtube_urls:  # Doing this to use less ram and not store all 5000 url video class
		youtube = YouTube(url)
		video = Video(youtube, destination, url)
		download(video, skip_existing)
	
	for url in playlist_urls:
		playlist = Playlist(url)
		for counter, youtube in enumerate(playlist.videos):
			video = Video(youtube, str(Path(destination, slugify(playlist.title, separator='_', lowercase=False, max_length=128))), url)
			video.filename = f"{counter+1}_{video.filename}"
			download(video, skip_existing)


if __name__ == '__main__':
	print("It does not work like this, use 'main.py -help' to know how to use")
