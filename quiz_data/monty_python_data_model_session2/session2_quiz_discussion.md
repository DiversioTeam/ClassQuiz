# Python Data Model – Session 2 Quiz: Discussion Guide

Quick warm-up (Session 1 recap), then deep protocol puzzles from Session 2.
Assume Python 3.x.

This document combines questions, correct answers, and explanations for
post-quiz review and discussion.

---

## Q1 – The Copy That Wasn't (Easy)

**Question:** What does this print?

```python
m = [[0] * 3] * 2
m[0][1] = 9
print(m)
```

**Choices:**
- A) `[[0, 9, 0], [0, 9, 0]]` ✅
- B) `[[0, 9, 0], [0, 0, 0]]`
- C) `[[0, 0, 0], [0, 9, 0]]`
- D) `[[0, 9, 0]]`

**Answer: A**

**Explanation:** `[[0] * 3] * 2` duplicates the *same inner list reference* twice. Mutating one row mutates both. This is the classic "bad matrix" gotcha from Session 1.

---

## Q2 – Alias vs Copy (Easy)

**Question:** What does this print?

```python
a = [1, 2]
b = a
c = a[:]

b.append(3)
print(a, c)
```

**Choices:**
- A) `[1, 2, 3] [1, 2]` ✅
- B) `[1, 2, 3] [1, 2, 3]`
- C) `[1, 2] [1, 2, 3]`
- D) `[1, 2] [1, 2]`

**Answer: A**

**Explanation:** `b = a` aliases the same list, but `c = a[:]` is a shallow copy. `b.append(3)` mutates `a` (and `b`), not `c`.

---

## Q3 – The Sneaky Shared List (Medium)

**Question:** What does this print?

```python
class C:
    xs = []
    def add(self, v):
        self.xs.append(v)

c1 = C()
c2 = C()

c1.add(1)
c2.add(2)

print(c1.xs, c2.xs)
```

**Choices:**
- A) `[1, 2] [1, 2]` ✅
- B) `[1] [2]`
- C) `[1, 2] [2]`
- D) `[] []`

**Answer: A**

**Explanation:** `xs` is a class attribute (shared). `self.xs.append(...)` mutates the shared list. Both `c1` and `c2` see the same list.

---

## Q4 – Shadowboxing Attributes (Medium)

**Question:** What does this print?

```python
class C:
    xs = []

c = C()

c.xs.append(1)      # mutate the class list
c.xs = ["local"]    # rebind: creates an instance attribute
C.xs.append(2)      # mutate the class list again

print(c.xs, C.xs)
```

**Choices:**
- A) `['local'] [1, 2]` ✅
- B) `[1, 2] [1, 2]`
- C) `['local', 2] [1]`
- D) `['local'] [2]`

**Answer: A**

**Explanation:** `c.xs.append(1)` mutates the class list (making it `[1]`). Then `c.xs = ["local"]` creates an instance attribute that shadows the class attribute. `C.xs.append(2)` mutates the class list again (making it `[1, 2]`). After shadowing, `c.xs` refers to the instance attribute `['local']`, while `C.xs` is `[1, 2]`.

---

## Q5 – Iterable Without __iter__ (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class W:
    def __init__(self):
        self.data = [10, 20]

    def __getitem__(self, i):
        print("get", i)
        return self.data[i]

for x in W():
    print("x", x)
```

**Choices:**
- A) `get 0 | x 10 | get 1 | x 20 | get 2` ✅
- B) `get 0 | get 1 | get 2`
- C) `x 10 | x 20`
- D) `TypeError`

**Answer: A**

**Explanation:** With no `__iter__`, `for` falls back to the *sequence protocol*: calls `__getitem__(0)`, `__getitem__(1)`, ... until `IndexError`. The final `get 2` prints, then indexing raises `IndexError` (since `self.data[2]` is out of bounds) and the loop ends silently. Note: the loop body runs *after* each successful `__getitem__` call.

---

## Q6 – __iter__ Returned a Liar (Hard)

**Question:** What prints?

```python
class BadIter:
    def __iter__(self):
        return self

