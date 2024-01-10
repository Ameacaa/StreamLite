from Shared import download_urlfile
from pytube import YouTube, Playlist, Stream, exceptions
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from dataclasses import dataclass, field
from mutagen.mp4 import MP4
from slugify import slugify
from colorama import Fore
from pathlib import Path
import speedtest
import logging
import shutil
import time
import os
import re


CHRONO_FUNC_FILEPATH = r'B:\Projects\_new_\StreamLite\logs\yt_speeds.txt'
LOGFILE = r'B:\Projects\_new_\StreamLite\logs\yt_debug.log'
LOGGINGLEVEL = logging.DEBUG
SHOW_EXTENTED_ERRORS = False
CPU_CORES_DOWNLOAD = 4  # Parrallel download => Max = cpu_count() = 12 for me

COLORS = {
	"reset"     : Fore.RESET,
	"error"     : Fore.RED,
	"warning"   : Fore.YELLOW,
	"exceptions": Fore.RED,
	
	"title"     : Fore.CYAN,
	"author"    : Fore.MAGENTA,
	"file_exist": Fore.BLUE,
	"dl_succeed": Fore.GREEN,
	"dl_failed" : Fore.RED
}

AUTHORS = {
	"Anthox Colaboy"                       : ("Anthox", ["Entertainment", "Favorite"]),
	"Anthox Colaboy VOD twitch (Officiel) ": ("Anthox VOD", ["Favorite", "VOD"]),
	"CacaboxTV"                            : ("CCB", ["Favorite", "VOD"]),
	"Hugo Délire"                          : ("Hugod", ["Favorite"]),
	"Hugo Délire - Les VOD"                : ("Hugod VOD", ["Favorite", "VOD"]),
	"Wankil Studio - Laink et Terracid"    : ("Wankil Studio", ["Favorite", "Entertainment"]),
	"Wankil Studio - Les VOD"              : ("Wankil VOD", ["Favorite", "VOD"]),
	"POTATOZ"                              : ("", ["Favorite", "Entertainment"]),
	"POTATOZ - LIVE & BEST-OF"             : ("", ["Favorite", "VOD", "Entertainment"]),
	"POTATOZ Clips"                        : ("", ["Favorite", "Entertainment"]),
	"anna dreamy ASMR"                     : ("Anna Dreamy", ["ASMR"]),
	"TOM ASMR"                             : ("Tom", ["ASMR"]),
	"Compilations Virgule Animale"         : ("Virgule Animale 2", ["Animals"]),
	"Virgule Animale"                      : ("", ["Favorite", "Animals"]),
	"ANIMAUX : MODE D'EMPLOI "             : ("Yvan Animaux", ["Animals"]),
	"12 Parsecs"                           : ("", ["Entertainment", "Learn", "Astronomy"]),
	"ACIDRAMA"                             : ("", ["Stories", "Mystery", "Favorite", "Icebergs"]),
	"Axolot"                               : ("", ["Learn"]),
	"BPS.space"                            : ("", ["Learn", "DIY", "Astronomy"]),
	"Officiel DEFAKATOR"                   : ("Defakator", ["Favorite", "Learn"]),
	"ALTER"                                : ("", ["Horror", "Movie"]),
	"0612 TV w/ NERDfirst"                 : ("", ["Learn", "Programming"]),
	"Abrège"                               : ("", ["DIY"]),
	"Ad Immensum"                          : ("", ["Learn", "Stories", "Mythology"]),
	"Adam Bros"                            : ("", ["Learn"]),
	"Alex Kister"                          : ("", ["Favorite", "Movie"]),
	"ALT 236"                              : ("", ["Favorite", "Stories"]),
	"AlterHis"                             : ("", ["Stories"]),
	"Amenoz Cotcot"                        : ("", ["Entertainment"]),
	"Ami des lobbies"                      : ("", ["Learn", "World", "Favorite"]),
	"Aminematue"                           : ("", ["Entertainment"]),
	"Andy Math"                            : ("", ["Learn", "Maths"]),
	"Artu"                                 : ("", ["Stories", "Movie"]),
	"ATOM"                                 : ("", ["Learn", "Design"]),
	"BABOR LELEFAN"                        : ("", ["Entertainment"]),
	"BADNEWS"                              : ("", ["Entertainment"]),
	"Balkan Gains"                         : ("", ["Motivation"]),
	"Basti Ui"                             : ("", ["Learn", "Design"]),
	"Benjamin Code"                        : ("", ["Learn", "Programming"]),
	"Benjamin Workshop"                    : ("", ["Entertainment", "Learn", "Mechanics"]),
	"Best Of du Grenier"                   : ("JDG 2", ["Entertainment", "VOD"]),
	"Branch Education"                     : ("", ["Learn"]),
	"Brick Experiment Channel"             : ("", ["Learn", "Entertainment"]),
	"Brick Technology"                     : ("", ["Entertainment", "Learn"]),
	"Bricolage c'est cool"                 : ("", ["Learn", "DIY"]),
	"Bruno Le Salé"                        : ("", ["World"]),
	"Charles Villa"                        : ("", ["Reportage", "World", "Favorite"]),
	"Chat Sceptique"                       : ("", ["Favorite", "Learn"]),
	"Chronik Fiction"                      : ("", ["Favorite", "Movie", "Stories"]),
	"clararunaway"                         : ("", ["Movie", "Stories"]),
	"Cleo Abram"                           : ("", ["Learn"]),
	"Clément Freze"                        : ("", ["Favorite", "Learn", "Entertainment"]),
	"Cnawak"                               : ("", ["Stories"]),
	"cocadmin"                             : ("", ["Favorite", "Programming"]),
	"Code BH"                              : ("", ["Favorite", "Gamedev"]),
	"Code Pointers"                        : ("", ["Programming"]),
	"Codeur de Nuit"                       : ("", ["Programming"]),
	"colinfurze"                           : ("", ["DIY"]),
	"Confessions d'Histoire"               : ("", ["History"]),
	"Consul Pazen "                        : ("", ["World"]),
	"Consulo Pazeno"                       : ("", ["World"]),
	"CULTUR3D"                             : ("", ["Learn", "Favorite"]),
	"CurieuxLive"                          : ("", ["Learn", "Favorite"]),
	"Cédrik JURASSIK"                      : ("", ["Learn", "Favorite", "Entertainment"]),
	"Daenys Horror Story"                  : ("", ["Stories", "Horror"]),
	"Dans Ton Corps"                       : ("", ["Learn"]),
	"Decode - Explore Media"               : ("Decode Media", ["Stories"]),
	"Defakator Vite Fait"                  : ("", ["Favorite", "Learn"]),
	"Defend Intelligence"                  : ("", ["Favorite", "Programming", "Learn"]),
	"DEO TOONS"                            : ("", ["Favorite", "Entertainment"]),
	"Diable Positif"                       : ("", ["Favorite"]),
	"Didi"                                 : ("", ["Stories"]),
	"Dimby Rakotomalala"                   : ("", ["Excel"]),
	"diorama111"                           : ("", ["Favorite"]),
	"DirtyBiology"                         : ("", ["Favorite", "Learn"]),
	"DIY Perks"                            : ("", ["Favorite", "Learn"]),
	"Dr Nozman"                            : ("", ["Learn"]),
	"Eddie Woo"                            : ("", ["Maths"]),
	"Edward"                               : ("", ["Favorite", "Stories"]),
	"EGO"                                  : ("", ["Favorite", "Stories"]),
	"ElectroBOOM"                          : ("", ["Learn"]),
	"Electronoobs"                         : ("", ["DIY"]),
	"Elie Lou"                             : ("", ["Stories"]),
	"Envato Tuts+"                         : ("", ["Programming"]),
	"Epic Teaching of History"             : ("", ["Favorite", "Learn", "Entertainment"]),
	"Et tout le monde s'en fout"           : ("", ["Learn"]),
	"Explore Media"                        : ("", ["Learn"]),
	"FabienOlicard"                        : ("", ["Learn", "Psychology"]),
	"Fabio Musanni - Programming Channel"  : ("Musanni Programming", ["Programming"]),
	"Feldup"                               : ("", ["Favorite", "Stories"]),
	"Fouloscopie"                          : ("", ["Favorite", "Psychology"]),
	"Fourmi des plaines"                   : ("", ["Favorite"]),
	"freeCodeCamp.org"                     : ("", ["Favorite", "Programming"]),
	"FRENCH DREAM TV"                      : ("", ["Favorite", "Cringe"]),
	"FRENCH DREAM TV RE"                   : ("", ["Favorite", "Cringe"]),
	"Frère Castor"                         : ("", ["Favorite", "Stories"]),
	"G Milgram"                            : ("", ["Favorite", "World"]),
	"G un kilo"                            : ("", ["Favorite", "World"]),
	"Gamedev Teacher"                      : ("", ["Gamedev"]),
	"Gaspard G"                            : ("", ["Favorite", "Reportage"]),
	"Gotabor"                              : ("", ["Favorite", "Learn"]),
	"Grafikart.fr"                         : ("", ["Programming"]),
	"Guillaume Cassar"                     : ("", ["Favorite", "Movie", "Stories"]),
	"Hackintux"                            : ("", ["Cybersecurity", "Learn"]),
	"Harley Guio Guitar"                   : ("", ["Guitar"]),
	"Hasheur"                              : ("", ["Favorite", "Crypto"]),
	"Hedacademy"                           : ("", ["Maths"]),
	"Heliox"                               : ("", ["DIY"]),
	"Henri Hihacks"                        : ("", ["DIY"]),
	"HighGame_Def"                         : ("", ["Learn", "Gamedev"]),
	"Hinfiney"                             : ("", ["Mythology", "History"]),
	"Horizon_Universe"                     : ("", ["Stories"]),
	"Horreur 404"                          : ("", ["Stories", "Movie", "Horror"]),
	"Hugo Lisoir"                          : ("", ["Favorite", "Astronomy"]),
	"Hugo Roth Raza"                       : ("", ["Entertainment"]),
	"Hygiène Mentale"                      : ("", ["Favorite", "Learn", "Psychology"]),
	"I did a thing"                        : ("", ["DIY"]),
	"Iconoclaste"                          : ("", ["Stories"]),
	"Illustre Connu"                       : ("", ["Movies", "Story"]),
	"INA Société"                          : ("", ["History"]),
	"Incroyables Expériences"              : ("", ["Favorite", "DIY"]),
	"Integza"                              : ("", ["Favorite", "Learn"]),
	"Jaihno"                               : ("", ["Favorite", "Stories"]),
	"JBV Creative"                         : ("", ["Favorite", "DIY"]),
	"Joey Carlino"                         : ("", ["Blender"]),
	"Josh Gambrell"                        : ("", ["Blender"]),
	"Joueur Du Grenier"                    : ("JDG", ["Favorite", "Entertainment"]),
	"Julien Bobroff"                       : ("", ["Favorite", "Learn"]),
	"Kaizen"                               : ("", ["Blender"]),
	"Kane Pixels"                          : ("", ["Favorite", "Movie"]),
	"Kayomil"                              : ("", ["Gamedev"]),
	"Kombo"                                : ("", ["Favorite", "Stories"]),
	"KT TechHD"                            : ("", ["Favorite", "Learn"]),
	"L'Effet Papillon"                     : ("", ["World"]),
	"La Psy Qui Parle"                     : ("", ["Learn", "Psychology"]),
	"La statistique expliquée à mon chat"  : ("", ["Favorite", "Maths"]),
	"LaGrandeRevue"                        : ("", ["Favorite", "Stories"]),
	"LaPatience"                           : ("", ["Favorite", "World"]),
	"LAPIN DU FUTUR"                       : ("", ["Favorite", "World"]),
	"Le Clap"                              : ("", ["Movie", "Stories"]),
	"Le Designer Auto"                     : ("", ["Favorite", "Design", "Learn"]),
	"LE GRAND JD"                          : ("", ["Favorite", "Horror", "Stories"]),
	"Le Muséum des ‽ourquois"              : ("Le Museum des Pourquois", ["Learn"]),
	"Le Point Genius"                      : ("", ["Favorite", "Learn"]),
	"Le Radis Irradié"                     : ("", ["Favorite", "World", "Entertainment"]),
	"Le Raptor"                            : ("", ["World"]),
	"LE ROI DES RATS"                      : ("", ["Favorite", "World"]),
	"Le Règlement"                         : ("", ["Music", "Stories"]),
	"Leffy62z"                             : ("", ["Entertainment"]),
	"Les Freres Poulain"                   : ("", ["Favorite", "DIY"]),
	"Les génies des sciences"              : ("", ["Favorite", "Learn"]),
	"Les Kassos"                           : ("", ["Favorite", "Entertainment"]),
	"Les Revues du Monde"                  : ("", ["Favorite", "Learn", "History"]),
	"Lesics"                               : ("", ["Learn"]),
	"Liu Zuo Lin"                          : ("", ["Programming"]),
	"LiveOverflow"                         : ("", ["Cybersecurity"]),
	"Livre Noir"                           : ("", ["World"]),
	"LORIS GIULIANO"                       : ("", ["Favorite", "Entertainment"]),
	"LOUP GAROU"                           : ("", ["Entertainment"]),
	"Léa Ricci"                            : ("", ["Learn"]),
	"Léo - TechMaker"                      : ("", ["Learn"]),
	"Léo-Paul "                            : ("", ["Favorite", "Entertainment"]),
	"Maskey"                               : ("", ["Favorite", "Entertainment", "Music"]),
	"MasterSnakou"                         : ("", ["Favorite"]),
	"MATH"                                 : ("", ["Movie", "Entertainment"]),
	"MATHIEU"                              : ("", ["Gamedev"]),
	"Mathieu Tutos Unreal Engine 5"        : ("Mathieu UE5", ["Gamedev"]),
	"Maudin Malin"                         : ("", ["Favorite", "World", "Psychology"]),
	"MaxEst ToujoursLa"                    : ("", ["World"]),
	"MaxEstLa"                             : ("", ["Favorite", "World"]),
	"Megan Morgan"                         : ("", ["Stories", "World"]),
	"Merci la physique"                    : ("", ["Learn"]),
	"Micode"                               : ("", ["Favorite", "Programming"]),
	"Millomaker"                           : ("", ["Favorite", "DIY"]),
	"Ming Jin"                             : ("", ["Learn"]),
	"Mister V"                             : ("", ["Favorite", "Entertainment"]),
	"MisterFlech"                          : ("", [""]),
	"Monsieur Bidouille"                   : ("", ["Favorite", "Learn"]),
	"Monsieur Phi"                         : ("", ["Favorite", "Psychology"]),
	"Montreux Comedy"                      : ("", ["Favorite", "Entertainment"]),
	"MyFuckinMess"                         : ("", ["Favorite", "Entertainment"]),
	"Mythos Realis"                        : ("", ["Mythology", "Stories"]),
	"Naj B Fit"                            : ("", ["Favorite", "Psychology"]),
	"NetworkChuck"                         : ("", ["Favorite", "Programming"]),
	"NeuralNine"                           : ("", ["Favorite", "Programming"]),
	"Nico71's Lego Technic Creations"      : ("Nico71's Lego", ["Learn"]),
	"Nota Bene"                            : ("", ["History"]),
	"Notseriou's"                          : ("", ["Favorite", "Movie", "Entertainment"]),
	"Olivier - Coach Webmarketing"         : ("", ["Learn"]),
	"Palmashow"                            : ("", ["Favorite", "Entertainment"]),
	"PARADOX"                              : ("", ["Horror", "Stories"]),
	"Parfaitement Web"                     : ("", ["Favorite", "Programming"]),
	"Pas Végan"                            : ("", ["Favorite", "Learn"]),
	"Plot Time"                            : ("", ["Favorite", "Movie", "Stories"]),
	"Polokus"                              : ("", ["Favorite", "Music", "Stories"]),
	"PortugueseFacts par Tiago"            : ("PortugueseFacts", ["Learn", "History"]),
	"Primer"                               : ("", ["Favorite", "Learn", "Programming"]),
	"Programiz"                            : ("", ["Programming"]),
	"Programming with Mosh"                : ("", ["Programming"]),
	"ProjectAir"                           : ("", ["DIY"]),
	"Psyhodelik"                           : ("", ["World"]),
	"pwnisher"                             : ("", ["Design"]),
	"RaAaK"                                : ("", ["Favorite"]),
	"RIAN"                                 : ("", ["Learn"]),
	"Romy Victory"                         : ("", ["TrueCrime"]),
	"Rui Santos"                           : ("", ["DIY"]),
	"Sabine"                               : ("", ["Learn", "World"]),
	"salut c'est cringe"                   : ("", ["Favorite", "Cringe"]),
	"Sandoz"                               : ("", ["Cybersecurity", "Entertainment"]),
	"Savage Games"                         : ("", ["Gamedev"]),
	"Scarabête"                            : ("", ["Animals"]),
	"Science de comptoir"                  : ("", ["Learn"]),
	"Science4All"                          : ("", ["Learn"]),
	"Scilabus"                             : ("", ["Favorite", "Learn"]),
	"SCP Foundation"                       : ("", ["Horror"]),
	"Scrotumdepoulpe"                      : ("", []),
	"SEB"                                  : ("", ["Favorite", "Stories"]),
	"Sebastian Lague"                      : ("", ["Favorite", "Programming"]),
	"SeriActu"                             : ("", ["World"]),
	"SEROTHS"                              : ("", ["Favorite", "Horror"]),
	"Servet Gulnaroglu"                    : ("", ["Programming"]),
	"Sheshounet"                           : ("", ["Favorite", "Entertainment"]),
	"Simon Puech"                          : ("", ["Favorite", "Stories", "World"]),
	"Sir_Thomas_ Gaming"                   : ("", ["Entertainment"]),
	"Sky Guitar"                           : ("", ["Guitar"]),
	"Slexno"                               : ("", ["Favorite", "Movie", "Learn"]),
	"SmarterEveryDay"                      : ("", ["Favorite", "Learn"]),
	"SQUEEZIE"                             : ("", ["Favorite", "Stories"]),
	"Steve Mould"                          : ("", ["Favorite", "Learn", "DIY"]),
	"Stream Theory"                        : ("", ["Favorite", "Learn"]),
	"Stupid Economics"                     : ("", ["Favorite", "Learn"]),
	"Stéphane Edouard"                     : ("", ["World"]),
	"Superconeri"                          : ("", ["Favorite", "Entertainment"]),
	"Sylartichot"                          : ("", ["Horror", "Mythology", "Stories"]),
	"Sylvdeux"                             : ("", ["Stories", "Programming"]),
	"Sylvqin"                              : ("", ["Favorite", "Stories", "Programming"]),
	"tableuh"                              : ("", ["Stories"]),
	"TAOQAN"                               : ("", ["Favorite", "Learn"]),
	"TechWorld with Nana"                  : ("", ["Programming"]),
	"Terrapodia"                           : ("", ["Favorite", "Animals", "Learn"]),
	"The Action Lab"                       : ("", ["Learn"]),
	"the roadmap"                          : ("", ["Programming"]),
	"The Sciencoder"                       : ("", ["Favorite", "Entertainment"]),
	"TheoBabac"                            : ("", ["Entertainment"]),
	"TheoBabac2"                           : ("", ["Entertainment"]),
	"Thomi et Skadi"                       : ("", ["Learn", "Animals", "Dogs"]),
	"Thoz"                                 : ("", ["Entertainment"]),
	"Théorus"                              : ("", ["Favorite", "Entertainment"]),
	"tn DNA"                               : ("", ["Favorite", "Psychology"]),
	"Tom Stanton"                          : ("", ["Favorite", "DIY"]),
	"TOUNY"                                : ("", ["Stories"]),
	"Tout Simplement – Kurzgesagt"         : ("Kurzgesagt FR", ["Learn"]),
	"Underscore_"                          : ("", ["Favorite", "Stories", "Programming"]),
	"UNF Games"                            : ("", ["Gamedev"]),
	"Useless Game Dev"                     : ("", ["Gamedev"]),
	"Valek"                                : ("", ["World"]),
	"Veritasium"                           : ("", ["Favorite", "Learn"]),
	"Victor Ferry"                         : ("", ["Favorite", "Psychology"]),
	"Vilebrequin"                          : ("", ["Favorite"]),
	"VLRN | Valerian"                      : ("", ["Gamedev"]),
	"Vous Avez Le Droit"                   : ("", ["Favorite", "Learn"]),
	"Waked XY"                             : ("", ["Favorite", "Cybersecurity"]),
	"White Box Dev"                        : ("", ["Favorite", "Programming"]),
	"Wildeye Demon"                        : ("", ["Favorite", "Reportage"]),
	"Yann Bouvier | YannToutCourt"         : ("Yann Bouvier", ["History"]),
	"Yann Piette"                          : ("", ["Psychology"]),
	"Zyger"                                : ("", ["Gamedev"])
}

