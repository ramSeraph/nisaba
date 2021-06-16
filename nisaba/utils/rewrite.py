# Copyright 2021 Nisaba Authors.
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

import pynini
from pynini.lib import byte


def Rewrite(rule: pynini.FstLike,
            left: pynini.FstLike = "",
            right: pynini.FstLike = "",
            sigma: pynini.Fst = byte.BYTE) -> pynini.Fst:
  return pynini.optimize(pynini.cdrewrite(rule, left, right, sigma.star))
