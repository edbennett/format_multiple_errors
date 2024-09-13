#!/usr/bin/env python3

"""Tests for formatting of Pandas DataFrames."""

import pandas as pd
import pytest

from format_multiple_errors import (
    format_dataframe_errors,
    ColumnSpec,
    format_column_errors,
)


@pytest.fixture(name="df")
def fixture_dataframe():
    """Generate a DataFrame of test data."""
    return pd.DataFrame(
        [
            {
                "a": 3,
                "b": 1,
                "c_value": 4.159,
                "c_error": 0.265,
                "c": "4.16(26)",
                "d_value": 3.589,
                "d_upper": 0.793,
                "d_lower": 0.238,
                "d_asymmetric": (0.793, 0.238),
                "d_systematic": 0.462,
                "d": "3.59(+79/-24)(46)",
            },
            {
                "a": 2,
                "b": 7,
                "c_value": 1.828,
                "c_error": 0.182,
                "c": "1.83(18)",
                "d_value": 8.459,
                "d_upper": 0.045,
                "d_lower": 0.235,
                "d_asymmetric": (0.045, 0.235),
                "d_systematic": 0.360,
                "d": "8.459(+45/-235)(360)",
            },
        ]
    )


def test_format_column_names(df):
    """Test that formatting a Series given a DataFrame and the column names works,
    including if a tuple of names is given for an asymmetric error."""
    result = format_column_errors(
        "d_value", ("d_upper", "d_lower"), "d_systematic", df=df, abbreviate=True
    )
    assert result.equals(df["d"])


def test_format_column_names_tuple(df):
    """Test that formatting a Series given a DataFrame and the column names works,
    if one column is an asymmetric error stored as tuples."""
    result = format_column_errors(
        "d_value", "d_asymmetric", "d_systematic", df=df, abbreviate=True
    )
    assert result.equals(df["d"])


def test_format_column_names_invalid_value(df):
    """Test that formatting a Series given a DataFrame fails if the value name
    looks wrong."""
    with pytest.raises(TypeError):
        format_column_errors(None, df=df)


def test_format_column_names_invalid_error(df):
    """Test that formatting a Series given a DataFrame fails if one of the error names
    looks wrong."""
    with pytest.raises(TypeError):
        format_column_errors("a", None, df)


def test_format_column_values(df):
    """Test that formatting a Series works given the input as Series,
    including if one uncertainty is specified as a tuple of Series."""
    result = format_column_errors(
        df["d_value"],
        (df["d_upper"], df["d_lower"]),
        df["d_systematic"],
        abbreviate=True,
    )
    assert result.equals(df["d"])


def test_format_column_values_tuple(df):
    """Test that formatting a Series works given the input as Series,
    including if one Series contains tuples representing asymmetric errors."""
    result = format_column_errors(
        df["d_value"], df["d_asymmetric"], df["d_systematic"], abbreviate=True
    )
    assert result.equals(df["d"])


def test_format_dataframe_names(df):
    """Test that formatting an entire DataFrame works correctly,
    given uncertainties specified as lists or tuples."""
    columns = [
        "a",
        "b",
        ("c_value", "c_error"),
        ["d_value", ("d_upper", "d_lower"), "d_systematic"],
    ]
    result = format_dataframe_errors(df, columns, abbreviate=True)
    assert result.equals(
        df[["a", "b", "c", "d"]].rename(columns={"c": "c_value", "d": "d_value"})
    )


def test_format_dataframe_columnspecs(df):
    """Test that formatting an entire DataFrame works correctly,
    given uncertainties specified ColumnSpec instances."""
    columns = [
        "a",
        "b",
        ColumnSpec("c_value", "c_error", name="c", abbreviate=True),
        ColumnSpec(
            "d_value", "d_asymmetric", "d_systematic", name="d", abbreviate=True
        ),
    ]
    result = format_dataframe_errors(df, columns, abbreviate=False)
    assert result.equals(df[["a", "b", "c", "d"]])
