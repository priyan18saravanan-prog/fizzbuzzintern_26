"""Tests for the fizzbuzz module."""

from fizzbuzz import fizzbuzz, main

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
    main()
    captured = capsys.readouterr()
    expected = "\n".join(fizzbuzz()) + "\n"

    assert captured.out == expected
