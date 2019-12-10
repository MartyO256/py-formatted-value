# py-formatted-value

[![Build Status](https://travis-ci.org/MartyO256/py-formatted-value.svg?branch=master)](https://travis-ci.org/MartyO256/py-formatted-value)

---

Format experimental values and their uncertainties using appropriate significant figures and matching decimal places.

---

## Installation

To install `fvalue`, run:
```shell script
pip install fvalue
```

## Examples

The following examples showcase the core features of the library.

```python
from fvalue import FormattedValue
from decimal import Decimal

FormattedValue(
    value=10_973_731.768_160,
    error=0.000_021,
    error_significant_figures=2,
    rounding=FormattedValue.RoundingOption.ROUND_HALF_EVEN,
).formatted(
    template=FormattedValue.SIUNITX_TEMPLATE,
    units=r"\per\meter",
)
# >>> "\SI{10973731.768160 \pm 0.000021 e0}{\per\meter}"

FormattedValue(
    value=0.000_002_671,
    error=0.000_000_452,
    error_significant_figures=1,
).formatted(
    template=FormattedValue.SIUNITX_NUM_TEMPLATE,
)
# >>> "\num{2.7 \pm 0.5 e-6}"

FormattedValue(
    0.000_002_671,
    0.000_000_452,
    error_significant_figures=2,
).formatted(
    FormattedValue.SIUNITX_NUM_TEMPLATE,
    multiplier=10 ** 3,
)
# >>> "0.00267 ± 0.00045"

FormattedValue(
    Decimal("1.602_176_634E-19"),
).formatted(
    FormattedValue.SIUNITX_VALUE_TEMPLATE,
    units=r"\coulomb",
)
# >>> "\SI{1.602176634 e-19}{\coulomb}"

FormattedValue(
    Decimal("1.416_784E32"),
    Decimal("0.000_016E32"),
    error_significant_figures=2,
).formatted(
    FormattedValue.NATURAL_TEMPLATE,
    units=r"K",
)
# >>> "(1416784 ± 16) x 10^26 K"

FormattedValue(
    656,
    10,
).formatted(
    FormattedValue.NATURAL_TEMPLATE,
    units=r"nm",
)
# >>> "(66 ± 1) x 10 nm"
```

## Usage

Instances of `FormattedValue` are used to produce string representations of experimental quantities with their uncertainties.
The number of significant figures in the error on a value is set on instantiation.
The decimal places of the value always match that of the error in formatted strings.
Values of small magnitude are automatically formatted with an appropriate decimal exponent in the scientific notation.

### Rounding

The rounding policies used in the formatting are those of the `decimal` library, namely: `ROUND_HALF_EVEN`, `ROUND_05UP`, `ROUND_CEILING`, `ROUND_DOWN`, `ROUND_FLOOR`, `ROUND_HALF_DOWN`, `ROUND_HALF_UP` and `ROUND_UP`.
All of these are conveniently available as an enumeration at `FormattedValue.RoundingOption`.
By default, `ROUND_HALF_EVEN` is used to mitigate some biases.

### Templates

Templates allow for the placement in strings of the rounded value, error, decimal exponent, and units optionally.
Using the `formatted` method of an instance of `FormattedValue`, strings and callable templates can be used.

If a given template is a string, then:

* `{0}` corresponds to the rounded value;
* `{1}` corresponds to the rounded error;
* `{2}` corresponds to the decimal exponent in scientific notation;
* `{3}` corresponds to the units.

For instance, `"({0} ± {1}) x 10^{2} {3}"` would generate `"(10 ± 1) x 10^0 m"` for a formatted value with value `10`, error `1`, and units `"m"`.

If a given template is a function, then it should have type signature `Callable[[str, str, str, str], str]`, with arguments `(value: str, error: str, exponent: str, units: str) -> str`. 
One such template is accessible at `FormattedValue.NATURAL_TEMPLATE`.

Various templates are available to speed up the generation of formatted strings.
The default template is for [SIUNITX](https://ctan.org/pkg/siunitx), which is accessible at `FormattedValue.SIUNITX_TEMPLATE` and produces strings as `"\SI{{0} \pm {1} e{2}}{{3}}"`.
Other templates include: `Formatted.SIUNITX_VALUE_TEMPLATE`, `Formatted.SIUNITX_ERROR_TEMPLATE`, `Formatted.SIUNITX_NUM_TEMPLATE`, `Formatted.SIUNITX_NUM_VALUE_TEMPLATE`, `Formatted.SIUNITX_NUM_ERROR_TEMPLATE`.

### Multiplier

The `formatted` method of instances of `FormattedValue` allows for a multiplier to be applied to both the value and error of the instance.
This allows for an experimental value to be used using the International System of Units for data processing, and prefixed units to be used for the presentation of results in reports.

## About

### Authors

- **Marc-Antoine Ouimet** - [MartyO256](https://github.com/MartyO256)

### License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md)
file for details.