download_result = {
	"SUCCESS"            : [],
	"SUCCESS_MINOR_ERROR": [],
	"FILE_EXISTS"        : [],
	"NO_STREAMS"         : [],
	"NO_THUMBNAIL"       : [],
	"DOWNLOAD"           : [],
	"COMBINE"            : [],
	"AGE_RESTRICTED"     : [],
	"RENAME"             : [],
	"METADATA"           : [],
	"DELETE_TEMP"        : []
}
total_download_gb = 0


@dataclass
class Video:
	url: str = field()
	destination: str = field()
	playlist_index: int = field()
	youtube: YouTube | None = field(init=False, default=True)
	title: str = field(init=False, default='')
	thumbnail_url: str | None = field(init=False, default='')
	audio_stream: Stream | None = field(init=False, default=None)
	video_stream: Stream | None = field(init=False, default=None)
	author: str = field(init=False, default='')
	duration: str = field(init=False, default='')
	tags: list[str] = field(init=False, default=list)
	filesize_mb: float = field(init=False, default=-1)
	result: str = field(init=False, default='')
	download_time_take: float = field(init=False, default=-1)
	
	def __post_init__(self):
		def get_youtube() -> YouTube | None:
			try:
				_youtube = YouTube(self.url)
				return _youtube if _youtube.watch_html is not None else None
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				return None
		
		def get_title() -> str:
			_yt_title = str(self.youtube.title).lower()  # To simplify replace
			_toreplace = [['asmr', ''], ['\'', ''], ['vod', '']]  # Need to be in lowercase
			return slugify(_yt_title, max_length=128, word_boundary=True, separator=" ", lowercase=False, replacements=_toreplace).title()
		
		def get_author() -> str:
			_toreplace = [['asmr', ''], ['\'', ''], ['vod', '']]  # Need to be in lowercase
			_author = self.youtube.author
			try:
				if _author in AUTHORS and AUTHORS.get(_author, ('', ''))[0] != '':
					return AUTHORS.get(_author, ('', ''))[0]
				else:
					_author = self.youtube.author
					return slugify(_author.lower(), max_length=48, word_boundary=True, separator=" ", lowercase=False, replacements=_toreplace).title()
			except Exception as e:
				_author = self.youtube.author
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(f"{COLORS['error']}The author {_author} in dictionary is not properly write{COLORS['reset']}")
				return slugify(_author.lower(), max_length=48, word_boundary=True, separator=" ", lowercase=False, replacements=_toreplace).title()
		
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
			
			return f'{hours}h{minutes}m{seconds}' if int(hours) > 0 else f'{minutes}m{seconds}' if int(minutes) > 0 else f'{seconds}s'
		
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
		# author_len = 24 | title_len = 105
		max_length = 140
		string = f"{COLORS['author']}{self.author:24}{COLORS['reset']} | {COLORS['title']}{self.title:100}"
		return f"{string[:max_length - 3]}{COLORS['reset']}..." if len(string) > max_length \
			else f"{string}{COLORS['reset']}"
	
	def __repr__(self):
		return (f'{Fore.MAGENTA}{self.author}{Fore.RESET} | {Fore.CYAN}{self.title}{Fore.RESET}\n'
				f'\t{Fore.BLUE}{self.duration} | {self.filesize_mb:.1f}Mb | {self.tags}\n'
				f'\tDestination: {self.destination}\n'
				f'\tVideo: {self.video_stream}\n'
				f'\tAudio: {self.audio_stream}{Fore.RESET}')
	
	@staticmethod
	def get_possible_errors():
		errors = [
			"If the problem is renaming or adding the metadata the delete function will keep be on",
			"Possible errors:",
			"\tThe file already exist with this same name -> (skip_existing (True=Passing; False=Overwrite))",
			"\tNo streams (audio or video) has been found -> Passing and retry at the end",
			"\tAge Restricted Exist for this video -> Passing",
			"\tDownload Thumbnail Error -> Continue without applying the thumbnail to the video",
			"\tDownload Streams Error -> Passing",
			"\tCombining Streams and thumbnail error -> Passing",
			"\tRenaming file error -> The video keeps the temporary name if we can else Passing",
			"\tAdding Metadata Error -> The video have no metadata on",
			"\tDeleting Folder Error -> The Temporary folder is not delete need to be delete manually",
			"\tGreen Succeed = All good; Yellow Succeed = Minor Errors (renaming or adding metadata)"
		]
		return "\n".join(errors)
	
	def get_filename(self, temp: bool = False, extension: bool = True):
		toreplace = [["asmr", ""], ["vod", ""], ["\'", ""], ["laink et terracid", ""]]
		filename = f'{self.playlist_index}_{self.title}' if self.playlist_index != -1 else f'{self.title}'
		filename = slugify(filename.lower(), max_length=64, separator='_', replacements=toreplace) if temp \
			else slugify(filename.lower(), max_length=128, separator=' ', replacements=toreplace).title()
		return f'{filename}.mp4' if extension else filename
	
	def download(self, skip_existing: bool) -> None:
		def can_download() -> bool:
			if skip_existing and Path(out_filepath).is_file():
				self.result += f"{COLORS['file_exist']}Already exist - Passing{Fore.RESET}"
				download_result["FILE_EXISTS"].append(self)
				return False
			
			if self.audio_stream is None or self.video_stream is None:
				self.result += f"{COLORS['error']}No stream{COLORS['reset']}"
				download_result["NO_STREAMS"].append(self)
				return False
			
			if self.youtube.age_restricted:
				self.result += f'{COLORS["error"]}Age Restricted{Fore.RESET}'
				download_result["AGE_RESTRICTED"].append(self)
				return False
			
			return True
		
		def download_thumbnail() -> bool:
			if self.thumbnail_url is None:
				download_result["NO_THUMBNAIL"].append(self)
				return False
			try:
				download_urlfile(self.thumbnail_url, _paths["thumbnail_path"], 1024 * 1024 * 24)
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error downloading the thumbnail of the video", COLORS["reset"])
				download_result["NO_THUMBNAIL"].append(self)
				return False
		
		def download_streams() -> bool:
			if self.audio_stream is None or self.video_stream is None:
				download_result["NO_STREAMS"].append(self)
				return False
			try:
				self.audio_stream.download(output_path=str(_paths["folder_path"]), filename="audio.webm", max_retries=4)
				self.video_stream.download(output_path=str(_paths["folder_path"]), filename="video.webm", max_retries=4)
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error downloading the streams of the video", COLORS["reset"])
				download_result["NO_STREAMS"].append(self)
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
				download_result["COMBINE"].append(self)
				return False
		
		def rename_video() -> bool:
			try:
				if Path(out_filepath).is_file():
					self.result += "File with the same name already exist "
					return False
				os.rename(Path(_paths["ffmpeg_filepath"]), Path(out_filepath))
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error renaming the video", COLORS["reset"])
				download_result["RENAME"].append(self)
				return False
		
		def add_metadata() -> bool:
			try:  # https://mutagen.readthedocs.io/en/latest/api/mp4.html
				mp4 = MP4(out_filepath)
				mp4["\xa9gen"] = "; ".join(self.tags)
				mp4["\xa9ART"] = self.author if self.author is not None else 'ErrorUnknow'
				mp4["\xa9cmt"] = self.youtube.publish_date.strftime('%d-%m-%Y')
				mp4.save()
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error Adding Metadata in the video", COLORS["reset"])
				download_result["METADATA"].append(self)
				return False
		
		def delete_temp_folder() -> bool:
			try:
				shutil.rmtree(_paths["folder_path"])
				return True
			except Exception as e:
				if SHOW_EXTENTED_ERRORS: print(COLORS["exceptions"], e, COLORS["reset"])
				if SHOW_EXTENTED_ERRORS: print(COLORS["warning"], "Error Deleting temp folder", COLORS["reset"])
				download_result["DELETE_TEMP"].append(self)
				return False
		
		self.result = f"{self}: "
		out_filepath = str(Path(self.destination, self.get_filename(temp=False, extension=True)))  # Final Destination
		
		if not can_download(): return
		
		# Prepare all paths needed
		_name = self.get_filename(temp=True, extension=False)  # Temporary name just for the dictionary
		_paths = {  # TEMPORARY PATHS
			"folder_path"    : Path(self.destination, _name),  # Create this file to contain audio. video and thumbnail
			"audio_path"     : str(Path(self.destination, _name, "audio.webm")),  # The absolute path of the audio
			"video_path"     : str(Path(self.destination, _name, "video.webm")),  # The absolute path of the video
			"thumbnail_path" : str(Path(self.destination, _name, "thumbnail.jpg")),  # The absolute path of the thumbnail
			"ffmpeg_filepath": str(Path(self.destination, self.get_filename(temp=True, extension=True)))  # This file is in destination folder but with a name that ffmpeg accept (old_name)
		}
		
		# Create the path if needed
		_paths["folder_path"].mkdir(parents=True, exist_ok=True)
		
		have_thumbnail = download_thumbnail()
		have_minor_errors = False
		if not download_streams():
			self.result += f'{COLORS["dl_failed"]}Download Failed{Fore.RESET}'
			return
		
		if not combine_ffmpeg():
			self.result += f'{COLORS["dl_failed"]}Combine FFMPEG Error{Fore.RESET}'
			return
		
		if Path(out_filepath).is_file():
			self.result += f'{COLORS["warning"]}Renaming Video Error - Continue with Temporary Name{Fore.RESET}'
			have_minor_errors = True
			out_filepath = _paths["ffmpeg_filepath"]
		elif not rename_video():
			self.result += f'{COLORS["error"]}Renaming Video Error - Stopping here{Fore.RESET}'
			have_minor_errors = True
			out_filepath = _paths["ffmpeg_filepath"]
		
		if not add_metadata():
			self.result += f'{COLORS["warning"]}Adding Metadata Error{Fore.RESET}'
			have_minor_errors = True
		
		if not delete_temp_folder():
			self.result += f'{COLORS["warning"]}Error deleting temp folder{Fore.RESET}'
			have_minor_errors = True
		if have_minor_errors:
			self.result += f'{COLORS["warning"]}Succeed{Fore.RESET}'
			download_result["SUCCESS_MINOR_ERROR"].append(self)
		else:
			self.result += f'{COLORS["dl_succeed"]}Succeed{Fore.RESET}'
			download_result["SUCCESS"].append(self)


