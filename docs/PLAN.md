# Refactoring FizzBuzz for Configurable Rules

## 1. Goal

Replace the hardcoded FizzBuzz rules (3 → Fizz, 5 → Buzz) with configurable rules supplied by the user.

Example user-defined rules:

- 2 → Boom
- 7 → Baz
- 9 → Bam

For each number in the sequence, the program should concatenate all words whose associated divisor divides the number, preserving the order in which the rules were provided. If no rule matches, the number itself is emitted as a string.

### Expected Behaviour

Given these rules:

- 2 → Boom
- 7 → Baz

The number 14 should output `BoomBaz` because 14 is divisible by both 2 and 7.

If the rules are provided in the opposite order:

- 7 → Baz
- 2 → Boom

Then 14 should output `BazBoom`, because rule order is preserved.

A number with no matching rules should be emitted as its decimal string (e.g., `1`, `11`).

---

## 2. Background: Generators and Streams

### 2.1 What Python generators are

A Python generator is a special kind of iterator defined by a function containing the `yield` keyword. Each call to `yield` suspends execution, saving the function's local state, and resumes on the next iteration. Generators produce values lazily, one at a time, only when requested by the caller.

Example:

```python
def count_up(start: int, limit: int):
    n = start
    while n <= limit:
        yield n
        n += 1
```

Generators are memory-efficient for sequences because they do not require building the entire sequence in memory at once.

### 2.2 How generators can be used to implement streams

In this project, a "stream" is an ordered, lazily produced sequence of values — one value per input number. A generator function can produce a stream by yielding one transformed value for each integer in a range. Consumers can iterate over a stream without knowing how it is produced.

For example, a stream of remainders for divisibility by 3 could be written as:

```python
def fizz_stream(n: int = 100):
    for i in range(1, n + 1):
        yield "Fizz" if i % 3 == 0 else ""
```

This yields an empty string when there is no match, allowing multiple streams to be combined per position.

### 2.3 What the "addition of streams" concept means in this project

"Addition of streams" means combining two or more streams position by position. For every integer position `i`, take the value from each stream at that position and concatenate them. Each stream contributes either a word (when the rule matches) or an empty string (when it does not). The result is a new combined stream.

For the classic FizzBuzz:

- The **Fizz stream** emits `"Fizz"` for multiples of 3 and `""` otherwise.
- The **Buzz stream** emits `"Buzz"` for multiples of 5 and `""` otherwise.
- Adding the streams position by position yields `"FizzBuzz"` for multiples of 15, `"Fizz"` for multiples of 3 only, `"Buzz"` for multiples of 5 only, and `""` for everything else.

When the concatenated result is empty, the program falls back to the original number string. With configurable rules, each user rule becomes its own stream, and the final output stream is the positional sum (concatenation) of all rule streams.

### 2.4 Why generators are preferred over repeatedly checking every rule with modulo operations

The current implementation combines all rules into nested `if/elif` branches with explicit modulo checks (`i % 15 == 0`, `i % 3 == 0`, `i % 5 == 0`). This approach has several drawbacks:

1. **Hardcoded logic**: Every new rule requires editing the core function and adding more branches.
2. **Scalability**: As the number of rules grows, the conditional complexity grows combinatorially because every combination of rules needs to be considered to preserve ordering.
3. **Duplication**: The divisibility checks are repeated inline for every combination.

Generators solve these problems by:

- Treating each rule as an independent stream.
- Avoiding nested conditionals — each rule only checks one divisor.
- Making the combination step uniform regardless of how many rules exist.
- Preserving insertion order naturally, because streams are iterated in the order the rules were provided.
- Keeping memory usage constant by producing one combined value at a time.

In short: a generator-based stream architecture separates the definition of each rule from the mechanism that combines them, making the system far easier to extend and test.

---

## 3. Proposed Architecture

### 3.1 Components

1. **Rule representation**
   - A rule pairs a divisor (`int`) with a word (`str`).
   - Rules are stored in an ordered container, such as a `list[tuple[int, str]]`, so that insertion order is preserved.

2. **Per-rule stream generator**
   - A generator function that accepts a rule and a limit, and yields one value per integer from 1 to `n`.
   - It yields the rule's word when the current number is divisible by the rule's divisor; otherwise it yields `""`.

3. **Stream combiner**
   - Accepts an ordered collection of rule streams and yields the concatenation of their values at each position.
   - If the concatenation is empty, yields the number as a string.