try:
    for x in BadIter():
        print("body", x)
except Exception as e:
    print(type(e).__name__)
```

**Choices:**
- A) `TypeError` ✅
- B) `StopIteration`
- C) `AttributeError`
- D) `body None`

**Answer: A**

**Explanation:** `__iter__` must return an *iterator* (something with `__next__`). Returning `self` without defining `__next__` makes `iter()` complain: "iter() returned non-iterator of type 'BadIter'". This is a `TypeError`.

---

## Q7 – "in" Without __contains__ (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class A:
    def __init__(self):
        self.data = [1, 2, 3]

    def __iter__(self):
        print("iter")
        for x in self.data:
            print("yield", x)
            yield x

class B(A):
    def __contains__(self, item):
        print("contains")
        return item in self.data

print("A:", 2 in A())
print("B:", 2 in B())
```

**Choices:**
- A) `iter | yield 1 | yield 2 | A: True | contains | B: True` ✅
- B) `contains | B: True | iter | yield 1 | yield 2 | A: True`
- C) `iter | yield 1 | yield 2 | yield 3 | A: True | contains | B: True`
- D) `A: True | B: True`

**Answer: A**

**Explanation:** If `__contains__` is missing, `in` falls back to iteration and stops as soon as it finds a match (`2`). That's why we see `yield 1`, then `yield 2`, then it stops (no `yield 3`). If `__contains__` exists, Python calls it directly (no iteration, fewer prints).

---

## Q8 – __contains__ Takes Priority (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class C:
    def __iter__(self):
        print("iter")
        yield 1

    def __contains__(self, item):
        print("contains")
        raise RuntimeError("boom")

try:
    print(1 in C())
except RuntimeError:
    print("caught")
```

**Choices:**
- A) `contains | caught` ✅
- B) `iter | contains | caught`
- C) `iter | caught`
- D) `False`

**Answer: A**

**Explanation:** Membership testing prefers `__contains__`. If `__contains__` raises, Python does *not* fall back to iteration; the exception propagates. The `__iter__` method is never called.

---

## Q9 – Slices Are Objects (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class S:
    def __getitem__(self, idx):
        print(type(idx).__name__, idx)
        return 0

s = S()
_ = s[1]
_ = s[1:4]
_ = s[:]
```

**Choices:**
- A) `int 1 | slice slice(1, 4, None) | slice slice(None, None, None)` ✅
- B) `int 1 | int 1:4 | int :`
- C) `slice 1 | slice 1:4 | slice :`
- D) `TypeError`

**Answer: A**

**Explanation:** `obj[i]` passes an `int`. `obj[a:b]` passes a `slice(a, b, None)`. `obj[:]` is `slice(None, None, None)`. Slices are first-class objects in Python, which is how custom containers can support slicing.

---

## Q10 – Truthiness: __bool__ Beats __len__ (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class W:
    def __len__(self):
        print("len")
        return 10

    def __bool__(self):
        print("bool")
        return False

w = W()
print(bool(w))

if w:
    print("T")
else:
    print("F")
```

**Choices:**
- A) `bool | False | bool | F` ✅
- B) `len | bool | False | F`
- C) `len | 10 | bool | False | F`
- D) `bool | False | len | 10 | F`

**Answer: A**

**Explanation:** When `__bool__` exists, it defines truthiness; `__len__` is ignored for boolean contexts. `bool(w)` calls `__bool__`, and `if w:` calls truthiness again (so `__bool__` runs twice). `__len__` is never called.

---

## Q11 – __bool__ Must Return bool (Medium)

**Question:** What prints?

```python
class Bad:
    def __bool__(self):
        return 1

try:
    print(bool(Bad()))
