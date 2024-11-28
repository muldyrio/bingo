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

def generate_card(card_info: list, pdf_object, font_size, ncol: int, nrow: int, template_path: str='template.png', page_y_offset: float=0) :
	try:
		pdf_object.image(template_path, x=0, y=page_y_offset, w=210, h=99, type='png')
	except FileNotFoundError:
		pass		
	
	# Bingo area is a 90x120mm box with top-left corner at (4.5mm, 85.5mm)
	offset_x, offset_y = 85.5, 4.5 + page_y_offset
	pdf_object.set_xy(offset_x, offset_y)
	cell_h = 90.0 / nrow
	cell_w = 120.0 / ncol

	# Print bingo words
	for i, row_info in enumerate(card_info):
		for j, cell_info in enumerate(row_info):
			text_height = get_num_of_lines_in_multicell(pdf_object, cell_info, cell_w) * (25.4 * font_size / 72 + 1)
			x, y = j * cell_w + offset_x, i * cell_h + (cell_h-text_height) / 2 + offset_y
			pdf_object.set_xy(x, y)
			pdf_object.multi_cell(txt=cell_info, border=0, align='C', w=cell_w, h=25.4 * font_size / 72 + 1)
	
	# Print bingo grid
	for i in range(1, nrow):
		pdf_object.line(offset_x, i * cell_h + offset_y, offset_x + 120, i * cell_h + offset_y)
	
	for j in range(1, ncol):
		pdf_object.line(j * cell_w + offset_x, offset_y, j * cell_w + offset_x, offset_y + 90)

	return pdf_object

def generate_card_preview(card_info: list, font_path: str, font_size: float, font_color: tuple, ncol: int, nrow: int, template_path='template.png') :
	# Setup PDF file
	pdf = FPDF(orientation = 'L', format = (99, 210))
	pdf.add_font('bingo_font', '', font_path, uni=True)
	pdf.set_font('bingo_font', '', font_size)
	pdf.set_text_color(*font_color)
	pdf.set_draw_color(*font_color)
	pdf.set_auto_page_break(False)
	pdf.set_margins(0, 0, 0)
	pdf.add_page()

	return generate_card(card_info, pdf, font_size, ncol, nrow)

def generate_sheet(card_info: list, pdf_object, font_size, ncol: int, nrow: int, template_path: str='template.png') :
	pdf_object.add_page()

	for i, card in enumerate(card_info):
		pdf_object = generate_card(card, pdf_object, font_size, ncol, nrow, template_path, page_y_offset=i*99)
	
	return pdf_object

def generate_multi_sheets(n_pages: int, card_info: list, font_path: str, font_size: float, font_color: tuple, ncol: int, nrow: int, template_path: str='template.png') -> None:
	# Setup PDF file
	pdf = FPDF(orientation = 'L', format = (297, 210))
	pdf.add_font('bingo_font', '', font_path, uni=True)
	pdf.set_font('bingo_font', '', font_size)
	pdf.set_text_color(*font_color)
	pdf.set_draw_color(*font_color)
	pdf.set_auto_page_break(False)
	pdf.set_margins(0, 0, 0)

	for i in range(n_pages):
		page_info = card_info[3*i:3*(i+1)]
		pdf = generate_sheet(page_info, pdf, font_size, ncol, nrow, template_path)
	
	pdf.output('generated_sheet.pdf', 'F')


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