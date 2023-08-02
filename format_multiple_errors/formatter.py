#!/usr/bin/env python3

"""Implementation of multiple error formatting."""

from collections.abc import Sequence

# It would be nice to vectorise this with numpy, but that needs more clever thinking.
import math


def _normalize_integrated_errors(value, errors):
    """Take any errors already included in `value` and prepends them to `errors`.

    Parameters:

    value:
        A central value that may have an associated uncertainty.

    errors:
        A list of other uncertainties.

    Returns:
        A tuple containing the central value, and a combined list of errors.
    """

    if hasattr(value, "nominal_value") and hasattr(value, "std_dev"):
        errors = [value.std_dev] + errors
        value = value.nominal_value
    elif hasattr(value, "value") and hasattr(value, "dvalue"):
        if value.dvalue == 0.0:
            raise ValueError(
                "pyerrors will not give an error before calling .gamma_method()"
            )
        errors = [value.dvalue] + errors
        value = value.value

    return value, errors


def _flatten_errors(errors, exclude=frozenset()):
    """Given a list of errors (number or tuples of two numbers),
    flatten it to a list of numbers."""

    flat_errors = []
    for error in errors:
        try:
            for value in error:
                if value not in exclude:
                    flat_errors.append(value)
        except (TypeError, ValueError):
            if error not in exclude:
                flat_errors.append(error)

    return flat_errors


def _get_smallest(errors):
    """Given a list of errors (number or tuples of two numbers),
    find the smallest number."""
    flat_errors = _flatten_errors(errors, exclude=[0, 0.0])
    if not flat_errors:
        return None

    return min(flat_errors)


def _get_length_value(value, errors, length_control):
    """
    Get the value that will be controlling the length,
    from either the central `value` or the list of `errors`.
    """

    if length_control == "central":
        return value
    if length_control == "smallest":
        length = _get_smallest(errors)
        if length is None:
            return value

        return length

    raise ValueError(
        f"{length_control} is not a value option for length_control."
        '(Available options are "smallest", "central".)'
    )


def _first_digit(value):
    """
    Return the first digit position of the given value, as an integer.
    0 is the digit just before the decimal point. Digits to the right
    of the decimal point have a negative position.
    Return 0 for a null value.
    """
    if value == 0:
        return 0

    return int(math.floor(math.log10(abs(value))))


def _map_recursive(func, data):
    """
    Map a function `f` across elements in some non-uniform nested structure of iterables.
    """
    ret = []
    for datum in data:
        if isinstance(datum, Sequence):
            ret.append(_map_recursive(func, datum))
        else:
            ret.append(func(datum))

    return type(data)(ret)


def _join_numbers(formatted_numbers, abbreviate, latex, exponent=0):
    """Take a list of `formatted_numbers`, and join them to form a full formatted string."""

    # Dict indexed by the tuple (abbreviate, latex, [is single-component])
    formatters = {
        (True, True, True): "({error})",
        (True, True, False): "({{}}^{{{error[0]}}}_{{{error[1]}}})",
        (True, False, True): "({error})",
        (True, False, False): "(+{error[0]}/-{error[1]})",
        (False, True, True): " \\pm {error}",
        (False, True, False): " {{}}^{{+{error[0]}}}_{{-{error[1]}}}",
        (False, False, True): " ± {error}",
        (False, False, False): " (+{error[0]} / -{error[1]})",
    }

    elements = formatted_numbers[:1]
    for error in formatted_numbers[1:]:
        elements.append(
            formatters[abbreviate, latex, isinstance(error, str)].format(error=error)
        )

    if exponent:
        if not abbreviate:
            # Errors and central value must be grouped together
            # so the exponent applies to all
            elements = ["("] + elements + [")"]
        if latex:
            elements.append(f" \\times 10^{{{exponent}}}")
        else:
            elements.append(f"e{exponent}")

    return "".join(elements)


def _normalize(value, errors):
    """
    Divides `value` and all elements of `errors` by a common power of 10
    such that `value` is in [1, 10).

    Arguments:

        value: a central value

        errors: a list of errors, either numbers or tuples of two numbers

    Returns:

        value: the normalized central value

        errors: the normalized errors

        exponent: the power of 10 by which the values have been multiplied
    """

    if value == 0:
        exponent = _first_digit(max(_flatten_errors(errors)))
    else:
        exponent = _first_digit(value)

    return (
        value / 10**exponent,
        _map_recursive(lambda error: error / 10**exponent, errors),
        exponent,
    )