except TypeError as e:
    print(type(e).__name__)
```

**Choices:**
- A) `TypeError` ✅
- B) `True`
- C) `1`
- D) `False`

**Answer: A**

**Explanation:** `__bool__` is required to return an actual `bool`. Returning `1` (an `int`) triggers `TypeError`: "__bool__ should return bool, returned int".

---

## Q12 – __len__ Must Be Non-Negative (Medium)

**Question:** What prints?

```python
class BadLen:
    def __len__(self):
        return -1

try:
    print(len(BadLen()))
except Exception as e:
    print(type(e).__name__)
```

**Choices:**
- A) `ValueError` ✅
- B) `-1`
- C) `TypeError`
- D) `0`

**Answer: A**

**Explanation:** `__len__` must return an integer `>= 0`. Returning `-1` raises `ValueError`: "__len__() should return >= 0".

---

## Q13 – __repr__ Must Return str (Medium)

**Question:** What prints?

```python
class BadRepr:
    def __repr__(self):
        return b"oops"

try:
    print(repr(BadRepr()))
except TypeError as e:
    print(type(e).__name__)
```

**Choices:**
- A) `TypeError` ✅
- B) `b'oops'`
- C) `'oops'`
- D) `AttributeError`

**Answer: A**

**Explanation:** `__repr__` must return a Python `str`, not `bytes`. Returning `b"oops"` triggers `TypeError`.

---

## Q14 – f-strings: !r vs default (Medium)

**Question:** What does this print?

```python
class X:
    def __repr__(self):
        return "R"

    def __str__(self):
        return "S"

x = X()
print(f"{x} {x!r}")
```

**Choices:**
- A) `S R` ✅
- B) `R S`
- C) `S S`
- D) `R R`

**Answer: A**

**Explanation:** `{x}` uses `__str__` (string form). `{x!r}` forces `repr(x)` (uses `__repr__`).

---

## Q15 – NotImplemented Is a Relay Baton (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class A:
    def __eq__(self, other):
        print("A")
        return NotImplemented

class B:
    def __eq__(self, other):
        print("B")
        return True

print(A() == B())
```

**Choices:**
- A) `A | B | True` ✅
- B) `A | True`
- C) `B | True`
- D) `A | B | False`

**Answer: A**

**Explanation:** `A.__eq__` returns `NotImplemented` to signal "I don't know how to compare with this type". Python then tries the reflected comparison `B.__eq__`, which returns `True`. `NotImplemented` is a relay baton, not a final answer.

---

## Q16 – When Nobody Knows (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class A:
    def __eq__(self, other):
        print("A")
        return NotImplemented

class B:
    def __eq__(self, other):
        print("B")
        return NotImplemented

print(A() == B())
```

**Choices:**
- A) `A | B | False` ✅
- B) `A | B | True`
- C) `A | False`
- D) `TypeError`

**Answer: A**

**Explanation:** Both sides return `NotImplemented`. For equality, Python falls back to identity comparison (`is`). Two distinct instances are not identical, so result is `False`. (Ordering comparisons raise `TypeError` instead of falling back.)

---

## Q17 – NotImplemented Even On Yourself (Very Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class A:
    def __eq__(self, other):
        print("eq")
        return NotImplemented

a = A()
print(a == a)
```

**Choices:**
- A) `eq | eq | True` ✅
- B) `eq | True`
- C) `True`
- D) `eq | eq | False`

**Answer: A**

**Explanation:** Python tries left `__eq__` first (prints "eq", returns `NotImplemented`), then the reflected `__eq__` (same method again, prints "eq", returns `NotImplemented`). After both return `NotImplemented`, Python falls back to identity. Since it's the same object, identity is `True`.

---

## Q18 – The Symmetry Bug (Very Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class A:
    def __eq__(self, other):
        print("A")
        return False  # notice: NOT NotImplemented

