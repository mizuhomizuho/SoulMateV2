import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    'soul_mate.cfg', r'C:\Users\xxxx0\Dropbox\soul_mate_cfg.py')
foo = importlib.util.module_from_spec(spec)
sys.modules['soul_mate.cfg'] = foo
spec.loader.exec_module(foo)

CFG: dict = foo.SoulMateCfg().get()