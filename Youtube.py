from Shared import download_urlfile, chronofunc
from dataclasses import dataclass, field
from pytube import YouTube, Playlist, Stream, exceptions
from mutagen.mp4 import MP4
from slugify import slugify
from colorama import Fore
from pathlib import Path
import speedtest
import logging
import shutil
import os
import re

CHRONO_FUNC_FILEPATH = r'B:\Projects\_new_\StreamLite\logs\yt_speeds.txt'
LOGFILE = r'B:\Projects\_new_\StreamLite\logs\yt_debug.log'
LOGGINGLEVEL = logging.DEBUG
SHOW_EXTENTED_ERRORS = False

COLORS = {
	"error": Fore.RED,
	"warning": Fore.YELLOW,
	"reset": Fore.RESET,
	"title": Fore.CYAN,
	"author": Fore.MAGENTA,
	"exceptions": Fore.BLUE,
	"file_exist": Fore.WHITE,
	"dl_succeed": Fore.GREEN,
	"dl_failed": Fore.RED
}

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
	"Wankil Studio - Laink et Terracid": ("Wankil Studio", ["Favorite", "Entertainment"]),
	"Wankil Studio - Les VOD": ("Wankil VOD", ["Favorite", "VOD"]),
	"White Box Dev": ("", ["Favorite", "Programming"]),
	"Wildeye Demon": ("", ["Favorite", "Reportage"]),
	"Yann Bouvier | YannToutCourt": ("", ["History"]),
	"Yann Piette": ("", ["Psychology"]),
	"Zyger": ("", ["Gamedev"])
}

retry_later = []
internet_speed = -1


