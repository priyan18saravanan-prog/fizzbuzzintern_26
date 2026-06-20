"""Tests for the fizzbuzz module."""

from fizzbuzz import DEFAULT_RULES, fizzbuzz, main

import pytest


FIRST_FIFTEEN = [
    "1",
    "2",
    "Fizz",
    "4",
    "Buzz",
    "Fizz",
    "7",
    "8",
    "Fizz",
    "Buzz",
    "11",
    "Fizz",
    "13",
    "14",
    "FizzBuzz",
]


@pytest.mark.parametrize(
    ("limit", "expected"),
    [
        pytest.param(0, [], id="zero limit"),
        pytest.param(1, ["1"], id="single item"),
        pytest.param(3, ["1", "2", "Fizz"], id="multiple of three"),
        pytest.param(5, ["1", "2", "Fizz", "4", "Buzz"], id="multiple of five"),
        pytest.param(15, FIRST_FIFTEEN, id="multiple of fifteen"),
    ],
)
def test_fizzbuzz_returns_expected_sequence(limit, expected):
    result = list(fizzbuzz(limit))

    assert result == expected


@pytest.mark.parametrize(
    "limit",
    [1, 15, 100, 1000],
    ids=["one", "fifteen", "one hundred", "one thousand"],
)
def test_fizzbuzz_with_positive_limit_has_exactly_limit_items(limit):
    result = list(fizzbuzz(limit))

    assert len(result) == limit


def test_fizzbuzz_with_negative_limit_returns_empty_sequence():
    result = list(fizzbuzz(-5))

    assert result == []


def test_fizzbuzz_default_limit_is_one_hundred():
    result = list(fizzbuzz())

    assert len(result) == 100


def test_fizzbuzz_default_limit_ends_with_buzz():
    result = list(fizzbuzz())

    assert result[-1] == "Buzz"


def test_main_prints_default_fizzbuzz_sequence(capsys):
    main([])
    captured = capsys.readouterr()
    expected = "\n".join(fizzbuzz()) + "\n"

    assert captured.out == expected


def test_main_with_custom_rules(capsys):
    main(["2:Boom", "7:Baz"])
    captured = capsys.readouterr()
    expected = "\n".join(fizzbuzz(rules=[(2, "Boom"), (7, "Baz")])) + "\n"

    assert captured.out == expected


def test_main_custom_rules_preserve_order(capsys):
    main(["7:Baz", "2:Boom"])
    captured = capsys.readouterr()

    assert captured.out.splitlines()[13] == "BazBoom"


def test_main_rejects_invalid_rule_format():
    with pytest.raises(SystemExit):
        main(["invalid"])


def test_default_rules_are_classic():
    assert DEFAULT_RULES == [(3, "Fizz"), (5, "Buzz")]


@pytest.mark.parametrize(
    ("limit", "rules", "expected"),
    [
        pytest.param(
            5,
            [(3, "Fizz")],
            ["1", "2", "Fizz", "4", "5"],
            id="single fizz rule",
        ),
        pytest.param(
            4,
            [(2, "Boom")],
            ["1", "Boom", "3", "Boom"],
            id="single boom rule",
        ),
    ],
)
def test_fizzbuzz_with_single_rule(limit, rules, expected):
    assert list(fizzbuzz(limit, rules)) == expected


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


@pytest.mark.parametrize(
    ("limit", "rules", "expected"),
    [
        pytest.param(
            10,
            [(2, "Boom"), (5, "Buzz")],
            [
                "1",
                "Boom",
                "3",
                "Boom",
                "Buzz",
                "Boom",
                "7",
                "Boom",
                "9",
                "BoomBuzz",
            ],
            id="concatenated output",
        ),
    ],
)
def test_fizzbuzz_concatenates_matching_words(limit, rules, expected):
    assert list(fizzbuzz(limit, rules)) == expected


@pytest.mark.parametrize(
    ("rules", "expected_last"),
    [
        pytest.param(
            [(2, "Boom"), (7, "Baz")],
            "BoomBaz",
            id="boom before baz",
        ),
        pytest.param(
            [(7, "Baz"), (2, "Boom")],
            "BazBoom",
            id="baz before boom",
        ),
    ],
)
def test_fizzbuzz_preserves_rule_order(rules, expected_last):
    assert list(fizzbuzz(14, rules))[-1] == expected_last


@pytest.mark.parametrize(
    ("index", "expected"),
    [
        pytest.param(0, "1", id="first number"),
        pytest.param(5, "6", id="non-multiple in middle"),
        pytest.param(9, "10", id="last number"),
    ],
)
def test_fizzbuzz_emits_number_when_no_rule_matches(index, expected):
    rules = [(7, "Baz"), (9, "Bam")]
    result = list(fizzbuzz(10, rules))

    assert result[index] == expected


def test_fizzbuzz_with_empty_rules_returns_numbers():
    assert list(fizzbuzz(5, [])) == ["1", "2", "3", "4", "5"]


def test_fizzbuzz_rejects_zero_divisor():
    with pytest.raises(ValueError, match="divisor must be a non-zero integer"):
        list(fizzbuzz(5, [(0, "Bad")]))


def test_fizzbuzz_rejects_empty_word():
    with pytest.raises(ValueError, match="word must be a non-empty string"):
        list(fizzbuzz(5, [(2, "")]))
