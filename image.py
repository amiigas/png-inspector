import zlib
from chunk import Chunk
import lookup_tables as lt
import numpy as np


class PNG_Image:
  def __init__(self, filepath):
    self.filepath = filepath
    self.chunks = []

  def set_raw_data(self):
    try:
      f = open(self.filepath, "rb")
      self.data = bytearray(f.read())
      f.close()
      return True
    except IOError as e:
      print(e)
      return False

  def save(self):
    with open(self.filepath, "wb") as file:
      try:
        file.write(self.data)
        print("Image saved successfully.")
      except:
        print("Saving image failed.")

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
    self.chunks.clear()
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
  
  def get_chunk_by_name(self, name):
    for chunk in self.chunks:
        if chunk.name == name:
          return chunk

  def get_chunk_data(self, start, datasize):
    return self.data[start+8:start+8+datasize]

  def delete_metadata(self):
    to_delete = []
    for chunk in self.chunks:
      if ord(chunk.name[0]) > 96:
        to_delete.append(chunk.name)
    for chunk_name in to_delete:
      chunk = self.get_chunk_by_name(chunk_name)
      self.delete_chunk(chunk)

  def delete_chunk(self, chunk):
    start = chunk.start
    end = chunk.start+4+4+chunk.datasize+4
    try:
      self.data = np.delete(self.data, np.s_[start:end])
      print("Chunk", chunk.name, "deleted successfully.")
    except:
      print("Could not delete chunk", chunk.name)

    self.index_chunks()

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
    elif name == "iTXt":
      self.print_iTXt_chunk()
    else:
      for chunk in self.chunks:
        if chunk.name == name:
          print(chunk)

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
        compressed_icc_profile = chunk_data[len(profile_name)+2:]
        icc_profile = zlib.decompress(compressed_icc_profile)

        profile_size = int.from_bytes(icc_profile[0:4], byteorder="big", signed=False)
        cmm_type = icc_profile[4:8].decode('utf-8')
        v = list(hex(int.from_bytes(icc_profile[8:12], byteorder="big", signed=False)))
        version = f"{v[2]}.{v[3]}"
        device_class = icc_profile[12:16].decode('utf-8')
        color_space = icc_profile[16:20].decode('utf-8')
        connection_space = icc_profile[20:24].decode('utf-8')
        year = int.from_bytes(icc_profile[24:26], byteorder="big", signed=False)
        month = int.from_bytes(icc_profile[26:28], byteorder="big", signed=False)
        day = int.from_bytes(icc_profile[28:30], byteorder="big", signed=False)
        hour = int.from_bytes(icc_profile[30:32], byteorder="big", signed=False)
        minute = int.from_bytes(icc_profile[32:34], byteorder="big", signed=False)
        second = int.from_bytes(icc_profile[34:36], byteorder="big", signed=False)
        date = f"{day:02}-{month:02}-{year}"
        time = f"{hour:02}:{minute:02}:{second:02}"
        acsp = icc_profile[36:40].decode('utf-8')
        target_platform = icc_profile[40:44].decode('utf-8')
        manufacturer = icc_profile[48:52].decode('utf-8')
        device_model = icc_profile[52:56].decode('utf-8')

        text = '{0:16}{1:<}\n'.format("chunk name:", chunk.name)
        text += '{0:16}{1:<}\n'.format("profile size:", profile_size)
        text += '{0:16}{1:<}\n'.format("CMM type:", cmm_type)
        text += '{0:16}{1:}\n'.format("version:", version)
        text += '{0:16}{1:<12}{2}\n'.format("device class:", device_class, lt.iccp_device_class[device_class])
        text += '{0:16}{1:<}\n'.format("color space:", color_space)
        text += '{0:16}{1:<}\n'.format("connect space:", connection_space)
        text += '{0:16}{1:<}\n'.format("date:", date)
        text += '{0:16}{1:<}\n'.format("time:", time)
        text += '{0:16}{1:<12}{2}\n'.format("signature:", acsp, "Correct" if acsp == 'acsp' else "Incorrect")
        text += '{0:16}{1:<12}{2}\n'.format("platform:", target_platform, lt.iccp_platform[target_platform])
        text += '{0:16}{1:<}\n'.format("manufacturer:", manufacturer)
        text += '{0:16}{1:<}\n'.format("device model:", device_model)
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
            text = '{0:8} | {1:<}\n'.format("index:", "alpha [0-255]")
            text += '{0}'.format("--------------------")
            print(text)
            for index, alpha in enumerate(chunk_data):
              print('{0:<8} | {1:<}'.format(index, alpha))
          print("")

  def print_iTXt_chunk(self):
    for chunk in self.chunks:
        if chunk.name == "iTXt":
          chunk_data = self.get_chunk_data(chunk.start, chunk.datasize)
          fragments = []
          data_fragment = []
          for i in chunk_data:
            if not i == 0x00:
              data_fragment.append(i)
            else:
              fragments.append("".join(list(map(chr, data_fragment))))
              data_fragment = []
          fragments.append("".join(list(map(chr, data_fragment))))
          text = '{0:24}{1:<}\n'.format("chunk name:", chunk.name)
          text = '{0:24}{1:<}\n'.format("keyword:", fragments[0])
          text += '{0:24}{1:<}\n'.format("compression flag:", "0" if fragments[1] == '' else fragments[1])
          text += '{0:24}{1:<}\n'.format("compression method:", "0" if fragments[2] == '' else fragments[2])
          text += '{0:24}{1:<}\n'.format("language tag:", fragments[3])
          text += '{0:24}{1:<}\n'.format("translated keyword:", fragments[4])
          for line in fragments[5].split("\n"):
            text += '{0:24}{1:<}\n'.format("", line)
          print(text)
          
  def get_color_type(self):
    for chunk in self.chunks:
        if chunk.name == "IHDR":
          chunk_data = self.data[chunk.start+8:chunk.start+8+chunk.datasize]
          return chunk_data[9]

  def print_all_chunks(self):
    for chunk in self.chunks:
      print(chunk)