4. **Public API**
   - The existing `fizzbuzz` function should accept an optional list of rules.
   - Default rules should preserve today's classic behaviour: `[(3, "Fizz"), (5, "Buzz")]`.
   - `main()` should continue to print the default sequence but may be updated later to support command-line rule configuration (out of scope for this refactor unless requested).

### 3.2 Data flow

```
User-supplied rules
        │
        ▼
┌──────────────────┐
│  Ordered rules   │
│  list of tuples  │
└──────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  For each rule, build a per-rule      │
│  generator stream over 1..n           │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  Combine streams position by position:  │
│  concatenated = sum of all rule words   │
│  at index i                             │
└─────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│  If concatenated is empty, emit str(i); │
│  otherwise emit concatenated            │
└─────────────────────────────────────────┘
        │
        ▼
   Yield final value
```

---

## 4. Files to Modify

| File | Reason |
|------|--------|
| `src/fizzbuzz/fizzbuzz.py` | Core logic must be refactored to use configurable rules and generators. |
| `tests/test_fizzbuzz.py` | Existing tests rely on hardcoded `Fizz`/`Buzz`; they must be updated to pass rules explicitly and new tests must be added. |

`src/fizzbuzz/__init__.py` and `src/fizzbuzz/__main__.py` should remain unchanged unless a public-facing export or CLI argument handling is added later.

---

## 5. How Configurable Rules Should Flow Through the Program

### 5.1 Signature change

Change the `fizzbuzz` function signature from:

```python
def fizzbuzz(n: int = 100):
```

to:

```python
from collections.abc import Sequence

def fizzbuzz(n: int = 100, rules: Sequence[tuple[int, str]] | None = None):
```

When `rules` is `None`, default to the classic rules `[(3, "Fizz"), (5, "Buzz")]`.

### 5.2 Validation

Consider validating rules:

- Each divisor must be a non-zero integer. A divisor of zero would cause a `ZeroDivisionError` during modulo checks.
- Each word must be a non-empty string. Empty words would silently produce no output and could confuse concatenation.

Validation can either raise `ValueError` immediately when the function is called or be tested as documented preconditions. For this refactor, raising a clear `ValueError` for invalid rules is recommended.

### 5.3 Implementation approach

Inside `fizzbuzz(n, rules)`:

1. Resolve `rules` to a concrete `list` with a stable order.
2. Loop `i` from `1` to `n` (inclusive).
3. For each `i`, iterate over `rules` in order:
   - If `i % divisor == 0`, append `word` to a result buffer.
4. After all rules are checked:
   - If the result buffer is non-empty, yield `''.join(buffer)`.
   - Else, yield `str(i)`.

This loop is itself a generator because it includes `yield`, so values are produced lazily.

Example structure:

```python
def fizzbuzz(n: int = 100, rules: Sequence[tuple[int, str]] | None = None):
    if rules is None:
        rules = [(3, "Fizz"), (5, "Buzz")]

    for divisor, word in rules:
        if not isinstance(divisor, int) or divisor == 0:
            raise ValueError(f"Invalid divisor: {divisor!r}")
        if not isinstance(word, str) or not word:
            raise ValueError(f"Invalid word: {word!r}")

    for i in range(1, n + 1):
        out = ''.join(word for divisor, word in rules if i % divisor == 0)
        yield out if out else str(i)
```

This single generator directly implements the stream-combination idea. Alternatively, you may implement separate `rule_stream(rule, n)` and `combine_streams(streams, n)` helpers for clarity and reuse.

### 5.4 Maintaining backward compatibility

Because `rules` defaults to the classic rules, all existing callers that pass only a limit continue to work. Callers that pass no arguments still receive the classic 1–100 sequence.

`main()` should call `fizzbuzz()` without arguments so that the default rules apply.

---

## 6. How Rule Order Will Be Preserved

Insertion order is preserved by two design choices:

1. **Rule container**: Use an ordered sequence (`list` or `tuple`) rather than an unordered set or dictionary.
2. **Iteration order**: When building the output for each number, always iterate over the rules in the order they appear in the container and append matching words to the result buffer in that same order.

Given rules `[(2, "Boom"), (7, "Baz")]` and the number 14, the inner join sees `"Boom"` first and `"Baz"` second, yielding `"BoomBaz"`. Reversing the list reverses the concatenation.

