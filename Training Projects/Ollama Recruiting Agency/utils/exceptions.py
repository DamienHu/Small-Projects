class ResumeProcessError(Exception):
    """Base exception for resume processing errors"""

    pass

class ExtractionError(ResumeProcessError):
    """Raised when resume extraction fails"""

    pass

class AnalysisError(ResumeProcessError):
    """raised when resume analysis fails"""

    pass

class MatchingError(ResumeProcessError):
    """Raised when job matching fails"""

    pass

class Screeningerror(ResumeProcessError):
    """Raised when candidate screening fails"""

    pass

class RecommendationError(ResumeProcessError):
    """Raised when generating recommedations fails"""

    pass