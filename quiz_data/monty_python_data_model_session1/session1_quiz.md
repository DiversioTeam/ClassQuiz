---
title: Python Data Model – Session 1 Quiz
---

# Python Data Model – Session 1 Quiz

Tricky review of identity, mutability, aliasing, and class vs instance attributes from Session 1.

---

## Q1 – Identity vs Equality (Lists)

Given:

```python
x = [1, 2, 3]
y = x
z = [1, 2, 3]
```

Which combination is correct?

- [ ] `x == y` is True and `x is y` is False  
- [ ] `x == z` is False and `x is z` is True  
- [x] `x == y` is True and `x is y` is True, but `x is z` is False  
- [ ] `x == y == z` is True and `x is y is z` is True  

---

## Q2 – Mutate vs Rebind (List Alias)

```python
nums = [1, 2]
alias = nums

nums.append(3)
nums = nums + [4]
```

What are the final values?

- [ ] `nums == [1, 2, 3]` and `alias == [1, 2]`  
- [ ] `nums == [1, 2, 3, 4]` and `alias == [1, 2, 3, 4]`  
- [x] `nums == [1, 2, 3, 4]` and `alias == [1, 2, 3]`  
- [ ] `nums == [1, 2, 3]` and `alias == [1, 2, 3, 4]`  

---

## Q3 – `+=` and Identity

```python
lst = [1, 2, 3]
before = id(lst)
lst += [4]
after = id(lst)
```

Which statement is correct?

- [x] `before == after` because `+=` on lists mutates in place  
- [ ] `before != after` because `+=` always creates a new list  
- [ ] `before == after` only if the list is small enough  
- [ ] It is undefined whether `before == after`  

---

## Q4 – “Bad Matrix” (Shared Rows)

```python
matrix = [[0] * 3] * 3
matrix[0][0] = 1
print(matrix)
```

What gets printed?

- [ ] `[[1, 0, 0], [0, 0, 0], [0, 0, 0]]`  
- [x] `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`  
- [ ] `[[1, 0, 0], [1, 1, 0], [1, 1, 1]]`  
- [ ] `[[1, 0, 0], [0, 0, 0]]`  

---

## Q5 – “Good Matrix” (Separate Rows)

```python
matrix = [[0] * 3 for _ in range(3)]
matrix[0][0] = 1
print(matrix)
```

What gets printed?

- [x] `[[1, 0, 0], [0, 0, 0], [0, 0, 0]]`  
- [ ] `[[1, 0, 0], [1, 0, 0], [1, 0, 0]]`  
- [ ] `[[1, 0, 0], [1, 1, 0], [1, 1, 1]]`  
- [ ] `[[1, 0, 0], [0, 0, 0]]`  

---

## Q6 – Aliasing with Dicts

```python
stats = {"count": 0}
alias = stats

alias["count"] += 1
stats["count"] += 2
```

What is `stats["count"]` at the end?

- [ ] `0`  
- [ ] `1`  
- [ ] `2`  
- [x] `3`  

---

## Q7 – Class vs Instance Attribute (Config.debug)

```python
class Config:
    debug = False

c1 = Config()
c2 = Config()

Config.debug = True
c1.debug = False

print("Config.debug:", Config.debug)
print("c1.debug:", c1.debug)
print("c2.debug:", c2.debug)
```

What is printed?

- [ ] `Config.debug: False`, `c1.debug: False`, `c2.debug: False`  
- [ ] `Config.debug: True`, `c1.debug: True`, `c2.debug: True`  
- [x] `Config.debug: True`, `c1.debug: False`, `c2.debug: True`  
- [ ] `Config.debug: False`, `c1.debug: False`, `c2.debug: True`  

---

## Q8 – Where Does the Attribute Live?

Continuing the Config example from Q7, which statement best describes where the values live?

- [ ] Both `c1.debug` and `c2.debug` live only in `Config.__dict__`  
- [x] `c1.debug` lives in `c1.__dict__`, `c2.debug` lives in `Config.__dict__`  
- [ ] Both `c1.debug` and `c2.debug` live only in their instance `__dict__`s  
- [ ] All three values live only in `Config.__dict__`  

---

## Q9 – Mutability Classification

