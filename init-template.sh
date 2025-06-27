#! /bin/zsh
##############################################################################
# Project Template Initializer
#
# This script interactively sets up a new project from a template repository.
# It prompts for project variables, replaces placeholders, and initializes git.
#
# Usage:
#   curl -sSL https://example.com/init-template.sh | zsh
#
# Copyright (c) 2025
# Gert Verhoog [All rights reserved].
##############################################################################

# --- BEGIN: Interactive Functions (from example-setup.sh) ---
txtbyel="$(tput bold)$(tput setaf 3)"
txtbred="$(tput bold)$(tput setaf 1)"
txtbgrn="$(tput bold)$(tput setaf 2)"
txtyel="$(tput setaf 3)"
txtblu="$(tput setaf 4)"
txtmag="$(tput setaf 5)"
txtcya="$(tput setaf 6)"
txtnorm="$(tput setaf 7)$(tput sgr0)"
txtibyel="$(tput smso)$(tput setaf 3)"

message() {
    echo "${txtyel}   $@${txtnorm}"
}
message_ok() {
    echo "${txtbgrn}✅ $@${txtnorm}"
}
message_err() {
    echo "${txtbred}❌ $@${txtnorm}"
}
message_info() {
    echo "ℹ️  $@"
}

# Prompt for multi-choice user input
global_reply=""
ask() {
    prompt="$1"; shift
    default="$1"; shift
    echo -n "${txtcya}❓ $prompt${txtnorm} [${default}]: "
    read reply
    if [ -z "$reply" ]; then
        reply="$default"
    fi
    global_reply="$reply"
}

# --- END: Interactive Functions ---

# --- BEGIN: Command Line Option Parsing ---
show_help() {
    cat <<EOF
Usage: $0 [options]

Options:
  -n, --project-name NAME      Project name
  -a, --author-name NAME       Author name
  -e, --author-email EMAIL     Author email
  -d, --db-name NAME           Database name
  -c, --cli-name NAME          CLI tool name
  -v, --docker-volume NAME     Docker volume name
  -V, --version VERSION        Template release version (default: latest)
  -h, --help                   Show this help and exit

If any option is omitted, you will be prompted interactively.

You can run this script either locally (after git clone) or remotely:
  curl -sSL https://example.com/init-template.sh | zsh

By default, the latest release is used. To specify a version:
  curl -sSL https://example.com/init-template.sh | zsh -- -V v1.2.3

Template variables replaced:
  TEMPLATE_PROJECT_NAME
  TEMPLATE_AUTHOR_NAME
  TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM
  TEMPLATE_DB_NAME
  TEMPLATE_CLI_NAME
  TEMPLATE_DOCKER_VOLUME
EOF
}

# Default values
PROJECT_NAME=""
AUTHOR_NAME=""
AUTHOR_EMAIL=""
DB_NAME=""
CLI_NAME=""
DOCKER_VOLUME=""

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--project-name)
            PROJECT_NAME="$2"; shift 2;;
        -a|--author-name)
            AUTHOR_NAME="$2"; shift 2;;
        -e|--author-email)
            AUTHOR_EMAIL="$2"; shift 2;;
        -d|--db-name)
            DB_NAME="$2"; shift 2;;
        -c|--cli-name)
            CLI_NAME="$2"; shift 2;;
        -v|--docker-volume)
            DOCKER_VOLUME="$2"; shift 2;;
        -V|--version)
            TEMPLATE_VERSION="$2"; shift 2;;
        -h|--help)
            show_help; exit 0;;
        *)
            message_err "Unknown option: $1"; show_help; exit 1;;
    esac
done
# --- END: Command Line Option Parsing ---

# --- BEGIN: Main Script Logic ---

message "Welcome to the Project Template Initializer!"

if [ -z "$PROJECT_NAME" ]; then
    ask "Enter your project name" "MyApp"
    PROJECT_NAME="$global_reply"
fi
if [ -z "$AUTHOR_NAME" ]; then
    ask "Enter author name" "Jane Doe"
    AUTHOR_NAME="$global_reply"
