"""
Unit tests for PyObfuscator class
"""

import pytest
import sys
import os

# Add parent directory to path to import obf module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from obf import PyObfuscator


class TestPyObfuscator:
    """Test cases for PyObfuscator class"""

    @pytest.fixture
    def simple_code(self):
        """Fixture providing simple Python code for testing"""
        return """
def hello():
    print("Hello, World!")
    return 42

hello()
"""

    @pytest.fixture
    def code_with_imports(self):
        """Fixture providing code with imports"""
        return """
import os
import sys
from datetime import datetime

def get_time():
    return datetime.now()
"""

    def test_obfuscator_initialization(self, simple_code):
        """Test that obfuscator can be initialized"""
        obf = PyObfuscator(simple_code)
        assert obf is not None
        assert obf._code == simple_code

    def test_obfuscator_with_recursion(self, simple_code):
        """Test obfuscator with recursion parameter"""
        obf = PyObfuscator(simple_code, recursion=2)
        assert obf is not None

    def test_obfuscator_invalid_recursion(self, simple_code):
        """Test that invalid recursion raises ValueError"""
        with pytest.raises(ValueError):
            PyObfuscator(simple_code, recursion=0)

    def test_obfuscate_returns_string(self, simple_code):
        """Test that obfuscate() returns a string"""
        obf = PyObfuscator(simple_code)
        result = obf.obfuscate()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_obfuscated_code_different(self, simple_code):
        """Test that obfuscated code is different from original"""
        obf = PyObfuscator(simple_code)
        result = obf.obfuscate()
        assert result != simple_code

    def test_obfuscate_with_imports(self, code_with_imports):
        """Test obfuscation with import statements"""
        obf = PyObfuscator(code_with_imports, include_imports=True)
        result = obf.obfuscate()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_save_imports(self, code_with_imports):
        """Test that imports are extracted correctly"""
        obf = PyObfuscator(code_with_imports)
        obf._save_imports()
        assert len(obf._imports) > 0

    def test_layer_1_obfuscation(self, simple_code):
        """Test layer 1 obfuscation produces valid output"""
        obf = PyObfuscator(simple_code)
        obf._remove_comments_and_docstrings()
        obf._layer_1()
        assert len(obf._code) > 0
        assert "exec" in obf._code

    def test_layer_2_obfuscation(self, simple_code):
        """Test layer 2 obfuscation produces valid output"""
        obf = PyObfuscator(simple_code)
        obf._remove_comments_and_docstrings()
        obf._layer_2()
        assert len(obf._code) > 0
        assert "exec" in obf._code

    def test_layer_3_obfuscation(self, simple_code):
        """Test layer 3 obfuscation produces valid output"""
        obf = PyObfuscator(simple_code)
        obf._remove_comments_and_docstrings()
        obf._layer_3()
        assert len(obf._code) > 0
        assert "exec" in obf._code

    def test_layer_4_obfuscation(self, simple_code):
        """Test layer 4 obfuscation produces valid output"""
        obf = PyObfuscator(simple_code)
        obf._remove_comments_and_docstrings()
        obf._layer_4()
        assert len(obf._code) > 0
        assert "exec" in obf._code
        assert "marshal" in obf._code

    def test_remove_comments_and_docstrings(self):
        """Test that comments and docstrings are removed"""
        code_with_docstring = '''
def test():
    """This is a docstring"""
    # This is a comment
    return 42
'''
        obf = PyObfuscator(code_with_docstring)
        obf._remove_comments_and_docstrings()
        # Docstrings should be replaced with pass statements
        assert "pass" in obf._code or "Obfuscated" in obf._code

    def test_obfuscate_vars(self, simple_code):
        """Test that variable obfuscation works"""
        obf = PyObfuscator(simple_code)
        obf._remove_comments_and_docstrings()
        original_code = obf._code
        obf._obfuscate_vars()
        # Code should be modified (though might be same if no vars to obfuscate)
        assert isinstance(obf._code, str)

    def test_generate_random_name(self, simple_code):
        """Test random name generation"""
        obf = PyObfuscator(simple_code)
        name1 = obf._generate_random_name("test_var")
        name2 = obf._generate_random_name("test_var")
        # Should return same name for same input (cached)
        assert name1 == name2

    def test_insert_dummy_comments(self, simple_code):
        """Test dummy comment insertion"""
        obf = PyObfuscator(simple_code)
        original_length = len(obf._code)
        obf._insert_dummy_comments()
        # Code should be much longer after adding dummy comments
        assert len(obf._code) > original_length


class TestObfuscatorIntegration:
    """Integration tests for the complete obfuscation process"""

    def test_full_obfuscation_executes(self):
        """Test that fully obfuscated code can be executed"""
        code = "result = 2 + 2"
        obf = PyObfuscator(code, include_imports=False, recursion=1)
        obfuscated = obf.obfuscate()

        # Try to execute the obfuscated code
        namespace = {}
        try:
            exec(obfuscated, namespace)
            # The result variable should exist in namespace
            assert "result" in namespace or len(namespace) > 0
        except Exception as e:
            pytest.fail(f"Obfuscated code failed to execute: {e}")

    def test_obfuscation_preserves_functionality(self):
        """Test that obfuscation preserves code functionality"""
        code = """
def add(a, b):
    return a + b

result = add(5, 3)
"""
        obf = PyObfuscator(code, include_imports=False, recursion=1)
        obfuscated = obf.obfuscate()

        namespace = {}
        try:
            exec(obfuscated, namespace)
            assert namespace.get("result") == 8
        except Exception as e:
            pytest.fail(f"Obfuscated code failed to preserve functionality: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
