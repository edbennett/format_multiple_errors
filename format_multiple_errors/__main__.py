#!/usr/bin/env python3

"""Command-line interface for format_multiple_errors"""

from __future__ import annotations

from argparse import ArgumentParser, FileType, Namespace
import logging
from sys import exit, stderr

try:
    import pandas as pd
except ImportError:
    pd = None

from .formatter import format_multiple_errors
from .pandas import format_dataframe_errors, ColumnSpec


def _format_numbers(args: Namespace) -> None:
    """Format a single number."""
    print(
        format_multiple_errors(
            args.value,
            *args.errors,
            length_control=args.length_control,
            significant_figures=args.significant_figures,
            abbreviate=args.abbreviate,
            exponential=args.exponential,
            latex=args.latex,
        )
    )


def _check_pandas() -> None:
    """Check if Pandas is available; complain and exit if not."""
    if pd is None:
        print(
            "Pandas is not installed, but is required to process a table.",
            file=stderr,
        )
        exit()


def _format_table(args: Namespace) -> None:
    """Format a table from a CSV."""
    _check_pandas()
    if not args.latex:
        logging.warning(
            "--latex not specified; for LaTeX table output this will be forced on.",
        )

    if not args.headings:
        args.headings = None
    else:
        assert len(args.headings) == len(args.column_specs)

    df = pd.read_csv(args.input_file)
    formatted_df = format_dataframe_errors(
        df=df,
        columns=args.column_specs,
        length_control=args.length_control,
        significant_figures=args.significant_figures,
        abbreviate=args.abbreviate,
        exponential=args.exponential,
        latex=True,
    )
    formatted_df.to_latex(args.output_file, index=False, header=args.headings)


def _float_or_pair(arg: str) -> float | tuple[float, float]:
    """Takes a string containing either a float, or two floats separated by commas,
    and returns them as either a float or a tuple of floats."""

    split_arg = arg.split(",")
    if len(split_arg) == 1:
        return float(arg)
    elif len(split_arg) == 2:
        return tuple(map(float, split_arg))
    else:
        message = f"Can't parse {arg} as a number or pair of numbers."
        raise ValueError(message)


def _parse_columnspec(arg: str) -> str | ColumnSpec:
    """Take a string containing a specification for columns,
    and return a column name (if a single column is specified)
    or a ColumnSpec (if multiple columns are specified)."""

    split_arg = arg.split(",")
    if len(split_arg) == 1:
        return arg

    if not isinstance(split_arg[0], str):
        raise ValueError("First column has to be a single central value.")

    error_columns = []
    for error_spec in split_arg[1:]:
        split_error = error_spec.split("-")
        if len(split_error) == 1:
            error_columns.append(error_spec)
        else:
            error_columns.append(tuple(split_error))

    return ColumnSpec(split_arg[0], *error_columns)


def get_args(override_args: list | None = None) -> Namespace:
    """Parse command line."""
    parser = ArgumentParser(prog="format_multiple_errors")
    parser.add_argument(
        "--abbreviate",
        action="store_true",
        help="Abbreviate the uncertainty - e.g. 1.23(4) instead of 1.23 ± 0.04",
    )
    parser.add_argument(
        "--exponential", action="store_true", help="Use exponential notation"
    )
    parser.add_argument(
        "--latex",
        action="store_true",
        help="Use LaTeX rather than plain text format - e.g. 1.23 \\pm 0.04 instead of 1.23 ± 0.04",
    )
    parser.add_argument(
        "--significant_figures",
        type=int,
        default=2,
        help="Number of significant figures to display (used in conjunction with --length_control)",
    )
    parser.add_argument(
        "--length_control",
        default="smallest",
        choices=["smallest", "central"],
        help="Value to control the significant figures of (`smallest` uncertainty or `central` value)",
    )

    subparsers = parser.add_subparsers(title="commands")

    format_parser = subparsers.add_parser("format", help="Format a single number")
    format_parser.add_argument("value", type=float, help="The central value")
    format_parser.add_argument(
        "errors",
        type=_float_or_pair,
        metavar="error",
        nargs="+",
        help="Uncertainties in the value. Asymmetric uncertainties are specified as upper,lower.",
    )
    format_parser.set_defaults(func=_format_numbers)

    table_parser = subparsers.add_parser(
        "table", help="Format a CSV file into a LaTeX table"
    )
    table_parser.add_argument(
        "input_file", type=FileType("r"), help="The CSV file to read in"
    )
    table_parser.add_argument(
        "--output_file",
        type=FileType("w"),
        default="-",
        help="Where to place the output LaTeX",
    )
    table_parser.add_argument(
        "column_specs",
        type=_parse_columnspec,
        metavar="column_spec",
        nargs="+",
        help="Specifications of columns to include in the table, in the form value_column[,error_column[-lower_error_column]][,error_column[-lower_error_column]][...]",
    )
    table_parser.add_argument(
        "--headings",
        nargs="+",
        metavar="heading",
        help="Column headings to use. By default, these are taken from the CSV. If supplied, the count must match the number of specified columns",
    )
    table_parser.set_defaults(func=_format_table)
    return parser.parse_args(override_args)


def cli(override_args: list | None = None) -> None:
    """Run the CLI."""
    args = get_args(override_args)
    args.func(args)


if __name__ == "__main__":
    cli()
