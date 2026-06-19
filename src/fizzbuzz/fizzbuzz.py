#!/usr/bin/env python3
"""FizzBuzz generator."""


def fizzbuzz(n: int = 100):
    """Yield FizzBuzz values from 1 to n (inclusive)."""
    for i in range(1, n + 1):
        if i % 15 == 0:
            yield "FizzBuzz"
        elif i % 3 == 0:
            yield "Fizz"
        elif i % 5 == 0:
            yield "Buzz"
        else:
            yield str(i)


def main():
    """Print the classic 1-100 FizzBuzz sequence."""
    for line in fizzbuzz():
        print(line)


if __name__ == "__main__":
    main()