def get_download_speed():
	st = speedtest.Speedtest()
	download_speed = st.download()
	return download_speed / 1_000_000  # Mbts


def download(arg: (str, str, str, str)):
	global total_download_gb
	url, destination, skip_existing, playlist_index = arg
	video = Video(url, destination, int(playlist_index))
	
	start = time.monotonic()
	
	video.download(bool(skip_existing))
	
	total_download_gb += (video.filesize_mb / 1024)
	video.download_time_take = time.monotonic() - start
	
	return video.result


def download_parallel(args: list[(str, str, str, str)]):
	cpus = CPU_CORES_DOWNLOAD if CPU_CORES_DOWNLOAD <= cpu_count() else cpu_count() - 1
	results = ThreadPool(cpus).imap_unordered(download, args)
	for result in results:
		print(result)


def get_args(user_urls: list[str], destination: str, skip_existing: bool) -> list[(str, str, str, str)]:
	def separe_urls() -> (list[str], list[str]):
		def transform_playlist_url() -> str:
			# Pattern => Playlist watching video. Like This: https://www.youtube.com/watch?v=fpX4n8rRyiU&list=PLnCmeDfRjs0Kwx6gGEqz2CyRsUTo-CeM3&index=2
			match = re.match(r"https://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)(?:&list=([a-zA-Z0-9_-]+)(?:&index=\d+)?)?", url)
			if match is None: return ''
			# Extract playlist ID from the matched groups
			playlist_id = match.group(2)
			# return the transformed URL. Like This: https://www.youtube.com/list=PLnCmeDfRjs0Kwx6gGEqz2CyRsUTo-CeM3
			return f'https://www.youtube.com/playlist?list={playlist_id}' if playlist_id else ''
		
		ytb_urls, pls_urls = [], []
		
		ytb_combine = re.compile(r"(?:https://www.youtube.com/watch[?]v=)[a-zA-Z0-9_-]{11}($|&t=[0-9]{1,}s)")
		pls_list_combine = re.compile(r"(?:https://www.youtube.com/playlist[?]list=)[a-zA-Z0-9_-]{34}$")
		
		for url in user_urls:
			if ytb_combine.match(url):
				ytb_urls.append(url);
				continue
			elif pls_list_combine.match(url):
				pls_urls.append(url);
				continue
			else:
				tr_url = transform_playlist_url()
				if pls_list_combine.match(tr_url):
					pls_urls.append(tr_url)
				else:
					print('This is not a valid url: ', url)
		
		return list(set(ytb_urls)), list(set(pls_urls))
	
	youtube_urls, playlist_urls = separe_urls()
	
	args = [(url, destination, str(skip_existing), str(-1)) for url in youtube_urls]
	
	for playlist_url in playlist_urls:
		playlist = Playlist(playlist_url)
		_destination = str(Path(destination, slugify(playlist.title, separator='_', lowercase=False, max_length=128)))
		for i, url in enumerate(playlist.video_urls):
			args.append((url, _destination, str(skip_existing), str(i + 1)))
	
	return args


def main(user_urls: list[str], destination: str, skip_existing: bool) -> None:
	# print("Checking internet speed: ", end="")
	# print(f'{get_download_speed():.1f} Mbts\n')
	
	print(f"Checking urls. ", end='')
	args = get_args(user_urls, destination, skip_existing)
	print(f"Found {len(args)} videos")
	
	download_parallel(args)
	
	print(f'Total Download Gbts: {total_download_gb}')
	
	print('-' * 150)
	for key, items in download_result.items():
		if len(items) == 0: continue
		print(key)
		for item in items:
			print(f'\t{item}')
			print(f'\t\t{item.url}')
		print('')


if __name__ == '__main__':
	print("It does not work like this, use 'main.py -help' to know how to use")
	__future__ = ["Download mp4 to not convert it to mp4 after"
				  "Future Updates - Not ordered",
				  "Rich console",
				  "Age restricted bypass",
				  "Download progress",
				  "Multi Download at the time",
				  "Predict time (filesize/internet_speed)",
				  "Retry download when failed",
				  "Debug Logs",
				  "Others views",
				  "GUI"]
	print(*__future__, sep='\n')
