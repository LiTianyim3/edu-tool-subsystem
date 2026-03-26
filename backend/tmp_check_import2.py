import importlib, inspect
m = importlib.import_module('module1.services.files_reader')
print('module file:', m.__file__)
print('module name:', m.__name__)
d = sorted(dir(m))
print('dir length:', len(d))
print('first 40 attrs:', d[:40])
print('contains extract_text_from_file?', 'extract_text_from_file' in d)
# try to open file and print snippet
with open(m.__file__, 'r', encoding='utf-8') as f:
    data = f.read()
print('\n--- file snippet start ---\n')
print(data[:800])
print('\n--- file snippet end ---')
