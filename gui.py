import io
import os
import PySimpleGUI as sg
from PIL import Image, ImageTk
import numpy as np
import matplotlib as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GUI:
  def __init__(self):
      self.window = None
      self.fig_agg = None

  def set_theme(self, theme='DefaultNoMoreNagging'):
      sg.theme(theme)

  def init_layout(self):
      title_font_size = 20

      file_list_column = [
          [
              sg.Text("Image Folder", font=("Helvetica", title_font_size)),
          ],
          [
              sg.In(size=(24, 1), enable_events=True, key="-FOLDER-"),
              sg.FolderBrowse(),
          ],
          [
              sg.Listbox(values=[], enable_events=True, size=(30,40), key="-FILE LIST-")
          ]
      ]

      chunk_list_column = [
          [
              sg.Text("Image chunks", font=("Helvetica", title_font_size))
          ],
          [
              sg.Button("Delete Metadata")
          ],
          [
              sg.Listbox(values=[], enable_events=True, size=(20,40), key="-CHUNK LIST-")
          ]
      ]

      image_section = [
          [
              sg.Text("Image", font=("Helvetica", title_font_size)),
          ],
          [
              sg.Image(size=(40,40), key="-IMAGE-"),
          ]
      ]

      plot_section = [
          [
              sg.Text("Fourier Spectrum", font=("Helvetica", title_font_size)),
          ],
          [
              sg.Canvas(key="-FOURIER-"),
          ]
      ]

      output_section = [
          [
              sg.Text("Console", font=("Helvetica", title_font_size)),
          ],
          [
              sg.Output(size=(60,25), font=("Menlo"), key='-OUTPUT-'),
          ]
      ]

      raw_data_section = [
          [
              sg.Text("Raw data", font=("Helvetica", title_font_size)),
          ],
          [
              sg.MLine(key='-RAW-'+sg.WRITE_ONLY_KEY, font=("Menlo"), size=(60,25)),
          ]
      ]

      info_column = [
          [
              sg.Column(output_section),
              sg.VSeperator(),
              sg.Column(raw_data_section),
          ],
          [
              sg.HSeparator()
          ],
          [
              sg.Column(image_section),
              sg.VSeperator(),
              sg.Column(plot_section),
          ],
      ]

      layout = [
          [
              sg.Column(file_list_column),
              sg.VSeperator(),
              sg.Column(chunk_list_column),
              sg.VSeperator(),
              sg.Column(info_column),
          ]
      ]

      self.window = sg.Window("Image Viewer", layout, font=("Helvetica", 14))
    
  def fill_image_list(self, values):
    folder = values["-FOLDER-"]
    try:
      file_list = os.listdir(folder)
    except:
      file_list = []
    fnames = [
      f
      for f in file_list
      if os.path.isfile(os.path.join(folder, f))
      and f.lower().endswith((".png"))
    ]
    self.window["-FILE LIST-"].update(fnames)

  def fill_chunk_list(self, img):
    chunk_names = []
    for chunk in img.chunks:
      chunk_names.append(chunk.name)
    self.window["-CHUNK LIST-"].update(chunk_names)

  def print_chunk_named(self, name, img):
    img.print_chunk_named(name)

  def print_raw_output(self, name, img):
    for chunk in img.chunks:
      if chunk.name == name:
        data = img.data[chunk.start:chunk.start + 8 + chunk.datasize + 4]
        self.window['-RAW-'+sg.WRITE_ONLY_KEY].print(pretty(data, 20), "\n\n")

  def display_image(self, filepath):
    try:
      self.window["-IMAGE-"].update(data=self.get_img_data(filepath))
    except:
      pass

  def display_spectrum(self):
    if self.fig_agg is not None:
      self.delete_fig_agg(self.fig_agg)
    fig = self.make_fig()
    self.fig_agg = self.draw_figure(self.window["-FOURIER-"].TKCanvas, fig)

  def get_img_data(self, filename, resize=(500, 500)):
    image = Image.open(filename)
    width, height = image.size
    if resize:
      new_width, new_height = resize
      scale = min(new_height/height, new_width/width)
      image = image.resize((int(width*scale), int(height*scale)), Image.ANTIALIAS)
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    del image
    return bio.getvalue()

  def draw_figure(self, canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg

  def make_fig(self):
    fig = plt.figure.Figure(figsize=(5, 4), dpi=100)
    t = np.arange(0, 3, .01)
    fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
    return fig

  def delete_fig_agg(self,fig_agg):
    fig_agg.get_tk_widget().forget()

  def clear_consoles(self):
    self.window["-OUTPUT-"].update("")
    self.window['-RAW-'+sg.WRITE_ONLY_KEY].update("")


def pretty(bytes, linewidth):
  i = 1
  text = ""
  for byte in bytes:
    if i % linewidth == 0:
      text += '{:02X}\n'.format(byte)
    else:
      text += '{:02X} '.format(byte)
    i += 1
  return text
