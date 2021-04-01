import os.path
from PySimpleGUI.PySimpleGUI import Window

import matplotlib as plt
import PySimpleGUI as sg

from image import PNG_Image
from gui import GUI


def run_main_gui_loop(gui):
  plt.use("TkAgg")
  img = None
  chunk_name = None

  while True:
    event, values = gui.window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
      break
    if event == "-FOLDER-":
      gui.fill_image_list(values)
    elif event == "-FILE LIST-":
      try:
        chunk_name = None
        filepath = os.path.join(values["-FOLDER-"], values["-FILE LIST-"][0])
        gui.clear_consoles()
        gui.set_buttons_state(chunk_name, filepath)
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
      try:
        chunk_name = values["-CHUNK LIST-"][0]
        gui.clear_consoles()
        gui.set_buttons_state(chunk_name, filepath)
        gui.print_chunk_named(chunk_name, img)
        gui.print_raw_output(chunk_name, img)
      except:
        continue
    elif event == "-DELETE METADATA-":
      print("cliked delete meta of", img.filepath)
      try:
        chunk_name = None
        gui.clear_consoles()
        gui.set_buttons_state(chunk_name, filepath)
        img.delete_metadata()
        gui.fill_chunk_list(img)
      except:
        continue
    elif event == "-DELETE CHUNK-":
      print("cliked delete chunk", chunk_name)


def main():
  gui = GUI()
  gui.set_theme()
  gui.init_layout()
  run_main_gui_loop(gui)
  gui.window.close()

if __name__== "__main__":
  main()