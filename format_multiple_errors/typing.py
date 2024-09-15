#!/usr/bin/env python3

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pyerrors import Obs  # type: ignore
    from uncertainties import UFloat  # type: ignore

    Value = float | Obs | UFloat
else:
    Value = float


Error = float | tuple[float, float]
Errors = list[Error]
