"""Tests for the logger module."""

import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from backend.app.v1.logger.logs import setup_logger


@pytest.mark.unit
def test_setup_logger_default_parameters() -> None:
    """Test logger creation with default parameters."""
    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO


@pytest.mark.unit
def test_setup_logger_custom_name() -> None:
    """Test logger creation with custom name."""
    custom_name = "test_logger_custom"
    logger = setup_logger(name=custom_name)

    assert logger.name == custom_name


@pytest.mark.unit
@pytest.mark.parametrize(
    "log_level",
    [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
    ],
)
def test_setup_logger_custom_levels(log_level: int) -> None:
    """Test logger creation with various logging levels."""
    logger = setup_logger(level=log_level)

    assert logger.level == log_level


@pytest.mark.unit
def test_setup_logger_console_handler() -> None:
    """Test that console handler is added to logger."""
    logger = setup_logger()

    console_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
    assert len(console_handlers) >= 1
    assert console_handlers[0].formatter is not None


@pytest.mark.unit
def test_setup_logger_formatter_format() -> None:
    """Test that formatter has correct format string."""
    logger = setup_logger()

    console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    formatter = console_handler.formatter

    assert formatter is not None
    assert "%(asctime)s" in formatter._style._fmt
    assert "%(levelname)-8s" in formatter._style._fmt
    assert "%(name)s" in formatter._style._fmt
    assert "%(message)s" in formatter._style._fmt


@pytest.mark.unit
def test_setup_logger_formatter_datefmt() -> None:
    """Test that formatter has correct date format."""
    logger = setup_logger()

    console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    formatter = console_handler.formatter

    assert formatter is not None
    assert formatter.datefmt == "%Y-%m-%d %H:%M:%S"


@pytest.mark.unit
def test_setup_logger_file_handler() -> None:
    """Test logger creation with file logging."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        log_file = tmp.name

    try:
        logger = setup_logger(log_file=log_file)

        file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
        assert len(file_handlers) == 1
        assert file_handlers[0].baseFilename == log_file
    finally:
        Path(log_file).unlink(missing_ok=True)


@pytest.mark.unit
def test_setup_logger_rotating_file_handler_config() -> None:
    """Test that RotatingFileHandler has correct configuration."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        log_file = tmp.name

    try:
        logger = setup_logger(log_file=log_file)

        file_handler = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))
        assert file_handler.maxBytes == 5_000_000
        assert file_handler.backupCount == 3
    finally:
        Path(log_file).unlink(missing_ok=True)


@pytest.mark.unit
def test_setup_logger_no_duplicate_handlers() -> None:
    """Test that calling setup_logger multiple times doesn't add duplicate handlers."""
    logger_name = "test_no_duplicates"
    initial_handler_count = 0

    logger1 = setup_logger(name=logger_name)
    initial_handler_count = len(logger1.handlers)

    logger2 = setup_logger(name=logger_name)

    assert len(logger2.handlers) == initial_handler_count
    assert logger1 is logger2


@pytest.mark.unit
def test_setup_logger_logging_functionality() -> None:
    """Test that logger actually logs messages."""

    logger_name = "test_logging_functionality"
    logger = setup_logger(name=logger_name, level=logging.INFO)

    # Clear any existing handlers first
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add a custom handler to capture logs
    log_records = []

    class TestHandler(logging.Handler):
        def emit(self, record):
            log_records.append(record)

    test_handler = TestHandler()
    logger.addHandler(test_handler)

    test_message = "Test log message"
    logger.info(test_message)

    assert len(log_records) == 1
    assert log_records[0].getMessage() == test_message
    assert log_records[0].levelno == logging.INFO


@pytest.mark.unit
def test_setup_logger_file_handler_formatter() -> None:
    """Test that file handler has the same formatter as console handler."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".log") as tmp:
        log_file = tmp.name

    try:
        logger = setup_logger(log_file=log_file)

        console_handler = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
        file_handler = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))

        assert console_handler.formatter._style._fmt == file_handler.formatter._style._fmt
        assert console_handler.formatter.datefmt == file_handler.formatter.datefmt
    finally:
        Path(log_file).unlink(missing_ok=True)


@pytest.mark.unit
def test_setup_logger_without_log_file() -> None:
    """Test that no file handler is added when log_file is None."""
    logger = setup_logger(log_file=None)

    file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    assert len(file_handlers) == 0


@pytest.mark.unit
def test_setup_logger_returns_configured_instance() -> None:
    """Test that setup_logger returns a fully configured logger instance."""
    logger_name = "test_configured_instance"
    logger = setup_logger(name=logger_name, level=logging.DEBUG)

    assert isinstance(logger, logging.Logger)
    assert logger.name == logger_name
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0
