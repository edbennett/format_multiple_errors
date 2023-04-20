#!/usr/bin/env python3

from collections import namedtuple

import pytest

from format_multiple_errors import format_multiple_errors


IntegerTestCase = namedtuple(
    "IntegerTestCase",
    [
        "expect",
        "name",
        "value",
        "errors",
        "length_control",
        "significant_figures",
        "abbreviate",
        "latex",
    ],
    defaults=["default", 12345, [6789, (1011, 1213)], "smallest", 2, False, False],
)


def label_testcase(args):
    """Turn an IntegerTestCase into a label that pytest can display."""
    return (
        f"{args.name}-{args.length_control}-{args.significant_figures}sf"
        + ("-abbr" if args.abbreviate else "")
        + ("-latex" if args.latex else "")
    )


integer_tests = [
    IntegerTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"12000(7000)({}^{+1000}_{-1000})",
    ),
    IntegerTestCase(
        length_control="central", abbreviate=True, expect="12000(7000)(+1000/-1000)"
    ),
    IntegerTestCase(
        length_control="central",
        latex=True,
        expect=r"12000 \pm 7000 {}^{+1000}_{-1000}",
    ),
    IntegerTestCase(length_control="central", expect="12000 ± 7000 (+1000 / -1000)"),
    IntegerTestCase(
        abbreviate=True, latex=True, expect=r"12300(6800)({}^{+1000}_{-1200})"
    ),
    IntegerTestCase(abbreviate=True, expect="12300(6800)(+1000/-1200)"),
    IntegerTestCase(latex=True, expect=r"12300 \pm 6800 {}^{+1000}_{-1200}"),
    IntegerTestCase(expect="12300 ± 6800 (+1000 / -1200)"),
    IntegerTestCase(
        significant_figures=4, abbreviate=True, expect="12345(6789)(+1011/-1213)"
    ),
    IntegerTestCase(
        name="heterogenous",
        errors=[12, (3456, 789)],
        abbreviate=True,
        expect="12345(12)(+3456/-789)",
    ),
]


@pytest.mark.parametrize("args", integer_tests, ids=label_testcase)
def test_abbr_latex_no_decimals_trailing_zeroes(args):
    """Check that calling the function with the specified `args` gives the expected value."""
    assert (
        format_multiple_errors(
            args.value,
            *args.errors,
            length_control=args.length_control,
            significant_figures=args.significant_figures,
            abbreviate=args.abbreviate,
            exponential=False,
            latex=args.latex,
        )
        == args.expect
    )
