from typing import Any, Dict, Iterator

from pygments.lexer import DelegatingLexer
from pygments.lexers import PythonLexer
from pygments.token import Name, _TokenType
from sphinx.application import Sphinx
from sphinx.highlighting import lexers
from tree_sitter import Language, Node, Parser
import tree_sitter_python


KNOWN_MODULES = {
    "ablate",
    "ablate.sources",
    "ablate.queries",
    "ablate.blocks",
    "ablate.exporters",
}


class TreeSitterOverlayLexer(PythonLexer):
    def __init__(self, **options: Any) -> None:
        super().__init__(**options)
        self.parser = Parser(Language(tree_sitter_python.language()))

    def get_tokens_unprocessed(
        self,
        text: str,
    ) -> Iterator[tuple[int, _TokenType, str]]:
        byte_text = text.encode("utf-8")
        tree = self.parser.parse(byte_text)
        spans: dict[tuple[int, str], _TokenType] = {}

        def classify(node: Node, value: str) -> _TokenType:
            p = node.parent
            gp = p.parent if p else None

            if (
                p
                and p.type == "attribute"
                and gp
                and gp.type == "call"
                and p == gp.child_by_field_name("function")
                and node == p.child_by_field_name("attribute")
            ):
                return Name.Function if value[0].islower() else Name.Class

            if p and p.type == "call" and node == p.child_by_field_name("function"):
                return Name.Function if value[0].islower() else Name.Class

            if p and p.type == "attribute":
                if node == p.child_by_field_name("object"):
                    return Name.Namespace
                if node == p.child_by_field_name("attribute"):
                    return Name.Namespace if value.islower() else Name.Class

            if p and "import" in p.type:
                return Name.Namespace

            return Name.Class if value[0].isupper() else Name

        def walk(node: Node) -> None:
            if node.type == "identifier":
                val = byte_text[node.start_byte : node.end_byte].decode(
                    "utf-8", errors="ignore"
                )
                spans.setdefault((node.start_byte, val), classify(node, val))
            for child in node.children:
                walk(child)

        walk(tree.root_node)

        for index, token, val in super().get_tokens_unprocessed(text):
            yield index, spans.get((index, val), token), val


class AblateLexer(DelegatingLexer):
    name = "ablate-python"
    aliases = ["ablate-python"]

    _KNOWN_MODULE_PARTS = {
        "ablate",
        "sources",
        "queries",
        "blocks",
        "exporters",
        "ablate.sources",
        "ablate.queries",
        "ablate.blocks",
        "ablate.exporters",
    }

    def __init__(self, **options: Any) -> None:
        super().__init__(PythonLexer, TreeSitterOverlayLexer, **options)

    def get_tokens_unprocessed(
        self,
        text: str,
    ) -> Iterator[tuple[int, _TokenType, str]]:
        for index, token, val in super().get_tokens_unprocessed(text):
            if token in {Name, Name.Namespace} and val in self._KNOWN_MODULE_PARTS:
                yield index, Name.Class, val
            else:
                yield index, token, val


def setup(app: Sphinx) -> Dict[str, Any]:
    lexers["python"] = AblateLexer(startinline=True)
    return {
        "version": "0.1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
