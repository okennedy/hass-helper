import emoji

def is_emoji(c):
  return c in emoji.UNICODE_EMOJI

def split_emoji(c):
  if c in emoji.UNICODE_EMOJI:
    return (c, None)
  else:
    return (None, c)

def extract_emoji(str):
  emo, rest = zip(*[ split_emoji(c) for c in str ])
  emo  = [c for c in emo  if c is not None]
  rest = [c for c in rest if c is not None]
  return (emo, "".join(rest))

if __name__ == "__main__":
  test = u"This is a 🍩"
  print(test)
  for c in test:
    print("{}: {}".format(c, ord(c)))
  print(extract_emoji(test))
  print(extract_emoji(u"💒 in a 🍲"))
  icon, text = extract_emoji(u"Eat a tasty donut🍩")
  print("[{:x}]: {}".format(ord(icon[0]), text))