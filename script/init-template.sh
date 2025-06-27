#! /bin/sh
##############################################################################
# Project Template Initializer
#
# This script interactively sets up a new project from a template repository.
# It prompts for project variables, replaces placeholders, and initializes git.
#
# Usage:
#   curl -sSL https://example.com/init-template.sh | sh
#   sh init-template.sh
#
# Copyright (c) 2025
# Gert Verhoog [All rights reserved].
##############################################################################

#############################################################################
# User interaction functions
#############################################################################

txtbyel="$(tput bold)$(tput setaf 3)"
txtbred="$(tput bold)$(tput setaf 1)"
txtbgrn="$(tput bold)$(tput setaf 2)"
txtyel="$(tput setaf 3)"
txtblu="$(tput setaf 4)"
txtmag="$(tput setaf 5)"
txtcya="$(tput setaf 6)"
txtnorm="$(tput setaf 7)$(tput sgr0)"
txtibyel="$(tput smso)$(tput setaf 3)"

help() {
    echo "$(
        cat <<__EOF__

${txtbyel}NAME${txtnorm}
    Project Template Initializer

${txtbyel}DESCRIPTION${txtnorm}
    This script interactively sets up a new project from a template repository. It prompts for project variables,
    replaces placeholders, and initializes git. You can run it locally (after git clone) or remotely via curl.

${txtbyel}OPTIONS${txtnorm}
    ${txtcya}-n${txtnorm}, --project-name NAME      Project name
    ${txtcya}-a${txtnorm}, --author-name NAME       Author name
    ${txtcya}-e${txtnorm}, --author-email EMAIL     Author email
    ${txtcya}-d${txtnorm}, --db-name NAME           Database name
    ${txtcya}-c${txtnorm}, --cli-name NAME          CLI tool name
    ${txtcya}-v${txtnorm}, --docker-volume NAME     Docker volume name
    ${txtcya}-V${txtnorm}, --version VERSION        Template release version (default: latest)
    ${txtcya}-h${txtnorm}, --help                   Show this help and exit

    If any option is omitted, you will be prompted interactively.

    Template variables replaced:
      TEMPLATE_PROJECT_NAME
      TEMPLATE_AUTHOR_NAME
      TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM
      TEMPLATE_DB_NAME
      TEMPLATE_DOCKER_VOLUME
__EOF__
    )"
}

message() {
    echo "${txtyel}   $@${txtnorm}"
}

message_info() {
    echo "ℹ️  $@"
}

message_ok() {
    echo "${txtbgrn}✅ $@${txtnorm}"
}

message_err() {
    echo "${txtbred}❌ $@${txtnorm}"
}


ask_reply=""
ask() {
    prompt="$1"; shift
    default="$1"; shift
    print -n "${txtcya}❓ $prompt${txtnorm} [${default}]: "
    read reply < /dev/tty
    if [ -z "$reply" ]; then
        reply="$default"
    fi
    ask_reply="$reply"
}