def _abbreviated_single_error(error, decimal_places):
    """
    Take a single `error` and return its correct abbreviation
    to the given number of `decimal_places`.
    """
    if error >= 1:
        return f"{error:.0{decimal_places}f}"

    return str(int(round(error * 10**decimal_places)))


def _unabbreviated_single_error(error, decimal_places):
    """
    Take a single `error` and return its correct unabbreviated format
    to the given number of `decimal_places`.
    """

    rounded_error = round(error, decimal_places)
    if rounded_error == 0:
        if decimal_places > 0:
            return "0.0"

        return "0"

    return f"{rounded_error:.0{decimal_places}f}"


def get_rounding_indices(length_value, significant_figures):
    """
    Get the index of the first digit of length_value,
    and from it the number of decimal places corresponding to the
    given value of significant_figures.
    """

    # Repeat, as the first pass will break
    # if the rounding changes the number of significant figures
    for _ in range(2):
        first_digit_index = _first_digit(length_value)
        decimal_places = significant_figures - first_digit_index - 1
        length_value = round(length_value, decimal_places)

    return first_digit_index, decimal_places


def _decimals_required(first_digit_index, significant_figures, exponential):
    """
    Determine whether a decimal point is needed to represent a number to a particular precision.
    """
    return first_digit_index + 1 < significant_figures or exponential


def _format_errors_only(errors, decimal_places, abbreviate):
    """
    Return a list of `errors` formatted to the specified number of `decimal_places`.
    If `abbreviate` is specified, format only the portion of the number needed
    to express the error.
    """
    formatters = {True: _abbreviated_single_error, False: _unabbreviated_single_error}

    return _map_recursive(
        lambda error: formatters[abbreviate](error, decimal_places), errors
    )


def format_multiple_errors(
    value,
    *errors,
    length_control="smallest",
    significant_figures=2,
    abbreviate=False,
    exponential=False,
    latex=False,
):
    """Formats the value and errors consistently.

    Parameters:

    value:
        The central value to format.
        If a number with error (pyerrors.Obs or uncertainties.UFloat),
        then the nominal value is taken and the uncertainty is prepended to `errors`.

    *errors:
        The uncertainties to format.
        Each should be a single number (symmetric), or a tuple of two numbers (upper, lower).

    length_control (default: "smallest"):
        The variable to use for controlling the length of the printed number.
        Options:
            "smallest": The smallest uncertainty is printed
                        with `significant_figures` significant figures.
            "central": The central `value` is printed
                       with `significant_figures` significant figures.

    significant_figures (default: 2):
        The number of significant figures to format.
        Other values printed may have more significant figures, but will not have fewer.

    abbreviate (default: False):
        Abbreviate the uncertainties with bracketed notation.
        (I.e. 1.234(56) instead of 1.234 +/- 0.056.)

    exponential (default: False):
        Use standard form (e.g. 1.2 × 10^{-3}) rather than leading/trailing zeroes (0.0012).

    latex (default: False):
        Format the numbers in LaTeX form rather than plain text.
    """

    value, errors = _normalize_integrated_errors(value, list(errors))
    exponent = 0
    if exponential:
        value, errors, exponent = _normalize(value, errors)

    length_value = _get_length_value(value, errors, length_control)
    first_digit_index, decimal_places = get_rounding_indices(
        length_value, significant_figures
    )

    if _decimals_required(first_digit_index, significant_figures, exponential):
        formatted_numbers = [f"{value:.0{decimal_places}f}"] + _format_errors_only(
            errors, decimal_places, abbreviate
        )
    else:
        formatted_numbers = _map_recursive(
            lambda value: str(int(round(value, decimal_places))),
            [value] + list(errors),
        )

    return _join_numbers(
        formatted_numbers, exponent=exponent, abbreviate=abbreviate, latex=latex
    )


if __name__ == "__main__":
    print(
        format_multiple_errors(12345.0, 10, (22, 36), 255, abbreviate=True, latex=False)
    )
