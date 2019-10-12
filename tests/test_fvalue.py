from typing import Union, List, Tuple

import pytest

from decimal import Decimal
from fvalue import FormattedValue, RoundingOption

test_error_setter_data: List[Tuple[Union[int, float, Decimal],
                                   Union[None, ValueError]]] = [
    (0, None),
    (1.0, None),
    (Decimal(1.0), None),
    (5e10, None),
    (-1, ValueError),
    (-1.0, ValueError),
    (Decimal(-1.0), ValueError),
    (Decimal(-5e10), ValueError),
]


@pytest.mark.parametrize("error, exception", test_error_setter_data)
def test_error_setter(
        error: Union[int, float, Decimal],
        exception: Union[None, ValueError]
) -> None:
    valid_value = 10
    if exception:
        with pytest.raises(exception):
            FormattedValue(valid_value, error)


test_error_significant_figures_setter_data: \
    List[Tuple[Union[None, int, float, Decimal],
               Union[None, TypeError, ValueError]]] = [
    (None, None),
    (1, None),
    (2, None),
    (10, None),
    (-1, ValueError),
    (1.0, TypeError),
    (Decimal(1), TypeError),
]


@pytest.mark.parametrize("error_significant_figures, exception",
                         test_error_significant_figures_setter_data)
def test_error_significant_error_figures_setter(
        error_significant_figures: Union[None, int, float, Decimal],
        exception: Union[None, ValueError, TypeError]
):
    valid_value = 10
    valid_error = 1
    if exception:
        with pytest.raises(exception):
            FormattedValue(
                valid_value,
                valid_error,
                error_significant_figures=error_significant_figures,
            )


test_rounding_setter_data: List[Tuple[Union[str, RoundingOption],
                                      Union[None, ValueError]]] = [
    ("Invalid Rounding", ValueError)
] + [(rounding, None) for rounding in RoundingOption]


@pytest.mark.parametrize("rounding, exception", test_rounding_setter_data)
def test_rounding_setter(
        rounding: Union[str, RoundingOption],
        exception: Union[None, ValueError]
):
    valid_value = 10
    valid_error = 1
    if exception:
        with pytest.raises(exception):
            FormattedValue(
                valid_value,
                valid_error,
                rounding=rounding,
            )


test_actual_data_data: List[Tuple[Union[int, float, Decimal],
                                  Union[int, float, Decimal]]] = [
    (1, 1),
    (1, 1.0),
    (1.0, 1),
    (1.0, 1.0),
    (1, Decimal(1)),
    (Decimal(1), 1),
    (Decimal(1), Decimal(1)),
    (1.0, Decimal(1)),
    (Decimal(1), 1.0),
]


@pytest.mark.parametrize("value, error", test_actual_data_data)
def test_actual_data(
        value: Union[int, float, Decimal],
        error: Union[int, float, Decimal],
):
    for expected, actual in zip((value, error),
                                FormattedValue(value, error).actual_data()):
        assert expected == actual


test_rounded_data_data: List[Tuple[FormattedValue,
                                   Union[None, int, float],
                                   Tuple[Decimal, Decimal]]] = [
    (FormattedValue(10.0, 0.1, 1), None, (Decimal("10.0"), Decimal("0.1"))),
    (FormattedValue(10.0, 0.10, 1), None, (Decimal("10.0"), Decimal("0.1"))),
    (FormattedValue(10.0, 0.1, 2), None, (Decimal("10.00"), Decimal("0.10"))),
    (FormattedValue(10.0, 0.1, 3), None, (Decimal("10.000"), Decimal("0.100"))),
    (FormattedValue(0.001, 0.0001, 1), 1000, (Decimal("1.0"), Decimal("0.1"))),
    (FormattedValue(100, 10, 1), None, (Decimal("100"), Decimal("10"))),
]


@pytest.mark.parametrize("value, multiplier, rounded", test_rounded_data_data)
def test_rounded_data(
        value: FormattedValue,
        multiplier: Union[None, int, float],
        rounded: Tuple[Decimal, Decimal],
):
    for expected, actual in zip(rounded, value.rounded_data(multiplier)):
        assert expected == actual


test_formatted_data: List[Tuple[FormattedValue,
                                Union[None, str],
                                Union[None, int, float],
                                str,
                                str]] = [
    (
        FormattedValue(10, 0.1),
        r"\SI{{{0} \pm {1}}}{{{2}}}",
        None,
        r"\centi\meter",
        r"\SI{10.0 \pm 0.1}{\centi\meter}"
    ),
    (
        FormattedValue(10, 0.1),
        r"\SI{{{0} \pm {1}}}{{{2}}}",
        1 / 100,
        r"\meter",
        r"\SI{0.100 \pm 0.001}{\meter}"
    )
]


@pytest.mark.parametrize("value, template, multiplier, units, expected",
                         test_formatted_data)
def test_formatted(
        value: FormattedValue,
        template: Union[None, str],
        multiplier: Union[None, int, float],
        units: Union[None, str],
        expected: str,
):
    assert expected == value.formatted(template, multiplier, units)


def test_str():
    assert "10.0 ± 0.1" == str(FormattedValue(10, 0.1))

