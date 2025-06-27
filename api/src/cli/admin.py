from dotenv import load_dotenv
import sys
import argparse
from app.db import get_engine, get_session
from app.models import User

load_dotenv()

def main():
    parser = argparse.ArgumentParser(
        description="TEMPLATE_PROJECT_NAME Admin CLI",
        usage="""
Usage: python -m cli.admin FLAGS COMMAND OPTIONS

Flags:
  -n             Dry run (do not modify the database, just print what would happen)
  -f             Force overwrite existing entries

Command:
  help           Show this help and exit
  TEMPLATE_PROJECT_NAME_LOWER OPTIONS  upload TEMPLATE_PROJECT_NAME_LOWER information to the database
  user OPTIONS   add/delete users

Command "TEMPLATE_PROJECT_NAME_LOWER" usage: python -m cli.admin FLAGS TEMPLATE_PROJECT_NAME_LOWER OPTIONS

TEMPLATE_PROJECT_NAME_LOWER Options:
  -d DIR         Directory containing images (mandatory)
  -i YAML_FILE   YAML file with TEMPLATE_PROJECT_NAME_LOWER entries (mandatory)

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
        print("[herbs] Command not yet implemented.")
        sys.exit(0)
    if args.command == 'user':
        handle_user(args)
        sys.exit(0)
    parser.print_usage()
    sys.exit(1)

def handle_user(args):
    parser = argparse.ArgumentParser(prog="user", add_help=False)
    subparsers = parser.add_subparsers(dest="action", required=True)
    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("-u", dest="name", type=str)
    add_parser.add_argument("email", type=str)
    del_parser = subparsers.add_parser("del")
    del_parser.add_argument("email", type=str)
    subparsers.add_parser("list")
    subargs = parser.parse_args(args.subargs)
    engine = get_engine()
    session = get_session(engine)
    dry_run = args.n
    force = args.f
    if subargs.action == 'add':
        name = subargs.name or subargs.email
        existing = session.query(User).filter_by(email=subargs.email).first()
        if existing and not force:
            print(f"User with email {subargs.email} already exists. Use -f to overwrite.")
            sys.exit(1)
        if dry_run:
            print(f"[DRY RUN] Would add user: {subargs.email} (name: {name})")
            return
        if existing:
            session.delete(existing)
            session.commit()
        user = User(email=subargs.email, name=name)
        session.add(user)
        session.commit()
        print(f"User added: {user.email} (name: {user.name})")
    elif subargs.action == 'del':
        user = session.query(User).filter_by(email=subargs.email).first()
        if not user:
            print(f"User with email {subargs.email} not found.")
            sys.exit(1)
        if dry_run:
            print(f"[DRY RUN] Would delete user: {subargs.email}")
            return
        session.delete(user)
        session.commit()
        print(f"User deleted: {subargs.email}")
    elif subargs.action == 'list':
        users = session.query(User).all()
        if not users:
            print("No users found.")
            return
        print(f"{'Email':<30} {'Name':<20} {'Last Login':<20}")
        print("-" * 70)
        for user in users:
            last_login = user.last_login.isoformat() if user.last_login else "-"
            print(f"{user.email:<30} {user.name:<20} {last_login:<20}")

if __name__ == "__main__":
    main() 