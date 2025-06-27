# --- BEGIN: Download/Bootstrap Logic ---
TEMPLATE_MARKER="TEMPLATE_PROJECT_NAME"
DOWNLOAD_TEMPLATE=0
TEMPLATE_VERSION="latest"

# Parse -V/--version early
for arg in "$@"; do
    if [[ "$arg" == "-V" || "$arg" == "--version" ]]; then
        shift
        TEMPLATE_VERSION="$1"
        shift
        break
    fi
done

if ! grep -q "$TEMPLATE_MARKER" README.md 2>/dev/null; then
    DOWNLOAD_TEMPLATE=1
fi

if [ "$DOWNLOAD_TEMPLATE" = "1" ]; then
    if [ "$TEMPLATE_VERSION" = "latest" ]; then
        URL="https://github.com/gertalot/fullstack-quickstart/releases/latest/download/template-latest.tar.gz"
        DIR="template-latest"
    else
        URL="https://github.com/gertalot/fullstack-quickstart/releases/download/$TEMPLATE_VERSION/template-$TEMPLATE_VERSION.tar.gz"
        DIR="template-$TEMPLATE_VERSION"
    fi
    if [ "$INTERACTIVE" = true ]; then
        # Find the directory where this script is located
        SCRIPT_DIR="$(cd "$(dirname -- "$0")" && pwd)"
        REPO_ROOT="$SCRIPT_DIR"
        echo "ℹ️  Copying template from local repo at $REPO_ROOT to $DIR ..."
        mkdir -p "$DIR"
        cp -pr "$REPO_ROOT"/. "$DIR"/
        cd "$DIR"
        exec zsh -i ./init.sh "$@" < /dev/tty
        exit
    else
        echo "ℹ️  Downloading template from $URL ..."
        mkdir -p "$DIR"
        curl -L "$URL" | tar xz -C "$DIR" --strip-components=1
        cd "$DIR"
        exec zsh -i ./init.sh "$@" < /dev/tty
        exit
    fi
fi
# --- END: Download/Bootstrap Logic --- 