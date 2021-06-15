import zlib
import binascii

import numpy as np
from PIL import Image

import myrsa
import rsa
from chunk import Chunk
import lookup_tables as lt


class PNG_Image:
  def __init__(self, filepath):
    self.filepath = filepath
    self.chunks = []
    self.colors = []
    self.set_raw_data()
    if self.is_signature_correct():
      self.index_chunks()

  def set_raw_data(self):
    try:
      f = open(self.filepath, "rb")
      self.data = bytearray(f.read())
      f.close()
      return True
    except IOError as e:
      print(e)
      return False

  def save(self, new_filepath=None):
    fp = new_filepath if new_filepath else self.filepath
    with open(fp, "wb") as file:
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

  def delete_chunks_named(self, name):
    for chunk in self.chunks:
        if chunk.name == name:
          self.delete_chunk(chunk)
          self.delete_chunks_named(name)

  def insert_chunk(self, index, name, data):
    # try:
      size = int.to_bytes(len(data),4, byteorder='big', signed=False)
      uni_name = bytes([ord(c) for c in name])
      crc = int.to_bytes(binascii.crc32(uni_name + data), 4, byteorder='big', signed=False)
      chunk = [int(x) for x in size + uni_name + data + crc]
      preceding_chunk = self.chunks[index-1]
      start = preceding_chunk.start+8+preceding_chunk.datasize+4
      self.data = np.insert(self.data, start, chunk)
      print(f"Chunk {name} inserted successfully at {index}.")
      self.index_chunks()
    # except:
    #   print(f"Could not insert chunk {name} at index {index}")

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
        colors = []
        for color in range(palette_size):
          red = chunk_data[color*3]
          green = chunk_data[color*3+1]
          blue = chunk_data[color*3+2]
          colors.append((red, green, blue))
        self.set_colors(colors)
        text = ""
        for i, color in enumerate(colors):
          text += '{0:<8} | {1:3} {2:3} {3:3}\n'.format(i, color[0], color[1], color[2])
        print(text)

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

  def set_colors(self, colors):
    self.colors = colors

  def get_IDAT_data(self):
    result = bytearray()
    for chunk in self.chunks:
        if chunk.name == "IDAT":
          result.extend(self.get_chunk_data(chunk.start, chunk.datasize))
    return result

  def get_img_size(self):
    img = Image.open(self.filepath)
    return img.size

  def encrypt(self, public, bits=1024, mode='ECB', iv=0):
    compressed_data = self.get_IDAT_data()
    data = bytearray(zlib.decompress(compressed_data))

    block_length = bits // 8 - 1
    n_blocks = len(data) // block_length + 1
    
    encryptred_data = bytearray()

    if mode == 'ECB':
      for i in range(n_blocks):
        ### our imp
        c = myrsa.encrypt(int.from_bytes(data[i*block_length:i*block_length+block_length], byteorder='big', signed=False), public)
        encryptred_data.extend(int.to_bytes(c, bits//8, 'big', signed=False))
        ### rsa module
        # c = rsa.encrypt(data[i*block_length:i*block_length+block_length], public)
        # encryptred_data.extend(c)
    elif mode == 'CBC':
      prev_c = iv
      for i in range(n_blocks):
        plain = int.from_bytes(data[i*block_length:i*block_length+block_length], byteorder='big', signed=False)
        plain_xored = plain ^ prev_c
        c = myrsa.encrypt(plain_xored, public)
        c = int.to_bytes(c, bits//8, 'big', signed=False)
        encryptred_data.extend(c)
        prev_c = int.from_bytes(c[1:], byteorder='big', signed=False)

    compressed_encrypted_data = zlib.compress(bytes(encryptred_data))
    self.delete_chunks_named("IDAT")

    chunks = len(compressed_encrypted_data) // 32000 + 1
    for i in range(chunks):
      d = compressed_encrypted_data[i*32000:(i+1)*32000]
      self.insert_chunk(-1, "IDAT", d)

  def decrypt(self, private, bits=1024, mode='ECB', iv=0):
    compressed_data = self.get_IDAT_data()
    data = bytearray(zlib.decompress(compressed_data))

    block_length = bits // 8
    n_blocks = len(data) // block_length + 1

    decryptred_data = bytearray()

    if mode == 'ECB':
      for i in range(n_blocks):
        ### our imp
        c = myrsa.decrypt(int.from_bytes(data[i*block_length:i*block_length+block_length], byteorder='big', signed=False), private)
        decryptred_data.extend(int.to_bytes(c, bits//8-1, 'big', signed=False))
        ### rsa module
        # c = rsa.decrypt(data[i*block_length:i*block_length+block_length], private)
        # decryptred_data.extend(c)
    elif mode == 'CBC':
      prev_c = iv
      for i in range(n_blocks):
        c = data[i*block_length:i*block_length+block_length]
        plain_xored = myrsa.decrypt(int.from_bytes(c, byteorder='big', signed=False), private)
        plain = plain_xored ^ prev_c
        decryptred_data.extend(int.to_bytes(plain, bits//8-1, byteorder='big', signed=False))
        prev_c = int.from_bytes(c[1:], byteorder='big', signed=False)

    compressed_decrypted_data = zlib.compress(bytes(decryptred_data))

    self.delete_chunks_named("IDAT")

    chunks = len(compressed_decrypted_data) // 32000 + 1
    for i in range(chunks):
      d = compressed_decrypted_data[i*32000:(i+1)*32000]
      self.insert_chunk(-1, "IDAT", d)
