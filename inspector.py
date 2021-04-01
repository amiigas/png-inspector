import os.path

import matplotlib as plt
import PySimpleGUI as sg

from image import PNG_Image
from gui import GUI


def run_main_gui_loop(gui):
  plt.use("TkAgg")
  while True:
    event, values = gui.window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
      break
    if event == "-FOLDER-":
      gui.fill_image_list(values)
    elif event == "-FILE LIST-":
      gui.clear_consoles()
      filepath = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
      try:
        img = PNG_Image(filepath)
        img.set_raw_data()
        img.is_signature_correct()
        img.index_chunks()
      except:
        continue
      gui.fill_chunk_list(img)
      gui.display_image(filepath)
      gui.display_spectrum(filepath)
    elif event == "-CHUNK LIST-":
      gui.clear_consoles()
      chunk_name = values["-CHUNK LIST-"][0]
      gui.print_chunk_named(chunk_name, img)
      gui.print_raw_output(chunk_name, img)

def main():
  gui = GUI()
  gui.set_theme()
  gui.init_layout()
  run_main_gui_loop(gui)
  gui.window.close()

if __name__== "__main__":
  main()