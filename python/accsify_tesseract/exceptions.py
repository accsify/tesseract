"""
Custom Exceptions for Accsify Tesseract.
========================================
Company: accsify
Copyright (C) 2026 accsify. All rights reserved.
"""

class TesseractError(Exception):
    """Base exception for all Accsify Tesseract errors."""
    pass


class EngineInitError(TesseractError):
    """Raised when the engine fails to initialize with a language model."""
    def __init__(self, message: str, language: str, datapath: str, code: int):
        super().__init__(message)
        self.language = language
        self.datapath = datapath
        self.code = code


class ImageLoadError(TesseractError):
    """Raised when an image cannot be read or decoded."""
    pass


class RecognitionError(TesseractError):
    """Raised when recognition fails on an image."""
    pass


class ModelDownloadError(TesseractError):
    """Raised when a traineddata model download fails."""
    pass


class ModelNotFoundError(TesseractError):
    """Raised when a required traineddata file is missing."""
    pass