@dataclass
class Video:
	url: str = field()
	destination: str = field()
	youtube: YouTube | None = field()
	playlist_index: int = field()
	title: str = field(init=False, default='')
	thumbnail_url: str | None = field(init=False, default='')
	audio_stream: Stream | None = field(init=False, default=None)
	video_stream: Stream | None = field(init=False, default=None)
	author: str = field(init=False, default='')
	duration: str = field(init=False, default='')
	tags: list[str] = field(init=False, default=list)
	filesize_mb: float = field(init=False, default=-1)
	
	def __post_init__(self):
		def get_youtube() -> YouTube | None:
			if self.youtube is not None: return self.youtube
			try:
				_youtube = YouTube(self.url)
				return _youtube if _youtube.watch_html is not None else None
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				return None
		
		def get_title() -> str:
			_yt_title = str(self.youtube.title).lower()  # To simplify replace
			_toreplace = [['asmr', ''], ['\'', ''], ['vod', '']]  # Need to be in lowercase
			return slugify(_yt_title, max_length=128, word_boundary=True, separator=" ", lowercase=False,
						   replacements=_toreplace).title() + '.mp4'
		
		def get_author() -> str:
			_toreplace = [['asmr', ''], ['\'', ''], ['vod', '']]  # Need to be in lowercase
			_author = self.youtube.author
			try:
				if _author in AUTHORS and AUTHORS.get(_author, ('', ''))[0] != '':
					return AUTHORS.get(_author, ('', ''))[0]
			except Exception as e:
				_author = self.youtube.author
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(
					f"{COLORS['error']}The author {_author} in dictionary is not properly write{COLORS['reset']}")
			finally:
				return slugify(_author.lower(), max_length=24, word_boundary=True, separator=" ", lowercase=False,
							   replacements=_toreplace).title()
		
		def get_thumbnail_url() -> str | None:
			try:
				_url = self.youtube.thumbnail_url
				return _url if _url is not None or _url == '' else None
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				return None
		
		def get_duration() -> str:
			hours, remainder = divmod(self.youtube.length, 3600)
			minutes, seconds = divmod(remainder, 60)
			
			hours = str(hours).zfill(2)
			minutes = str(minutes).zfill(2)
			seconds = str(seconds).zfill(2)
			
			return f'{hours}h{minutes}m{seconds}' if int(hours) > 0 else f'{minutes}m{seconds}' if int(
				minutes) > 0 else f'{seconds}s'
		
		def get_tags() -> list[str]:
			try:
				author_tags = AUTHORS.get(self.youtube.author, ['Other'])[1]
				if author_tags is None: author_tags = []
			except IndexError:
				author_tags = []
			except Exception as e:
				author_tags = []
				print(e)
			
			return author_tags + [
				'TitTok' if self.youtube.length < 2 * 60 else 'Short' if self.youtube.length < 45 * 60 else 'Long']
		
		def get_audio_stream() -> Stream | None:
			try:
				return self.youtube.streams.filter(type='audio').order_by('abr').desc().first()
			except exceptions.AgeRestrictedError:
				if SHOW_EXTENTED_ERRORS: print(COLORS["error"], f"{self}: Age Restricted - Passing", COLORS["reset"])
				return None
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				return None
		
		def get_video_stream() -> Stream | None:
			try:
				return self.youtube.streams.filter(subtype='webm', type='video').order_by('resolution').desc().first()
			except exceptions.AgeRestrictedError:
				if SHOW_EXTENTED_ERRORS: print(COLORS["error"], f"{self}: Age Restricted - Passing", COLORS["reset"])
				return None
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				return None
		
		def get_filesize_mb() -> float:
			return -1 if self.audio_stream is None or self.video_stream is None \
				else (self.audio_stream.filesize_mb + self.video_stream.filesize_mb)
		
		self.youtube = get_youtube()
		if self.youtube is None: return
		self.title = get_title()
		self.author = get_author()
		self.thumbnail_url = get_thumbnail_url()
		self.duration = get_duration()
		self.tags = get_tags()
		self.audio_stream = get_audio_stream()
		self.video_stream = get_video_stream()
		self.filesize_mb = get_filesize_mb()
	
	def __str__(self):
		max_length = 140
		string = f"{COLORS['author']}{self.author}{COLORS['reset']} | {COLORS['title']}{self.title}"
		return f"{string[:max_length - 3]}{COLORS['reset']}..." if len(string) >= max_length \
			else f"{string}{COLORS['reset']}"
	
	def __repr__(self):
		return (f'{Fore.MAGENTA}{self.author}{Fore.RESET} | {Fore.CYAN}{self.title}{Fore.RESET}\n'
				f'\t{Fore.BLUE}{self.duration} | {self.filesize_mb:.1f}Mb | {self.tags}\n'
				f'\tDestination: {self.destination}\n'
				f'\tVideo: {self.video_stream}\n'
				f'\tAudio: {self.audio_stream}{Fore.RESET}')
	
	def get_filename(self, temp: bool = False, extension: bool = True):
		toreplace = [["asmr", ""], ["vod", ""], ["\'", ""], ["laink et terracid", ""]]
		filename = f'{self.playlist_index}_{self.title}' if self.playlist_index != -1 else f'{self.title}'
		filename = slugify(filename.lower(), max_length=64, separator='_',
						   replacements=toreplace) if temp else filename.title()
		return f'{filename}.mp4' if extension else filename
	
	def download(self, skip_existing: bool) -> None:
		def can_download() -> bool:
			if skip_existing:
				if Path(self.destination, self.title).is_file():
					print(f"{COLORS['file_exist']}: Already exist{Fore.RESET}")
					return False
			
			if self.audio_stream is None or self.video_stream is None:
				print(f"{COLORS['error']}: No stream{COLORS['reset']}")
				retry_later.append(self)
				return False
			
			return True
		
		def download_thumbnail() -> bool:
			if self.thumbnail_url is None: return False
			try:
				download_urlfile(self.thumbnail_url, _paths["thumbnail_path"], 1024 * 1024 * 24)
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error downloading the thumbnail of the video",
											   COLORS["reset"])
				return False
		
		def download_streams() -> bool:
			if self.audio_stream is None or self.video_stream is None: return False
			try:
				self.audio_stream.download(output_path=str(_paths["folder_path"]), filename="audio.webm", max_retries=4)
				self.video_stream.download(output_path=str(_paths["folder_path"]), filename="video.webm", max_retries=4)
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error downloading the streams of the video",
											   COLORS["reset"])
				retry_later.append(self)
				return False
		
		def combine_ffmpeg() -> bool:
			cmd_thumbnail = f'ffmpeg -hide_banner -loglevel error -i {_paths["video_path"]} -i {_paths["audio_path"]} -i {_paths["thumbnail_path"]} -map 0 -map 1 -map 2 -c copy -map_metadata 0 -disposition:2 attached_pic -y {_paths["ffmpeg_filepath"]}'
			cmd_nothumbnail = f'ffmpeg -hide_banner -loglevel error -i {_paths["video_path"]} -i {_paths["audio_path"]} -c copy -y {_paths["ffmpeg_filepath"]}'
			try:
				if have_thumbnail:
					os.system(cmd_thumbnail)
				else:
					os.system(cmd_nothumbnail)
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error combining the streams", COLORS["reset"])
				retry_later.append(self)
				return False
		
		def rename_video() -> bool:
			try:
				if Path(out_filepath).is_file():
					print(": File with the same name already exist ")
					return False
				os.rename(Path(_paths["ffmpeg_filepath"]), Path(out_filepath))
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error renaming the video", COLORS["reset"])
				return False
		
		def add_metadata() -> bool:
			try:  # https://mutagen.readthedocs.io/en/latest/api/mp4.html
				mp4 = MP4(out_filepath)
				mp4["\xa9gen"] = "; ".join(self.tags)
				mp4["\xa9ART"] = self.author
				mp4["\xa9cmt"] = self.youtube.publish_date.strftime('%d-%m-%Y')
				mp4.save()
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error Adding Metadata in the video", COLORS["reset"])
				return False
		
		def delete_temp_folder() -> bool:
			try:
				shutil.rmtree(_paths["folder_path"])
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error Deleting temp folder", COLORS["reset"])
				return False
		
		print(self, end=': ', flush=True)
		
		if not can_download(): return
		
		# Prepare all paths needed
		_name = self.get_filename(temp=True, extension=False)  # Temporary name just for the dictionary
		_paths = {  # TEMPORARY PATHS
			"folder_path": Path(self.destination, _name),  # Create this file to contain audio. video and thumbnail
			"audio_path": str(Path(self.destination, _name, "audio.webm")),  # The absolute path of the audio
			"video_path": str(Path(self.destination, _name, "video.webm")),  # The absolute path of the video
			"thumbnail_path": str(Path(self.destination, _name, "thumbnail.jpg")),  # The absolute path of the thumbnail
			"ffmpeg_filepath": str(Path(self.destination, self.get_filename(temp=True, extension=True)))
			# This file is in destination folder but with a name that ffmpeg accept (old_name)
		}
		out_filepath = str(Path(self.destination, self.get_filename(temp=False, extension=True)))  # This is the destination with the good name (new_name)
		
		# Create the path if needed
		_paths["folder_path"].mkdir(parents=True, exist_ok=True)
		
		have_thumbnail = download_thumbnail()
		have_errors = False
		if self.youtube.age_restricted:
			print(f'{COLORS["dl_failed"]}Age Restricted{Fore.RESET}')
			return
			
		if not download_streams():
			print(f'{COLORS["dl_failed"]}Download Failed{Fore.RESET}')
			return
		
		if not combine_ffmpeg():
			print(f'{COLORS["dl_failed"]}Combine FFMPEG Error{Fore.RESET}')
			return
		
		if Path(out_filepath).is_file():
			print(f'{COLORS["warning"]}Renaming Video Error (Already Exist - Keeping Temporary Name){Fore.RESET}', sep='\n')
			out_filepath = _paths["ffmpeg_filepath"]
		elif not rename_video():
			print(f'{COLORS["warning"]}Renaming Video Error{Fore.RESET}', sep='\n')
			return
		
		if not add_metadata():
			print(f'{COLORS["warning"]}Adding Metadata Error{Fore.RESET}', sep='\n')
			return
		
		if not delete_temp_folder():
			print(f'{COLORS["warning"]}Error deleting temp folder{Fore.RESET}', sep='\n')
			return
		
		print(f'{COLORS["warning"] if have_errors else COLORS["dl_succeed"]}Succeed{Fore.RESET}')