class B:
    def __eq__(self, other):
        print("B")
        return True

print(A() == B())
print(B() == A())
```

**Choices:**
- A) `A | False | B | True` ✅
- B) `A | B | True | B | A | True`
- C) `A | True | B | False`
- D) `B | True | A | False`

**Answer: A**

**Explanation:** Returning `False` is a *final answer*, so Python will *not* try the other side. `A() == B()` calls only `A.__eq__`, which returns `False`. `B() == A()` calls only `B.__eq__`, which returns `True`. This makes equality asymmetric — a classic reason to return `NotImplemented` for unknown types instead.

---

## Q19 – Ordering Is Less Forgiving (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class L:
    def __lt__(self, other):
        print("L<")
        return NotImplemented

class R:
    def __gt__(self, other):
        print("R>")
        return NotImplemented

try:
    print(L() < R())
except TypeError:
    print("TypeError")
```

**Choices:**
- A) `L< | R> | TypeError` ✅
- B) `L< | R> | False`
- C) `L< | False`
- D) `False`

**Answer: A**

**Explanation:** For ordering (`<`, `>`, etc.), if both sides return `NotImplemented`, Python raises `TypeError` (unlike equality, which falls back to `False`/identity). This is intentional: falling back to arbitrary ordering would be silently wrong.

---

## Q20 – "Why Can't I Put This In a set?" (Hard)

**Question:** What prints?

```python
class Person:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Person):
            return NotImplemented
        return self.name == other.name

p = Person("Ada")

try:
    {p}
except TypeError as e:
    print(type(e).__name__)
```

**Choices:**
- A) `TypeError` ✅
- B) `{'Ada'}`
- C) `{Person("Ada")}`
- D) `None`

**Answer: A**

**Explanation:** Defining `__eq__` makes Python set `__hash__ = None` by default (unhashable). This prevents "equal objects with different hashes" bugs unless you explicitly define a consistent `__hash__`. Adding to a set requires hashability.

---

## Q21 – The Broken Hash Contract (Hard)

**Question:** What does this print?

```python
class Person:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return isinstance(other, Person) and self.name == other.name

    __hash__ = object.__hash__  # identity-based hash

p1 = Person("Ada")
p2 = Person("Ada")

print(p1 == p2, len({p1, p2}))
```

**Choices:**
- A) `True 2` ✅
- B) `True 1`
- C) `False 2`
- D) `False 1`

**Answer: A**

**Explanation:** `p1 == p2` is `True`, but `__hash__ = object.__hash__` is identity-based, so their hashes differ. A `set` uses hashes to bucket items; different hashes means both get stored, so length is `2`. This violates the hash contract: equal objects must have equal hashes.

---

## Q22 – Mutating a Key After Insertion (Very Hard)

**Question:** What does this print?

```python
class Tag:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return isinstance(other, Tag) and self.name == other.name

t = Tag("prod")
s = {t}

print(t in s)
t.name = "dev"
print(t in s)
```

**Choices:**
- A) `True` then `False` ✅
- B) `True` then `True`
- C) `False` then `False`
- D) `TypeError`

**Answer: A**

**Explanation:** The set stores the object in a bucket based on its hash at insertion time (`hash("prod")`). Changing `name` to `"dev"` changes the hash, so later lookups search the wrong bucket (`hash("dev")`) and fail. This is why "hashable implies effectively immutable" is a design rule.

---

## Q23 – NotImplemented In Addition (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class L:
    def __add__(self, other):
        print("L+")
        return NotImplemented

class R:
    def __radd__(self, other):
        print("R+r")
        return "ok"

