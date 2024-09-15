#!/usr/bin/env python3

"""Functions to assist with formatting errors in Pandas DataFrames."""

from dataclasses import dataclass
from typing import cast
import warnings

try:
    import pandas as pd
except ImportError:
    warnings.warn("Unable to import Pandas.", RuntimeWarning)

from .formatter import format_multiple_errors


def _format_column(value: pd.Series, *errors: pd.Series, **fme_kwargs) -> pd.Series:
    """Formats the values and errors in a list of columns consistently.

    Parameters:

    value:
        A Pandas Series containing the central value to format.
        If a number with error (pyerrors.Obs or uncertainties.UFloat),
        then the nominal value is taken and the uncertainty is prepended to `errors`.

    *errors:
        A Pandas Series containing the uncertainties to format.
        Columns should contain a single number (symmetric),
        or a tuple of two numbers (upper, lower);
        a tuple of two columns may also be used to specify (upper, lower).

    **fme_kwargs:
        Optional keyword arguments passed to `format_multiple_errors`
        and documented therein.
    """
    errors_flattened = []
    for error in errors:
        if isinstance(error, tuple):
            errors_flattened.append(_tuplify(error))
        else:
            errors_flattened.append(error)

    df = pd.concat([value] + errors_flattened, axis=1)
    index = []
    formatted_errors = []
    for single_index, single_value, *single_errors in df.itertuples():
        index.append(single_index)
        formatted_errors.append(
            format_multiple_errors(single_value, *single_errors, **fme_kwargs)
        )
    return pd.Series(data=formatted_errors, index=index)


def _tuplify(columns: list[pd.Series]) -> pd.Series:
    """
    Turn columns into one column of tuples.
    Given a list of Pandas Series, returns a single Series
    containing the elements of each input series as a tuple.

    Parameters:

    columns:
        A list of Pandas Series objects.
    """
    df = pd.concat(columns, axis=1)
    index = []
    values = []
    for row in df.itertuples():
        index.append(row[0])
        values.append(tuple(row[1:]))
    return pd.Series(data=values, index=index)


def format_column_errors(
    value: str | pd.Series,
    *errors: str | pd.Series,
    df: pd.DataFrame | None = None,
    **fme_kwargs,
):
    """Formats the values and errors in a DataFrame consistently.

    Parameters:

    value:
        The column containing the central value to format.
        This may be a Pandas Series object, or if `df` is specified,
        then it may be the name of a column.
        If a number with error (pyerrors.Obs or uncertainties.UFloat),
        then the nominal value is taken and the uncertainty is prepended to `errors`.

    *errors:
        The columns containing the uncertainties to format.
        This may be a Pandas Series object, or if `df` is specified,
        then they may be the names of a columns,
        consistently with the argument to `values`.
        Columns should contain a single number (symmetric),
        or a tuple of two numbers (upper, lower);
        a tuple of two columns may also be used to specify (upper, lower).

    **fme_kwargs:
        Optional keyword arguments passed to `format_multiple_errors`
        and documented therein.
    """

    if df is None:
        value = cast(pd.Series, value)
        errors = cast(tuple[pd.Series], errors)
        return _format_column(value, *errors, **fme_kwargs)

    if not isinstance(value, str):
        message = (
            "If `df` is specified, then `value` must be a column name, "
            f"not {type(value)}."
        )
        raise TypeError(message)
    error_series = []
    for error_idx, error in enumerate(errors):
        if isinstance(error, str):
            error_series.append(df[error])
        elif isinstance(error, tuple):
            error_series.append(_tuplify([df[element] for element in error]))
        else:
            message = (
                f"Invalid error at index {error_idx}. "
                "If `df` is specified, then each element of `errors` must be "
                f"a column name or tuple of column names, not {type(error)}."
            )
            raise TypeError(message)

    return _format_column(df[value], *error_series, **fme_kwargs)


@dataclass
class ColumnSpec:
    """
    Specification of columns to include in calls to `format_dataframe_errors()`
    """

    def __init__(self, value: str, *errors: str, name: str | None = None, **fme_kwargs):
        """
        Specify a set of columns to turn into a single column containing formatted
        values and uncertainties.

        Arguments:

        value:
            The name of the column to use as the central value.
            If the column contains numbers with errors
            (pyerrors.Obs or uncertainties.UFloat), then the
            nominal value is taken and the uncertainty is prepended to `errors`.

        errors:
            Names of columns to use as symmetric uncertainties,
            and/or tuples of pairs of columns to use as upper and lower uncertainties.

        name:
            The name to give the resulting series.
            If not specified, the `value` argument will be used.

        **fme_kwargs:
            Arguments for formatting the uncertainties,
            to be passed to `format_multiple_errors()`.
        """
        self.value = value
        self.errors = errors
        self.fme_kwargs = fme_kwargs
        if name is not None:
            self.name = name
        else:
            self.name = value


def format_dataframe_errors(
    df: pd.DataFrame, columns: list[str], **fme_kwargs
) -> pd.DataFrame:
    """
    Formats groups of columns in a DataFrame into strings with errors.

    Parameters:

    df:
        The Pandas DataFrame to take data from.

    columns:
        A list of column specifications, either `str`, `tuple`, `list`, or `ColumnSpec`.
        Strings will be interpreted as columns to take with no modification.

        For tuples and lists,
        the first element is the name of the column containing the central value,
        and the subsequent elements the names of the columns containing the uncertainties
        (or tuples of column names for upper and lower uncertainties).
        The name of the value column will be used as the name of the formatted column.

    **fme_kwargs:
        Default arguments for formatting the errors.
        If columns are specified using ColumnSpec instances,
        then any arguments set therein will take priority over those specified here.
    """
    content = []
    for column_index, column in enumerate(columns):
        if isinstance(column, str):
            content.append(df[column])
            continue

        if isinstance(column, (tuple, list)):
            column = ColumnSpec(column[0], *column[1:])

        if not isinstance(column, ColumnSpec):
            message = (
                "Each column must be a str, tuple, list, or ColumnSpec, "
                f"not {type(column)} as found at index {column_index}."
            )
            raise TypeError(message)

        new_column = format_column_errors(
            column.value, *column.errors, df=df, **{**fme_kwargs, **column.fme_kwargs}
        )
        new_column.name = column.name
        content.append(new_column)

    return pd.concat(content, axis=1)
