---
title: Python Data Model – Session 1 Quiz – Answer Key
---

# Session 1 Quiz – Answer Key (Instructor)

Short justifications for each question, scoped to Session 1 topics.

## Q1 – Identity vs Equality (Lists)
**Correct:** Option 3  
`x` and `y` refer to the same list object, so `x == y` and `x is y` are both True. `z` is a separate but equal list, so `x == z` is True but `x is z` is False.

## Q2 – Mutate vs Rebind (List Alias)
**Correct:** Option 3  
`nums.append(3)` mutates the shared list, so both names see `[1, 2, 3]`. `nums = nums + [4]` creates a new list and rebinds `nums`, leaving `alias` still pointing at the old `[1, 2, 3]`.

## Q3 – `+=` and Identity
**Correct:** Option 1  
For lists, `+=` is implemented as in‑place extension (`list.__iadd__`), so the same list object is modified; `id` stays the same.

## Q4 – “Bad Matrix” (Shared Rows)
**Correct:** Option 2  
`[[0] * 3] * 3` repeats the same inner list reference three times. Changing `matrix[0][0]` changes column 0 in all three rows, so they all become `[1, 0, 0]`.

## Q5 – “Good Matrix” (Separate Rows)
**Correct:** Option 1  
The list comprehension builds three independent row lists. Only row 0 is mutated, so the result is `[[1, 0, 0], [0, 0, 0], [0, 0, 0]]`.

## Q6 – Aliasing with Dicts
**Correct:** Option 4 (value `3`)  
`stats` and `alias` both reference the same dict. The two increments add 1 then 2 to the same `"count"` entry: `0 → 1 → 3`.

## Q7 – Class vs Instance Attribute (Config.debug)
**Correct:** Option 3  
`Config.debug = True` changes the class attribute. `c1.debug = False` creates an instance attribute on `c1` that shadows the class attribute. `c2.debug` still sees the class value `True`.

## Q8 – Where Does the Attribute Live?
**Correct:** Option 2  
After the writes, `c1.__dict__` contains its own `"debug"` entry. `c2` has no `"debug"` in its `__dict__`, so attribute lookup falls back to `Config.__dict__`.

## Q9 – Mutability Classification
**Correct:** Option 2 (`tuple` and `str`)  
Both `tuple` and `str` are immutable. Lists, sets, dicts, and `bytearray` are all mutable in the sense used in Session 1.

## Q10 – Aliasing via Shared Row Reference
**Correct:** Option 3  
All three elements of `matrix` reference the same `row` object. Mutating `row[1]` updates the shared list, so each row prints as `[0, 1, 0]`.

## Q11 – Function Parameters: Mutate vs Rebind
**Correct:** Option 2  
Inside `add_marker`, `seq += ['X']` mutates the original list, so `a` becomes `[1, 'X']`. Inside `add_marker_copy`, `seq = seq + ['X']` rebinds the local name only; `b` outside remains `[1]`.

## Q12 – Dict Aliasing via Nested List
**Correct:** Option 3  
`opts` and `config["options"]` reference the same list. Both appends hit the same object, producing `["dark_mode", "beta"]`.

## Q13 – `__dict__` After Shadowing Class Attribute
**Correct:** Option 2  
Assigning `s1.theme = "dark"` creates/updates an instance attribute stored in `s1.__dict__`. Later changing `Settings.theme` only affects the class attribute. `s2` still has no instance `theme`, so it sees `"solarized"` from the class.

## Q14 – Garbage Collection and Last Reference
**Correct:** Option 2  
`del data` just removes one name; the list object remains alive as long as at least one reference (`alias`) exists. `alias.append(4)` is fine.

## Q15 – Shallow Copy and Nested Mutability
**Correct:** Option 2  
`list(nested)` creates a new outer list, but it still contains references to the same inner lists. Mutating `nested[0]` changes the shared inner list, so both `nested[0]` and `copy[0]` become `[0, 1]`.

## Q16 – Tuples Containing Mutable Objects
**Correct:** Option 1  
The tuple itself remains immutable because its set of references cannot change, but the mutable list it points to can be updated, so the tuple’s *effective* value appears different.

