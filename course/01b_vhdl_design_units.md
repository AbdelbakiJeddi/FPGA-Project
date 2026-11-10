# Chapter 3 — VHDL Design Units

VHDL uses the **black-box** approach: an **entity** (the box/interface) and an **architecture** (what's inside).

## 1. Entity — the interface

Declares the circuit's inputs/outputs (ports). Each port has a **name**, **mode**, and **type**.

```vhdl
entity killer_ckt is
port (
    life_in1        : in  std_logic;
    life_in2        : in  std_logic;
    ctrl_a, ctrl_b  : in  std_logic;
    kill_a          : out std_logic;
    kill_b, kill_c  : out std_logic);
end killer_ckt;
```

- Modes: `in`, `out` (and `inout` later).
- Types: `std_logic` (1 bit) or `std_logic_vector` (a **bundle**).
- Multiple names per line allowed; whitespace ignored — optimize readability.

## 2. Bundles

A **bundle** = several related signals (avoid the word "bus", which means a protocol).

```vhdl
port ( a_data : in  std_logic_vector(0 to 7);      -- 8-bit bundle
       data_out : out std_logic_vector(0 to 7));
```

- `downto` → MSB first (left); `to` → LSB first (left).
- Black-box notation: a slash with the bit count (`/8`).
- Prefer bundles over individual scalar signals.

`std_logic` has 9 values (`0 1 U X Z W L H -`) from IEEE 1164, enabling tri-state etc. The simpler `bit` type only has `0`/`1`.

## 3. Standard Libraries

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;   -- std_logic types
use IEEE.numeric_std.all;      -- unsigned, arithmetic, conversions
```

Avoid non-standard `std_logic_arith`, `std_logic_unsigned`, `std_logic_signed`.

## 4. Architecture — the behavior

Describes how the circuit works. **Many architectures can describe one entity**, and the coding style affects the synthesized hardware (size/speed).

Three modeling styles (plus hybrids):
- **Data-flow** — concurrent signal assignments.
- **Behavioral** — process statements (sequential inside).
- **Structural** — instantiating and wiring sub-components.

## 5. Signals vs. Variables

| | Signal | Variable |
| :--- | :--- | :--- |
| Declared | architecture, before `begin` | inside a `process` (local) |
| Assign | `<=` | `:=` |
| Updates | "some time" later (after expression evaluated) | immediately after assignment |
| Represents | a wire | local storage (C/Java-like) |

```vhdl
architecture circuit1_arc of circuit1 is
    signal sig_1 : std_logic;          -- architecture-level
begin
    process (A, B, C)
        variable var_1 : integer;      -- process-local
    begin
        F     <= not (A and B and C);  -- signal assignment
        var_1 := 34;                   -- variable assignment
    end process;
    G <= not (A and B);                -- concurrent with the process
end circuit1_arc;
```

## Key Points
- Entity = interface; Architecture = implementation.
- Use `std_logic_vector` bundles for grouped signals.
- Always include the IEEE libraries; `std_logic` only exists with them.
- A signal updates later; a variable updates immediately.
- Everything outside a process is **concurrent**; a process runs concurrently with it, but sequentially inside.
