# Copyright 2023 Nisaba Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Shortcuts for detailed logs.

Since all calls to absl/logging is made from this file, the log messages
include the name and location of the caller of the logging function as prefix.

Examples:
type_op.py/is_none: returns False, detail: int_0
type_op.py/is_nothing: returns True, detail: Nothing_Unassigned
type_op.py/is_equal: type mismatch between Fst_a and Phon_a
type_op.py/enforce_list: from:dict_{'a': 5}
type_op.py/enforce_list: returns [5]
"""

import inspect
import pathlib
from absl import logging
import pynini as pyn


def _add_caller(message: str, callstack_index: int) -> str:
  """Adds the public log function's caller name and location to the message.

  Args:
    message: log message
    callstack_index: index of the caller of the public log function's frame
      in the stack. This index is tracked by incrementing it by the number of
      calls in each function in the call tree.
  Returns:
    Messages formatted as <filename>/<caller>: <message>

  """

  f = inspect.stack()[callstack_index][0]
  if not f: return message
  caller = f.f_code
  filename = pathlib.Path(caller.co_filename).name
  return '%s/%s: %s' % (filename, caller.co_name, message)


def _return_message(return_value: ..., message: str = '') -> str:
  return_message = 'returns %s' % text_of(return_value)
  if message: return_message += ', detail: ' + message
  return return_message


## Public functions

# Log functions


def dbg_message(
    message: str,
    callstack_index: int = 0
) -> None:
  if logging.level_debug():
    logging.debug(_add_caller(message, callstack_index + 2))


def dbg_return(
    return_value: ...,
    message: str = '',
    callstack_index: int = 0
) -> ...:
  if logging.level_debug():
    dbg_message(_return_message(return_value, message), callstack_index + 1)
  return return_value


def dbg_return_true(
    message: str = '',
    callstack_index: int = 0
) -> bool:
  return dbg_return(True, message, callstack_index + 1)


def dbg_return_false(
    message: str = '',
    callstack_index: int = 0
) -> bool:
  return dbg_return(False, message, callstack_index + 1)


# Functions that return simple and readable strings to identify the objects.


def class_of(obj: ...) -> str:
  return obj.__class__.__name__


def text_of(obj: ...) -> str:
  if hasattr(obj, 'text'):
    text = obj.text
  elif isinstance(obj, pyn.Fst):
    try:
      text = obj.string()
    except pyn.FstOpError:
      text = '<non_string_fst>'
  else: text = str(obj)
  return text if text else '<no_text>'


def texts_of(*args) -> str:
  return ' ,'.join([text_of(arg) for arg in args])


def alias_of(obj: ...) -> str:
  return obj.alias if hasattr(obj, 'alias') else text_of(obj)


def class_and_alias(obj: ...) -> str:
  return '%s_%s' % (class_of(obj), alias_of(obj))


def class_and_text(obj: ...) -> str:
  return '%s_%s' % (class_of(obj), text_of(obj))


def from_class_and_text(obj: ...) -> str:
  return 'from:%s' % class_and_text(obj)
