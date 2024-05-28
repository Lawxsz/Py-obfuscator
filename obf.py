# blankOBF improved by lawxsz
#
#

import random, string, base64, codecs, argparse, os, sys, hashlib
from textwrap import wrap
from lzma import compress
from marshal import dumps

def printerr(data):
    print(data, file=sys.stderr)

class lawxszcrykt:
    def __init__(self, code, outputpath):
        self.code = code.encode()
        self.outpath = outputpath
        self.varlen = 5
        self.vars = {}

        self.marshal()
        self.encrypt1()
        self.encrypt2()
        self.finalize()

    def generate(self, name):
        res = self.vars.get(name)
        if res is None:
            res = "".join(random.choice(string.ascii_letters) for _ in range(self.varlen))
            self.varlen = random.randint(3, 10)
            self.vars[name] = res
        return res

    def encryptstring(self, string):
        # Using SHA256 hash to generate random-looking variable names
        hash_val = hashlib.sha256(string.encode()).hexdigest()
        cut = random.randint(5, 10)
        return hash_val[:cut]

    def marshal(self):
        self.code = dumps(compile(self.code, "<string>", "exec"))

    def encrypt1(self):
        # Base64 encoding then breaking into parts and encoding each with a different method
        encoded = base64.b64encode(self.code).decode()
        parts = wrap(encoded, 10)
        shuffled_parts = [codecs.encode(part, 'rot13') for part in parts]
        random.shuffle(shuffled_parts)
        var_names = [self.generate("var") for _ in range(len(shuffled_parts))]
        init = "; ".join(f'{var}="{part}"' for var, part in zip(var_names, shuffled_parts))

        self.code = f'''
# lawxszcrykt Advanced Obfuscation
{init}
exec("".join([codecs.decode(name, "rot13") for name in [{','.join(var_names)}]]))
'''.encode()

    def encrypt2(self):
        # Additional compression step
        self.code = compress(self.code)
        enc_code = base64.b64encode(self.code).decode()
        variable = self.generate("compressed")
        self.code = f'''
# lawxszcrykt Compressed and encoded
{variable} = "{enc_code}"
import base64, lzma; exec(lzma.decompress(base64.b64decode({variable})).decode())
'''.encode()

    def finalize(self):
        if os.path.dirname(self.outpath).strip() != "":
            os.makedirs(os.path.dirname(self.outpath), exist_ok=True)
        with open(self.outpath, "w") as e:
            e.write(self.code.decode())
            print("Saved as --> " + os.path.realpath(self.outpath))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="xszOBF", description="Obfuscates python program to make it harder to read")
    parser.add_argument("FILE", help="Path to the file containing the python code")
    parser.add_argument("-o", "--output", type=str, default=None, help='Output file path', dest="path")
    args = parser.parse_args()

    if not os.path.isfile(sourcefile := args.FILE):
        printerr(f'No such file: "{args.FILE}"')
        sys.exit(1)
    elif not sourcefile.endswith((".py", ".pyw")):
        printerr('The file does not have a valid python script extension!')
        sys.exit(1)

    if args.path is None:
        args.path = "Obfuscated_" + os.path.basename(sourcefile)

    with open(sourcefile) as file:
        code = file.read()

    lawxszcrykt(code, args.path)
