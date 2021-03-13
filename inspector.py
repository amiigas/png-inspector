from PIL import Image as PILImage
from PIL import ImageCms as PILImageCms
import zlib
import io
import lookup_tables as lt


class Image:
  def __init__(self):
    self.chunks = []

  def set_raw_data(self, filepath):
    try:
      f = open(filepath, "rb")
      self.data = bytearray(f.read())
      f.close()
      return True
    except IOError as e:
      print(e)
      return False

  def is_signature_correct(self):
    png_signature = [137, 80, 78, 71, 13, 10, 26, 10]
    for i in range(0,8):
      if not self.data[i] == png_signature[i]:
        print("Bad png file signature.")
        return False
    print("Correct png file signature.")
    return True

  def index_chunks(self):
    print("Indexing all chunks.")
    start = 8
    while start < len(self.data):
      chunk = self.get_chunk_at(start)
      self.chunks.append(chunk)
      start = start + 8 + chunk.datasize + 4
    print("Found", len(self.chunks), "chunks.\n")

  def get_chunk_at(self, start):
    datasize = int.from_bytes(self.data[start:start+4], byteorder="big", signed=False)
    name = ""
    for offset in range(4,8):
      name += chr(self.data[start + offset])
    return Chunk(start, name, datasize)

  def get_chunk_data(self, start, datasize):
    return self.data[start+8:start+8+datasize]

  def print_chunk_named(self, name):
    if name == "IHDR":
      self.print_IHDR_chunk()
    elif name == "PLTE":
      self.print_PLTE_chunk()
    elif name == "IDAT":
      self.print_IDAT_chunks()
    elif name == "IEND":
      self.print_IEND_chunk()
    elif name == "iCCP":
      self.print_iCCP_chunk()
    elif name == "tRNS":
      self.print_tRNS_chunk()

  def print_critical_chunks(self):
    self.print_IHDR_chunk()
    self.print_PLTE_chunk()
    self.print_IDAT_chunks()
    self.print_IEND_chunk()

  def print_IHDR_chunk(self):
      for chunk in self.chunks:
        if chunk.name == "IHDR":
          chunk_data = self.get_chunk_data(chunk.start, chunk.datasize)
          width = int.from_bytes(chunk_data[0:4], byteorder="big", signed=False)
          height = int.from_bytes(chunk_data[4:8], byteorder="big", signed=False)
          bit_depth = chunk_data[8]
          color_type = chunk_data[9]
          text = '{0:16}{1:<}\n'.format("chunk name:", chunk.name)
          text += '{0:16}{1:<}\n'.format("width [px]:", width)
          text += '{0:16}{1:<}\n'.format("height [px]:", height)
          text += '{0:16}{1:<}\n'.format("bit_depth:", bit_depth)
          text += '{0:16}{1:<8}{2}\n'.format("color_type:", color_type, lt.ihdr_color_type[color_type])
          print(text)

  def print_PLTE_chunk(self):
    for chunk in self.chunks:
      if chunk.name == "PLTE":
        chunk_data = self.get_chunk_data(chunk.start, chunk.datasize)
        palette_size = chunk.datasize//3
        text = '{0:16}{1}\n'.format("chunk name:", chunk.name)
        text += '{0:8} | {1:>3} {2:>3} {3:>3}\n'.format("color:", "R", "G", "B")
        text += '{0}'.format("--------------------")
        print(text)
        for color in range(palette_size):
          red = chunk_data[color*3]
          green = chunk_data[color*3+1]
          blue = chunk_data[color*3+2]
          print('{0:<8} | {1:3} {2:3} {3:3}'.format(color, red, green, blue))
        print("")

  def print_IDAT_chunks(self):
    for chunk in self.chunks:
      if chunk.name == "IDAT":
        print(chunk)

  def print_IEND_chunk(self):
    for chunk in self.chunks:
      if chunk.name == "IEND":
        print(chunk)

  def print_iCCP_chunk(self):
    for chunk in self.chunks:
      if chunk.name == "iCCP":
        chunk_data = self.get_chunk_data(chunk.start, chunk.datasize)
        profile_name = []
        for i in chunk_data:
          if not i == 0x00:
            profile_name.append(i)
          else:
            break
        profile_name = "".join(list(map(chr, profile_name)))
        compression_type = chunk_data[len(profile_name)+1]
        compressed_icc_profile = chunk_data[len(profile_name)+2:]
        icc_profile = zlib.decompress(compressed_icc_profile)
        f_stream = io.BytesIO(icc_profile)
        profile = PILImageCms.ImageCmsProfile(f_stream)
        text = '{0:16}{1:<}\n'.format("chunk name:", chunk.name)
        text += '{0:16}{1:<}\n'.format("profile name:", profile_name)
        text += '{0:16}{1:<}\n'.format("compression:", compression_type)
        text += '{0:16}{1:}\n'.format("creation date:", profile.profile.creation_date)
        text += '{0:16}{1:<}\n'.format("version:", profile.profile.version)
        text += '{0:16}{1:<}\n'.format("color space:", profile.profile.xcolor_space)
        text += '{0:16}{1:<}\n'.format("device class:", profile.profile.device_class)
        text += '{0:16}{1:<}\n'.format("copyright:", profile.profile.copyright)
        text += '{0:16}{1:<}\n'.format("description:", profile.profile.profile_description)
        print(text)

  def print_tRNS_chunk(self):
    for chunk in self.chunks:
        if chunk.name == "tRNS":
          chunk_data = self.get_chunk_data(chunk.start, chunk.datasize)
          color_type = self.get_color_type()
          print('{0:16}{1:<}\n'.format("chunk name:", chunk.name))
          if color_type == 0:
            alpha = int.from_bytes(chunk_data, byteorder="big", signed=False)
            print('{0:16}{1:<}'.format("alpha:", alpha))
          elif color_type == 2:
            red = int.from_bytes(chunk_data[0:2], byteorder="big", signed=False)
            green = int.from_bytes(chunk_data[2:4], byteorder="big", signed=False)
            blue = int.from_bytes(chunk_data[4:6], byteorder="big", signed=False)
            print('{0:16}{1:3} {2:3} {3:3}'.format("alpha:", red, green, blue))
          elif color_type == 3:
            text += '{0:8} | {1:<}\n'.format("index:", "alpha [0-255]")
            text += '{0}'.format("--------------------")
            print(text)
            for index, alpha in enumerate(chunk_data):
              print('{0:<8} | {1:<}'.format(index, alpha))
          print("")

  def get_color_type(self):
    for chunk in self.chunks:
        if chunk.name == "IHDR":
          chunk_data = self.data[chunk.start+8:chunk.start+8+chunk.datasize]
          return chunk_data[9]

  def print_all_chunks(self):
    for chunk in self.chunks:
      print(chunk)


