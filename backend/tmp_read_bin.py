import importlib, os
importlib.invalidate_caches()
# ensure backend in sys.path
import sys
sys.path.insert(0, 'backend')
from module1.services import files_reader
fn = files_reader.__file__
print('file path:', fn)
print('exists:', os.path.exists(fn))
print('size os.path.getsize:', os.path.getsize(fn))
with open(fn, 'rb') as f:
    b = f.read()
print('bytes len:', len(b))
print('first bytes:', b[:120])
