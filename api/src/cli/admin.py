import sys
import argparse
from api.db import get_engine, get_session
from api.models import User

def main():
    parser = argparse.ArgumentParser(
        description="Savour Herbs Admin CLI",
        usage="""
Usage: python -m cli.admin FLAGS COMMAND OPTIONS

Flags:
  -n             Dry run (do not modify the database, just print what would happen)
  -f             Force overwrite existing entries

Command:
  help           Show this help and exit
  herbs OPTIONS  upload herb information to the database
  user OPTIONS   add/delete users

Command "herbs" usage: python -m cli.admin FLAGS herbs OPTIONS

herbs Options:
  -d DIR         Directory containing images (mandatory)
  -i YAML_FILE   YAML file with herb entries (mandatory)

Command "user" usage: python -m cli.admin FLAGS user add|del OPTIONS EMAIL

Command "user" options:
  add            Add a user to the user database
  del            Delete a user from the user database
  list           List all users (email, name, and last login datetime)
  -u NAME        set user's name to NAME
  EMAIL          the user's email - this is how the user authenticates.
"""
    )
    parser.add_argument('-n', action='store_true', help='Dry run (do not modify the database)')
    parser.add_argument('-f', action='store_true', help='Force overwrite existing entries')
    parser.add_argument('command', nargs='?', help='Command to run (herbs, user, help)')
    parser.add_argument('subargs', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.command in (None, 'help'):
        parser.print_usage()
        sys.exit(0)

    if args.command == 'herbs':
        handle_herbs(args)
    elif args.command == 'user':
        handle_user(args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_usage()
        sys.exit(1)

def handle_herbs(args):
    print("[herbs] Command not yet implemented.")

def handle_user(args):
    print("[user] Command not yet implemented.")

if __name__ == "__main__":
    main() 