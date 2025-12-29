from .python_gen import PythonGenerator
from .java_gen import JavaGenerator
from .rust_gen import RustGenerator
from .go_gen import GoGenerator
from .cpp_gen import CppGenerator
from .js_gen import JavaScriptGenerator

_GENERATORS = {
    "python": PythonGenerator(),
    "java": JavaGenerator(),
    "rust": RustGenerator(),
    "go": GoGenerator(),
    "golang": GoGenerator(),  # 兼容别名
    "cpp": CppGenerator(),
    "js": JavaScriptGenerator(),
}

def get_generator(lang: str):
    lang = (lang or "").strip().lower()
    if lang not in _GENERATORS:
        raise ValueError(f"no generator for lang={lang}")
    return _GENERATORS[lang]