Which pair lists **two immutable** built‑in types?

- [ ] `list` and `tuple`  
- [x] `tuple` and `str`  
- [ ] `set` and `dict`  
- [ ] `list` and `bytearray`  

---

## Q10 – Aliasing via Shared Row Reference

```python
row = [0, 0, 0]
matrix = [row, row, row]
row[1] = 1
print(matrix)
```

What gets printed?

- [ ] `[[0, 1, 0], [0, 0, 0], [0, 0, 0]]`  
- [ ] `[[0, 0, 0], [0, 1, 0], [0, 0, 0]]`  
- [x] `[[0, 1, 0], [0, 1, 0], [0, 1, 0]]`  
- [ ] `[[0, 0, 0]]`  

---

## Q11 – Function Parameters: Mutate vs Rebind

```python
def add_marker(seq):
    seq += ["X"]

def add_marker_copy(seq):
    seq = seq + ["X"]

a = [1]
b = [1]

add_marker(a)
add_marker_copy(b)
print("a:", a)
print("b:", b)
```

What gets printed?

- [ ] `a: [1]`, `b: [1]`  
- [x] `a: [1, 'X']`, `b: [1]`  
- [ ] `a: [1]`, `b: [1, 'X']`  
- [ ] `a: [1, 'X']`, `b: [1, 'X']`  

---

## Q12 – Dict Aliasing via Nested List

```python
config = {"options": []}
opts = config["options"]

opts.append("dark_mode")
config["options"].append("beta")

print(config["options"])
```

What is printed?

- [ ] `["dark_mode"]`  
- [ ] `["beta"]`  
- [x] `["dark_mode", "beta"]`  
- [ ] `[]`  

---

## Q13 – `__dict__` After Shadowing Class Attribute

```python
class Settings:
    theme = "light"

s1 = Settings()
s2 = Settings()

s1.theme = "dark"
Settings.theme = "solarized"

print("s1.__dict__:", s1.__dict__)
print("s2.__dict__:", s2.__dict__)
print("Settings.theme:", Settings.theme)
```

Which is most accurate?

- [ ] `s1.__dict__` is `{}`, `s2.__dict__` is `{}`, and `Settings.theme` is `"dark"`  
- [x] `s1.__dict__` is `{'theme': 'dark'}`, `s2.__dict__` is `{}`, and `Settings.theme` is `"solarized"`  
- [ ] `s1.__dict__` is `{}`, `s2.__dict__` is `{'theme': 'solarized'}`, and `Settings.theme` is `"solarized"`  
- [ ] `s1.__dict__` and `s2.__dict__` both contain `"theme": "solarized"`  

---

## Q14 – Garbage Collection and Last Reference

```python
data = [1, 2, 3]
alias = data

del data
alias.append(4)
```

Right after this runs in CPython, which statement is most accurate?

- [ ] The list was garbage‑collected when `del data` ran, so `alias.append(4)` fails  
- [x] The list is still alive because `alias` still refers to it  
- [ ] Whether the list is alive is undefined and may change between runs  
- [ ] `del data` also deletes `alias` because they pointed to the same list  

---

## Q15 – Shallow Copy and Nested Mutability

```python
nested = [[0], [0]]
copy = list(nested)

nested[0].append(1)

print("nested:", nested)
print("copy:", copy)
```

What gets printed?

- [ ] `nested: [[0, 1], [0]]`, `copy: [[0], [0]]`  
- [x] `nested: [[0, 1], [0]]`, `copy: [[0, 1], [0]]`  
- [ ] `nested: [[0], [0]]`, `copy: [[0, 1], [0]]`  
- [ ] `nested: [[0, 1], [0, 1]]`, `copy: [[0, 1], [0, 1]]`  

---

## Q16 – Tuples Containing Mutable Objects

If a tuple contains a reference to a mutable list, and that list is subsequently modified, which statement about the tuple is correct?

- [x] The tuple is still considered immutable, but its effective value has changed.  
- [ ] The tuple's identity changes because its contained value has been altered.  
- [ ] A `TypeError` is raised when the list is modified, as this violates the tuple's immutability.  
- [ ] The tuple implicitly becomes a mutable object to accommodate the change.  

---

