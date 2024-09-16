# format_multiple_errors

[![Run tests](https://github.com/edbennett/format_multiple_errors/actions/workflows/pytest.yaml/badge.svg)](https://github.com/edbennett/format_multiple_errors/actions/workflows/pytest.yaml)
[![Code quality](https://github.com/edbennett/format_multiple_errors/actions/workflows/codequality.yaml/badge.svg)](https://github.com/edbennett/format_multiple_errors/actions/workflows/codequality.yaml)

A small library intended to make it easy to format numbers like

$$1.623(11)({}^{3}_{4})\times 10^{-7}$$

or

$$(6.829 \pm 0.013 {}^{+0.104}_{-0.096})\times10^{5}$$


## Installation

To install, open a terminal and run:

    pip install https://github.com/edbennett/format_multiple_errors


## Usage as a library

### Formatting numbers

The `format_multiple_errors` package provides a function to format numbers,
also named `format_multiple_errors`.

    from format_multiple_errors import format_multiple_errors

This function takes a central value,
and zero or more uncertainties.
It returns a string containing all numbers formatted to the same absolute precision.

Uncertainties may be single numbers:

    >>> format_multiple_errors(1, 0.1, 0.2)
    '1.00 ± 0.10 ± 0.20'

or they may also be tuples of two numbers,
representing the upper and lower error respectively:

    >>> format_multiple_errors(1, 0.1, (0.2, 0.3))
    '1.00 ± 0.10 (+0.20 / -0.30)'

A number of keyword arguments control the formatting.
The `abbreviate` option uses the compact form of expressing errors:

    >>> format_multiple_errors(1.001, 0.010, (0.020, 0.034), abbreviate=True)
    '1.001(10)(+20 / -34)'

The `latex` option uses LaTeX macros rather than Unicode characters,
and generally formats the result for inclusion in a LaTeX document:

    >>> format_multiple_errors(1.001, 0.010, (0.020, 0.034), latex=True)
    '1.001 \\pm 0.010 {}^{+0.020}_{-0.034}'

Numbers are formatted by default with leading or trailing zeroes.
To use exponential notation instead,
use the `exponential` parameter:

    >>> format_multiple_errors(0.00123, 0.00045, (0.00067, 0.00089), exponential=True)
    '(1.23 ± 0.45 (+0.67 / -0.89))e-3'

By default the precision is controlled
by setting the number of significant digits presented for the smallest uncertainty.
Setting `length_control="central"` instead controls the significant digits of the central value:

    >>> format_multiple_errors(1.0, 0.1, (0.2, 0.3), length_control="central")
    '1.0 ± 0.1 (+0.2 / -0.3)'

The number of significant figures presented can be controlled with the `significant_figures` parameter:

    >>> format_multiple_errors(1.001, 0.001, (0.002, 0.0034), significant_figures=1)
    '1.001 ± 0.001 (+0.002 / -0.003)'

These options may be combined:

    >>> format_multiple_errors(123.45, 3.14, (2.82, 12.91), length_control="central", significant_figures=5, latex=True, abbreviate=True, exponential=True)
    '1.2345(314)({}^{282}_{1291}) \\times 10^{2}'


### Formatting DataFrames

The library provides two functions for working with Pandas DataFrames.

The `format_column_errors` function accepts and returns columns.
For example,
it can take `pd.Series` objects:

    >>> import pandas as pd
    >>> from format_multiple_errors import format_column_errors
    >>> df = pd.DataFrame([{"a": 3.14, "b": 0.59, "c": 0.26}, {"a": 2.17, "b": 0.82, "c":   0.81}])
    >>> format_column_errors(df["a"], (df["b"], df["c"]), abbreviate=True)
    0    3.14(+59/-26)
    1    2.17(+82/-81)
    dtype: object

It can also take a `pd.DataFrame` and specifications of the column names to use:

    >>> format_column_errors("a", ("b", "c"), df=df, abbreviate=True)
    0    3.14(+59/-26)
    1    2.17(+82/-81)
    dtype: object


### Interaction with `pyerrors` and `uncertainties`

If the central value passed to `format_multiple_errors` already has an uncertainty,
due to being an instance of `pyerrors.Obs` or `uncertainties.UFloat`,
then this is prepended to the list of errors.
For example,

    >>> from uncertainties import ufloat
    >>> result = ufloat(1.01, 0.1)
    >>> systematic = (0.2, 0.34)
    >>> format_multiple_errors(result, systematic)
    '1.01 ± 0.10 (+0.20 / -0.34)'

Instances of `pyerrors.Obs` must already have an uncertainty computed
(must have had the `.gamma_method()` method called on them)
before being passed to `format_multiple_errors`,
otherwise an error is raised.


## Command-line interface

A command-line interface is also provided.
To format a single number,
use the `format_multiple_errors format` command:

    $ format_multiple_errors --abbreviate format 3.141 0.059 0.026,0.053
    3.141(59)(+26/-53)

To format a CSV as a LaTeX table,
use the `format_multiple_errors table` command:

    $ format_multiple_errors --latex --abbreviate table input.csv \
    > a b c_value,c_error d_value,d_upper-d_lower,d_systematic \
    > --headings '$a$' '$b$' '$c$' '$d$' --output_file output.tex
    $ cat output.tex
    \begin{tabular}{rrll}
    \toprule
    $a$ & $b$ & $c$ & $d$ \\
    \midrule
    3 & 1 & $4.16(26)$ & $3.59({}^{79}_{24})(46)$ \\
    2 & 7 & $1.83(18)$ & $8.459({}^{45}_{235})(360)$ \\
    \bottomrule
    \end{tabular}

Formatting options are specified before the subcommand (`format` or `table`).
Options specific to the command are specified afterwards.


## Development

To be able to run the test suite,
create a virtual environment using the tooling of your choice,
and then install the developer dependencies:

    pip install -r requirements_dev.txt


The test suite can then be run by calling

    pytest

Before committing,
you should ensure that the repository's pre-commit hooks are installed:

    pre-commit install

Then some basic code quality checks will be run by Git
before it accepts your commit.
