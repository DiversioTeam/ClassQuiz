# Python Data Model – Session 2 Quiz (Hard Mode)

Quick warm-up (Session 1 recap), then deep protocol puzzles from Session 2.
Assume Python 3.x.

---

## Q1 – The Copy That Wasn't (Easy)

What does this print?

```python
m = [[0] * 3] * 2
m[0][1] = 9
print(m)
```

- [x] `[[0, 9, 0], [0, 9, 0]]`
- [ ] `[[0, 9, 0], [0, 0, 0]]`
- [ ] `[[0, 0, 0], [0, 9, 0]]`
- [ ] `[[0, 9, 0]]`

Time: 60

---

## Q2 – Alias vs Copy (Easy)

What does this print?

```python
a = [1, 2]
b = a
c = a[:]

b.append(3)
print(a, c)
```

- [x] `[1, 2, 3] [1, 2]`
- [ ] `[1, 2, 3] [1, 2, 3]`
- [ ] `[1, 2] [1, 2, 3]`
- [ ] `[1, 2] [1, 2]`

Time: 60

---

## Q3 – The Sneaky Shared List (Medium)

What does this print?

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

- [x] `[1, 2] [1, 2]`
- [ ] `[1] [2]`
- [ ] `[1, 2] [2]`
- [ ] `[] []`

Time: 75

---

## Q4 – Shadowboxing Attributes (Medium)

What does this print?

```python
class C:
    xs = []

c = C()

c.xs.append(1)      # mutate the class list
c.xs = ["local"]    # rebind: creates an instance attribute
C.xs.append(2)      # mutate the class list again

print(c.xs, C.xs)
```

- [x] `['local'] [1, 2]`
- [ ] `[1, 2] [1, 2]`
- [ ] `['local', 2] [1]`
- [ ] `['local'] [2]`

Time: 75

---

## Q5 – Iterable Without __iter__ (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `get 0 | x 10 | get 1 | x 20 | get 2`
- [ ] `get 0 | get 1 | get 2`
- [ ] `x 10 | x 20`
- [ ] `TypeError`

Time: 90

---

## Q6 – __iter__ Returned a Liar (Hard)

What prints?

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

- [x] `TypeError`
- [ ] `StopIteration`
- [ ] `AttributeError`
- [ ] `body None`

Time: 90

---

## Q7 – "in" Without __contains__ (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `iter | yield 1 | yield 2 | A: True | contains | B: True`
- [ ] `contains | B: True | iter | yield 1 | yield 2 | A: True`
- [ ] `iter | yield 1 | yield 2 | yield 3 | A: True | contains | B: True`
- [ ] `A: True | B: True`

Time: 90

---

## Q8 – __contains__ Takes Priority (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `contains | caught`
- [ ] `iter | contains | caught`
- [ ] `iter | caught`
- [ ] `False`

Time: 90

---

## Q9 – Slices Are Objects (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `int 1 | slice slice(1, 4, None) | slice slice(None, None, None)`
- [ ] `int 1 | int 1:4 | int :`
- [ ] `slice 1 | slice 1:4 | slice :`
- [ ] `TypeError`

Time: 90

---

## Q10 – Truthiness: __bool__ Beats __len__ (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `bool | False | bool | F`
- [ ] `len | bool | False | F`
- [ ] `len | 10 | bool | False | F`
- [ ] `bool | False | len | 10 | F`

Time: 90

---

## Q11 – __bool__ Must Return bool (Medium)

What prints?

```python
class Bad:
    def __bool__(self):
        return 1

try:
    print(bool(Bad()))
except TypeError as e:
    print(type(e).__name__)
```

- [x] `TypeError`
- [ ] `True`
- [ ] `1`
- [ ] `False`

Time: 75

---

## Q12 – __len__ Must Be Non-Negative (Medium)

What prints?

```python
class BadLen:
    def __len__(self):
        return -1

try:
    print(len(BadLen()))
except Exception as e:
    print(type(e).__name__)
```

- [x] `ValueError`
- [ ] `-1`
- [ ] `TypeError`
- [ ] `0`

Time: 75

---

## Q13 – __repr__ Must Return str (Medium)

What prints?

```python
class BadRepr:
    def __repr__(self):
        return b"oops"

try:
    print(repr(BadRepr()))
except TypeError as e:
    print(type(e).__name__)
```

- [x] `TypeError`
- [ ] `b'oops'`
- [ ] `'oops'`
- [ ] `AttributeError`

Time: 75

---

