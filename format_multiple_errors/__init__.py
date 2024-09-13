#!/usr/bin/env python3

"""A package for formatting numbers with zero or more errors or pairs of errors"""

import warnings

from .formatter import format_multiple_errors as format_multiple_errors

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from .pandas import (
        format_column_errors as format_column_errors,
        format_dataframe_errors as format_dataframe_errors,
        ColumnSpec as ColumnSpec,
    )

del warnings
