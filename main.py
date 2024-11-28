import customtkinter
import tkinter
import tkinter.messagebox
import os
from CTkColorPicker import *
from CTkMessagebox import CTkMessagebox
from bingo_generator import *
from PIL import ImageTk, Image
from pdf2image import convert_from_path


class Generator(customtkinter.CTk):

	def __init__(self, title: str, geometry: str):
		super().__init__()

		# Set configuration
		self.title(title)
		self.geometry(geometry)
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self.font_color = (0, 0, 0)
		self.font_path = '/usr/share/fonts/truetype/hack/Hack-Regular.ttf'
	
		# Create display frame
		self.display_frame = customtkinter.CTkFrame(self, width=500)
		self.display_frame.grid(row=0, column=0, sticky='nw', padx=(10, 10), pady=(10, 10))
		
		# Create display frame elements
		self.display_title = customtkinter.CTkLabel(self.display_frame, text='Card Preview', font=customtkinter.CTkFont(size=20, weight="bold"))
		self.display_title.pack(pady=(10, 10))
		template = customtkinter.CTkImage(Image.open('template.png'), size=(840, 396))
		self.display_image = customtkinter.CTkLabel(self.display_frame, text='', image=template)
		self.display_image.pack(padx=(20, 20))
		self.generate_button = customtkinter.CTkButton(self.display_frame, text='Generate preview' ,command=self.generate_bingo_card)
		self.generate_button.pack(pady=(10, 10))

		# Create config frame
		self.config_frame = customtkinter.CTkFrame(self, width=420)
		self.config_frame.grid(column=1, row=0, sticky='ne', padx=(10, 10), pady=(10, 10))
		self.config_frame.grid_columnconfigure(2)

		# Create config frame elements
		self.spotify_link = customtkinter.CTkEntry(self.config_frame, width=400, placeholder_text='Link to Spotify playlist...')
		self.spotify_link.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(20, 10))
		self.spotify_button = customtkinter.CTkButton(self.config_frame, text='Import from Spotify' ,command=self.generate_list_spotify)
		self.spotify_button.grid(row=1, column=0, columnspan=1, pady=(10, 10))
		self.artist_check = customtkinter.CTkSwitch(self.config_frame, text='Include artists')
		self.artist_check.grid(row=1, column=1, columnspan=1, pady=(10, 10))
		self.card_items = customtkinter.CTkTextbox(self.config_frame, width=400, height=300)
		self.card_items.grid(row=2, column=0, columnspan=2, pady=(10, 10))
		self.font_select_button = customtkinter.CTkButton(self.config_frame, text='Select font', command=self.select_font)
		self.font_select_button.grid(row=4, column=0, columnspan=1, padx=(10, 10))
		self.font_color_picker = customtkinter.CTkButton(self.config_frame, text='Select font colour', command=self.set_font_color)
		self.font_color_picker.grid(row=4, column=1, pady=(10, 10))
		self.font_size_slider = customtkinter.CTkSlider(self.config_frame, from_=1, to=16, number_of_steps=15, command=self.set_font_size)
		self.font_size_slider.grid(row=5, column=0, columnspan=1, pady=(10, 10))
		self.font_size_display = customtkinter.CTkLabel(self.config_frame, text='_')
		self.font_size_display.grid(row=5, column=1, columnspan=1)
		self.generate_sheet_button = customtkinter.CTkButton(self.config_frame, text='Generate sheet', command=self.generate_bingo_sheet, font=customtkinter.CTkFont(size=20, weight="bold"), width=280, height=56)
		self.generate_sheet_button.grid(row=6, columnspan=2, pady=(20, 20))
		
	# Define functions for buttons
	def generate_list_spotify(self):
		spotify_uri = self.spotify_link.get()
		auth = SpotifyOAuth(scope = 'user-library-read')
		spotify_client = spotipy.Spotify(auth_manager=auth)
		playlist = fetch_playlist(spotify_uri, spotify_client)
		playlist_cleaned = extract_track_artist(playlist, self.artist_check.get())
		self.card_items.delete('0.0', customtkinter.END)
		self.card_items.insert('0.0','\n'.join(playlist_cleaned))
	
	def generate_bingo_card(self):
		info = generate_card_info(self.card_items.get(0.0, customtkinter.END).split('\n')[:-1], (3, 4), 4)
		pdf = generate_card_preview(info, self.font_path, self.font_size_slider.get(), self.font_color, 4, 3, 'template.png')
		pdf.output('temp.pdf', 'F')
		pdf_image = convert_from_path('temp.pdf')[0]
		os.remove('temp.pdf')
		
		image = customtkinter.CTkImage(pdf_image, size=(840, 396))
		self.display_image.configure(image=image)
		self.display_image.image=image
	
	def set_font_size(self, value):
		self.font_size = value
		self.font_size_display.configure(text=value)
		
	def select_font(self):
		filename = customtkinter.filedialog.askopenfilename()
		self.font_path = filename

	def set_font_color(self):
		pick_color = AskColor()
		hex_color = pick_color.get()[1:]
		self.font_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
	
	def generate_bingo_sheet(self):
		dialog = customtkinter.CTkInputDialog(text='Enter number of sheets', title=self.title())
		try:
			n_pages = int(dialog.get_input())
			assert n_pages > 0
		except (ValueError, AssertionError):
			CTkMessagebox(title='Error', message='Number of sheets must be a positive whole number!', icon='cancel')

		info = []
		for _ in range(3 * n_pages):
			info.append(generate_card_info(self.card_items.get(0.0, customtkinter.END).split('\n')[:-1], (3, 4), 4))

		generate_multi_sheets(n_pages, info, self.font_path, self.font_size_slider.get(), self.font_color, 4, 3, 'template.png')

def main():
	app = Generator('Bingo Generator', '1200x800')
	app.mainloop()

if __name__ == '__main__':
	main()