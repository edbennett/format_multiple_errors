#!/usr/bin/env python3

from collections import namedtuple
from functools import partial

import pytest

from pyerrors import Obs
from uncertainties import ufloat

from format_multiple_errors import format_multiple_errors, formatter


def label_testcase(args):
    """Turn an FormatTestCase into a label that pytest can display."""
    return (
        f"{args.name}-{args.length_control}-{args.significant_figures}sf"
        + ("-abbr" if args.abbreviate else "")
        + ("-exp" if args.exponential else "")
        + ("-latex" if args.latex else "")
    )


FormatTestCase = namedtuple(
    "FormatTestCase",
    [
        "expect",
        "name",
        "value",
        "errors",
        "length_control",
        "significant_figures",
        "abbreviate",
        "exponential",
        "latex",
    ],
    defaults=["smallest", 2, False, False, False],
)

IntegerTestCase = partial(
    FormatTestCase, name="integer", value=12345, errors=[6789, (1011, 1213)]
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
        name="heterogenous_integer",
        errors=[12, (3456, 789)],
        abbreviate=True,
        expect="12345(12)(+3456/-789)",
    ),
]

SmallTestCase = partial(
    FormatTestCase,
    name="small",
    value=0.0012345,
    errors=[0.0006789, (0.0001011, 0.0000121)],
)
MedTestCase = partial(
    FormatTestCase, name="med", value=1.2345, errors=[0.0067, (0.0089, 0.1011), 1.2131]
)
LargeTestCase = partial(
    FormatTestCase, name="large", value=1234.5, errors=[6.7, (8.9, 101.1)]
)

decimal_tests = [
    SmallTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"0.0012(7)({}^{+1}_{-0})",
    ),
    SmallTestCase(
        length_control="central",
        latex=True,
        expect=r"0.0012 \pm 0.0007 {}^{+0.0001}_{-0.0}",
    ),
    SmallTestCase(
        length_control="central", abbreviate=True, expect=r"0.0012(7)(+1/-0)"
    ),
    SmallTestCase(length_control="central", expect=r"0.0012 ± 0.0007 (+0.0001 / -0.0)"),
    SmallTestCase(
        abbreviate=True, latex=True, expect=r"0.001234(679)({}^{+101}_{-12})"
    ),
    SmallTestCase(
        latex=True, expect=r"0.001234 \pm 0.000679 {}^{+0.000101}_{-0.000012}"
    ),
    SmallTestCase(abbreviate=True, expect=r"0.001234(679)(+101/-12)"),
    SmallTestCase(expect=r"0.001234 ± 0.000679 (+0.000101 / -0.000012)"),
    LargeTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"1200(0)({}^{+0}_{-100})",
    ),
    LargeTestCase(
        length_control="central", latex=True, expect=r"1200 \pm 0 {}^{+0}_{-100}"
    ),
    LargeTestCase(
        length_control="central", abbreviate=True, expect=r"1200(0)(+0/-100)"
    ),
    LargeTestCase(length_control="central", expect=r"1200 ± 0 (+0 / -100)"),
    LargeTestCase(
        abbreviate=True, latex=True, expect=r"1234.5(6.7)({}^{+8.9}_{-101.1})"
    ),
    LargeTestCase(latex=True, expect=r"1234.5 \pm 6.7 {}^{+8.9}_{-101.1}"),
    LargeTestCase(abbreviate=True, expect=r"1234.5(6.7)(+8.9/-101.1)"),
    LargeTestCase(expect=r"1234.5 ± 6.7 (+8.9 / -101.1)"),
]

SmallExpTestCase = partial(SmallTestCase, exponential=True)
MedExpTestCase = partial(MedTestCase, exponential=True)
LargeExpTestCase = partial(LargeTestCase, exponential=True)

