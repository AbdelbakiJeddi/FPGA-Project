# Chapter 4 — VHDL Programming Paradigm

VHDL **describes hardware, not software**. Statements are **concurrent** (run in parallel); source order does not matter. `<=` defines a signal relationship, not a copy.

## The Four Concurrent Statements

### 1. Concurrent Signal Assignment
```vhdl
F <= NOT (A AND B AND C);          -- 3-input NAND
F3 <= ((NOT L) AND (NOT M) AND N) OR (L AND M);
```
Intermediate signals (declared before `begin`, no mode) break up complex logic:
```vhdl
signal A1, A2 : std_logic;
A1 <= (NOT L) AND (NOT M) AND N;
F3 <= A1 OR A2;
```

### 2. Conditional Signal Assignment (`when ... else`)
First true condition wins; last expression is the catch-all. Like `if/else`.
```vhdl
MX_OUT <= D3 when (SEL = "11") else
          D2 when (SEL = "10") else
          D1 when (SEL = "01") else
          D0 when (SEL = "00") else
          '0';
```

### 3. Selected Signal Assignment (`with ... select`)
One chooser expression; like `switch`. `when others` is required and must be last.
```vhdl
with SEL select
    MX_OUT <= D3 when "11",
              D2 when "10",
              D1 when "01",
              D0 when "00",
              '0' when others;
```

### 4. Process Statement
A **concurrent** statement whose body executes **sequentially**. Covered later.

## Key Points
- Single quotes `'1'` = one bit; double quotes `"11"` = vector; `SEL(1)` = one bit.
- Different code can synthesize to the same hardware — prefer clarity.
- Entity outputs cannot be read on the RHS; use intermediate signals.
- Enumerate all cases; use `when others` as a safety net.
