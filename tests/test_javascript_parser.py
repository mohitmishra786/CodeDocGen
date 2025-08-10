import textwrap
from pathlib import Path

from code_doc_gen.config import Config
from code_doc_gen.parsers.javascript_parser import JavaScriptParser
from code_doc_gen.generator import DocumentationGenerator


def test_js_parser_function_declaration(tmp_path: Path):
    src = tmp_path / "a.js"
    src.write_text("function sum(a, b) { return a + b; }\n")
    cfg = Config()
    parser = JavaScriptParser(cfg)
    parsed = parser.parse_file(src)
    assert len(parsed.functions) == 1
    assert parsed.functions[0].name == "sum"
    assert [p.name for p in parsed.functions[0].parameters] == ["a", "b"]


def test_js_parser_arrow_and_class(tmp_path: Path):
    src = tmp_path / "b.js"
    src.write_text(textwrap.dedent(
        """
        const inc = (x) => x + 1;
        class C { doIt(x) { return x; } }
        """
    ))
    cfg = Config()
    parser = JavaScriptParser(cfg)
    parsed = parser.parse_file(src)
    names = sorted([f.name for f in parsed.functions])
    assert names == ["doIt", "inc"]


def test_js_generator_inserts_jsdoc(tmp_path: Path):
    src = tmp_path / "c.js"
    src.write_text("const inc = (x) => x + 1;\n")
    cfg = Config()
    parser = JavaScriptParser(cfg)
    functions = parser.parse_file(src).functions
    gen = DocumentationGenerator(cfg)
    docs = gen.generate_documentation(functions, "javascript")
    gen.apply_documentation_inplace(src, docs)
    out = src.read_text()
    assert "/**" in out and "@param" in out and "@returns" in out
    # Ensure no double blank line before @param
    assert "*\n\n * @param" not in out

