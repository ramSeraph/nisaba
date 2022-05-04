# Copyright 2022 Nisaba Authors.
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

"""CDRewrite related utility functions."""

from typing import Iterable

import pynini
from pynini.lib import byte


def Rewrite(rule: pynini.FstLike,
            left: pynini.FstLike = "",
            right: pynini.FstLike = "",
            sigma: pynini.Fst = byte.BYTE) -> pynini.Fst:
  return pynini.optimize(pynini.cdrewrite(rule, left, right, sigma.star))


def ComposeFsts(fsts: Iterable[pynini.Fst]) -> pynini.Fst:
  """Composes the given FSTs together, ordered by a heuristics for speed."""
  fsts = list(fsts)
  if len(fsts) < 2:
    return fsts[0]

  # Heuristics for speed:
  # Adjacent FSTs with minimum number of total states are composed first.
  # After that first composition, we recurse on that shorter list of FSTs.
  num_states = [fst.num_states() for fst in fsts]
  num_states_sum = [sum(pair) for pair in zip(num_states, num_states[1:])]
  i = num_states_sum.index(min(num_states_sum))
  composed = (fsts[i] @ fsts[i+1]).optimize()
  return ComposeFsts(fsts[:i] + [composed] + fsts[i+2:])


def RewriteAndComposeFsts(fsts: Iterable[pynini.Fst],
                          sigma: pynini.Fst) -> pynini.Fst:
  composed = sigma.star
  for fst in fsts:
    composed @= Rewrite(fst, sigma=sigma)
  return composed.optimize()
