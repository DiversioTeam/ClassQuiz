# Python Data Model – Session 2 Quiz (Hard Mode) — Answer Key

This matches `session2_quiz.md` exactly (Q1–Q30).

---

## Q1 – The Copy That Wasn't
**Correct:** `[[0, 9, 0], [0, 9, 0]]`
**Why:** `[[0] * 3] * 2` duplicates the *same inner list reference* twice. Mutating one row mutates both.

## Q2 – Alias vs Copy
**Correct:** `[1, 2, 3] [1, 2]`
**Why:** `b = a` aliases the same list, but `c = a[:]` is a shallow copy. `b.append(3)` mutates `a` (and `b`), not `c`.

## Q3 – The Sneaky Shared List
**Correct:** `[1, 2] [1, 2]`
**Why:** `xs` is a class attribute (shared). `self.xs.append(...)` mutates the shared list.

## Q4 – Shadowboxing Attributes
**Correct:** `['local'] [1, 2]`
**Why:** `c.xs.append(1)` mutates the class list. Then `c.xs = ["local"]` creates an instance attribute that shadows the class attribute. `C.xs.append(2)` mutates the class list again.

---

## Q5 – Iterable Without __iter__
**Correct:** `get 0 | x 10 | get 1 | x 20 | get 2`
**Why:** With no `__iter__`, `for` falls back to the *sequence protocol*: calls `__getitem__(0)`, `__getitem__(1)`, ... until `IndexError`. The final `get 2` prints, then indexing raises `IndexError` and the loop ends.

## Q6 – __iter__ Returned a Liar
**Correct:** `TypeError`
**Why:** `__iter__` must return an *iterator* (something with `__next__`). Returning `self` without `__next__` makes `iter()` complain: "returned non-iterator".

## Q7 – "in" Without __contains__
**Correct:** `iter | yield 1 | yield 2 | A: True | contains | B: True`
**Why:** If `__contains__` is missing, `in` falls back to iteration and stops as soon as it finds a match (`2`). If `__contains__` exists, Python calls it directly (no iteration, fewer prints).

## Q8 – __contains__ Takes Priority
**Correct:** `contains | caught`
**Why:** Membership testing prefers `__contains__`. If `__contains__` raises, Python does not fall back to iteration; the exception propagates (and gets caught here).

## Q9 – Slices Are Objects
**Correct:** `int 1 | slice slice(1, 4, None) | slice slice(None, None, None)`
**Why:** `obj[i]` passes an `int`. `obj[a:b]` passes a `slice(a, b, None)`. `obj[:]` is `slice(None, None, None)`.

## Q10 – Truthiness: __bool__ Beats __len__
**Correct:** `bool | False | bool | F`
**Why:** When `__bool__` exists, it defines truthiness; `__len__` is ignored for `if w:`. `bool(w)` calls `__bool__`, and `if w:` calls truthiness again (so `__bool__` runs twice).

## Q11 – __bool__ Must Return bool
**Correct:** `TypeError`
**Why:** `__bool__` is required to return an actual `bool`. Returning `1` (an `int`) triggers `TypeError`.

## Q12 – __len__ Must Be Non-Negative
**Correct:** `ValueError`
**Why:** `__len__` must return an integer `>= 0`. Returning `-1` raises `ValueError`.

## Q13 – __repr__ Must Return str
**Correct:** `TypeError`
**Why:** `__repr__` must return a Python `str`, not `bytes`.

## Q14 – f-strings: !r vs default
**Correct:** `S R`
**Why:** `{x}` uses `__str__` (string form). `{x!r}` forces `repr(x)` (uses `__repr__`).

---

## Q15 – NotImplemented Is a Relay Baton
**Correct:** `A | B | True`
**Why:** `A.__eq__` returns `NotImplemented` to signal "I don't know". Python then tries the reflected comparison `B.__eq__`, which returns `True`.

## Q16 – When Nobody Knows
**Correct:** `A | B | False`
**Why:** Both sides return `NotImplemented`. For equality, Python falls back to identity comparison (`is`). Two distinct instances are not identical, so result is `False`.

## Q17 – NotImplemented Even On Yourself
**Correct:** `eq | eq | True`
**Why:** Python tries left `__eq__` then the reflected `__eq__` (same method again here) when it sees `NotImplemented`. After both return `NotImplemented`, it falls back to identity. Since it's the same object, identity is `True`.

## Q18 – The Symmetry Bug
**Correct:** `A | False | B | True`
**Why:** Returning `False` is a *final answer*, so Python will not try the other side. That makes `A() == B()` and `B() == A()` disagree — a classic reason to return `NotImplemented` for unknown types instead.

## Q19 – Ordering Is Less Forgiving
**Correct:** `L< | R> | TypeError`
**Why:** For ordering (`<`, `>`, etc.), if both sides return `NotImplemented`, Python raises `TypeError` (unlike equality, which falls back to `False`/identity).

---

## Q20 – "Why Can't I Put This In a set?"
**Correct:** `TypeError`
**Why:** Defining `__eq__` makes Python set `__hash__ = None` by default (unhashable). This prevents "equal objects with different hashes" bugs unless you explicitly define a consistent hash.

## Q21 – The Broken Hash Contract
**Correct:** `True 2`
**Why:** `p1 == p2` is `True`, but `__hash__ = object.__hash__` is identity-based, so their hashes differ. A `set` uses hashes to bucket items; different hashes means both get stored, so length is `2`.

## Q22 – Mutating a Key After Insertion
**Correct:** `True` then `False`
**Why:** The set stores the object in a bucket based on its hash at insertion time. Changing `name` changes the hash, so later lookups search the wrong bucket and fail. (This is why "hashable implies effectively immutable" is a design rule.)

---

## Q23 – NotImplemented In Addition
**Correct:** `L+ | R+r | ok`
**Why:** `L.__add__` returns `NotImplemented`, so Python tries the reflected method `R.__radd__`, which returns `"ok"`.

## Q24 – Why sum() Fails Without __radd__
**Correct:** `TypeError`
**Why:** `sum()` starts at `0`, so it first evaluates `0 + Num(1)`. That requires `Num.__radd__` to handle the `int` on the left. Without it, Python raises `TypeError`.

## Q25 – The sum() Identity Trick
**Correct:** `Num(3)`
**Why:** `__radd__` treats `other == 0` as the identity element, letting `sum()` bootstrap the first addition. Then normal `__add__` combines values.

---

## Q26 – Callable Objects Keep State
**Correct:** `1 3 4`
**Why:** The object stores state (`self.n`). Calls update it: `0→1`, then `+2` gives `3`, then `+1` gives `4`.

## Q27 – Memoization: Same Input, Less Work
**Correct:** `miss 3 | hit 3 | miss 4 | 9 9 16`
**Why:** First `3` is computed and cached. Second `3` is a cache hit. `4` is a miss. The final `print(...)` prints the returned values.

---

## Q28 – __exit__ Can Swallow Exceptions
**Correct:** `enter | in VALUE | exit ZeroDivisionError | after`
**Why:** Returning `True` from `__exit__` suppresses the exception, so execution continues after the `with`.

## Q29 – __exit__ Still Runs, But Exception Escapes
**Correct:** `enter | in VALUE | exit ZeroDivisionError | crash`
**Why:** `__exit__` runs on exception, but returning `False` (or `None`) means "do not swallow", so the exception is re-raised and caught by the outer `try`.

## Q30 – Two Managers, One With: Exit Order
**Correct:** `enter A | enter B | body | exit B | exit A`
**Why:** Multiple context managers in one `with` behave like nested `with` blocks: enter left-to-right, exit right-to-left (stack discipline).

---
