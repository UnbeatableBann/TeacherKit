from app.domain.enums import Subject
from app.evaluators.base import SubjectPlugin
from app.evaluators.english.plugin import EnglishPlugin
from app.evaluators.general.plugin import GeneralPlugin
from app.evaluators.history.plugin import HistoryPlugin
from app.evaluators.mathematics.plugin import MathematicsPlugin
from app.evaluators.science.plugin import SciencePlugin

PLUGINS: dict[Subject, SubjectPlugin] = {
    Subject.MATHEMATICS: MathematicsPlugin(),
    Subject.SCIENCE: SciencePlugin(),
    Subject.ENGLISH: EnglishPlugin(),
    Subject.HISTORY: HistoryPlugin(),
    Subject.GENERAL: GeneralPlugin(),
}


def get_plugin(subject: Subject) -> SubjectPlugin:
    return PLUGINS.get(subject, PLUGINS[Subject.GENERAL])
