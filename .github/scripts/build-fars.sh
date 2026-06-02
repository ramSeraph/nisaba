#!/usr/bin/env bash

set -euo pipefail

readonly bazel_bin_name="${BAZEL_BIN_NAME:-bazelisk-linux-amd64}"
readonly compilation_mode="${BAZEL_COMPILATION_MODE:-opt}"
readonly bazel_jobs="${BAZEL_JOBS:-8}"
readonly output_dir="${FAR_ROOT:?set FAR_ROOT to the FAR staging directory}"
readonly package_set='set(//nisaba/scripts/brahmic:* //nisaba/scripts/abjad_alphabet:* //nisaba/scripts/natural_translit/romanization:* //nisaba/scripts/natural_translit/deromanization:* //nisaba/scripts/natural_translit/g2p:* //nisaba/scripts/natural_translit/languages:*)'
readonly query="attr(generator_function, \".*grm.*\", ${package_set})"

far_targets=()
while IFS= read -r target; do
  far_targets+=("${target}")
done < <(
  "./${bazel_bin_name}" query "${query}" \
    | LC_ALL=C sort \
    | grep -F -v ':_' \
    | grep -v '\.' \
    | grep -E -v '(_test|_byte|_sttable)$'
)

if [[ "${#far_targets[@]}" -eq 0 ]]; then
  echo "No FAR targets found." >&2
  exit 1
fi

rm -rf "${output_dir}"
mkdir -p "${output_dir}"

"./${bazel_bin_name}" run //:requirements.update

# Excluding dotted labels is intentional: the aggregate targets build the per-script
# FAR outputs transitively, while the dotted targets are intermediate/generated ones.
"./${bazel_bin_name}" build -c "${compilation_mode}" --jobs="${bazel_jobs}" "${far_targets[@]}"

readonly bazel_bin="$("./${bazel_bin_name}" info -c "${compilation_mode}" bazel-bin)"

find "${bazel_bin}/nisaba/scripts" -type f -name '*.far' -print0 \
  | while IFS= read -r -d '' far_path; do
      rel_path="${far_path#${bazel_bin}/}"
      mkdir -p "${output_dir}/$(dirname "${rel_path}")"
      cp "${far_path}" "${output_dir}/${rel_path}"
    done

(
  cd "${output_dir}"
  find . -type f -name '*.far' | sed 's#^\./##' | LC_ALL=C sort > far-files.txt
)

echo "Collected $(wc -l < "${output_dir}/far-files.txt" | tr -d ' ') FAR files into ${output_dir}"
