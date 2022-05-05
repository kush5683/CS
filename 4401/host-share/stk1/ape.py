import os
os.environ["GREENIE"] = 'a'* 92 + bytes(0x0d0a0d0a)
print(os.environ.get('GREENIE'))