## Q14 – f-strings: !r vs default (Medium)

What does this print?

```python
class X:
    def __repr__(self):
        return "R"

    def __str__(self):
        return "S"

x = X()
print(f"{x} {x!r}")
```

- [x] `S R`
- [ ] `R S`
- [ ] `S S`
- [ ] `R R`

Time: 75

---

## Q15 – NotImplemented Is a Relay Baton (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `A | B | True`
- [ ] `A | True`
- [ ] `B | True`
- [ ] `A | B | False`

Time: 90

---

## Q16 – When Nobody Knows (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `A | B | False`
- [ ] `A | B | True`
- [ ] `A | False`
- [ ] `TypeError`

Time: 90

---

## Q17 – NotImplemented Even On Yourself (Very Hard)

What is the exact output? Use `|` to represent newlines.

```python
class A:
    def __eq__(self, other):
        print("eq")
        return NotImplemented

a = A()
print(a == a)
```

- [x] `eq | eq | True`
- [ ] `eq | True`
- [ ] `True`
- [ ] `eq | eq | False`

Time: 90

---

## Q18 – The Symmetry Bug (Very Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `A | False | B | True`
- [ ] `A | B | True | B | A | True`
- [ ] `A | True | B | False`
- [ ] `B | True | A | False`

Time: 90

---

## Q19 – Ordering Is Less Forgiving (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `L< | R> | TypeError`
- [ ] `L< | R> | False`
- [ ] `L< | False`
- [ ] `False`

Time: 90

---

## Q20 – "Why Can't I Put This In a set?" (Hard)

What prints?

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

- [x] `TypeError`
- [ ] `{'Ada'}`
- [ ] `{Person("Ada")}`
- [ ] `None`

Time: 90

---

## Q21 – The Broken Hash Contract (Hard)

What does this print?

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

- [x] `True 2`
- [ ] `True 1`
- [ ] `False 2`
- [ ] `False 1`

Time: 90

---

## Q22 – Mutating a Key After Insertion (Very Hard)

What does this print?

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

- [x] `True` then `False`
- [ ] `True` then `True`
- [ ] `False` then `False`
- [ ] `TypeError`

Time: 90

---

## Q23 – NotImplemented In Addition (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `L+ | R+r | ok`
- [ ] `R+r | L+ | ok`
- [ ] `L+ | TypeError`
- [ ] `ok`

Time: 90

---

## Q24 – Why sum() Fails Without __radd__ (Hard)

What prints?

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

- [x] `TypeError`
- [ ] `Num(3)`
- [ ] `3`
- [ ] `NotImplemented`

Time: 90

---

## Q25 – The sum() Identity Trick (Hard)

What does this print?

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

- [x] `Num(3)`
- [ ] `3`
- [ ] `TypeError`
- [ ] `Num(1)`

Time: 90

---

## Q26 – Callable Objects Keep State (Medium)

What does this print?

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

- [x] `1 3 4`
- [ ] `1 2 3`
- [ ] `0 2 3`
- [ ] `1 2 4`

Time: 75

---

## Q27 – Memoization: Same Input, Less Work (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `miss 3 | hit 3 | miss 4 | 9 9 16`
- [ ] `miss 3 | miss 3 | miss 4 | 9 9 16`
- [ ] `hit 3 | hit 3 | hit 4 | 9 9 16`
- [ ] `miss 3 | hit 3 | miss 4 | 9 16 9`

Time: 90

---

## Q28 – __exit__ Can Swallow Exceptions (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `enter | in VALUE | exit ZeroDivisionError | after`
- [ ] `enter | in VALUE | ZeroDivisionError`
- [ ] `enter | exit ZeroDivisionError | after`
- [ ] `enter | in VALUE | exit None | after`

Time: 90

---

## Q29 – __exit__ Still Runs, But Exception Escapes (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `enter | in VALUE | exit ZeroDivisionError | crash`
- [ ] `enter | in VALUE | crash`
- [ ] `enter | in VALUE | exit ZeroDivisionError | after`
- [ ] `enter | exit ZeroDivisionError | crash`

Time: 90

---

## Q30 – Two Managers, One With: Exit Order (Hard)

What is the exact output? Use `|` to represent newlines.

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

- [x] `enter A | enter B | body | exit B | exit A`
- [ ] `enter A | enter B | body | exit A | exit B`
- [ ] `enter A | body | enter B | exit B | exit A`
- [ ] `enter A | enter B | exit B | exit A | body`

Time: 90

---
