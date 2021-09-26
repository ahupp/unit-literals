import tokenize
from io import StringIO
from pegen.tokenizer import Tokenizer
import token
import pint
from typing import Generator, List, Tuple, Callable, Iterable
from .parser import GeneratedParser

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

def Quantity(value, units):
  return ureg.Quantity(value, units)

VERBOSE = False

def parse(code: str):
    file = StringIO(code)
    tokengen = tokenize.generate_tokens(file.readline)
    tokenizer = Tokenizer(tokengen, verbose=VERBOSE)
    parser = GeneratedParser(tokenizer, verbose=VERBOSE)
    return parser.start()

def hook_ipython():
  import IPython
  ip = IPython.get_ipython()
  if hasattr(ip, 'input_transformers_cleanup'):
    ip.input_transformers_cleanup.append(transform_lines)
  else:
    # support IPython 5, which is used in Google Colab
    # https://ipython.org/ipython-doc/3/config/inputtransforms.html
    from IPython.core.inputtransformer import StatelessInputTransformer

    @StatelessInputTransformer.wrap
    def fn(line):
      return transform(line)

    ip.input_splitter.logical_line_transforms.append(fn())
    ip.input_transformer_manager.logical_line_transforms.append(fn())