print(L() + R())
```

**Choices:**
- A) `L+ | R+r | ok` ✅
- B) `R+r | L+ | ok`
- C) `L+ | TypeError`
- D) `ok`

**Answer: A**

**Explanation:** `L.__add__` returns `NotImplemented`, so Python tries the reflected method `R.__radd__`, which returns `"ok"`. The `__radd__` method handles the case where the left operand doesn't know how to add.

---

## Q24 – Why sum() Fails Without __radd__ (Hard)

**Question:** What prints?

```python
class Num:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return f"Num({self.x})"

    def __add__(self, other):
        if not isinstance(other, Num):
            return NotImplemented
        return Num(self.x + other.x)

try:
    print(sum([Num(1), Num(2)]))
except TypeError as e:
    print(type(e).__name__)
```

**Choices:**
- A) `TypeError` ✅
- B) `Num(3)`
- C) `3`
- D) `NotImplemented`

**Answer: A**

**Explanation:** `sum()` starts at `0` (the default), so it first evaluates `0 + Num(1)`. That requires `Num.__radd__` to handle the `int` on the left. Without it, `int.__add__` returns `NotImplemented` and there's no fallback, so Python raises `TypeError`.

---

## Q25 – The sum() Identity Trick (Hard)

**Question:** What does this print?

```python
class Num:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return f"Num({self.x})"

    def __add__(self, other):
        if not isinstance(other, Num):
            return NotImplemented
        return Num(self.x + other.x)

    def __radd__(self, other):
        if other == 0:      # for sum()
            return self
        return self.__add__(other)

print(sum([Num(1), Num(2)]))
```

**Choices:**
- A) `Num(3)` ✅
- B) `3`
- C) `TypeError`
- D) `Num(1)`

**Answer: A**

**Explanation:** `__radd__` treats `other == 0` as the identity element, letting `sum()` bootstrap the first addition (`0 + Num(1)` returns `Num(1)`). Then normal `__add__` combines values (`Num(1) + Num(2)` returns `Num(3)`).

---

## Q26 – Callable Objects Keep State (Medium)

**Question:** What does this print?

```python
class Counter:
    def __init__(self):
        self.n = 0

    def __call__(self, step=1):
        self.n += step
        return self.n

c = Counter()
print(c(), c(2), c())
```

**Choices:**
- A) `1 3 4` ✅
- B) `1 2 3`
- C) `0 2 3`
- D) `1 2 4`

**Answer: A**

**Explanation:** The object stores state (`self.n`). Calls update it: `0+1=1`, then `1+2=3`, then `3+1=4`. Callable objects are a great way to create functions with persistent state.

---

## Q27 – Memoization: Same Input, Less Work (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class Cache:
    def __init__(self):
        self.cache = {}

    def __call__(self, x):
        if x in self.cache:
            print("hit", x)
            return self.cache[x]
        print("miss", x)
        self.cache[x] = x * x
        return self.cache[x]

f = Cache()
print(f(3), f(3), f(4))
```

**Choices:**
- A) `miss 3 | hit 3 | miss 4 | 9 9 16` ✅
- B) `miss 3 | miss 3 | miss 4 | 9 9 16`
- C) `hit 3 | hit 3 | hit 4 | 9 9 16`
- D) `miss 3 | hit 3 | miss 4 | 9 16 9`

**Answer: A**

**Explanation:** First `f(3)` is computed and cached ("miss 3"). Second `f(3)` is a cache hit ("hit 3"). `f(4)` is a miss ("miss 4"). The final `print(...)` prints the returned values `9 9 16`.

---

## Q28 – __exit__ Can Swallow Exceptions (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class Demo:
    def __enter__(self):
        print("enter")
        return "VALUE"

    def __exit__(self, exc_type, exc, tb):
        print("exit", exc_type.__name__ if exc_type else None)
        return True

with Demo() as v:
    print("in", v)
    1 / 0

