"""Create a consistent SQLite snapshot; run in the deployed service with its volume."""
import argparse,sqlite3
from pathlib import Path
import storage
p=argparse.ArgumentParser();p.add_argument('destination',help='Path outside the live database, e.g. /data/backups/guide.sqlite3');args=p.parse_args();out=Path(args.destination)
if out.resolve()==storage.DB.resolve():raise SystemExit('Destination must differ from the live database')
if out.exists():raise SystemExit('Destination already exists; choose a new filename')
out.parent.mkdir(parents=True,exist_ok=True)
with storage.connect() as source,sqlite3.connect(out) as target:source.backup(target)
print('Backup completed.')
