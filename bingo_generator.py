#import sys
import spotipy
import random
from fpdf import FPDF
from spotipy.oauth2 import SpotifyOAuth

def fetch_playlist(uri: str, client: spotipy.client.Spotify) -> dict:
	return client.playlist(uri)

def extract_track_artist(playlist: dict, include_artists: bool) -> list:
	extract_info = lambda track: track['track']['name']
	if include_artists:
		extract_info = lambda track: track['track']['name'] + ' - ' + ', '.join(d['name'] for d in track['track']['artists'])
	
	return list(map(extract_info, playlist['tracks']['items']))

def generate_card_info(playlist: list, dimension: tuple, goal_per_row: int) -> list:
	assert dimension[1] >= goal_per_row
	assert len(playlist) >= dimension[0] * goal_per_row

	random.shuffle(playlist)
	rows = []

	for _ in range(dimension[0]):
		row_items = playlist[:goal_per_row] + [None] * (dimension[1]-goal_per_row)
		random.shuffle(row_items)
		rows.append(row_items)
		playlist = playlist[goal_per_row:]

	return rows

def get_num_of_lines_in_multicell(pdf, message: str, CELL_WIDTH: float) -> int:
    words = message.split(" ")
    line = ""
    n = 1
    for word in words:
        line += word + " "
        line_width = pdf.get_string_width(line)
        if line_width > CELL_WIDTH - 1:
            n += 1
            line = word + " "
    return n

def generate_card(card_info: list, **kwargs) -> None:
	n_rows = len(card_info)
	n_cols = len(card_info[0])
	pdf = FPDF(orientation = 'L', format = (n_rows * kwargs['cell_h'], n_cols * kwargs['cell_w']))
	pdf.add_font('comic_sans', '', r'/home/hest/Downloads/Comic Sans MS.ttf', uni=True)
	pdf.set_auto_page_break(False)
	pdf.add_page()
	pdf.set_xy(0, 0)
	pdf.set_font(kwargs['font'], '', kwargs['font_size'])
	pdf.set_margins(0, 0, 0)
	for i, row_info in enumerate(card_info):
		for j, cell_info in enumerate(row_info):
			if cell_info is None:
				cell_info = ''
			
			text_height = get_num_of_lines_in_multicell(pdf, cell_info, kwargs['cell_w']) * (25.4 * kwargs['font_size'] / 72 + 1)
			x, y = j * kwargs['cell_w'], i * kwargs['cell_h'] + (kwargs['cell_h']-text_height) / 2
			pdf.set_xy(x, y)
			pdf.multi_cell(txt=cell_info, border=0, align='C', w=kwargs['cell_w'], h=25.4 * kwargs['font_size'] / 72 + 1)
			pdf.rect(j * kwargs['cell_w'], i * kwargs['cell_h'], kwargs['cell_w'], kwargs['cell_h'])
		pdf.ln()
	return pdf

# def main():
# 	spotify_uri = sys.argv[1]
# 	auth = SpotifyOAuth(scope = 'user-library-read')
# 	spotify_client = spotipy.Spotify(auth_manager=auth)
# 	playlist = fetch_playlist(spotify_uri, spotify_client)
# 	playlist_cleaned = extract_track_artist(playlist)
# 	info_test = generate_card_info(playlist_cleaned, (3, 4), 4)
# 	options = {
# 		'font': 'comic_sans',
# 		'font_size': 18.0,
# 		'cell_w': 50,
# 		'cell_h': 40
# 	}
# 	generate_card(info_test, **options)

# if __name__ == '__main__':
# 	main()