Tests should explicitly verify both orderings for the same number to ensure this behaviour is locked in.

---

## 7. Updating Existing Tests

### 7.1 Default-rule tests

The tests `test_fizzbuzz_returns_expected_sequence` and `test_fizzbuzz_with_positive_limit_has_exactly_limit_items` already call `fizzbuzz(limit)`. Because the default rules remain `[(3, "Fizz"), (5, "Buzz")]`, these tests should continue to pass unchanged, but their assertions should be reviewed to ensure they match the new default.

### 7.2 Default-limit tests

- `test_fizzbuzz_default_limit_is_one_hundred` can remain unchanged.
- `test_fizzbuzz_default_limit_ends_with_buzz` can remain unchanged.

### 7.3 Main-capture test

`test_main_prints_default_fizzbuzz_sequence` currently compares the captured stdout against `"\n".join(fizzbuzz()) + "\n"`. Because `main()` will continue to use the default rules, this test can remain as-is.

### 7.4 Refactoring recommendations

Consider extracting the classic rules into a module constant so tests can import them rather than duplicating `[(3, "Fizz"), (5, "Buzz")]`:

```python
DEFAULT_RULES: list[tuple[int, str]] = [(3, "Fizz"), (5, "Buzz")]
```

This reduces duplication and makes intent explicit.

---

## 8. New Tests to Add

All new tests should live in `tests/test_fizzbuzz.py`. Use `parametrize` where appropriate to keep the file clean.

### 8.1 Single rule

Verify that a single rule produces the expected word for its multiples and the number string for non-matches.

```python
@pytest.mark.parametrize(
    ("limit", "expected"),
    [
        pytest.param(5, [(3, "Fizz")], ["1", "2", "Fizz", "4", "5"], id="single fizz rule"),
    ],
)
def test_fizzbuzz_with_single_rule(limit, rules, expected):
    assert list(fizzbuzz(limit, rules)) == expected
```

### 8.2 Multiple rules without overlap

Verify that multiple rules apply independently when numbers are not multiples of more than one divisor.

```python
@pytest.mark.parametrize(
    ("limit", "rules", "expected"),
    [
        pytest.param(
            6,
            [(2, "Boom"), (5, "Buzz")],
            ["1", "Boom", "3", "Boom", "Buzz", "Boom"],
            id="two rules no overlap",
        ),
    ],
)
def test_fizzbuzz_with_multiple_rules(limit, rules, expected):
    assert list(fizzbuzz(limit, rules)) == expected
```

### 8.3 Concatenated outputs

Verify that a number matching more than one rule receives all matching words concatenated.

```python
@pytest.mark.parametrize(
    ("limit", "rules", "expected"),
    [
        pytest.param(
            10,
            [(2, "Boom"), (5, "Buzz")],
            ["1", "Boom", "3", "Boom", "Buzz", "Boom", "7", "Boom", "9", "BoomBuzz"],
            id="concatenated output",
        ),
    ],
)
def test_fizzbuzz_concatenates_matching_words(limit, rules, expected):
    assert list(fizzbuzz(limit, rules)) == expected
```

### 8.4 Preservation of insertion order

Verify that reversing the rule list reverses the concatenated output.

```python
@pytest.mark.parametrize(
    ("rules", "expected"),
    [
        pytest.param(
            [(2, "Boom"), (7, "Baz")],
            [..., "BoomBaz", ...],
            id="boom before baz",
        ),
        pytest.param(
            [(7, "Baz"), (2, "Boom")],
            [..., "BazBoom", ...],
            id="baz before boom",
        ),
    ],
)
def test_fizzbuzz_preserves_rule_order(rules, expected):
    assert list(fizzbuzz(14, rules))[-1] == expected[-1]
```

A more explicit version checks the 14th item directly:

```python
def test_rule_order_affects_concatenation():
    assert list(fizzbuzz(14, [(2, "Boom"), (7, "Baz")]))[-1] == "BoomBaz"
    assert list(fizzbuzz(14, [(7, "Baz"), (2, "Boom")]))[-1] == "BazBoom"
```

### 8.5 Numbers with no matching rule

Verify that when none of the rules match a number, the raw number string is emitted.

```python
def test_fizzbuzz_emits_number_when_no_rule_matches():
    rules = [(7, "Baz"), (9, "Bam")]
    result = list(fizzbuzz(10, rules))

    assert result[0] == "1"
    assert result[5] == "6"
    assert result[9] == "10"
```