## Q17 – Reference Counting Limitation
**Correct:** Option 4  
Reference counting alone cannot reclaim objects that participate in reference cycles; CPython needs an additional cyclic garbage collector to find and free those.

## Q18 – Why Not Rely on `__del__`?
**Correct:** Option 2  
`__del__` is called when an object is being finalized, but the timing is not guaranteed, especially during interpreter shutdown, so critical cleanup should use context managers or explicit `close()` calls instead.

## Q19 – `is` vs `==`
**Correct:** Option 1  
`is` checks whether two variables refer to the exact same object (identity), while `==` delegates to the objects’ equality logic to compare their values.


## Q20 – Attribute Lookup Order
**Correct:** Option 4  
Attribute access first checks the instance’s own `__dict__`; only if the name is missing there does Python walk up through the class and its bases.



## Q21 – Rebind vs In-Place with `+=`
**Correct:** Option 4  
`a = a + [5]` builds a new list and rebinds `a`, leaving `b` pointing at the original `[10]`; `a += [5]` performs an in-place extension so both `a` and `b` see the mutated list.

## Q22 – Row Aliasing Across Copies
**Correct:** Option 1  
`matrix` and `clone` are two outer lists that both contain three references to the single `row` list. Both `row.append(1)` and `matrix[1].append(2)` mutate that same inner list, so all three rows and `row` end up as `[0, 1, 2]`.

## Q23 – Tuple of Lists: Shared vs Copied
**Correct:** Option 1  
`t1` stores two references to the same `inner` list, so appending to `inner` changes both elements in `t1`. `t2` was built from two separate copies using `inner[:]`, so it still shows `([0], [0])`.

## Q24 – Dict Values: Mutate vs Rebind
**Correct:** Option 1  
Both keys initially point at the same `shared` list, so `config["a"].append(1)` makes it `[1]`. The assignment `config["b"] = config["b"] + [2]` creates a new list `[1, 2]` and rebinds only `"b"`, leaving `"a"` still pointing at the original `[1]`.

## Q25 – Mutate Inner, Then Rebind Slot
**Correct:** Option 1  
Inside `tweak`, `first.append("X")` mutates the original inner list in slot 0, then `seq[0] = first + ["Y"]` replaces that slot with a brand‑new list. The outer list itself is mutated in place, so both `data` and `alias` see `[[1, 'X', 'Y'], [2]]`.

## Q26 – Breaking Aliases with Rebinding
**Correct:** Option 1  
`a` and `nums` start as aliases, and `b` is a shallow copy. The expression `nums = nums + [4]` creates a new list and rebinds `nums`, breaking the alias to `a`. The later `nums.append(5)` mutates only that new list, so `a` and `b` both stay `[1, 2, 3]` while `nums` becomes `[1, 2, 3, 4, 5]`.

## Q27 – Outer Rebind vs Inner Mutate with Slices
**Correct:** Option 1  
`alias` and `rows` are the same outer list; `clone` is a new outer list with the same two inner lists. `alias[0] = [1]` replaces slot 0 in the shared outer list with a new list, leaving `clone[0]` still pointing at the original `[0]`. `clone[1].append(2)` mutates the shared second inner list, so both `rows`/`alias` and `clone` see `[0, 2]` in position 1.

## Q28 – `*=` with Nested Lists
**Correct:** Option 1  
`nested *= 2` extends the list in place, repeating the existing inner list references, so indices 0 and 2 both point to the same `[1]` list. Appending `3` to `nested[0]` mutates that shared inner list, giving `[[1, 3], [2], [1, 3], [2]]` for both `nested` and `alias`.

## Q29 – Module vs Class vs Instance Name
**Correct:** Option 1  
Name lookup for `x` in `show` starts in the local scope, then falls back to the module global, so the first value is `"module"`. `self.x` reads the instance attribute `"instance"`, and `Thing.x` reads the class attribute `"class"`, so the output is `module instance class`.

## Q30 – Global Rebinding vs Aliased List
**Correct:** Option 1  
`add()` appends `"A"` into the original list, so both `items` and `alias` refer to `['A']`. In `reset()`, the `global items` declaration allows rebinding `items` to a brand‑new empty list; `alias` still points at the old list, so the prints show `items: []` and `alias: ['A']`.
