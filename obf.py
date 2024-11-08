import random, string, base64, codecs, argparse, os, sys, subprocess
from textwrap import wrap
from lzma import compress
from marshal import dumps

def printerr(data):
    print(data, file=sys.stderr)

class PrysmaticObfuscator:
    def __init__(self, code, outputpath):
        self.code = code.encode()
        self.outpath = outputpath
        self.varlen = random.randint(5, 10)
        self.vars = {}

        self.marshal()
        self.encrypt1()
        self.encrypt2()
        self.encrypt3()
        self.finalize()

    def generate(self, name):
        res = self.vars.get(name)
        if res is None:
            res = "_" + "".join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=self.varlen))
            self.varlen += 1
            self.vars[name] = res
        return res

    def encrypt_string(self, string):
        b64 = base64.b64encode(string.encode()).decode()
        return f'__import__("base64").b64decode("{b64}").decode()'

    def encryptor(self):
        def func_(string):
            return self.encrypt_string(string)
        return func_

    def compress(self):
        compressed_code = compress(self.code)
        return base64.b64encode(compressed_code).decode()

    def marshal(self):
        compiled_code = compile(self.code, "<string>", "exec")
        self.code = dumps(compiled_code)

    def encrypt1(self):
        code_b64 = base64.b64encode(self.code).decode()
        parts = wrap(code_b64, random.randint(15, 40))
        
        var_names = [self.generate(f"var{i}") for i in range(4)]
        
        init_statements = [
            f'{var_names[0]}="{codecs.encode(parts[0], "rot13")}"',
            f'{var_names[1]}="{parts[1]}"',
            f'{var_names[2]}="{parts[2][::-1]}"',
            f'{var_names[3]}="{parts[3]}"'
        ]

        random.shuffle(init_statements)
        
        self.code = f'''
# Obfuscated Code by github.com/lawxsz/py-obfuscator
{"; ".join(init_statements)};
exec(__import__("marshal").loads(__import__("base64").b64decode(__import__("codecs").decode({var_names[0]}, "rot13") + {var_names[1]} + {var_names[2]}[::-1] + {var_names[3]})))
'''.strip().encode()

    def encrypt2(self):
        compressed_code = self.compress()
        
        var_names = [self.generate(f"var{i}") for i in range(5)]
        
        self.code = f'''# Obfuscated Code
{var_names[0]} = __import__("base64").b64decode("{compressed_code}");
try:
    exec(__import__("marshal").loads({var_names[0]}))
except Exception as e:
    print("Decompression or execution error:", e)
'''.strip().encode()

    def encrypt3(self):
        compressed_code = base64.b64encode(self.code).decode()
        
        # Adding an extra layer of obfuscation
        obfuscated_exec = f'''
import base64; 
exec(base64.b64decode("{compressed_code}"))
'''
        
        # Randomly shuffle the execution order to make it less predictable
        shuffled_exec_parts = random.sample(obfuscated_exec.splitlines(), len(obfuscated_exec.splitlines()))
        
        self.code = '\n'.join(shuffled_exec_parts).encode()

    def finalize(self):
        if os.path.dirname(self.outpath).strip() != "":
            os.makedirs(os.path.dirname(self.outpath), exist_ok=True)
        
        with open(self.outpath, "w", encoding='utf-8') as e:
            e.write(self.code.decode())
            print("Saved as --> " + os.path.realpath(self.outpath))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=sys.argv[0], description="Obfuscates Python program to make it harder to read")
    parser.add_argument("FILE", help="Path to the file containing the Python code")
    parser.add_argument("-o", type=str, help='Output file path [Default: "Obfuscated_<FILE>.py"]', dest="path")
    
    args = parser.parse_args()

    if not os.path.isfile(sourcefile := args.FILE):
        printerr(f'No such file: "{args.FILE}"')
        os._exit(1)
    elif not sourcefile.endswith((".py", ".pyw")):
        printerr('The file does not have a valid Python script extension!')
        os._exit(1)
    
    if args.path is None:
        args.path = "Obfuscated_" + os.path.basename(sourcefile)
    
    with open(sourcefile, encoding='utf-8') as sourcefile:
        code = sourcefile.read()
    
    PrysmaticObfuscator(code, args.path)
