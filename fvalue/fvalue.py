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
        """
        Constructs a formatted value for the presentation of an experimental
        result as a string.

        A formatted value is turned into a string using the `formatted` method.

        :param value: The value.
        :param error: The error on the value.
        :param error_significant_figures: The number of significant figures to
        keep in the error.
        Defaults to one, which is suitable for values with low sample sizes.
        :param leading_zeroes_threshold: The maximal number of leading zeroes
        in the formatted value and error. Fine-tuning of the leading zeroes
        is made using the multiplier in the `formatted` method.
        :param rounding: The rounding policy on the value and error.
        Defaults to half-even to mitigate some biases.
        """
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
        """
        :param error:
        :raises ValueError: error < 0
        """
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
        """
        :param error_significant_figures:
        :raises TypeError: type(error_significant_figures) is not int
        :raises ValueError: error_significant_figures < 1
        """
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
        """
        :param leading_zeroes_threshold:
        :raises TypeError: type(leading_zeroes_threshold) is not int
        :raises ValueError: leading_zeroes_threshold < 0
        """
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
        """
        :param rounding:
        :raises ValueError: RoundingOption(rounding) not in RoundingOption
        """
        if RoundingOption(rounding) not in RoundingOption:
            raise ValueError(f"Unsupported rounding option {rounding}.")
        self.__rounding = rounding

    def _rounded_error(
            self,
            multiplier: Union[None, int, float]
    ) -> Decimal:
        """
        Rounds the error on the formatted value up to the parameterized number
        of significant figures in the error.

        The error is rounded using the parameterized rounding option for the
        formatted value.

        The returned Decimal for the error is multiplied by the multiplier
        beforehand.

        :param multiplier: The multiplier applied to the error for formatting.
        :return: The rounded error.
        """
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
        """
        Rounds the value on the formatted value to match the decimal places of
        the rounded error.

        The value is rounded using the parameterized rounding option for the
        formatted value.

        The returned Decimal for the value is multiplied by the multiplier
        beforehand.

        :param rounded_error: The rounded error on the value.
        :param multiplier: The multiplier applied to the value for formatting.
        :return: The rounded value.
        """
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
        """
        Determines the number of leading zeroes after the decimal for a given
        numerical value.

        This corresponds to the absolute value of the decimal exponent of the
        value in scientific notation.

        :param value: The value for which to determine the number of leading
        zeroes.
        :return: The number of leading zeroes for the given value.
        """
        scientific_notation = "%E" % value
        exponent_token = scientific_notation[scientific_notation.index("E"):]
        exponent = int(exponent_token[1:])
        return 0 if exponent >= 0 else -exponent

    def rounded_data(
            self,
            multiplier: Union[None, int, float] = None,
    ) -> Tuple[Decimal, Decimal, int]:
        """
        Rounds the error and value up to the parameterized significant figures
        in the error, and with respect to the threshold on the number of leading
        zeroes in the error and value.

        :param multiplier:
        :return: A tuple with the rounded value and error, and the decimal
        exponent on both of them as in the scientific notation.
        """
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

    _SIUNITX_INNER_TEMPLATE = r"{0} \pm {1} e{2}"
    SIUNITX_TEMPLATE = r"\SI{{" + _SIUNITX_INNER_TEMPLATE + r"}}{{{3}}}"
    SIUNITX_VALUE_TEMPLATE = r"\SI{{{0} e{2}}}{{{3}}}"
    SIUNITX_ERROR_TEMPLATE = r"\SI{{{1} e{2}}}{{{3}}}"
    SIUNITX_NUM_TEMPLATE = r"\num{{" + _SIUNITX_INNER_TEMPLATE + r"}}"
    SIUNITX_NUM_VALUE_TEMPLATE = r"\num{{{0} e{2}}}"
    SIUNITX_NUM_ERROR_TEMPLATE = r"\num{{{1} e{2}}}"

    def formatted(
            self,
            template: Union[None, str, Callable[[str, str, str, str], str]],
            multiplier: Union[None, int, float] = None,
            units: str = "",
    ) -> str:
        """
        Formats the rounded value and error using the given template.

        The template can either be a string or a function.
        If it is a string, then:
            `{0}` corresponds to the value;
            `{1}` corresponds to the error;
            `{2}` corresponds to the decimal exponent;
            `{3}` corresponds to the units.
        If it is a function, then the arguments are all strings, and in order,
        correspond to the literals in string templates as above.

        The multiplier and units should match.
        That is, if the value and error are in meters, but should be displayed
        in nanometers, then the multiplier would have value `10 ** 9` and the
        units would have value `"\\nano\\meter"`.

        :param template: Either a string or a function on the value, error,
        decimal exponent and units in order.
        :param multiplier: The multiplier to apply to the value and error in the
        template.
        :param units: The units on the formatted value with the parameterized
        multiplier.
        :return: The formatted value as a string.
        """
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