#############################################################################
# set up variables
#############################################################################
if [ -t 0 ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
fi

if [ "$INTERACTIVE" = "true" ]; then
    message_info "Running interactively"
fi


# Parse -V/--version early
for arg in "$@"; do
    if [[ "$arg" == "-V" || "$arg" == "--version" ]]; then
        shift
        TEMPLATE_VERSION="$1"
        shift
        break
    fi
done

#############################################################################
# download and unpack
#############################################################################

DIR="fullstack-quickstart"
if [ "$INTERACTIVE" = true ]; then
    # Find the directory where this script is located (assume repo root)
    SCRIPT_DIR="$(cd "$(dirname -- "$0")" && pwd)"
    REPO_ROOT="$SCRIPT_DIR"
    echo "ℹ️  Copying template from local repo at $REPO_ROOT to $DIR ..."
    mkdir -p "$DIR"
    cp -pr "$REPO_ROOT"/. "$DIR"/
else
    if [ "$TEMPLATE_VERSION" = "latest" ]; then
        URL="https://github.com/gertalot/fullstack-quickstart/releases/latest/download/template-latest.tar.gz"
    else
        DIR="fullstack-quickstart-$TEMPLATE_VERSION"
        URL="https://github.com/gertalot/fullstack-quickstart/releases/download/$TEMPLATE_VERSION/template-$TEMPLATE_VERSION.tar.gz"
    fi

    echo "ℹ️  Downloading template and installing in $DIR ..."
    mkdir -p "$DIR"
    curl -sSL "$URL" | tar xz -C "$DIR" --strip-components=1
fi


#############################################################################
# variable replacement
#############################################################################

# Default values
PROJECT_NAME=""
AUTHOR_NAME=""
AUTHOR_EMAIL=""
DB_NAME=""
CLI_NAME=""
DOCKER_VOLUME=""

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

message_ok "Welcome to the Fullstack Quickstart template!"
message_info "This script will help you set up a new project from the Fullstack Quickstart template."
message_info "Run it with -h for help."
echo ""

if [ -z "$PROJECT_NAME" ]; then
    ask "Enter your project name" "MyApp"
    PROJECT_NAME="$ask_reply"
fi
if [ -z "$AUTHOR_NAME" ]; then
    ask "Enter author name" "Jane Doe"
    AUTHOR_NAME="$ask_reply"
fi
if [ -z "$AUTHOR_EMAIL" ]; then
    ask "Enter author email" "me@example.com"
    AUTHOR_EMAIL="$ask_reply"
fi
if [ -z "$DB_NAME" ]; then
    ask "Enter database name" "myapp_db"
    DB_NAME="$ask_reply"
fi
if [ -z "$CLI_NAME" ]; then
    ask "Enter CLI tool name" "myapp-admin"
    CLI_NAME="$ask_reply"
fi
if [ -z "$DOCKER_VOLUME" ]; then
    ask "Enter Docker volume name" "myapp-data"
    DOCKER_VOLUME="$ask_reply"
fi


message_info "Project Name: $PROJECT_NAME"
message_info "Author: $AUTHOR_NAME <$AUTHOR_EMAIL>"
message_info "Database: $DB_NAME"
message_info "CLI Tool: $CLI_NAME"
message_info "Docker Volume: $DOCKER_VOLUME"
echo -n "${txtcya}Proceed with these settings? [Y/n]: ${txtnorm}"
read proceed < /dev/tty
if [[ "$proceed" =~ ^[Nn] ]]; then
    message_err "Aborted by user."
    exit 1
fi

# 3. Recursively replace placeholders in all files (excluding .git, node_modules, .venv, etc.)
message "Replacing placeholders in files..."
find $DIR \( \
        -path './.git' -o -path './node_modules' -o -path './.venv' \
        -o -name '*.pyc' -o -name '*.log' \) -prune -false \
        -o -type f \( -name '*' -o -name '.env' -o -name '.env.example' \
    \) | while read file; do
    if file "$file" | grep -q text; then
        echo "Processing: $file"
        if ! LC_CTYPE=C sed -i '' \
            -e "s/TEMPLATE_PROJECT_NAME/$PROJECT_NAME/g" \
            -e "s/TEMPLATE_AUTHOR_NAME/$AUTHOR_NAME/g" \
            -e "s/TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM/$AUTHOR_EMAIL/g" \
            -e "s/TEMPLATE_DB_NAME/$DB_NAME/g" \
            -e "s/TEMPLATE_DOCKER_VOLUME/$DOCKER_VOLUME/g" "$file"; then
            echo "ERROR processing $file"
        fi
    fi
done

# 4. Optionally rename directories/files with placeholders
find $DIR -depth -name '*TEMPLATE_PROJECT_NAME*' | while read oldpath; do
    newpath="${oldpath//TEMPLATE_PROJECT_NAME/$PROJECT_NAME}"
    mv "$DIR/$oldpath" "$DIR/$newpath"
done

message_ok "Project initialized!"
message_info "You can now start developing your project."