class Chunk:
  def __init__(self, start, name, datasize):
    self.start = start
    self.name = name
    self.datasize = datasize

  def __str__(self):
    text = '{0:16}{1}\n'.format("chunk name:", self.name)
    text += '{0:16}{1}\n'.format("starting index:", self.start)
    text += '{0:16}{1}\n'.format("size of data:", self.datasize)
    return text


def display_greetings():
  print("\nWelcome to the PNG Inspector!")

def menu():
  text = "========== MENU ==========\n"
  text += "1 - Display image\n"
  text += "2 - Print chunk list\n"
  text += "3 - Print critical chunks\n"
  # text += "4 - Print ancillary chunks\n"
  text += "5 - Print specific chunk\n"
  # text += "6 - Remove ancillary chunks\n"
  text += "q - Exit\n"
  text += "Your choice: "
  return text

def pretty_print(bytes, linewidth):
  i = 1
  for byte in bytes:
    if i % linewidth == 0:
      print('{:02X} '.format(byte))
    else:
      print('{:02X} '.format(byte), end="")
    i += 1
  print("")

def display_image(filepath):
  img = PILImage.open(filepath)
  img.show()

def query_filename():
  filepath = input("Enter png image file path. ('q' to quit): ")
  if filepath == "q":
    exit()
  else:
    inspect(filepath)

def inspect(filepath):
  img = Image()
  if img.set_raw_data(filepath):
    if img.is_signature_correct():
      img.index_chunks()
      option = ""
      while option != "q":
        if option == "1":
          display_image(filepath)
        elif option == "2":
          img.print_all_chunks()
        elif option == "3":
          img.print_critical_chunks()
        elif option == "5":
          chunk_name = input("Enter name of chunk to print: ")
          print("")
          img.print_chunk_named(chunk_name)
        option = input(menu())
        print("")

def main():
  display_greetings()
  while True:
    query_filename()


if __name__== "__main__":
  main()