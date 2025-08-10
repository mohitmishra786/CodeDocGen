import textwrap
from pathlib import Path

from code_doc_gen.config import Config
from code_doc_gen.parsers.java_parser import JavaParser
from code_doc_gen.generator import DocumentationGenerator


def test_java_parser_methods(tmp_path: Path):
    src = tmp_path / "Sample.java"
    src.write_text(textwrap.dedent(
        """
        public class Sample {
            public int mul(int a, int b) { return a * b; }
            public static String greet(String name) { return "Hello, " + name; }
        }
        """
    ))
    cfg = Config()
    parser = JavaParser(cfg)
    parsed = parser.parse_file(src)
    names = sorted([f.name for f in parsed.functions])
    assert names == ["greet", "mul"]


def test_java_generator_inserts_javadoc(tmp_path: Path):
    src = tmp_path / "S.java"
    src.write_text(textwrap.dedent(
        """
        public class S { public int add(int a, int b) { return a + b; } }
        """
    ))
    cfg = Config()
    parser = JavaParser(cfg)
    functions = parser.parse_file(src).functions
    gen = DocumentationGenerator(cfg)
    docs = gen.generate_documentation(functions, "java")
    gen.apply_documentation_inplace(src, docs)
    out = src.read_text()
    assert "/**" in out and "@param" in out and "@return" in out
    # Ensure no double blank line before @param
    assert "*\n\n * @param" not in out

