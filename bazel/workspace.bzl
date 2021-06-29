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

"""Collection of rules exported by Nisaba project.

Please include this file in all the downstream Bazel dependencies of Nisaba.
"""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

def _clean_dep(dep):
    """Sanitizes a dependency.

    The dependencies need to resolve correctly from code that includes Nisaba as
    a submodule.
    """
    return str(Label(dep))

def nisaba_public_repositories(name = ""):
    """All external dependencies for Nisaba builds in downstream projects.

    Args:
      name: Name of the rule.
    """

    # -------------------------------------------------------------------------
    # utfcpp: The low-level UTF8 handling library. See
    #   https://github.com/nemtrif/utfcpp
    # -------------------------------------------------------------------------
    utfcpp_version = "3.2.1"

    http_archive(
        name = "com_github_utfcpp",
        urls = ["https://github.com/nemtrif/utfcpp/archive/v%s.tar.gz" % utfcpp_version],
        sha256 = "8d6aa7d77ad0abb35bb6139cb9a33597ac4c5b33da6a004ae42429b8598c9605",
        build_file = _clean_dep("//bazel:utfcpp.BUILD.bazel"),
        strip_prefix = "utfcpp-%s" % utfcpp_version,
    )