## Q17 – Reference Counting Limitation

In CPython, the primary garbage collection mechanism is reference counting. What is its main limitation?

- [ ] It can be slow to update the counts for frequently referenced objects.  
- [ ] It requires the entire program to pause periodically for a full scan.  
- [ ] It cannot manage the memory of objects defined in C extension modules.  
- [x] It cannot reclaim objects involved in a reference cycle on its own.  

---

## Q18 – Why Not Rely on `__del__`?

Why is it generally unsafe to rely on the `__del__` method for critical resource cleanup, such as closing a database connection?

- [ ] It is only called when an object is explicitly deleted with the `del` keyword.  
- [x] Its execution time is not guaranteed, and it might not be called at all during interpreter shutdown.  
- [ ] It prevents an object from being garbage collected if it raises an exception.  
- [ ] The `__del__` method significantly slows down the creation of new objects.  

---

## Q19 – `is` vs `==`

What is the key difference between the `is` operator and the `==` operator in Python?

- [x] `is` compares the identity (object addresses) of two objects, while `==` compares their values.  
- [ ] `is` checks if two objects have the same type, while `==` checks if they have the same value.  
- [ ] `is` is used for comparing built-in types, while `==` is for user-defined classes.  
- [ ] `is` performs a shallow comparison, while `==` performs a deep comparison of contents.  

---


## Q20 – Attribute Lookup Order

When an attribute is accessed on a class instance, for example `my_instance.name`, what is the first location Python checks to find this attribute?

- [ ] The namespace of the class from which the instance was created.  
- [ ] The `__dict__` of any base classes in the method resolution order (MRO).  
- [ ] The global namespace of the module where the class is defined.  
- [x] The `__dict__` of the instance itself.  

---



## Q21 – Rebind vs In-Place with `+=`

Given `a = [10]` and `b = a`, what is the difference between `a = a + [5]` and `a += [5]`?

- [ ] There is no difference; both operations modify the list in-place.  
- [ ] Both operations create new list objects, breaking the connection between `a` and `b`.  
- [ ] `a = a + [5]` modifies the list in-place, while `a += [5]` creates a new list.  
- [x] `a = a + [5]` creates a new list and reassigns `a`, while `a += [5]` modifies the original list in-place.  

---

## Q22 – Row Aliasing Across Copies

```python
row = [0]
matrix = [row] * 3
clone = matrix[:]

row.append(1)
matrix[1].append(2)

print("row:", row)
print("matrix:", matrix)
print("clone:", clone)
```

What is printed?

- [x] `row: [0, 1, 2], matrix: [[0, 1, 2], [0, 1, 2], [0, 1, 2]], clone: [[0, 1, 2], [0, 1, 2], [0, 1, 2]]`  
- [ ] `row: [0, 1, 2], matrix: [[0, 1, 2], [0, 1, 2], [0, 1, 2]], clone: [[0, 1], [0, 1], [0, 1]]`  
- [ ] `row: [0, 1], matrix: [[0, 1, 2], [0, 1, 2], [0, 1, 2]], clone: [[0, 1], [0, 1], [0, 1]]`  
- [ ] `row: [0, 1, 2], matrix: [[0, 1], [0, 1], [0, 1]], clone: [[0, 1, 2], [0, 1, 2], [0, 1, 2]]`  

---

## Q23 – Tuple of Lists: Shared vs Copied

```python
inner = [0]
t1 = (inner, inner)
t2 = (inner[:], inner[:])

inner.append(1)

print("t1:", t1)
print("t2:", t2)
```

What is printed?

- [x] `t1: ([0, 1], [0, 1]), t2: ([0], [0])`  
- [ ] `t1: ([0], [0]), t2: ([0, 1], [0, 1])`  
- [ ] `t1: ([0, 1], [0, 1]), t2: ([0, 1], [0, 1])`  
- [ ] `t1: ([0], [0, 1]), t2: ([0], [0, 1])`  

---

## Q24 – Dict Values: Mutate vs Rebind

```python
shared = []
config = {"a": shared, "b": shared}

config["a"].append(1)
config["b"] = config["b"] + [2]

print("config['a']:", config["a"])
print("config['b']:", config["b"])
```

What is printed?

