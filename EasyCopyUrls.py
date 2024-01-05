import time
import pyperclip

__version__ = '1.0'
__future__ = ('Create a keyboard shortcut to stop the program'
			  'https://stackoverflow.com/questions/13207678/whats-the-simplest-way-of-detecting-keyboard-input-in-a-script-from-the-termina'
			  'Create a notification more easy to see when you copy a url to confirm the copy')

FILEPATH = 'B:/Temporary Files/download.txt'
STOP = 'stop'  # Copy this to stop the program


def stop(text: str) -> bool:
	return text.lower() == STOP


def is_url(text: str) -> bool:
	return text.startswith(("http://", "https://", "ftp://"))


def append_to_file(url, filepath: str) -> None:
	with open(filepath, 'a') as file:
		file.write(url + '\n')


def main(filepath: str = ""):
	if filepath == "": filepath = FILEPATH
	print(f'The filepath is: {FILEPATH}\nTo stop the program, just copy \'{STOP}\' to the clipboard')
	
	copy_history = set()
	while True:
		current_copy = pyperclip.paste()
		
		if stop(current_copy): quit()
		
		if current_copy not in copy_history and is_url(current_copy):
			print(f"Detected URL: {current_copy}")
			append_to_file(current_copy, filepath)
			copy_history.add(current_copy)
		time.sleep(0.2)  # Time between 2 copy


if __name__ == '__main__':
	main()
