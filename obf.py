import os
import ast
import sys
import zlib
import base64
import string
import random
import builtins
import argparse
import marshal

# Obfuscator by Blank-C and Lawxsz

class PyObfuscator:
    def __init__(self, code: str, include_imports: bool = False, recursion: int = 1) -> None:
        self._code = code
        self._imports = []
        self._aliases = {}
        self._valid_identifiers = [chr(i) for i in range(256, 0x24976) if chr(i).isidentifier()]

        # Options
        self.__include_imports = include_imports
        if recursion < 1:
            raise ValueError("Recursion length cannot be less than 1")
        else:
            self.__recursion = recursion

    def obfuscate(self) -> str:
        self._remove_comments_and_docstrings()
        self._save_imports()

        layers = [
            self._layer_1,
            self._layer_2,
            self._layer_3,
            self._layer_4
        ] * self.__recursion
        random.shuffle(layers)

        if layers[-1] == self._layer_3:
            for index, layer in enumerate(layers):
                if layer != self._layer_3:
                    layers[index] = self._layer_3
                    layers[-1] = layer
                    break

        for layer in layers:
            layer()

        if self.__include_imports:
            self._prepend_imports()
        return self._code

    def _remove_comments_and_docstrings(self) -> None:
        tree = ast.parse(self._code)
        tree.body.insert(0, ast.Expr(
                    value=ast.Constant(":: prysmax is the best st3al3r ev3r ::")
                ))
        for index, node in enumerate(tree.body[1:]):

            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                tree.body[index] = ast.Pass()

            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for i, expr in enumerate(node.body):
                    if isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Constant):
                        node.body[i] = ast.Pass()

            elif isinstance(node, ast.ClassDef):
                for i, expr in enumerate(node.body):
                    if isinstance(expr, ast.Expr) and isinstance(expr.value, ast.Constant):
                        node.body[i] = ast.Pass()
                    elif isinstance(expr, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        for j, n in enumerate(expr.body):
                            if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant):
                                expr.body[j] = ast.Pass()
        self._code = ast.unparse(tree)

    def _save_imports(self) -> None:
        def visit_node(node):
            if isinstance(node, ast.Import):
                for name in node.names:
                    self._imports.append((None, name.name))
            elif isinstance(node, ast.ImportFrom):
                module = node.module
                for name in node.names:
                    self._imports.append((module, name.name))

            for child_node in ast.iter_child_nodes(node):
                visit_node(child_node)

        tree = ast.parse(self._code)
        visit_node(tree)
        self._imports.sort(reverse=True, key=lambda x: len(x[1]) + len(x[0]) if x[0] is not None else 0)

    def _prepend_imports(self) -> None:
        for module, submodule in self._imports:
            if module is not None:
                statement = f"from {module} import {submodule}\n"
            else:
                statement = f"import {submodule}\n"
            self._code = statement + self._code

    def _layer_1(self) -> None:
        self._insert_dummy_comments()
        layer = """
fire = 'some_encoded_string_1'
water = 'some_encoded_string_2'
earth = 'some_encoded_string_3'
wind = 'some_encoded_string_4'

exec(__import__('zlib').decompress(__import__('base64').b64decode(fire + water + earth + wind)))
"""
        # Encode the code and split into parts
        encoded = base64.b64encode(zlib.compress(self._code.encode())).decode()
        parts = [encoded[i:i + len(encoded) // 4] for i in range(0, len(encoded), len(encoded) // 4)]
        parts.reverse()

        # Insert the parts into the layer code
        tree = ast.parse(layer)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and parts:
                before = "".join(random.choices(string.ascii_letters, k=random.randint(5, 100)))
                after = "".join(random.choices(string.ascii_letters, k=random.randint(5, 100)))
                part = parts.pop()
                node.value = ast.Subscript(
                    value=ast.Constant(value=before + part + after),
                    slice=ast.Slice(
                        upper=ast.Constant(value=len(before) + len(part)),
                        lower=ast.Constant(value=len(before)),
                        step=None
                    ),
                    ctx=ast.Store()
                )
        self._code = ast.unparse(tree)
        self._obfuscate_vars()
        self._insert_dummy_comments()

    def _layer_2(self) -> None:
        layer = """
encrypted = []
for i in range(1, 100):
    if encrypted[in_loc] ^ i == encrypted[re_loc]:
        exec(__import__('zlib').decompress(bytes(map(lambda x: x ^ i, encrypted[:in_loc] + encrypted[in_loc+1:re_loc] + encrypted[re_loc+1:]))))
        break
"""
        key = random.randint(1, 100)
        in_byte = random.randbytes(1)[0]
        re_byte = in_byte ^ key

        encrypted = list(map(lambda x: key ^ x, zlib.compress(self._code.encode())))

        in_loc = random.randint(0, int(len(encrypted)/2))
        re_loc = random.randint(in_loc, len(encrypted) - 1)
        encrypted.insert(in_loc, in_byte)
        encrypted.insert(re_loc, re_byte)
        layer = layer.replace("in_loc", str(in_loc)).replace("re_loc", str(re_loc))

        tree = ast.parse(layer)
        for node in ast.walk(tree):
            if isinstance(node, ast.List):
                node.elts = [ast.Constant(value=x) for x in encrypted]

        self._code = ast.unparse(tree)
        self._obfuscate_vars()
        self._insert_dummy_comments()

    def _layer_3(self) -> None:
        layer = """
ip_table = []
data = list([int(x) for item in [value.split(".") for value in ip_table] for x in item])
exec(compile(__import__('zlib').decompress(__import__('base64').b64decode(bytes(data))), '<(*3*)>', 'exec'))
"""
        def bytes2ip(data: bytes) -> list:
            ip_addresses = []
            for index in range(0, len(data), 4):
                ip_bytes = data[index:index+4]
                ip_addresses.append(".".join([str(x) for x in ip_bytes]))
            return ip_addresses

        encrypted = base64.b64encode(zlib.compress(self._code.encode()))
        ip_addresses = bytes2ip(encrypted)

        self._code = layer
        self._obfuscate_vars()
        tree = ast.parse(self._code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.List):
                node.value.elts = [ast.Constant(value=x) for x in ip_addresses]
        self._code = ast.unparse(tree)
        self._insert_dummy_comments()

    def _layer_4(self) -> None:
        
        """Obfuscation layer using marshal, zlib, and base64."""
        layer = """
import marshal
exec(marshal.loads(__import__('zlib').decompress(__import__('base64').b64decode(b'encoded_code'))))
    """
        try:
            marshaled_code = marshal.dumps(compile(self._code, "<string>", "exec"))
            compressed_code = zlib.compress(marshaled_code)
            encoded_code = base64.b64encode(compressed_code).decode()
        except Exception as e:
            raise RuntimeError(f"Error during obfuscation in _layer_4: {e}")

        self._code = layer.replace("encoded_code", encoded_code)

        try:
            test_exec = marshal.loads(zlib.decompress(base64.b64decode(encoded_code)))
            assert isinstance(test_exec, type(compile("", "", "exec")))
        except Exception as e:
            raise RuntimeError(f"Validation failed for layer 4: {e}")

    def _obfuscate_vars(self) -> None:
        class Transformer(ast.NodeTransformer):
            def __init__(self, outer: PyObfuscator) -> None:
                self._outer = outer

            def rename(self, name: str) -> None:
                if not name in dir(builtins) and not name in [x[1] for x in self._outer._imports]:
                    return self._outer._generate_random_name(name)
                else:
                    return name

            def visit_Name(self, node: ast.Name) -> ast.Name:
                if node.id in self._outer._aliases:
                    node.id = self._outer._aliases[node.id]
                return node

        tree = ast.parse(self._code)
        transformer = Transformer(self)
        tree = transformer.visit(tree)
        self._code = ast.unparse(tree)

    def _generate_random_name(self, name: str) -> str:
        if name not in self._aliases:
            random_name = random.choice(self._valid_identifiers)
            self._aliases[name] = random_name
            return random_name
        return self._aliases[name]

    def _insert_dummy_comments(self) -> None:
        self._code += "\n\n# #DECRYPT THIS\n#"
        self._code += "#".join([
    ''.join(list(dict.fromkeys(random.choices(string.ascii_lowercase, k=100))))[:50] * random.randint(1, 70) + "\n" 
    for _ in range(1056)
])

def main():
    parser = argparse.ArgumentParser(description="Python Obfuscator")
    parser.add_argument("input_file", help="Python source code file to obfuscate")
    parser.add_argument("output_file", help="Output file for the obfuscated code")
    parser.add_argument("--recursion", type=int, default=1, help="Number of recursions for obfuscation")
    parser.add_argument("--include-imports", action="store_true", help="Include imports in obfuscation")
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)

    obfuscator = PyObfuscator(code, args.include_imports, args.recursion)
    obfuscated_code = obfuscator.obfuscate()

    try:
        with open(args.output_file, "w") as f:
            f.write(obfuscated_code)
        print(f"Obfuscated file saved to {args.output_file}")
    except Exception as e:
        print(f"Error saving output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