### 8.6 Empty rules

Add a test for an empty rule list to document that the function returns number strings only.

```python
def test_fizzbuzz_with_empty_rules_returns_numbers():
    assert list(fizzbuzz(5, [])) == ["1", "2", "3", "4", "5"]
```

### 8.7 Invalid rules

Add tests for invalid rule inputs to ensure clear, early failures.

```python
def test_fizzbuzz_rejects_zero_divisor():
    with pytest.raises(ValueError):
        list(fizzbuzz(5, [(0, "Bad")]))


def test_fizzbuzz_rejects_empty_word():
    with pytest.raises(ValueError):
        list(fizzbuzz(5, [(2, "")]))
```

---

## 9. Implementation Steps

Follow these steps in order. Do not move to the next step until the current one is fully implemented and tested.

1. **Understand the current code**
   - Read `src/fizzbuzz/fizzbuzz.py` and `tests/test_fizzbuzz.py`.
   - Confirm the current hardcoded `if/elif` logic and the existing test expectations.

2. **Add a default rules constant**
   - In `src/fizzbuzz/fizzbuzz.py`, add a module-level constant:
     ```python
     DEFAULT_RULES: list[tuple[int, str]] = [(3, "Fizz"), (5, "Buzz")]
     ```

3. **Update the `fizzbuzz` function signature**
   - Add a `rules` parameter with type `Sequence[tuple[int, str]] | None`.
   - Default it to `None` and resolve to `DEFAULT_RULES` inside the function.

4. **Implement rule validation**
   - Inside `fizzbuzz`, validate every `(divisor, word)` pair:
     - `divisor` must be a non-zero integer.
     - `word` must be a non-empty string.
   - Raise `ValueError` with a descriptive message for invalid input.

5. **Replace hardcoded branches with configurable concatenation**
   - Remove the `if/elif` chain.
   - For each integer `i` from `1` to `n`, build `output = ''.join(word for divisor, word in rules if i % divisor == 0)`.
   - Yield `output` if it is non-empty; otherwise yield `str(i)`.

6. **Ensure `main()` still uses defaults**
   - Verify that `main()` calls `fizzbuzz()` with no arguments so the default rules apply.
   - No change should be needed unless `main()` is later extended for CLI rule configuration.

7. **Run existing tests**
   - Execute `pytest` to ensure that default-rule behaviour is preserved.
   - If necessary, update any broken tests to align with the new signature or `main()` behaviour.

8. **Add new tests for configurable rules**
   - Single rule (`[(3, "Fizz")]`).
   - Multiple rules without overlap (`[(2, "Boom"), (5, "Buzz")]`).
   - Concatenated outputs (e.g., 10 with rules 2 and 5).
   - Preservation of insertion order (14 with `[(2, "Boom"), (7, "Baz")]` and reversed).
   - Numbers with no matching rule.
   - Empty rule list.
   - Invalid rule inputs (zero divisor, empty word).

9. **Run the full test suite**
   - Execute `pytest -v`.
   - Verify that all new and existing tests pass.

10. **Review and document**
    - Re-read `src/fizzbuzz/fizzbuzz.py` to confirm it is clear, type-annotated, and docstrings are updated.
    - Update docstrings on `fizzbuzz()` and `main()` to mention the new `rules` parameter and default behaviour.
    - Ensure `README.md` accurately describes how to use the configurable rules.
    - Verify that `pyproject.toml` does not require dependency changes for this refactor.

---

## 10. Acceptance Criteria

After implementation, the project should satisfy all of the following:

- [ ] `fizzbuzz.py` accepts an optional ordered sequence of `(divisor, word)` rules.
- [ ] Default behaviour (no rules provided) remains the classic 3 → Fizz, 5 → Buzz sequence.
- [ ] Multiple matching rules for one number produce a concatenated string in rule order.
- [ ] Non-matching numbers produce their decimal string representation.
- [ ] Rule order changes are reflected in the output.
- [ ] Invalid rules raise `ValueError` with a clear message.
- [ ] All existing tests pass after any required updates.
- [ ] New tests cover single rules, multiple rules, concatenation, order preservation, non-matching numbers, empty rules, and invalid rules.
- [ ] The full test suite passes with no errors or warnings.