def separate_urls(user_urls: list[str]) -> (list[str], list[str]):
	def transform_playlist_url(url: str) -> str:
		pattern_pl = r"https://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)(?:&list=([a-zA-Z0-9_-]+)(?:&index=\d+)?)?"
		match = re.compile(pattern_pl).match(url)
		if match is None: return ''
		
		playlist_id = match.group(2)
		return f'https://www.youtube.com/playlist?list={playlist_id}' if playlist_id else ''
	
	re_watch = r"(?:https://www.youtube.com/watch[?]v=)[a-zA-Z0-9_-]{11}($|&t=[0-9]{1,}s)"
	re_pl_list = r"(?:https://www.youtube.com/playlist[?]list=)[a-zA-Z0-9_-]{34}$"
	re_pl_watch = r"(?:https://www.youtube.com/watch[?]v=)[a-zA-Z0-9_-]{11}(?:&list=)[a-zA-Z0-9_-]{34}"
	
	youtube_urls, playlist_urls = [], []
	
	for user_url in user_urls:
		if re.search(re_watch, user_url) is not None:
			youtube_urls.append(user_url)
		elif re.search(re_pl_list, user_url) is not None:
			playlist_urls.append(user_url)
		
		elif re.search(re_pl_watch, user_url) is not None:
			returned_url = transform_playlist_url(user_url)
			if returned_url == '' or re.search(re_pl_list, returned_url) is None:
				print(f"{COLORS['error']}ERROR: Not valid url => {returned_url}{COLORS['reset']}")
				continue
			playlist_urls.append(returned_url)
		else:
			print(f"{COLORS['error']}ERROR: Not valid url => {user_url}{COLORS['reset']}")
			continue
	
	return list(set(youtube_urls)), list(set(playlist_urls))


