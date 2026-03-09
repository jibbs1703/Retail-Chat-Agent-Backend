"""Tests for logger module."""

import logging
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

import pytest

from backend.app.v1.logger.logs import setup_logger


@pytest.mark.unit
def test_setup_logger_creates_logger() -> None:
    """Test that setup_logger creates a logger instance."""
    logger = setup_logger("test_logger_1")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_logger_1"


@pytest.mark.unit
def test_setup_logger_default_level() -> None:
    """Test that logger uses INFO level by default."""
    logger = setup_logger("test_logger_2")

    assert logger.level == logging.INFO


@pytest.mark.unit
def test_setup_logger_custom_level() -> None:
    """Test that logger respects custom logging levels."""
    logger_debug = setup_logger("test_logger_debug", level=logging.DEBUG)
    logger_warning = setup_logger("test_logger_warning", level=logging.WARNING)

    assert logger_debug.level == logging.DEBUG
    assert logger_warning.level == logging.WARNING


@pytest.mark.unit
def test_setup_logger_has_console_handler() -> None:
    """Test that logger has a console handler."""
    logger = setup_logger("test_logger_console")

    assert len(logger.handlers) > 0
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)


@pytest.mark.unit
def test_setup_logger_console_handler_formatter() -> None:
    """Test that console handler has correct formatter."""
    logger = setup_logger("test_logger_formatter")

    console_handler = next(
        (h for h in logger.handlers if isinstance(h, logging.StreamHandler)),
        None,
    )
    assert console_handler is not None
    assert console_handler.formatter is not None
    fmt = console_handler.formatter._fmt or ""
    assert "%(asctime)s" in fmt
    assert "%(levelname)-8s" in fmt
    assert "%(name)s" in fmt
    assert "%(message)s" in fmt


@pytest.mark.unit
def test_setup_logger_with_log_file() -> None:
    """Test that logger creates file handler when log_file is provided."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        logger = setup_logger("test_logger_file", log_file=str(log_file))

        assert any(isinstance(handler, RotatingFileHandler) for handler in logger.handlers)
        assert log_file.exists()


@pytest.mark.unit
def test_setup_logger_file_handler_configuration() -> None:
    """Test that file handler is configured with correct parameters."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        logger = setup_logger("test_logger_file_config", log_file=str(log_file))

        file_handler = next(
            (h for h in logger.handlers if isinstance(h, RotatingFileHandler)),
            None,
        )
        assert file_handler is not None
        assert file_handler.maxBytes == 5_000_000
        assert file_handler.backupCount == 3


@pytest.mark.unit
def test_setup_logger_prevents_duplicate_handlers() -> None:
    """Test that calling setup_logger twice doesn't duplicate handlers."""
    logger_name = "test_logger_duplicate_prevention"

    logger1 = setup_logger(logger_name)
    initial_handler_count = len(logger1.handlers)

    logger2 = setup_logger(logger_name)
    final_handler_count = len(logger2.handlers)

    assert initial_handler_count == final_handler_count
    assert logger1 is logger2


@pytest.mark.unit
def test_setup_logger_file_handler_formatter() -> None:
    """Test that file handler has correct formatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        logger = setup_logger("test_logger_file_formatter", log_file=str(log_file))

        file_handler = next(
            (h for h in logger.handlers if isinstance(h, RotatingFileHandler)),
            None,
        )
        assert file_handler is not None
        assert file_handler.formatter is not None
        fmt = file_handler.formatter._fmt or ""
        assert "%(asctime)s" in fmt
        assert "%(levelname)-8s" in fmt
        assert "%(name)s" in fmt
        assert "%(message)s" in fmt


@pytest.mark.unit
def test_setup_logger_logs_to_console(caplog) -> None:
    """Test that logger actually logs messages to console."""
    logger = setup_logger("test_logger_log_message", level=logging.INFO)

    with caplog.at_level(logging.INFO):
        logger.info("Test message")

    assert "Test message" in caplog.text


@pytest.mark.unit
def test_setup_logger_logs_to_file() -> None:
    """Test that logger actually logs messages to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        logger = setup_logger("test_logger_file_write", log_file=str(log_file))
        logger.info("Test file message")

        log_content = log_file.read_text()
        assert "Test file message" in log_content


@pytest.mark.unit
def test_setup_logger_respects_log_level() -> None:
    """Test that logger respects configured log level."""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_file = Path(tmpdir) / "test.log"

        logger = setup_logger(
            "test_logger_level_filter", level=logging.WARNING, log_file=str(log_file)
        )

        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")

        log_content = log_file.read_text()
        assert "Debug message" not in log_content
        assert "Info message" not in log_content
        assert "Warning message" in log_content


@pytest.mark.unit
def test_setup_logger_without_log_file() -> None:
    """Test that logger works without file handler."""
    logger = setup_logger("test_logger_no_file")

    file_handlers = [h for h in logger.handlers if isinstance(h, RotatingFileHandler)]
    assert len(file_handlers) == 0


@pytest.mark.unit
def test_setup_logger_default_name() -> None:
    """Test setup_logger with default name parameter."""
    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "backend.app.v1.logger.logs"