- [x] `config['a']: [1], config['b']: [1, 2]`  
- [ ] `config['a']: [1, 2], config['b']: [1, 2]`  
- [ ] `config['a']: [1, 2], config['b']: [2]`  
- [ ] `config['a']: [1], config['b']: [2]`  

---

## Q25 – Mutate Inner, Then Rebind Slot

```python
def tweak(seq):
    first = seq[0]
    first.append("X")
    seq[0] = first + ["Y"]

data = [[1], [2]]
alias = data

tweak(data)

print("data:", data)
print("alias:", alias)
```

What is printed?

- [x] `data: [[1, 'X', 'Y'], [2]], alias: [[1, 'X', 'Y'], [2]]`  
- [ ] `data: [[1, 'X'], [2]], alias: [[1, 'X'], [2]]`  
- [ ] `data: [[1, 'X', 'Y'], [2]], alias: [[1], [2]]`  
- [ ] `data: [[1], [2]], alias: [[1, 'X', 'Y'], [2]]`  

---

## Q26 – Breaking Aliases with Rebinding

```python
nums = [1, 2, 3]
a = nums
b = nums[:]

nums = nums + [4]
nums.append(5)

print("a:", a)
print("b:", b)
print("nums:", nums)
```

What is printed?

- [x] `a: [1, 2, 3], b: [1, 2, 3], nums: [1, 2, 3, 4, 5]`  
- [ ] `a: [1, 2, 3, 4, 5], b: [1, 2, 3], nums: [1, 2, 3, 4, 5]`  
- [ ] `a: [1, 2, 3, 4], b: [1, 2, 3], nums: [1, 2, 3, 4, 5]`  
- [ ] `a: [1, 2, 3, 4], b: [1, 2, 3, 4], nums: [1, 2, 3, 4, 5]`  

---

## Q27 – Outer Rebind vs Inner Mutate with Slices

```python
rows = [[0], [0]]
alias = rows
clone = rows[:]

alias[0] = [1]
clone[1].append(2)

print("rows:", rows)
print("alias:", alias)
print("clone:", clone)
```

What is printed?

- [x] `rows: [[1], [0, 2]], alias: [[1], [0, 2]], clone: [[0], [0, 2]]`  
- [ ] `rows: [[1], [0]], alias: [[1], [0]], clone: [[1], [0, 2]]`  
- [ ] `rows: [[1], [0, 2]], alias: [[1], [0]], clone: [[0], [0, 2]]`  
- [ ] `rows: [[1], [0, 2]], alias: [[1], [0, 2]], clone: [[1], [0, 2]]`  

---

## Q28 – `*=` with Nested Lists

```python
nested = [[1], [2]]
alias = nested

nested *= 2
nested[0].append(3)

print("nested:", nested)
print("alias:", alias)
```

What is printed?

- [x] `nested: [[1, 3], [2], [1, 3], [2]], alias: [[1, 3], [2], [1, 3], [2]]`  
- [ ] `nested: [[1, 3], [2], [1], [2]], alias: [[1, 3], [2], [1], [2]]`  
- [ ] `nested: [[1, 3], [2], [1, 3], [2]], alias: [[1], [2]]`  
- [ ] `nested: [[1], [2], [1], [2]], alias: [[1, 3], [2], [1, 3], [2]]`  

## Q29 – Module vs Class vs Instance Name

```python
x = "module"

class Thing:
    x = "class"
    def __init__(self):
        self.x = "instance"
    def show(self):
        print(x, self.x, Thing.x)

obj = Thing()
obj.show()
```

What does `obj.show()` print?

- [x] It prints `module instance class`.  
- [ ] It prints `class instance class`.  
- [ ] It prints `module class instance`.  
- [ ] It prints `instance instance instance`.  

---

## Q30 – Global Rebinding vs Aliased List

```python
items = []

def add():
    items.append("A")

def reset():
    global items
    items = []

add()
alias = items
reset()

print("items:", items)
print("alias:", alias)
```

What is printed?

- [x] `items: []`, `alias: ['A']`  
- [ ] `items: ['A']`, `alias: ['A']`  
- [ ] `items: []`, `alias: []`  
- [ ] `items: ['A']`, `alias: []`  
