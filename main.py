import customtkinter
import tkinter
import tkinter.messagebox
import os
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
	
		# Create display frame
		self.display_frame = customtkinter.CTkFrame(self, width=500)
		self.display_frame.grid(row=0, column=0, sticky='nw', padx=(5, 5))
		
		# Create display frame elements
		self.display_title = customtkinter.CTkLabel(self.display_frame, text='Card Preview', font=customtkinter.CTkFont(size=20, weight="bold"))
		self.display_title.pack()

		# Create config frame
		self.config_frame = customtkinter.CTkFrame(self, width=420)
		self.config_frame.grid(column=1, row=0, sticky='ne', padx=(10, 10), pady=(10, 10))
		self.config_frame.grid_columnconfigure(2)

		# Create display frame elements
		self.spotify_link = customtkinter.CTkEntry(self.config_frame, width=400, placeholder_text='Link to Spotify playlist...')
		self.spotify_link.grid(row=0, column=0, columnspan=2, padx=(10, 10), pady=(10, 10))
		self.spotify_button = customtkinter.CTkButton(self.config_frame, text='Generate' ,command=self.generate_list_spotify)
		self.spotify_button.grid(row=1, column=0, columnspan=1, pady=(10, 10))
		self.artist_check = customtkinter.CTkSwitch(self.config_frame, text='Include artists')
		self.artist_check.grid(row=1, column=1, columnspan=1, pady=(10, 10))
		self.card_items = customtkinter.CTkTextbox(self.config_frame, width=400, height=600)
		self.card_items.grid(row=2, column=0, columnspan=2, pady=(10, 10))
		self.generate_button = customtkinter.CTkButton(self.config_frame, text='Generate card' ,command=self.generate_bingo_card)
		self.generate_button.grid(row=3, column=0, columnspan=2, pady=(10, 10))
	
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
		options = {
			'font': 'comic_sans',
			'font_size': 18.0,
			'cell_w': 50,
			'cell_h': 40
		}
		pdf = generate_card(info, **options)
		pdf.output('temp.pdf', 'F')
		pdf_image = convert_from_path('temp.pdf')[0]
		#os.remove('temp.pdf')
		image = customtkinter.CTkImage(pdf_image)
		image_frame = customtkinter.CTkLabel(self.display_frame, image=image, height=200, width=200, text='')
		image_frame.pack()

def main():
	app = Generator('test', '1200x800')
	app.mainloop()

if __name__ == '__main__':
	main()