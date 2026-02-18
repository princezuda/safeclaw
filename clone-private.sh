#!/usr/bin/env bash
#
# clone-private.sh
#
# Creates a private clone of the princezuda/safeclaw repository
# as princezuda/safeclaw-private on GitHub.
#
# Prerequisites:
#   - gh CLI installed and authenticated (gh auth login)
#   - git installed
#
# Usage:
#   ./clone-private.sh
#

set -euo pipefail

OWNER="princezuda"
SOURCE_REPO="safeclaw"
TARGET_REPO="safeclaw-private"
TARGET_FULL="${OWNER}/${TARGET_REPO}"

echo "==> Creating private repository: ${TARGET_FULL}"

# Check if gh is authenticated
if ! gh auth status &>/dev/null; then
    echo "Error: gh CLI is not authenticated. Run 'gh auth login' first."
    exit 1
fi

# Check if the target repo already exists
if gh repo view "${TARGET_FULL}" &>/dev/null 2>&1; then
    echo "Error: Repository ${TARGET_FULL} already exists."
    echo "Delete it first or choose a different name."
    exit 1
fi

# Create the new private repository (empty, no template)
gh repo create "${TARGET_FULL}" --private --description "Private clone of ${SOURCE_REPO}"

echo "==> Cloning source repository..."
TMPDIR=$(mktemp -d)
git clone --bare "https://github.com/${OWNER}/${SOURCE_REPO}.git" "${TMPDIR}/${SOURCE_REPO}.git"

echo "==> Pushing all branches and tags to private repository..."
cd "${TMPDIR}/${SOURCE_REPO}.git"
git push --mirror "https://github.com/${TARGET_FULL}.git"

echo "==> Cleaning up temporary files..."
rm -rf "${TMPDIR}"

echo ""
echo "Done! Your private clone is at: https://github.com/${TARGET_FULL}"
echo ""
echo "To clone it locally:"
echo "  git clone https://github.com/${TARGET_FULL}.git"
