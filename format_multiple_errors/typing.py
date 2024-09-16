#!/usr/bin/env python3

from typing import Union, TYPE_CHECKING


if TYPE_CHECKING:
    from pyerrors import Obs  # type: ignore[import-untyped]
    from uncertainties import UFloat  # type: ignore[import-untyped]

    Value = Union[float, Obs, UFloat]
else:
    Value = float


Error = Union[float, tuple[float, float]]
Errors = list[Error]
