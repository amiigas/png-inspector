from PIL import Image as PILImage

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


  def print_critical_chunks(self):
    self.print_IHDR_chunk()
    # self.print_PLTE_chunk()
    # self.print_IDAT_chunks()
    # self.print_IEND_chunk()


  def print_IHDR_chunk(self):
      for chunk in self.chunks:
        if chunk.name == "IHDR":
          chunk_data = self.data[chunk.start+8:chunk.start+8+chunk.datasize]
          width = int.from_bytes(chunk_data[0:4], byteorder="big", signed=False)
          height = int.from_bytes(chunk_data[4:8], byteorder="big", signed=False)
          bit_depth = chunk_data[8]
          color_type = chunk_data[9]
          text = '{0:18}{1}\n'.format("chunk name:", chunk.name)
          text += '{0:18}{1}\n'.format("width [px]:", width)
          text += '{0:18}{1}\n'.format("height [px]:", height)
          text += '{0:18}{1}\n'.format("bit_depth:", bit_depth)
          text += '{0:18}{1}\n'.format("color_type:", color_type)
          print(text)


  def print_chunks(self):
    for chunk in self.chunks:
      print(chunk)


class Chunk:
  def __init__(self, start, name, datasize):
    self.start = start
    self.name = name
    self.datasize = datasize


  def __str__(self):
    text = '{0:18}{1}\n'.format("chunk name:", self.name)
    text += '{0:18}{1}\n'.format("starting index:", self.start)
    text += '{0:18}{1}\n'.format("size of data:", self.datasize)
    return text


def display_greetings():
  print("\nWelcome to the PNG Inspector!")


def menu():
  text = "======= MENU =======\n"
  text += "1 - Display image\n"
  text += "2 - Print chunk list\n"
  text += "3 - Print critical chunks\n"
  # text += "4 - Print ancillary chunks\n"
  # text += "5 - Print specific chunk\n"
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
          img.print_chunks()
        elif option == "3":
          img.print_critical_chunks()
        option = input(menu())
        print("")


def main():
  display_greetings()
  while True:
    query_filename()
  

if __name__== "__main__":
  main()