exponential_tests = [
    SmallExpTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"1.2(7)({}^{+1}_{-0}) \times 10^{-3}",
    ),
    SmallExpTestCase(
        length_control="central",
        latex=True,
        expect=r"(1.2 \pm 0.7 {}^{+0.1}_{-0.0}) \times 10^{-3}",
    ),
    SmallExpTestCase(
        length_control="central", abbreviate=True, expect=r"1.2(7)(+1/-0)e-3"
    ),
    SmallExpTestCase(length_control="central", expect=r"(1.2 ± 0.7 (+0.1 / -0.0))e-3"),
    SmallExpTestCase(
        abbreviate=True,
        latex=True,
        expect=r"1.234(679)({}^{+101}_{-12}) \times 10^{-3}",
    ),
    SmallExpTestCase(
        latex=True, expect=r"(1.234 \pm 0.679 {}^{+0.101}_{-0.012}) \times 10^{-3}"
    ),
    SmallExpTestCase(abbreviate=True, expect=r"1.234(679)(+101/-12)e-3"),
    SmallExpTestCase(expect=r"(1.234 ± 0.679 (+0.101 / -0.012))e-3"),
    MedExpTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"1.2(0)({}^{+0}_{-1})(1.2)",
    ),
    MedExpTestCase(
        length_control="central",
        latex=True,
        expect=r"1.2 \pm 0.0 {}^{+0.0}_{-0.1} \pm 1.2",
    ),
    MedExpTestCase(
        length_control="central", abbreviate=True, expect=r"1.2(0)(+0/-1)(1.2)"
    ),
    MedExpTestCase(length_control="central", expect=r"1.2 ± 0.0 (+0.0 / -0.1) ± 1.2"),
    MedExpTestCase(
        abbreviate=True, latex=True, expect=r"1.2345(67)({}^{+89}_{-1011})(1.2131)"
    ),
    MedExpTestCase(
        latex=True, expect=r"1.2345 \pm 0.0067 {}^{+0.0089}_{-0.1011} \pm 1.2131"
    ),
    MedExpTestCase(abbreviate=True, expect=r"1.2345(67)(+89/-1011)(1.2131)"),
    MedExpTestCase(expect=r"1.2345 ± 0.0067 (+0.0089 / -0.1011) ± 1.2131"),
    LargeExpTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"1.2(0)({}^{+0}_{-1}) \times 10^{3}",
    ),
    LargeExpTestCase(
        length_control="central",
        latex=True,
        expect=r"(1.2 \pm 0.0 {}^{+0.0}_{-0.1}) \times 10^{3}",
    ),
    LargeExpTestCase(
        length_control="central", abbreviate=True, expect=r"1.2(0)(+0/-1)e3"
    ),
    LargeExpTestCase(length_control="central", expect=r"(1.2 ± 0.0 (+0.0 / -0.1))e3"),
    LargeExpTestCase(
        abbreviate=True,
        latex=True,
        expect=r"1.2345(67)({}^{+89}_{-1011}) \times 10^{3}",
    ),
    LargeExpTestCase(
        latex=True, expect=r"(1.2345 \pm 0.0067 {}^{+0.0089}_{-0.1011}) \times 10^{3}"
    ),
    LargeExpTestCase(abbreviate=True, expect=r"1.2345(67)(+89/-1011)e3"),
    LargeExpTestCase(expect=r"(1.2345 ± 0.0067 (+0.0089 / -0.1011))e3"),
]

