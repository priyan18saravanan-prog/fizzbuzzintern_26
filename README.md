# FizzBuzz

A configurable Python FizzBuzz package with tests.

## Installation

```bash
pip install -e .
```

## Usage

### Default rules

Run directly with Python:

```bash
python -m fizzbuzz
```

Or, after installing, run the CLI entry point:

```bash
fizzbuzz
```

With no arguments, the program prints the classic 1–100 FizzBuzz sequence
using the default rules `3:Fizz` and `5:Buzz`:

```text
1
2
Fizz
4
Buzz
Fizz
...
```

### Custom rules from the command line

Pass custom rules as `divisor:word` arguments. Rules are evaluated in the
order you provide them.

```bash
fizzbuzz 2:Boom 7:Baz
```

Output:

```text
1
Boom
3
Boom
5
Boom
Baz
Boom
9
Boom
11
Boom
13
BoomBaz
15
...
```

Rule order matters. Reversing the rules reverses the concatenation:

```bash
fizzbuzz 7:Baz 2:Boom
```

For the number 14, this prints `BazBoom` instead of `BoomBaz`.

### Custom rules from Python

The `fizzbuzz` function accepts an optional ordered sequence of
`(divisor, word)` rules. Default rules are `[(3, "Fizz"), (5, "Buzz")]`.

```python
from fizzbuzz import fizzbuzz

# Classic rules.
print(list(fizzbuzz(15)))

# Custom rules, evaluated in order.
print(list(fizzbuzz(20, [(2, "Boom"), (7, "Baz")])))
```

Matching rules are concatenated in the order they were provided. If no rule
matches, the number itself is emitted as a string.

### Validation

Rules are validated before the sequence is generated:

- The divisor must be a non-zero integer.
- The word must be a non-empty string.

Invalid rules raise `ValueError` with a clear message.

## Tests

After installing, run:

```bash
pytest -v
```

Or without installing:

```bash
PYTHONPATH=src pytest -v
```
