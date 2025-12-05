# Python Code Obfuscator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A powerful multi-layer Python code obfuscator designed to protect your source code from reverse engineering and unauthorized access.

## Features

- **Multi-Layer Obfuscation**: Applies 4 different obfuscation techniques
- **Recursive Protection**: Apply layers multiple times for stronger security
- **No External Dependencies**: Uses only Python standard library
- **Variable Name Obfuscation**: Replaces variable names with Unicode identifiers
- **Code Compression**: Reduces code size with zlib compression
- **Multiple Encoding Schemes**: Base64, XOR, IP encoding, and marshal
- **Easy to Use**: Simple command-line interface

## Obfuscation Techniques

### Layer 1: Base64 + Zlib
- Compresses code with zlib
- Encodes with base64
- Splits data into multiple parts with random padding
- Uses string slicing for reassembly

### Layer 2: XOR Encryption
- Compresses with zlib
- XOR encrypts all bytes with a random key (1-100)
- Runtime brute-forces the key
- Decodes and executes when key is found

### Layer 3: IP Address Encoding
- Converts binary data to fake IP addresses
- Disguises code as network configuration
- Each IP represents 4 bytes of data

### Layer 4: Marshal + Compression
- Compiles code to Python bytecode
- Serializes with marshal
- Compresses and encodes
- Most resistant to static analysis

## Installation

### From Source
```bash
git clone https://github.com/Lawxsz/Py-obfuscator.git
cd Py-obfuscator
pip install .
```

### For Development
```bash
git clone https://github.com/Lawxsz/Py-obfuscator.git
cd Py-obfuscator
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage
```bash
python obf.py input.py output.py
```

### With Recursion (Stronger Protection)
```bash
python obf.py input.py output.py --recursion 2
```

### Include Import Statements
```bash
python obf.py input.py output.py --include-imports
```

### Full Example
```bash
python obf.py my_script.py obfuscated_script.py --recursion 3 --include-imports
```

### Using as Installed Command
After installation with `pip install .`:
```bash
pyobf input.py output.py --recursion 2
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `input_file` | Python source file to obfuscate | Required |
| `output_file` | Output file for obfuscated code | Required |
| `--recursion N` | Number of times to apply layers | 1 |
| `--include-imports` | Include import statements in output | False |

## Example

### Before Obfuscation
```python
def greet(name):
    """Greet someone by name."""
    message = f"Hello, {name}!"
    print(message)
    return message

greet("World")
```

### After Obfuscation
The code becomes unreadable with multiple layers of encoding, compression, and variable name obfuscation. The output will contain:
- Encoded strings
- XOR encrypted bytes
- Fake IP addresses
- Random Unicode variable names
- Thousands of dummy comments

## Requirements

- Python 3.9 or higher
- No external dependencies (uses only standard library)

## Recommended Python Version

Python **3.10.6** or higher for best compatibility.

## Use Cases

- **Source Code Protection**: Protect proprietary algorithms
- **License Enforcement**: Make code harder to crack or modify
- **Intellectual Property**: Protect trade secrets in distributed code
- **Educational**: Learn about code obfuscation techniques

## Important Notes

### Security Considerations
- Obfuscation is NOT encryption - determined attackers can still reverse engineer
- Use in combination with other security measures
- Obfuscated code will be slower than original code
- Do not rely on obfuscation alone for critical security

### Limitations
- Cannot protect against runtime analysis or debugging
- May break code that uses introspection (inspect module)
- Some IDEs may have trouble with heavily obfuscated code
- Increased file size due to dummy comments

### Legal Use Only
This tool is intended for legitimate source code protection. Users are responsible for ensuring their use complies with applicable laws and regulations.

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black obf.py

# Lint code
flake8 obf.py

# Type checking
mypy obf.py
```

## Project Structure

```
Py-obfuscator/
├── obf.py                 # Main obfuscator code
├── setup.py               # Installation script
├── pyproject.toml         # Project configuration
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── LICENSE                # MIT License
├── README.md              # This file
├── CHANGELOG.md           # Version history
└── tests/                 # Test directory (future)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

- **Blank-C** - Original concept and development
- **Lawxsz** - Development and maintenance

## Contact

- Telegram: [@lawxsz](https://t.me/lawxsz)
- Telegram Dev: [@lawxszdev](https://t.me/lawxszdev)
- Website: [https://prysmax.xyz](https://prysmax.xyz)

## Acknowledgments

- Thanks to the Python community for excellent documentation
- Inspired by various code protection techniques

## Behavior Examples

### Without Obfuscation
![Without OBF](https://github.com/Lawxsz/Py-obfuscator/assets/116668706/033daecf-117b-4838-bc09-cc3cf8b750cf)

### With Obfuscation
![With OBF](https://github.com/Lawxsz/Py-obfuscator/assets/116668706/52c9d17f-db2f-48d3-8ad6-a9d428d616a6)

---

**Disclaimer**: This tool is provided as-is for legitimate code protection purposes. The authors are not responsible for any misuse of this software.
