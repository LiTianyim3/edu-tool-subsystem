import importlib
m = importlib.import_module('module1.services.files_reader')
print('__file__:', getattr(m, '__file__', None))
print('has extract_text_from_file:', hasattr(m, 'extract_text_from_file'))
print('attrs:', [a for a in dir(m) if 'extract' in a.lower()])
print('repr source start')
import inspect
print(inspect.getsource(m))
