"""Create a portable release without local QA dependencies or screenshots."""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
files = [ROOT/name for name in ['selfsteal.sh','selfsteal.upstream.sh','README.md','LICENSE.upstream','build-info.json']]
files += [ROOT/name for name in ['PRODUCT.md','DESIGN.md'] if (ROOT/name).exists()]
files += [p for p in (ROOT/'site').rglob('*') if p.is_file()]
files += [p for p in (ROOT/'tools').glob('*.py')]
files += [p for p in (ROOT/'tools').glob('*.sh')]
files += [ROOT/'tools/qa'/n for n in ['check.mjs','check_media.mjs','package.json','package-lock.json']]
files += [ROOT/'.impeccable'/n for n in ['config.json','design.json','direction.md'] if (ROOT/'.impeccable'/n).exists()]
with zipfile.ZipFile(ROOT/'selfsteal-landings.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as release:
    for p in files:
        if not p.exists():
            raise FileNotFoundError(p)
        release.write(p,p.relative_to(ROOT))
print(f'Release: {ROOT / "selfsteal-landings.zip"} ({(ROOT/"selfsteal-landings.zip").stat().st_size:,} bytes, {len(files)} files)')
