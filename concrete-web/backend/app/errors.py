class ModelUnavailableError(Exception):
    """Prediction requested before the model bundle was loaded."""


class PredictionError(Exception):
    """Unexpected failure while running inference."""
