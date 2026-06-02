#!/usr/bin/env bash

set -euo pipefail

readonly artifact_root="${1:?usage: publish-far-releases.sh <artifact-root> [release-channel]}"
readonly release_channel="${2:-upstream}"
readonly scripts_root="${artifact_root%/}/nisaba/scripts"
readonly commit_full="$(git rev-parse HEAD)"
readonly base_commit_ref="$(git rev-parse HEAD^)"
readonly base_commit_short="$(git rev-parse --short=6 "${base_commit_ref}")"
readonly upstream_repo_url="https://github.com/google-research/nisaba"
readonly upstream_license_url="${upstream_repo_url}/blob/main/LICENSE"
readonly upstream_citation_url="${upstream_repo_url}#citation"

github_https_url() {
  local remote_url="${1}"
  remote_url="${remote_url%.git}"
  case "${remote_url}" in
    git@github.com:*)
      printf 'https://github.com/%s\n' "${remote_url#git@github.com:}"
      ;;
    https://github.com/*)
      printf '%s\n' "${remote_url}"
      ;;
    *)
      echo "Unsupported GitHub remote URL: ${remote_url}" >&2
      exit 1
      ;;
  esac
}

readonly local_repo_url="$(github_https_url "$(git remote get-url origin)")"
readonly local_commit_url="${local_repo_url}/commit/${commit_full}"
readonly base_commit_url="${upstream_repo_url}/commit/${base_commit_ref}"

if [[ ! -d "${scripts_root}" ]]; then
  echo "Expected FAR directory at ${scripts_root}" >&2
  exit 1
fi

if [[ "${DRY_RUN:-0}" != "1" && -z "${GH_TOKEN:-}" ]]; then
  echo "GH_TOKEN is required unless DRY_RUN=1." >&2
  exit 1
fi

release_dirs=()
while IFS= read -r release_dir; do
  release_dirs+=("${release_dir}")
done < <(
  find "${scripts_root}" -type f -name '*.far' -print \
    | sed "s#^${scripts_root}/##" \
    | awk -F/ '
        $1 == "natural_translit" && NF >= 3 { print $1 "/" $2; next }
        NF >= 2 { print $1 }
      ' \
    | LC_ALL=C sort -u
)

if [[ "${#release_dirs[@]}" -eq 0 ]]; then
  echo "No FAR release directories found under ${scripts_root}" >&2
  exit 1
fi

release_tmp_dir="$(mktemp -d)"
cleanup() {
  rm -rf "${release_tmp_dir}"
}
trap cleanup EXIT

for release_dir in "${release_dirs[@]}"; do
  slug="${release_dir//\//-}"
  release_name="${slug}-${release_channel}-${base_commit_short}"
  manifest_path="${release_tmp_dir}/manifest.json"
  manifest_url="${local_repo_url}/releases/download/${release_name}/manifest.json"
  notes_path="${release_tmp_dir}/${release_name}.md"
  far_assets=()

  while IFS= read -r far_asset; do
    far_assets+=("${far_asset}")
  done < <(find "${scripts_root}/${release_dir}" -type f -name '*.far' | LC_ALL=C sort)

  python3 ./.github/scripts/write-far-manifest.py \
    --scripts-root "${scripts_root}" \
    --release-dir "${release_dir}" \
    --release-name "${release_name}" \
    --repo-url "${local_repo_url}" \
    --output "${manifest_path}" \
    "${far_assets[@]}"
  cat > "${notes_path}" <<EOF
FAR files for \`${release_dir}\` built from commit [\`${commit_full}\`](${local_commit_url}).

Release suffix source commit: [\`${base_commit_ref}\`](${base_commit_url}) (the parent commit of the build-fix branch tip).

If you use these FAR files in academic writing or publications, please cite the
original [Nisaba](${upstream_repo_url}) authors and papers rather than citing
this release alone.

See the upstream citation guidance in the original repository:
[google-research/nisaba#citation](${upstream_citation_url}).

These FAR files are assumed to be covered by the repository's
[Apache License 2.0](${upstream_license_url}).

Assets:
- individual \`.far\` files from \`${release_dir}\`
- [manifest.json](${manifest_url}): manifest of FAR files, release URLs, and internal FST byte ranges
EOF

  if [[ "${DRY_RUN:-0}" == "1" ]]; then
    echo "Would publish ${release_name} (${#far_assets[@]} FARs)"
    continue
  fi

  if gh release view "${release_name}" >/dev/null 2>&1; then
    gh release delete "${release_name}" --yes --cleanup-tag
  fi

  gh release create "${release_name}" \
    "${far_assets[@]}" \
    "${manifest_path}" \
    --target "${commit_full}" \
    --title "${release_name}" \
    --notes-file "${notes_path}"
done
