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
