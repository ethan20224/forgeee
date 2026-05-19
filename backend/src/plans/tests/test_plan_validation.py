"""Unit tests for plan validation and helper functions."""

import pytest

from src.plans.service import _build_mock_plan, _strip_markdown_fences, validate_plan


def test_strip_markdown_json_fence():
    raw = '```json\n{"key": "value"}\n```'
    assert _strip_markdown_fences(raw) == '{"key": "value"}'


def test_strip_markdown_bare_fence():
    raw = '```\n{"key": "value"}\n```'
    assert _strip_markdown_fences(raw) == '{"key": "value"}'


def test_strip_no_fence():
    raw = '{"key": "value"}'
    assert _strip_markdown_fences(raw) == '{"key": "value"}'


def test_mock_plan_validates():
    mock = _build_mock_plan()
    result = validate_plan(mock)
    assert result.program_name == "Foundation Builder (Mock)"
    assert len(result.weeks) == 13
    total_days = sum(len(w.days) for w in result.weeks)
    assert total_days == 91


def test_validate_plan_wrong_week_count():
    mock = _build_mock_plan()
    mock["weeks"] = mock["weeks"][:5]
    with pytest.raises(ValueError, match="13 weeks"):
        validate_plan(mock)


def test_validate_plan_unknown_task_id():
    mock = _build_mock_plan()
    mock["weeks"][0]["days"][0]["tasks"][0]["library_task_id"] = "fake-999"
    with pytest.raises(ValueError, match="Unknown task ID"):
        validate_plan(mock)


def test_validate_plan_missing_fields():
    with pytest.raises(Exception):
        validate_plan({"program_name": "test"})
