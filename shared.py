from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import urllib3


@dataclass
class DownloadInfos:
	download_date: datetime
	download_result: str


def get_random_str(string_length: int, keep: str = 'ludw', adicional_chars: str = '') -> str:
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


def download_file(url: str, filepath: str, chunk_size: int = 1073741824):
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
