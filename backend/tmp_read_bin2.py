import importlib, os, sys
sys.path.insert(0, 'backend')
importlib.invalidate_caches()
from module1.services import files_reader
print('module file:', files_reader.__file__)
print('has func:', hasattr(files_reader, 'extract_text_from_file'))
print('callable:', callable(getattr(files_reader, 'extract_text_from_file', None)))
print('attrs sample:', [a for a in dir(files_reader) if 'extract' in a.lower()])
