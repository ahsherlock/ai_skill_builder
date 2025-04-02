from .professor import professor_agent
from .advisor import advisor_agent
from .librarian import librarian_agent
from .assistant import teaching_assistant_agent
from .resume import resume_scanner_agent
from .quiz import quiz_generator_agent
from .analyzer import quiz_analyzer_agent
from .module import module_generator_agent

__all__ = [
    "professor_agent",
    "advisor_agent",
    "librarian_agent",
    "teaching_assistant_agent",
    "resume_scanner_agent",
    "quiz_generator_agent",
    "quiz_analyzer_agent",
    "module_generator_agent",
]