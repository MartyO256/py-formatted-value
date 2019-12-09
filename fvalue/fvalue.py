from typing import Tuple, Union, Callable

from decimal import Decimal, ROUND_HALF_EVEN, ROUND_05UP, ROUND_CEILING, \
    ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_UP, ROUND_UP
from enum import Enum, unique
from math import floor


@unique
class RoundingOption(Enum):
    ROUND_HALF_EVEN = ROUND_HALF_EVEN
    ROUND_05UP = ROUND_05UP
    ROUND_CEILING = ROUND_CEILING
    ROUND_DOWN = ROUND_DOWN
    ROUND_FLOOR = ROUND_FLOOR
    ROUND_HALF_DOWN = ROUND_HALF_DOWN
    ROUND_HALF_UP = ROUND_HALF_UP
    ROUND_UP = ROUND_UP


class FormattedValue:
    def __init__(
            self,
            value: Union[int, float, Decimal],
            error: Union[int, float, Decimal] = 0,
            error_significant_figures: int = 1,
            rounding: RoundingOption = RoundingOption.ROUND_HALF_EVEN,
    ):
        self.value = value
        self.error = error
        self.error_significant_figures = error_significant_figures
        self.rounding = rounding

    @property
    def error(self) -> Union[int, float, Decimal]:
        return self.__error

    @error.setter
    def error(self, error: Union[int, float, Decimal]) -> None:
        if error < 0:
            raise ValueError(
                f"The error on a value should be non-negative, not {error}."
            )
        self.__error = error

    @property
    def error_significant_figures(self) -> int:
        return self.__error_significant_figures

    @error_significant_figures.setter
    def error_significant_figures(self, error_significant_figures: int) -> None:
        if type(error_significant_figures) is not int:
            raise TypeError("The significant figures in the error should be "
                            f"integral, not {error_significant_figures}.")
        if error_significant_figures < 1:
            raise ValueError("The significant figures in the error should be "
                             f"positive, not {error_significant_figures}.")
        self.__error_significant_figures = error_significant_figures

    @property
    def rounding(self) -> RoundingOption:
        return self.__rounding

    @rounding.setter
    def rounding(self, rounding: RoundingOption) -> None:
        if RoundingOption(rounding) not in RoundingOption:
            raise ValueError(f"Unsupported rounding option {rounding}.")
        self.__rounding = rounding

    def _rounded_error(
            self,
            multiplier: Union[None, int, float]
    ) -> Decimal:
        error = Decimal(self.error)
        error = error * Decimal(multiplier) if multiplier else error
        significant_error_format = f"%#.{self.error_significant_figures}g"
        return error.quantize(
            Decimal(significant_error_format % error),
            rounding=self.rounding.value
        )

    def _rounded_value(
            self,
            rounded_error: Decimal,
            multiplier: Union[None, int, float]
    ) -> Decimal:
        value = Decimal(self.value)
        value = value * Decimal(multiplier) if multiplier else value
        return value.quantize(
            rounded_error,
            rounding=self.rounding.value
        )

    def actual_data(self) -> Tuple[Union[int, float, Decimal],
                                   Union[int, float, Decimal]]:
        return self.value, self.error

    def rounded_data(
            self,
            multiplier: Union[None, int, float] = None,
    ) -> Tuple[Decimal, Decimal, int]:
        error = self._rounded_error(multiplier)
        value = self._rounded_value(error, multiplier)
        error_significant_figures = self.error_significant_figures
        exponent = floor(error.log10())
        exponent = 0 if exponent < error_significant_figures \
            else exponent - error_significant_figures + 1
        return value.scaleb(-exponent), error.scaleb(-exponent), exponent

    SIUNITX_TEMPLATE = r"\SI{{{0} \pm {1} e{2}}}{{{3}}}"
    SIUNITX_NUM_TEMPLATE = r"\num{{{0} \pm {1} e{2}}}"

    def formatted(
            self,
            template: Union[None, str, Callable[[str, str, str, str], str]],
            multiplier: Union[None, int, float] = None,
            units: str = "",
    ) -> str:
        template = template if template else FormattedValue.SIUNITX_TEMPLATE
        rounded_value, rounded_error, exponent = self.rounded_data(multiplier)
        value = "{:f}".format(rounded_value)
        error = "{:f}".format(rounded_error)
        exponent = "{:d}".format(exponent)
        if type(template) is str:
            return template.format(value, error, exponent, units)
        else:
            return template(value, error, exponent, units)

    @staticmethod
    def _natural_format(value: str, error: str, exponent: str, units: str):
        if exponent == "0":
            return f"({value} ± {error}) {units}" if units \
                else f"{value} ± {error}"
        elif exponent == "1":
            return f"({value} ± {error}) x 10 {units}" if units \
                else f"({value} ± {error}) x 10"
        else:
            return f"({value} ± {error}) x 10^{exponent} {units}" if units \
                else f"({value} ± {error}) x 10^{exponent}"

    NATURAL_TEMPLATE = _natural_format

    def __str__(self) -> str:
        return self.formatted(FormattedValue.NATURAL_TEMPLATE)
