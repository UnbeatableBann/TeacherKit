import os

plugins = {
    'science': ['OptionStrategy', 'ExactStrategy', 'ConceptStrategy', 'FactualStrategy', 'SemanticStrategy'],
    'mathematics': ['OptionStrategy', 'ExactStrategy', 'NumericStrategy', 'FormulaStrategy', 'ConceptStrategy', 'SemanticStrategy'],
    'english': ['OptionStrategy', 'ExactStrategy', 'ConceptStrategy', 'SemanticStrategy', 'GrammarStrategy'],
    'history': ['OptionStrategy', 'ExactStrategy', 'ConceptStrategy', 'FactualStrategy', 'SemanticStrategy'],
    'general': ['OptionStrategy', 'ExactStrategy', 'NumericStrategy', 'ConceptStrategy', 'SemanticStrategy']
}

template = """from app.evaluators.base import SubjectPlugin
from app.strategies.core import Strategy
from app.strategies.core import (
    {imports}
)
from app.strategies.llm import LLMStrategy

class {ClassName}(SubjectPlugin):
    name = "{name}"

    @property
    def strategies(self) -> list[Strategy]:
        return [
            {strategies},
            LLMStrategy(),
        ]
"""

for name, strats in plugins.items():
    class_name = name.capitalize() + 'Plugin'
    imports = ',\n    '.join(strats)
    strategies = '(),\n            '.join(strats) + '()'
    content = template.format(imports=imports, ClassName=class_name, name=name, strategies=strategies)
    with open(f'app/evaluators/{name}/plugin.py', 'w') as f:
        f.write(content)
