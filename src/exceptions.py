class UserNotFoundError(Exception):
    """Raised when the worker does not exist in the database."""
    pass

class BusinessError(Exception):
    """Generic base class for all business rule violations."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

# Exceções específicas que herdam de BusinessError
class SequenciaInvalidaError(BusinessError):
    """
    Raised when the clock-in order is incorrect.
    Ex: Clocking out without an open clock-in for the day.
    """
    pass

class BatidaDuplicadaError(BusinessError):
    """
    Raised to prevent fraud or double clicks.
    Ex: Trying to clock in twice within a 1-minute interval.
    """
    pass