print("after")
```

**Choices:**
- A) `enter | in VALUE | exit ZeroDivisionError | after` ✅
- B) `enter | in VALUE | ZeroDivisionError`
- C) `enter | exit ZeroDivisionError | after`
- D) `enter | in VALUE | exit None | after`

**Answer: A**

**Explanation:** Returning `True` from `__exit__` suppresses the exception, so execution continues after the `with` block. The "after" message prints because the exception was swallowed.

---

## Q29 – __exit__ Still Runs, But Exception Escapes (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class Demo:
    def __enter__(self):
        print("enter")
        return "VALUE"

    def __exit__(self, exc_type, exc, tb):
        print("exit", exc_type.__name__ if exc_type else None)
        return False

try:
    with Demo() as v:
        print("in", v)
        1 / 0
    print("after")
except ZeroDivisionError:
    print("crash")
```

**Choices:**
- A) `enter | in VALUE | exit ZeroDivisionError | crash` ✅
- B) `enter | in VALUE | crash`
- C) `enter | in VALUE | exit ZeroDivisionError | after`
- D) `enter | exit ZeroDivisionError | crash`

**Answer: A**

**Explanation:** `__exit__` runs on exception, but returning `False` (or `None`) means "do not swallow", so the exception is re-raised and caught by the outer `try`. Note that `__exit__` *always* runs, even if there's an exception.

---

## Q30 – Two Managers, One With: Exit Order (Hard)

**Question:** What is the exact output? Use `|` to represent newlines.

```python
class M:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print("enter", self.name)
        return self

    def __exit__(self, exc_type, exc, tb):
        print("exit", self.name)
        return False

with M("A"), M("B"):
    print("body")
```

**Choices:**
- A) `enter A | enter B | body | exit B | exit A` ✅
- B) `enter A | enter B | body | exit A | exit B`
- C) `enter A | body | enter B | exit B | exit A`
- D) `enter A | enter B | exit B | exit A | body`

**Answer: A**

**Explanation:** Multiple context managers in one `with` behave like nested `with` blocks: enter left-to-right, exit right-to-left (stack discipline). This ensures proper cleanup order — the last resource acquired is the first to be released.

---

## Summary of Key Concepts

### Session 1 Recap (Q1–Q4)
- **List multiplication** creates shared references
- **Aliases vs copies**: `b = a` vs `c = a[:]`
- **Class attributes** are shared across instances
- **Shadowing**: assignment creates instance attributes

### Iteration Protocol (Q5–Q9)
- **Sequence fallback**: `__getitem__` with incrementing indices
- **Iterator requirements**: `__iter__` must return object with `__next__`
- **Membership fallback**: `in` uses `__iter__` if no `__contains__`
- **Slices are objects**: `slice(start, stop, step)`

### Truthiness (Q10–Q13)
- **`__bool__` takes priority** over `__len__`
- **Return type requirements**: `__bool__` → `bool`, `__len__` → `int >= 0`, `__repr__` → `str`

### String Representations (Q14)
- **`__str__` vs `__repr__`**: f-strings use `__str__` by default, `!r` forces `__repr__`

### Comparison Protocol (Q15–Q19)
- **`NotImplemented`** signals "let the other side try"
- **Equality fallback**: identity (`is`) when both return `NotImplemented`
- **Ordering**: raises `TypeError` when both return `NotImplemented`
- **Symmetry bug**: returning `False`/`True` instead of `NotImplemented` breaks symmetry

### Hash Contract (Q20–Q22)
- **Equal objects must have equal hashes**
- **Defining `__eq__` sets `__hash__ = None`** (unhashable by default)
- **Mutable keys**: changing a key after insertion breaks lookups

### Arithmetic Protocol (Q23–Q25)
- **Reflected methods**: `__radd__` handles `other + self`
- **`sum()` identity trick**: handle `0` specially in `__radd__`

### Callable Objects (Q26–Q27)
- **`__call__`** makes instances callable
- **Memoization**: cache results using instance state

### Context Managers (Q28–Q30)
- **`__exit__` return value**: `True` swallows exceptions, `False` re-raises
- **Exit order**: LIFO (stack discipline) for multiple managers