LongErrorTestCase = partial(
    FormatTestCase,
    name="longerror",
    value=1.2345,
    errors=[0.123456789, (0.00987654321, 0.0102030405)],
)
long_error_tests = [
    LongErrorTestCase(
        length_control="central",
        abbreviate=True,
        latex=True,
        expect=r"1.2(1)({}^{+0}_{-0})",
    ),
    LongErrorTestCase(
        length_control="central", latex=True, expect=r"1.2 \pm 0.1 {}^{+0.0}_{-0.0}"
    ),
    LongErrorTestCase(
        length_control="central", abbreviate=True, expect=r"1.2(1)(+0/-0)"
    ),
    LongErrorTestCase(length_control="central", expect=r"1.2 ± 0.1 (+0.0 / -0.0)"),
    LongErrorTestCase(
        abbreviate=True, latex=True, expect=r"1.2345(1235)({}^{+99}_{-102})"
    ),
    LongErrorTestCase(latex=True, expect=r"1.2345 \pm 0.1235 {}^{+0.0099}_{-0.0102}"),
    LongErrorTestCase(abbreviate=True, expect=r"1.2345(1235)(+99/-102)"),
    LongErrorTestCase(expect=r"1.2345 ± 0.1235 (+0.0099 / -0.0102)"),
]


def single_test_case(args):
    """Check that calling the function with the specified `args` gives the expected value."""
    assert (
        format_multiple_errors(
            args.value,
            *args.errors,
            length_control=args.length_control,
            significant_figures=args.significant_figures,
            abbreviate=args.abbreviate,
            exponential=args.exponential,
            latex=args.latex,
        )
        == args.expect
    )


@pytest.mark.parametrize("args", integer_tests, ids=label_testcase)
def test_abbr_latex_no_decimals_trailing_zeroes(args):
    """Test formatting numbers that we don't expect to include decimal points."""
    single_test_case(args)


@pytest.mark.parametrize("args", decimal_tests, ids=label_testcase)
def test_decimals(args):
    """Test formatting numbers that we don't expect to include decimal points."""
    single_test_case(args)


@pytest.mark.parametrize("args", exponential_tests, ids=label_testcase)
def test_exponentials(args):
    """Test formatting numbers that we don't expect to include decimal points."""
    single_test_case(args)


@pytest.mark.parametrize("args", long_error_tests, ids=label_testcase)
def test_long_errors(args):
    """Test formatting numbers that we don't expect to include decimal points."""
    single_test_case(args)


@pytest.mark.parametrize("exponent", range(-5, 6))
def test_normalize(exponent):
    expect_value = 1.234
    expect_errors = [0.01, (0.123, 0.234), 0.49]

    value = expect_value * 10**exponent
    errors = formatter._map_errors(lambda error: error * 10**exponent, expect_errors)

    assert formatter._normalize(value, errors) == (
        pytest.approx(expect_value),
        formatter._map_errors(pytest.approx, expect_errors),
        exponent,
    )


def test_normalize_zero():
    errors = [0.01, (0.123, 0.234), 0.49]

    assert formatter._normalize(0.0, errors) == (
        0.0,
        formatter._map_errors(lambda error: pytest.approx(error * 10), errors),
        -1,
    )


@pytest.mark.xfail
def test_rounding():
    assert (
        formatter.format_multiple_errors(
            1.0, 0.0999, significant_figures=2, abbreviate=True
        )
        == "1.00(10)"
    )


def test_ufloat():
    assert (
        formatter.format_multiple_errors(
            ufloat(1.234, 0.012), (0.034, 0.056), significant_figures=2, abbreviate=True
        )
        == "1.234(12)(+34/-56)"
    )


def test_pyerrors():
    """Test that pyerrors Obs instances have their errors correctly included."""

    obs = Obs([[1.0, 0.9, 1.0, 1.1, 1.0]], ["sample"])
    obs.gamma_method()
    assert (
        formatter.format_multiple_errors(
            obs, (0.034, 0.056), significant_figures=2, abbreviate=True
        )
        == "1.000(36)(+34/-56)"
    )


def test_pyerrors_pre_gamma():
    """Test that pyerrors Obs instances that have not yet had gamma_method() applied refuse to cooperate."""
    obs = Obs([[1.0, 0.9, 1.0, 1.1, 1.0]], ["sample"])
    with pytest.raises(ValueError):
        formatter.format_multiple_errors(obs)
