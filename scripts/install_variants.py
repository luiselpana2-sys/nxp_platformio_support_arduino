"""Copy board variants from an official mcx-arduino-core checkout into this platform."""
import argparse
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('core_root', help='Path to an mcx-arduino-core checkout or its variants directory')
args = parser.parse_args()
core_root = Path(args.core_root).expanduser().resolve()
variant_roots = (
    core_root / 'variants',
    core_root / 'hardware' / 'nxp' / 'mcx' / 'variants',
    core_root,
)
source = next((path for path in variant_roots if path.is_dir() and path.name == 'variants'), None)
target = Path(__file__).resolve().parents[1] / 'framework' / 'variants'
if source is None:
    parser.error(f'Cannot find variants/ in {core_root} or the standard Arduino hardware layout')

boards = []
for board_file in sorted((target.parent.parent / 'boards').glob('*.json')):
    board_data = json.loads(board_file.read_text(encoding='utf-8'))
    build = board_data.get('build', {})
    boards.append((board_file.stem, build.get('variant'), build.get('ldscript')))

missing = []
for board, variant_name, ldscript in boards:
    folder = source / (variant_name or '')
    if not folder.is_dir():
        missing.append(f'{board}: missing variant {variant_name!r}')
    elif not ldscript or not (folder / 'linker' / ldscript).is_file():
        missing.append(f'{board}: missing linker {ldscript!r}')

if missing:
    parser.error('Incomplete core checkout:\n  ' + '\n  '.join(missing))

for _, variant_name, _ in boards:
    shutil.copytree(source / variant_name, target / variant_name, dirs_exist_ok=True)
    print(f'Installed {variant_name}')