def get_nvideos(playlist_urls: list[str]) -> int:
	counter = 0
	for url in playlist_urls: counter += len(Playlist(url).video_urls)
	return counter


def get_download_speed():
	st = speedtest.Speedtest()
	download_speed = st.download()
	return download_speed / 1_000_000  # Mbts


def main(user_urls: list[str], destination: str, skip_existing: bool) -> None:
	global internet_speed
	
	print("Checking internet speed: ", end="")
	internet_speed = get_download_speed()
	print(f'{internet_speed:.1f} Mbts\n')
	
	youtube_urls, playlist_urls = separate_urls(user_urls)
	nvideos = len(youtube_urls) + get_nvideos(playlist_urls)
	print(f"Found {len(youtube_urls) + len(playlist_urls)} urls for {nvideos} videos")
	
	dl_nvideos = 1
	for url in youtube_urls:
		print(f'[{dl_nvideos}/{nvideos}]: ', end='', flush=True)
		video = Video(url=url, destination=destination, youtube=None, playlist_index=-1)
		video.download(skip_existing)
		dl_nvideos += 1
	
	for url in playlist_urls:
		playlist = Playlist(url)
		for counter, youtube in enumerate(playlist.videos):
			_destination = str(Path(destination, slugify(playlist.title, separator='_', lowercase=False, max_length=128)))
			video = Video(url=url, destination=_destination, youtube=youtube, playlist_index=counter)
			video.download(skip_existing)
			dl_nvideos += 1


if __name__ == '__main__':
	print("It does not work like this, use 'main.py -help' to know how to use")
	__future__ = ["Future Updates - Not ordered"
				  "Rich console"
				  "Download progress"
				  "Multi Download at the time"
				  "Predict time (filesize/internet_speed)"
				  "Retry download when failed"
				  "Debug Logs"
				  "Others views"
				  "GUI"]
	print(*__future__, sep='\n')
	