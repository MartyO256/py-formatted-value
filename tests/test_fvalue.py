from typing import Union, List, Tuple, Callable

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
    else:
        FormattedValue(valid_value, error)


test_error_significant_figures_setter_data: \
    List[Tuple[Union[None, int, float, Decimal],
               Union[None, TypeError, ValueError]]] = [
        (None, TypeError),
        (1, None),
        (2, None),
        (10, None),
        (-1, ValueError),
        (1.0, TypeError),
        (Decimal(1), TypeError),
    ]


@pytest.mark.parametrize(
    "error_significant_figures, exception",
    test_error_significant_figures_setter_data
)
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
    else:
        FormattedValue(
            valid_value,
            valid_error,
            error_significant_figures=error_significant_figures,
        )


test_rounding_setter_data: List[Tuple[Union[str, RoundingOption],
                                      Union[None, ValueError]]] = \
    [("Invalid Rounding", ValueError)] \
    + [(rounding, None) for rounding in RoundingOption] \
    + [(rounding.value, None) for rounding in RoundingOption]


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
    else:
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
    for actual, expected in zip(
            FormattedValue(value, error).actual_data(),
            (value, error)
    ):
        assert actual == expected


test_rounded_data_data: List[Tuple[FormattedValue,
                                   Union[None, int, float],
                                   Tuple[Decimal, Decimal]]] = [
    (FormattedValue(10.0, 0.1, 1), None, (Decimal("10.0"), Decimal("0.1"))),
    (FormattedValue(10.0, 0.10, 1), None, (Decimal("10.0"), Decimal("0.1"))),
    (FormattedValue(10.0, 0.1, 2), None, (Decimal("10.00"), Decimal("0.10"))),
    (FormattedValue(10.0, 0.1, 3), None, (Decimal("10.000"), Decimal("0.100"))),
    (FormattedValue(0.001, 0.0001, 1), 1000, (Decimal("1.0"), Decimal("0.1"))),
]


@pytest.mark.parametrize("value, multiplier, rounded", test_rounded_data_data)
def test_rounded_data(
        value: FormattedValue,
        multiplier: Union[None, int, float],
        rounded: Tuple[Decimal, Decimal],
):
    for actual, expected in zip(value.rounded_data(multiplier), rounded):
        assert actual == expected


test_formatted_data: List[Tuple[FormattedValue,
                                Union[None, str],
                                Union[None, int, float],
                                str,
                                str]] = [
    (
        FormattedValue(10, 0.1),
        r"\SI{{{0} \pm {1}}}{{{3}}}",
        None,
        r"\centi\meter",
        r"\SI{10.0 \pm 0.1}{\centi\meter}"
    ),
    (
        FormattedValue(10, 0.1),
        r"\SI{{{0} \pm {1}}}{{{3}}}",
        1 / 100,
        r"\meter",
        r"\SI{0.100 \pm 0.001}{\meter}"
    ),
    (
        FormattedValue(100, 10),
        None,
        None,
        r"\meter",
        r"\SI{10 \pm 1 e1}{\meter}"
    ),
    (
        FormattedValue(1000, 100),
        None,
        None,
        r"\meter",
        r"\SI{10 \pm 1 e2}{\meter}"
    ),
    (
        FormattedValue(10000, 1000),
        None,
        None,
        r"\meter",
        r"\SI{10 \pm 1 e3}{\meter}"
    ),
    (
        FormattedValue(10000, 1000),
        lambda value, error, exponent, _:
        f"({value} ± {error}) x 10^{exponent}",
        None,
        None,
        "(10 ± 1) x 10^3"
    ),
    (
        FormattedValue(10000, 1000, 2),
        lambda value, error, exponent, units:
        f"({value} ± {error}) x 10^{exponent} {units}",
        None,
        "m",
        "(100 ± 10) x 10^2 m"
    ),
    (
        FormattedValue(10000, 1000, 3),
        lambda value, error, exponent, _:
        f"({value} ± {error}) x 10^{exponent}",
        None,
        None,
        "(1000 ± 100) x 10^1"
    )
]


@pytest.mark.parametrize(
    "value, template, multiplier, units, expected",
    test_formatted_data
)
def test_formatted(
        value: FormattedValue,
        template: Union[None, str, Callable[[str, str, str], str]],
        multiplier: Union[None, int, float],
        units: Union[None, str],
        expected: str,
):
    assert expected == value.formatted(template, multiplier, units)


test_str_data: List[Tuple[FormattedValue, str]] = [
    (FormattedValue(10, 0.01), "10.00 ± 0.01"),
    (FormattedValue(10, 0.1), "10.0 ± 0.1"),
    (FormattedValue(100, 10), "(10 ± 1) x 10"),
    (FormattedValue(1000, 100), "(10 ± 1) x 10^2")
]


@pytest.mark.parametrize(
    "value, expected",
    test_str_data
)
def test_str(value: FormattedValue, expected: str):
    assert str(value) == expected
