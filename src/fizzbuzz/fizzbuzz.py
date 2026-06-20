#!/usr/bin/env python3
"""FizzBuzz generator with configurable rules.

Rules are modeled as independent streams. Each rule yields a word at positions
where it matches and an empty string otherwise. The output stream is the
position-by-position concatenation ("addition") of all rule streams.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator, Sequence

DEFAULT_RULES: list[tuple[int, str]] = [(3, "Fizz"), (5, "Buzz")]


def _validate_rules(rules: Sequence[tuple[int, str]]) -> None:
    """Validate a sequence of FizzBuzz rules.

    Args:
        rules: Ordered sequence of ``(divisor, word)`` pairs.

    Raises:
        ValueError: If a divisor is zero or not an integer, or if a word is
            not a non-empty string.
    """
    for divisor, word in rules:
        if not isinstance(divisor, int) or divisor == 0:
            raise ValueError(
                f"Rule divisor must be a non-zero integer, got {divisor!r}"
            )
        if not isinstance(word, str) or not word:
            raise ValueError(
                f"Rule word must be a non-empty string, got {word!r}"
            )


def _rule_stream(rule: tuple[int, str], n: int) -> Iterator[str]:
    """Yield one value per integer from 1 to ``n`` for a single rule.

    Args:
        rule: A ``(divisor, word)`` pair.
        n: Upper bound of the sequence.

    Yields:
        ``word`` when the current number is divisible by ``divisor``,
        otherwise an empty string.
    """
    divisor, word = rule
    for i in range(1, n + 1):
        yield word if i % divisor == 0 else ""


def _combine_streams(streams: Sequence[Iterator[str]]) -> Iterator[str]:
    """Combine rule streams position by position.

    For each position, concatenate the values from every stream. If the
    concatenation is empty, emit the position number as a string instead.

    Args:
        streams: Ordered rule streams to combine.

    Yields:
        The combined output at each position.
    """
    for i, parts in enumerate(zip(*streams), start=1):
        out = "".join(parts)
        yield out if out else str(i)


def fizzbuzz(
    n: int = 100,
    rules: Sequence[tuple[int, str]] | None = None,
) -> Iterator[str]:
    """Yield FizzBuzz values from 1 to ``n`` (inclusive).

    Args:
        n: Upper bound of the sequence.
        rules: Ordered sequence of ``(divisor, word)`` rules. When ``None``,
            the classic rules ``[(3, "Fizz"), (5, "Buzz")]`` are used.

    Yields:
        The concatenation of all matching rule words for each number, or the
        number itself as a string when no rule matches.

    Raises:
        ValueError: If any rule is invalid.
    """
    if rules is None:
        rules = DEFAULT_RULES

    _validate_rules(rules)

    if not rules:
        # With no rules there are no streams to combine; emit the numbers.
        yield from (str(i) for i in range(1, n + 1))
        return

    streams = [_rule_stream(rule, n) for rule in rules]
    yield from _combine_streams(streams)


def _parse_rule(raw: str) -> tuple[int, str]:
    """Parse a ``divisor:word`` rule string.

    Args:
        raw: A rule in the form ``"2:Boom"``.

    Returns:
        A ``(divisor, word)`` pair.

    Raises:
        ValueError: If the rule is not in ``divisor:word`` form, the divisor
            is not a valid non-zero integer, or the word is empty.
    """
    if ":" not in raw:
        raise ValueError(
            f"Rule must be in 'divisor:word' format, got {raw!r}"
        )

    divisor_text, word = raw.split(":", 1)
    try:
        divisor = int(divisor_text)
    except ValueError as exc:
        raise ValueError(
            f"Rule divisor must be an integer, got {divisor_text!r}"
        ) from exc

    if not word:
        raise ValueError(f"Rule word must be non-empty in {raw!r}")

    return divisor, word


def main(argv: Sequence[str] | None = None) -> None:
    """Print the FizzBuzz sequence.

    If no rules are supplied, the classic rules ``3:Fizz`` and ``5:Buzz``
    are used. Rules are given as ``divisor:word`` pairs, e.g. ``2:Boom``.
    """
    parser = argparse.ArgumentParser(
        description="Configurable FizzBuzz generator."
    )
    parser.add_argument(
        "rules",
        nargs="*",
        help=(
            "Optional rules as divisor:word pairs "
            "(e.g., 2:Boom 7:Baz). Defaults to 3:Fizz 5:Buzz."
        ),
    )
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.rules:
        try:
            rules = [_parse_rule(r) for r in args.rules]
        except ValueError as exc:
            parser.error(str(exc))
    else:
        rules = None

    for line in fizzbuzz(rules=rules):
        print(line)


if __name__ == "__main__":
    main()
