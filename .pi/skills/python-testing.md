---
name: python-testing
description: Rules for writing high-quality pytest unit tests
---

- Always use pytest.
- Never generate unittest code.
- Never generate test classes.
- Generate standalone test functions only.
- Use @pytest.mark.parametrize whenever two or more test cases follow the same pattern.
- Use pytest fixtures whenever setup is shared between multiple tests.
- Every test must contain exactly one assert.
- Test names must clearly describe the behavior being tested.
- Cover normal cases, edge cases, and boundary conditions.
- Keep tests concise and readable.