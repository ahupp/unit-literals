from . import parse

if __name__ == "__main__":
  tests = [
    "1",
    "1 * meter",
    "1 meter/s**2",
    "1 meter",
    "1 meter/s^2",
    "1 meter/s * 1 second",
    "2**4 meters",
    # TODO
    "x meters",
  ]
  for i in tests:
    print(i, "->", parse(i))

