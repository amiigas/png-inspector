import io
import os
import PySimpleGUI as sg
from PIL import Image, ImageTk
import numpy as np
import matplotlib as plt
import matplotlib.pyplot as pyplt
import cv2
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
              sg.FolderBrowse(button_color=("black", "orange")),
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
              sg.Button("Delete Metadata", enable_events=True, disabled=True, key="-DELETE METADATA-", button_color=("black", "orange")),
              sg.Button("Delete Chunk", enable_events=True, disabled=True, key="-DELETE CHUNK-", button_color=("black", "orange"))
          ],
          [
              sg.Listbox(values=[], enable_events=True, size=(25,40), key="-CHUNK LIST-")
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

  def display_spectrum(self, filepath):
    if self.fig_agg is not None:
      self.delete_fig_agg(self.fig_agg)
    fig = self.make_fig(filepath)
    self.fig_agg = self.draw_figure(self.window["-FOURIER-"].TKCanvas, fig)

  def display_palette(self, colors):
    pyplt.ion()
    fig, ax = pyplt.subplots()
    for i in range(16):
      for j in range(16):
        try:
          r = colors[i*16+j][0]
          g = colors[i*16+j][1]
          b = colors[i*16+j][2]
          hex_color = f"#{r:02x}{g:02x}{b:02x}"
        except:
          hex_color = (0.0, 0.0, 0.0, 0.0)
        ax.broken_barh([(j*10, 10)], (i*10, 10), facecolors=hex_color)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

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

  def make_fig(self, filepath, resize=(500, 500)):
    fig = plt.figure.Figure(figsize=(5, 4))
    img = cv2.imread(filepath, 0)
    width, height = (img.shape[1], img.shape[0])
    new_width, new_height = resize
    scale = min(new_height/height, new_width/width)
    dimensions = (int(width*scale), int(height*scale))
    resized_img = cv2.resize(img, dimensions)
    fourier_img = np.fft.fftshift(np.fft.fft2(resized_img))
    fig.figimage(20*np.log(np.abs(fourier_img)), cmap="gray", resize=True)
    return fig

  def delete_fig_agg(self,fig_agg):
    fig_agg.get_tk_widget().forget()

  def clear_consoles(self):
    self.window["-OUTPUT-"].update("")
    self.window['-RAW-'+sg.WRITE_ONLY_KEY].update("")
  
  def set_buttons_state(self, chunk_name, filename):
    if filename:
      self.window["-DELETE METADATA-"].update(disabled=False)
    else:
      self.window["-DELETE METADATA-"].update(disabled=True)
    if chunk_name:
      self.window["-DELETE CHUNK-"].update(disabled=False)
    else:
      self.window["-DELETE CHUNK-"].update(disabled=True)


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
