from image import PNG_Image


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

def query_filename():
  filepath = input("Enter png image file path. ('q' to quit): ")
  if filepath == "q":
    exit()
  else:
    inspect(filepath)

def inspect(filepath):
  img = PNG_Image(filepath)
  if img.set_raw_data():
    if img.is_signature_correct():
      img.index_chunks()
      option = ""
      while option != "q":
        if option == "1":
          img.display()
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