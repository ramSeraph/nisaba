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

# Lint as: python3
"""End-to-end natural transliteration for Hindi."""

import pynini as p
from pynini.export import multi_grm

import nisaba.scripts.brahmic.natural_translit.iso2typ as iso
import nisaba.scripts.brahmic.natural_translit.txn2nat as txn
import nisaba.scripts.brahmic.natural_translit.typ2txn as typ


def generator_main(exporter_map: multi_grm.ExporterMapping):
  """Generates FAR for natural transliteration."""
  for token_type in ('byte', 'utf8'):
    with p.default_token_type(token_type):

      iso_to_txn = iso.iso_to_typ() @ typ.typ_to_txn()

      exporter = exporter_map[token_type]
      exporter['ISO_TO_PSAF'] = (
          iso_to_txn @
          txn.txn_to_psaf()).optimize()
      exporter['ISO_TO_PSAC'] = (
          iso_to_txn @
          txn.txn_to_psac()).optimize()


if __name__ == '__main__':
  multi_grm.run(generator_main)
