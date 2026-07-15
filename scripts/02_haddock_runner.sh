#!/usr/bin/env bash
#
# Downloads haddock-runner from GitHub releases. No Rust toolchain needed.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/_common.sh"

HADDOCK_RUNNER_BIN="$BIN_DIR/haddock-runner"
HADDOCK_RUNNER_STAMP="$BIN_DIR/.haddock-runner-version"

if [ -x "$HADDOCK_RUNNER_BIN" ] && [ "$(cat "$HADDOCK_RUNNER_STAMP" 2>/dev/null)" = "$HADDOCK_RUNNER_TAG" ]; then
  echo "[=] haddock-runner $HADDOCK_RUNNER_TAG already installed, skipping"
  exit 0
fi

# musl build on Linux avoids GLIBC version mismatches on older/cluster nodes.
case "$(uname -s)" in
Linux)
  case "$(uname -m)" in
  x86_64 | amd64) RUNNER_TARGET="x86_64-unknown-linux-musl" ;;
  arm64 | aarch64) RUNNER_TARGET="aarch64-unknown-linux-musl" ;;
  *)
    echo "[!!] Unsupported architecture for prebuilt haddock-runner on Linux: $(uname -m)"
    exit 1
    ;;
  esac
  ;;
Darwin)
  case "$(uname -m)" in
  x86_64 | amd64) RUNNER_TARGET="x86_64-apple-darwin" ;;
  arm64 | aarch64) RUNNER_TARGET="aarch64-apple-darwin" ;;
  *)
    echo "[!!] Unsupported architecture for prebuilt haddock-runner on macOS: $(uname -m)"
    exit 1
    ;;
  esac
  ;;
*)
  echo "[!!] Unsupported OS for prebuilt haddock-runner: $(uname -s)"
  exit 1
  ;;
esac

RUNNER_TAG="$HADDOCK_RUNNER_TAG"

RUNNER_ASSET="haddock-runner-${RUNNER_TAG}-${RUNNER_TARGET}.tar.gz"
RUNNER_URL="https://github.com/haddocking/haddock-runner/releases/download/${RUNNER_TAG}/${RUNNER_ASSET}"

echo "[+] Downloading ${RUNNER_URL}"
RUNNER_TMP="$(mktemp -d)"
curl -fsSL "$RUNNER_URL" -o "$RUNNER_TMP/haddock-runner.tar.gz"
tar -xzf "$RUNNER_TMP/haddock-runner.tar.gz" -C "$BIN_DIR" haddock-runner
chmod +x "$HADDOCK_RUNNER_BIN"
rm -rf "$RUNNER_TMP"
echo "$RUNNER_TAG" >"$HADDOCK_RUNNER_STAMP"
