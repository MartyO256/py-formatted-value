from decimal import Decimal, ROUND_HALF_EVEN, ROUND_05UP, ROUND_CEILING, \
    ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_UP, ROUND_UP
from enum import Enum
from typing import Tuple, Union


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
        if rounding not in RoundingOption:
            raise ValueError(f"Unsupported rounding option {rounding}.")
        self.__rounding = rounding

    def _rounded_error(
            self,
            multiplier: Union[None, int, float]
    ) -> Decimal:
        error = Decimal(self.error)
        error = error if multiplier is None else error * Decimal(multiplier)
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
        value = value if multiplier is None else value * Decimal(multiplier)
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
    ) -> Tuple[Decimal, Decimal]:
        error = self._rounded_error(multiplier)
        value = self._rounded_value(error, multiplier)
        return value, error
        
    def formatted(
            self,
            template: str = r"\SI{{{0} \pm {1}}}{{{2}}}",
            multiplier: Union[None, int, float] = None,
            units: str = "",
    ) -> str:
        rounded_value, rounded_error = self.rounded_data(multiplier)
        return template.format(
            "{:f}".format(rounded_value),
            "{:f}".format(rounded_error),
            units,
        )

    def __str__(self) -> str:
        return self.formatted("{0} ± {1}")
