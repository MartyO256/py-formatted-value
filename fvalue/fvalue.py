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
    RoundingOption = RoundingOption

    def __init__(
            self,
            value: Union[int, float, Decimal],
            error: Union[int, float, Decimal] = 0,
            error_significant_figures: int = 1,
            leading_zeroes_threshold: int = 3,
            rounding: RoundingOption = RoundingOption.ROUND_HALF_EVEN,
    ):
        self.value = value
        self.error = error
        self.error_significant_figures = error_significant_figures
        self.leading_zeroes_threshold = leading_zeroes_threshold
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
            raise TypeError(
                "The significant figures in the error should be an integer, "
                f"not {error_significant_figures}."
            )
        if error_significant_figures < 1:
            raise ValueError(
                "The significant figures in the error should be positive, "
                f"not {error_significant_figures}."
            )
        self.__error_significant_figures = error_significant_figures

    @property
    def leading_zeroes_threshold(self) -> int:
        return self.__leading_zeroes_threshold

    @leading_zeroes_threshold.setter
    def leading_zeroes_threshold(self, leading_zeroes_threshold: int) -> None:
        if type(leading_zeroes_threshold) is not int:
            raise TypeError(
                "The significant figures in the error should be an integer, "
                f"not {leading_zeroes_threshold}."
            )
        if leading_zeroes_threshold < 0:
            raise ValueError(
                "The leading zeroes threshold should be non-negative, "
                f"not {leading_zeroes_threshold}."
            )
        self.__leading_zeroes_threshold = leading_zeroes_threshold

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

    @staticmethod
    def _leading_zeroes(value: Union[int, float, Decimal]):
        scientific_notation = "%E" % value
        exponent_token = scientific_notation[scientific_notation.index("E"):]
        exponent = int(exponent_token[1:])
        return 0 if exponent >= 0 else -exponent

    def rounded_data(
            self,
            multiplier: Union[None, int, float] = None,
    ) -> Tuple[Decimal, Decimal, int]:
        error = self._rounded_error(multiplier)
        value = Decimal(self.value) if (
                error == 0
        ) else self._rounded_value(error, multiplier)
        minimum_leading_zeroes = min(
            FormattedValue._leading_zeroes(value),
            FormattedValue._leading_zeroes(error)
        ) if error != 0 else FormattedValue._leading_zeroes(value)
        exponent = minimum_leading_zeroes if (
                minimum_leading_zeroes > self.leading_zeroes_threshold
        ) else 0
        error_significant_figures = self.error_significant_figures
        if error != 0:
            correction = floor(error.log10())
            correction = 0 if correction < error_significant_figures \
                else correction - error_significant_figures + 1
            exponent -= correction
        return value.scaleb(exponent), error.scaleb(exponent), -exponent

    SIUNITX_INNER_TEMPLATE = r"{0} \pm {1} e{2}"
    SIUNITX_TEMPLATE = r"\SI{{" + SIUNITX_INNER_TEMPLATE + r"}}{{{3}}}"
    SIUNITX_NUM_TEMPLATE = r"\num{{" + SIUNITX_INNER_TEMPLATE + r"}}"

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
            return f"({value} ± {error}) {units}" if (
                units
            ) else f"{value} ± {error}"
        elif exponent == "1":
            return f"({value} ± {error}) x 10 {units}" if (
                units
            ) else f"({value} ± {error}) x 10"
        else:
            return f"({value} ± {error}) x 10^{exponent} {units}" if (
                units
            ) else f"({value} ± {error}) x 10^{exponent}"

    NATURAL_TEMPLATE = _natural_format

    def __str__(self) -> str:
        return self.formatted(FormattedValue.NATURAL_TEMPLATE)
