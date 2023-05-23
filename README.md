# format_multiple_errors

A small library intended to make it easy to format numbers like

$$1.623(11)({}^{3}_{4})\times 10^{-7}$$

or

$$(6.829 \pm 0.013 {}^{+0.104}_{-0.096})\times10^{5}$$


## Installation

To install, open a terminal and run:

    pip install https://github.com/edbennett/format_multiple_errors


## Usage

The `format_multiple_errors` package provides a single function,
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


## Interaction with `pyerrors` and `uncertainties`

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
