"""
Python Code Obfuscator

A multi-layer obfuscation tool that protects Python source code through
various encoding and transformation techniques.

Author: Blank-C and Lawxsz
License: MIT
"""

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
import logging
from typing import List, Tuple, Optional, Callable

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Constants for Unicode identifiers
MIN_UNICODE_IDENTIFIER = 256
MAX_UNICODE_IDENTIFIER = 0x24976

# Constants for obfuscation layers
XOR_KEY_MIN = 1
XOR_KEY_MAX = 100
DUMMY_COMMENT_COUNT = 1056
RANDOM_STRING_MIN_LENGTH = 5
RANDOM_STRING_MAX_LENGTH = 100
RANDOM_STRING_LENGTH = 100
MAX_STRING_REPETITIONS = 70
IP_BYTES_PER_ADDRESS = 4

class PyObfuscator:
    """
    Multi-layer Python code obfuscator for source code protection.

    This class applies various obfuscation techniques to Python source code including:
    - Base64 encoding with zlib compression
    - XOR encryption with dynamic key discovery
    - IP address encoding scheme
    - Marshal serialization
    - Variable name obfuscation using Unicode identifiers
    - Comment and docstring removal
    - Dummy comment injection

    The obfuscation layers are applied in random order and can be recursively
    applied multiple times for stronger protection.

    Attributes:
        _code (str): The Python source code being obfuscated
        _imports (List[Tuple]): Extracted import statements from the code
        _aliases (dict): Mapping of original to obfuscated variable names
        _valid_identifiers (List[str]): Valid Unicode characters for identifiers

    Args:
        code: Python source code to obfuscate
        include_imports: Whether to prepend import statements to output (default: False)
        recursion: Number of times to apply obfuscation layers (default: 1, min: 1)

    Raises:
        ValueError: If recursion is less than 1

    Example:
        >>> with open('script.py', 'r') as f:
        ...     code = f.read()
        >>> obfuscator = PyObfuscator(code, recursion=2)
        >>> obfuscated = obfuscator.obfuscate()
    """

    def __init__(self, code: str, include_imports: bool = False, recursion: int = 1) -> None:
        self._code = code
        self._imports: List[Tuple[Optional[str], str]] = []
        self._aliases: dict = {}
        self._valid_identifiers: List[str] = [
            chr(i) for i in range(MIN_UNICODE_IDENTIFIER, MAX_UNICODE_IDENTIFIER)
            if chr(i).isidentifier()
        ]

        # Options
        self.__include_imports = include_imports
        if recursion < 1:
            raise ValueError("Recursion length cannot be less than 1")
        else:
            self.__recursion = recursion
            logger.debug(f"Initialized PyObfuscator with recursion={recursion}")

    def obfuscate(self) -> str:
        """
        Apply all obfuscation layers to the source code.

        This method orchestrates the obfuscation process by:
        1. Removing comments and docstrings
        2. Extracting import statements
        3. Randomly shuffling obfuscation layers
        4. Applying each layer sequentially
        5. Optionally prepending imports

        The layers are applied in random order, but layer_3 is never last
        (as it would break execution).

        Returns:
            str: The obfuscated Python code

        Note:
            The obfuscation process is deterministic within a single call
            but varies between calls due to random shuffling.
        """
        logger.info("Starting obfuscation process...")
        self._remove_comments_and_docstrings()
        self._save_imports()

        layers: List[Callable[[], None]] = [
            self._layer_1,
            self._layer_2,
            self._layer_3,
            self._layer_4
        ] * self.__recursion
        random.shuffle(layers)

        # Ensure layer_3 is never last (it needs to be wrapped)
        if layers[-1] == self._layer_3:
            for index, layer in enumerate(layers):
                if layer != self._layer_3:
                    layers[index] = self._layer_3
                    layers[-1] = layer
                    break

        logger.info(f"Applying {len(layers)} obfuscation layers...")
        for layer in layers:
            layer()

        if self.__include_imports:
            self._prepend_imports()

        logger.info("Obfuscation completed successfully")
        return self._code

    def _remove_comments_and_docstrings(self) -> None:
        """
        Remove comments and docstrings from the code using AST manipulation.

        This method parses the code into an AST, identifies all docstrings
        (module-level, function, and class docstrings) and replaces them
        with pass statements to maintain valid Python syntax.

        The removal helps reduce code size and removes documentation that
        could help reverse engineering.
        """
        tree = ast.parse(self._code)
        # Add a module docstring placeholder
        tree.body.insert(0, ast.Expr(
                    value=ast.Constant("Obfuscated Python Code")
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
        """
        Extract and save all import statements from the code.

        This method recursively walks the AST to find all import and
        import-from statements, storing them for later use. The imports
        are sorted by length (longest first) to handle complex imports first.
        """
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
        """
        Prepend saved import statements to the obfuscated code.

        This reconstructs import statements from the saved imports and
        adds them to the beginning of the obfuscated code, ensuring
        all dependencies are available when the code executes.
        """
        for module, submodule in self._imports:
            if module is not None:
                statement = f"from {module} import {submodule}\n"
            else:
                statement = f"import {submodule}\n"
            self._code = statement + self._code

    def _layer_1(self) -> None:
        """
        Apply base64 + zlib compression obfuscation layer.

        This layer:
        1. Compresses the code with zlib
        2. Encodes with base64
        3. Splits the encoded string into 4 parts
        4. Wraps each part with random padding
        5. Uses string slicing to extract the actual data
        6. Obfuscates variable names
        7. Adds dummy comments

        The resulting code reassembles and executes the original via exec().
        """
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
                before = "".join(random.choices(string.ascii_letters, k=random.randint(RANDOM_STRING_MIN_LENGTH, RANDOM_STRING_MAX_LENGTH)))
                after = "".join(random.choices(string.ascii_letters, k=random.randint(RANDOM_STRING_MIN_LENGTH, RANDOM_STRING_MAX_LENGTH)))
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
        """
        Apply XOR encryption with key discovery obfuscation layer.

        This layer:
        1. Compresses the code with zlib
        2. XOR encrypts all bytes with a random key (1-100)
        3. Inserts two validation bytes at random positions
        4. The deobfuscator brute-forces the key by testing XOR values
        5. When correct key is found, decodes and executes

        This creates a cryptographic puzzle that must be solved at runtime.
        """
        layer = """
encrypted = []
for i in range(1, 100):
    if encrypted[in_loc] ^ i == encrypted[re_loc]:
        exec(__import__('zlib').decompress(bytes(map(lambda x: x ^ i, encrypted[:in_loc] + encrypted[in_loc+1:re_loc] + encrypted[re_loc+1:]))))
        break
"""
        key = random.randint(XOR_KEY_MIN, XOR_KEY_MAX)
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
        """
        Apply IP address encoding obfuscation layer.

        This layer:
        1. Compresses and base64 encodes the code
        2. Converts byte data into fake IP addresses (4 bytes = 1 IP)
        3. Stores IPs as strings in a list
        4. Runtime decodes IPs back to bytes, decompresses, and executes

        This disguises binary data as network addresses, making the code
        look like network configuration rather than executable code.
        """
        layer = """
ip_table = []
data = list([int(x) for item in [value.split(".") for value in ip_table] for x in item])
exec(compile(__import__('zlib').decompress(__import__('base64').b64decode(bytes(data))), '<(*3*)>', 'exec'))
"""
        def bytes2ip(data: bytes) -> List[str]:
            """Convert bytes to IP address strings (4 bytes per IP)."""
            ip_addresses = []
            for index in range(0, len(data), IP_BYTES_PER_ADDRESS):
                ip_bytes = data[index:index+IP_BYTES_PER_ADDRESS]
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
        """
        Apply marshal + zlib + base64 obfuscation layer.

        This layer:
        1. Compiles the code to bytecode
        2. Serializes bytecode with marshal
        3. Compresses with zlib
        4. Encodes with base64
        5. Validates the encoding worked correctly

        This is one of the strongest layers as it converts Python source
        to compiled bytecode, making static analysis much harder.

        Raises:
            RuntimeError: If obfuscation or validation fails
        """
        layer = """
import marshal
exec(marshal.loads(__import__('zlib').decompress(__import__('base64').b64decode(b'encoded_code'))))
    """
        try:
            marshaled_code = marshal.dumps(compile(self._code, "<string>", "exec"))
            compressed_code = zlib.compress(marshaled_code)
            encoded_code = base64.b64encode(compressed_code).decode()
        except Exception as e:
            logger.error(f"Error during obfuscation in _layer_4: {e}")
            raise RuntimeError(f"Error during obfuscation in _layer_4: {e}")

        self._code = layer.replace("encoded_code", encoded_code)

        # Validate the obfuscation worked
        try:
            test_exec = marshal.loads(zlib.decompress(base64.b64decode(encoded_code)))
            assert isinstance(test_exec, type(compile("", "", "exec")))
        except Exception as e:
            logger.error(f"Validation failed for layer 4: {e}")
            raise RuntimeError(f"Validation failed for layer 4: {e}")

    def _obfuscate_vars(self) -> None:
        """
        Obfuscate variable names using Unicode identifiers.

        This method walks the AST and replaces variable names with random
        Unicode characters that are valid Python identifiers. Built-in names
        and imported module names are preserved.

        The obfuscation makes code extremely difficult to read while
        maintaining functionality.
        """
        class Transformer(ast.NodeTransformer):
            def __init__(self, outer: PyObfuscator) -> None:
                self._outer = outer

            def rename(self, name: str) -> str:
                """Rename a variable to a random Unicode identifier."""
                if not name in dir(builtins) and not name in [x[1] for x in self._outer._imports]:
                    return self._outer._generate_random_name(name)
                else:
                    return name

            def visit_Name(self, node: ast.Name) -> ast.Name:
                """Visit Name nodes and replace with obfuscated names."""
                if node.id in self._outer._aliases:
                    node.id = self._outer._aliases[node.id]
                return node

        tree = ast.parse(self._code)
        transformer = Transformer(self)
        tree = transformer.visit(tree)
        self._code = ast.unparse(tree)

    def _generate_random_name(self, name: str) -> str:
        """
        Generate or retrieve a random Unicode identifier for a variable name.

        Args:
            name: Original variable name

        Returns:
            str: Random Unicode identifier (cached if previously generated)
        """
        if name not in self._aliases:
            random_name = random.choice(self._valid_identifiers)
            self._aliases[name] = random_name
            return random_name
        return self._aliases[name]

    def _insert_dummy_comments(self) -> None:
        """
        Insert dummy comments at the end of the code.

        Adds a large block of random, meaningless comments to inflate
        the file size and further obfuscate the code structure. This makes
        manual analysis more tedious and automated analysis slower.
        """
        self._code += "\n\n# Obfuscated code - Do not modify\n#"
        self._code += "#".join([
            ''.join(list(dict.fromkeys(random.choices(string.ascii_lowercase, k=RANDOM_STRING_LENGTH))))[:50] * random.randint(1, MAX_STRING_REPETITIONS) + "\n"
            for _ in range(DUMMY_COMMENT_COUNT)
        ])

def main() -> None:
    """
    Main entry point for the command-line obfuscator tool.

    Parses command-line arguments, reads the input Python file,
    applies obfuscation, and writes the result to the output file.

    Command-line arguments:
        input_file: Path to Python source file to obfuscate
        output_file: Path to write obfuscated code
        --recursion: Number of times to apply obfuscation layers (default: 1)
        --include-imports: Include import statements in output

    Exit codes:
        0: Success
        1: File I/O error
        2: Obfuscation error
    """
    parser = argparse.ArgumentParser(
        description="Python Code Obfuscator - Protect your Python source code",
        epilog="Example: python obf.py input.py output.py --recursion 2 --include-imports"
    )
    parser.add_argument("input_file", help="Python source code file to obfuscate")
    parser.add_argument("output_file", help="Output file for the obfuscated code")
    parser.add_argument(
        "--recursion",
        type=int,
        default=1,
        help="Number of recursions for obfuscation (default: 1, min: 1)"
    )
    parser.add_argument(
        "--include-imports",
        action="store_true",
        help="Include import statements in the obfuscated output"
    )
    args = parser.parse_args()

    # Read input file
    try:
        logger.info(f"Reading input file: {args.input_file}")
        with open(args.input_file, "r", encoding="utf-8") as f:
            code = f.read()
    except FileNotFoundError:
        logger.error(f"Input file not found: {args.input_file}")
        sys.exit(1)
    except PermissionError:
        logger.error(f"Permission denied reading file: {args.input_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        sys.exit(1)

    # Obfuscate the code
    try:
        obfuscator = PyObfuscator(code, args.include_imports, args.recursion)
        obfuscated_code = obfuscator.obfuscate()
    except ValueError as e:
        logger.error(f"Invalid argument: {e}")
        sys.exit(2)
    except Exception as e:
        logger.error(f"Error during obfuscation: {e}")
        sys.exit(2)

    # Write output file
    try:
        logger.info(f"Writing output file: {args.output_file}")
        with open(args.output_file, "w", encoding="utf-8") as f:
            f.write(obfuscated_code)
        logger.info(f"✓ Obfuscation complete! Output saved to: {args.output_file}")
    except PermissionError:
        logger.error(f"Permission denied writing file: {args.output_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error saving output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
