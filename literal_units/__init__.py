import itertools
import tokenize
from io import StringIO
from pegen.tokenizer import Tokenizer
import token
import pint
from typing import Iterator
from .parser import GeneratedParser
from pprint import pprint

ureg = pint.UnitRegistry(auto_reduce_dimensions=True)

def Quantity(value, units):
  return ureg.Quantity(value, units)

VERBOSE = False

def generate_tokens(code: str):
    file = StringIO(code)
    return tokenize.generate_tokens(file.readline)

def parse(code: str):
    tokens = generate_tokens(code)
    tokenizer = Tokenizer(tokens, verbose=VERBOSE)
    parser = GeneratedParser(tokenizer, verbose=VERBOSE)
    tree = parser.start()
    if not tree:
      err = parser.make_syntax_error("<input>")
      raise err
    return tree

def leading_whitespace(prev, node):
  if prev is None:
    return ''
  else:
    last_row, last_col = prev.end
    row, col = node.start
    if row != last_row:
      last_col = 0
    return ' ' * (col - last_col)

def untokenize(tokens: Iterator[tokenize.TokenInfo]) -> str:
  def untokenize_iter(tokens) -> Iterator[str]:
    last_token = None
    for t in tokens:
      whitespace = leading_whitespace(last_token, t)
      last_token = t
      if whitespace:
        yield whitespace
      yield t.string
  return "".join(untokenize_iter(tokens))

"""
Transform the AST returned by parse.GeneratedParser into a sequence of tokens.
"""
def transform_ast(node):
  if isinstance(node, list):
    for i in node:
      for tok in transform_ast(i):
        yield tok
  elif isinstance(node, tokenize.TokenInfo):
    yield node
  elif isinstance(node, tuple) and node[0] == 'unit_atom':
    value_tok = list(transform_ast(node[1]))
    units_tok = list(transform_ast(node[2]))

    start = value_tok[0].start
    end = units_tok[-1].end

    expr = 'literal_units.Quantity({}, "{}")'.format(
      untokenize(value_tok),
      untokenize(units_tok),
    )
    # kind of cheating, but makes untokenize simpler
    yield tokenize.TokenInfo(token.COMMENT, expr, start, end, None)
  elif node is None:
    # not sure what this represents
    pass
  else:
    raise ValueError('Unknown tree type: {}'.format(node))

def transform(code: str) -> str:
  tree = parse(code)
  return untokenize(transform_ast(tree))


def hook_ipython():
  import IPython
  ip = IPython.get_ipython()
  if hasattr(ip, 'input_transformers_cleanup'):
    # TODO
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

