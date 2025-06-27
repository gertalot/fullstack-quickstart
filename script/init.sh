#! /bin/sh
##############################################################################
# Project Template Initializer
#
# This script interactively sets up a new project from a template repository.
# It prompts for project variables, replaces placeholders, and initializes git.
#
# Usage:
#   curl -sSL https://example.com/init.sh | sh
#   sh init.sh
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
    printf '%s\n' "$(cat <<__EOF__

${txtbyel}NAME${txtnorm}
    Full Stack Quickstart Initialiser

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
    printf '%s\n' "${txtyel}   $*${txtnorm}"
}

message_info() {
    printf '%s\n' "ℹ️  $*"
}

message_ok() {
    printf '%s\n' "${txtbgrn}✅ $*${txtnorm}"
}

message_err() {
    printf '%s\n' "${txtbred}❌ $*${txtnorm}"
}

ask_reply=""
ask() {
    prompt="$1"
    default="$2"
    printf "%s" "${txtcya}❓ $prompt${txtnorm} [${default}]: "
    read reply < /dev/tty
    if [ "x$reply" = "x" ]; then
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

TEMPLATE_VERSION="latest"
set -- "$@"
while [ $# -gt 0 ]; do
    case "$1" in
        -V|--version)
            shift
            TEMPLATE_VERSION="$1"
            shift
            ;;
        *)
            shift
            ;;
    esac
done

#############################################################################
# download and unpack
#############################################################################

DIR="fullstack-quickstart"
# If interactive OR REPO_ROOT is set, use REPO_ROOT to copy files; otherwise, download
if [ "$INTERACTIVE" = "true" ] || [ -n "$REPO_ROOT" ]; then
    if [ -z "$REPO_ROOT" ]; then
        SCRIPT_DIR="$(cd "$(dirname -- "$0")" && pwd)"
        REPO_ROOT="$(dirname -- "$SCRIPT_DIR")"
    fi
    printf '%s\n' "ℹ️  Copying template from local repo at $REPO_ROOT to $DIR ..."
    mkdir -p "$DIR"
    DIR_ABS="$(cd "$DIR" && pwd)"
    (
        cd "$REPO_ROOT" && \
        tar \
            --exclude='.git' \
            --exclude='.venv' \
            --exclude='.env' \
            --exclude='.env.example' \
            --exclude='.github' \
            --exclude='node_modules' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='*.log' \
            -cf - . | (cd "$DIR_ABS" && tar -xf -)
    )
else
    if [ "$TEMPLATE_VERSION" = "latest" ]; then
        URL="https://github.com/gertalot/fullstack-quickstart/releases/latest/download/template-latest.tar.gz"
    else
        DIR="fullstack-quickstart-$TEMPLATE_VERSION"
        URL="https://github.com/gertalot/fullstack-quickstart/releases/download/$TEMPLATE_VERSION/template-$TEMPLATE_VERSION.tar.gz"
    fi

    printf '%s\n' "ℹ️  Downloading template and installing in $DIR ..."
    mkdir -p "$DIR"
    curl -sSL "$URL" | tar xz -C "$DIR" --strip-components=1
fi

#############################################################################
# variable replacement
#############################################################################

PROJECT_NAME=""
AUTHOR_NAME=""
AUTHOR_EMAIL=""
DB_NAME=""
CLI_NAME=""
DOCKER_VOLUME=""

set -- "$@"
while [ $# -gt 0 ]; do
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
            help; exit 0;;
        *)
            message_err "Unknown option: $1"; help; exit 1;;
    esac
done

message_ok "Welcome to the Fullstack Quickstart template!"
message_info "This script will help you set up a new project from the Fullstack Quickstart template."
message_info "Run it with -h for help."
printf '\n'

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
printf "%s" "${txtcya}Proceed with these settings? [Y/n]: ${txtnorm}"
read proceed < /dev/tty
case "$proceed" in
    [Nn]*)
        message_err "Aborted by user."
        exit 1
        ;;
esac

message "Replacing placeholders in files..."
find "$DIR" \
    \( -path "$DIR/.git" -o -path "$DIR/node_modules" -o -path "$DIR/.venv" \
    -o -name '*.pyc' -o -name '*.log' \) -prune -false \
    -o -type f \( -name '*' -o -name '.env' -o -name '.env.example' \) | while IFS= read -r file; do
    if file "$file" | grep -q text; then
        tmpfile="${file}.tmp.$$"
        sed \
            -e "s/TEMPLATE_PROJECT_NAME/$PROJECT_NAME/g" \
            -e "s/TEMPLATE_AUTHOR_NAME/$AUTHOR_NAME/g" \
            -e "s/TEMPLATE_AUTHOR_EMAIL@EXAMPLE.COM/$AUTHOR_EMAIL/g" \
            -e "s/TEMPLATE_DB_NAME/$DB_NAME/g" \
            -e "s/TEMPLATE_DOCKER_VOLUME/$DOCKER_VOLUME/g" "$file" > "$tmpfile" && mv "$tmpfile" "$file"
    fi
done

find "$DIR" -depth -name '*TEMPLATE_PROJECT_NAME*' | while IFS= read -r oldpath; do
    newpath="`echo "$oldpath" | sed "s/TEMPLATE_PROJECT_NAME/$PROJECT_NAME/g"`"
    mv "$oldpath" "$newpath"
done

# Initialize git repository if not already present
if [ ! -d "$DIR/.git" ]; then
    message_info "Initializing a new git repository..."
    (
        cd "$DIR" && \
        git init > /dev/null 2>&1 && \
        git add . > /dev/null 2>&1 && \
        git commit -m "Initial commit" > /dev/null 2>&1
    ) && message_ok "Git repository initialized and initial commit created." || message_err "Git initialization failed."
else
    message_info "Git repository already exists in $DIR. Skipping git init."
fi

message_ok "Project initialized!"
message_info "You can now start developing your project."