fi
if [ -z "$AUTHOR_EMAIL" ]; then
    ask "Enter author email" "TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM"
    AUTHOR_EMAIL="$global_reply"
fi
if [ -z "$DB_NAME" ]; then
    ask "Enter database name" "myapp_db"
    DB_NAME="$global_reply"
fi
if [ -z "$CLI_NAME" ]; then
    ask "Enter CLI tool name" "myapp-admin"
    CLI_NAME="$global_reply"
fi
if [ -z "$DOCKER_VOLUME" ]; then
    ask "Enter Docker volume name" "myapp-data"
    DOCKER_VOLUME="$global_reply"
fi

# Add more prompts as needed

# 2. Confirm before proceeding
message_info "Project Name: $PROJECT_NAME"
message_info "Author: $AUTHOR_NAME <$AUTHOR_EMAIL>"
message_info "Database: $DB_NAME"
message_info "CLI Tool: $CLI_NAME"
message_info "Docker Volume: $DOCKER_VOLUME"
echo -n "${txtcya}Proceed with these settings? [Y/n]: ${txtnorm}"
read proceed
if [[ "$proceed" =~ ^[Nn] ]]; then
    message_err "Aborted by user."
    exit 1
fi

# 3. Recursively replace placeholders in all files (excluding .git, node_modules, .venv, etc.)
message "Replacing placeholders in files..."
find . \( -path './.git' -o -path './node_modules' -o -path './.venv' -o -name '*.pyc' -o -name '*.log' \) -prune -false -o -type f \( -name '*' -o -name '.env' -o -name '.env.example' \) | while read file; do
    sed -i '' \
        -e "s/TEMPLATE_PROJECT_NAME/$PROJECT_NAME/g" \
        -e "s/TEMPLATE_AUTHOR_NAME/$AUTHOR_NAME/g" \
        -e "s/TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM/$AUTHOR_EMAIL/g" \
        -e "s/TEMPLATE_DB_NAME/$DB_NAME/g" \
        -e "s/TEMPLATE_CLI_NAME/$CLI_NAME/g" \
        -e "s/TEMPLATE_DOCKER_VOLUME/$DOCKER_VOLUME/g" "$file"
done

# 4. Optionally rename directories/files with placeholders
find . -depth -name '*TEMPLATE_PROJECT_NAME*' | while read path; do
    newpath="${path//TEMPLATE_PROJECT_NAME/$PROJECT_NAME}"
    mv "$path" "$newpath"
done

# 5. Remove .git and self, initialize new git repo
if [ -d .git ]; then
    message_info "A .git directory was found in this folder."
    message_info "This script is intended for use in a freshly unpacked template, not the original repository."
    echo -n "${txtcya}Are you sure you want to remove .git and reinitialize git here? [y/N]: ${txtnorm}"
    read confirm_git
    if [[ ! "$confirm_git" =~ ^[Yy]$ ]]; then
        message_err "Aborted git removal. Exiting."
        exit 1
    fi
    rm -rf .git
    message_ok ".git directory removed."
fi

SCRIPT_NAME="$(basename "$0")"
if [ -f "$SCRIPT_NAME" ]; then
    message "Removing setup script ($SCRIPT_NAME)..."
    rm -f "$SCRIPT_NAME"
fi

git init
git add .
git commit -m "Initial commit from template initializer"
message_ok "Project initialized!"
message_info "You can now start developing your project."

# --- END: Main Script Logic ---

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
        URL="https://github.com/yourorg/yourtemplate/releases/latest/download/template-latest.tar.gz"
        DIR="template-latest"
    else
        URL="https://github.com/yourorg/yourtemplate/releases/download/$TEMPLATE_VERSION/template-$TEMPLATE_VERSION.tar.gz"
        DIR="template-$TEMPLATE_VERSION"
    fi
    message_info "Downloading template from $URL ..."
    mkdir -p "$DIR"
    curl -L "$URL" | tar xz -C "$DIR" --strip-components=1
    cd "$DIR"
    exec ./init-template.sh "$@"
    exit
fi
# --- END: Download/Bootstrap Logic --- 