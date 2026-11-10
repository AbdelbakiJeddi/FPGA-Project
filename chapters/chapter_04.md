# Chapter 4: VHDL Programming Paradigm

## 4.1 Concurrent Statements
In VHDL, the primary execution paradigm is **concurrency**. Unlike procedural languages where statements execute sequentially from top to bottom according to a program counter, all statements within the statement region of an architecture body execute simultaneously in parallel.

### Key Concurrency Principles:
1. **Hardware Parallelism**: Statements model physical circuits connected across silicon routing channels. Each statement continuously drives its output net.
2. **Event-Driven Execution**: A concurrent statement remains dormant until an **event** (a state or logic transition) occurs on any signal present in its evaluation expression (right-hand side). The event immediately triggers evaluation of the expression and updates the target signal.
3. **Textual Order Independence**: The relative physical order of concurrent statements in the architecture source code has **zero effect** on simulation results or synthesized hardware. Swapping the position of two concurrent statements produces identical netlists and timing behavior.

## 4.2 Signal Assignment Operator "<="
The symbol `<=` denotes the **concurrent signal assignment operator**. It continuously binds an evaluated Boolean or arithmetic expression to a target signal net:

```text
target_net <= expression;
```

In contrast to the procedural variable assignment operator (`:=`), the signal assignment operator (`<=`) operates with non-blocking, event-driven semantics. Updates take effect after an infinitesimal delta delay ($\delta$) or at the subsequent active clock transition.

## 4.3 Concurrent Signal Assignment Statements
Concurrent Signal Assignment (CSA) expressions compute Boolean or arithmetic logic in continuous parallel hardware:

```text
f_out <= (a_in and b_in) or (c_in and not d_in);
```

- **Hardware Synthesis Mapping**: Simple CSA expressions synthesize directly into combinational Boolean networks mapped to FPGA Look-Up Tables (LUTs).
- **Multiple Driver Rule**: Assigning to the same target signal from multiple concurrent statements creates multiple active drivers on that net. In standard push-pull FPGA logic, conflicting drivers produce resolved unknown states (`'X'`) and result in synthesis or implementation DRC errors. A signal must be driven by exactly one concurrent source unless explicitly modeling a tri-state bus.

## Intermediate Signals & Output Port Limitation
Under VHDL-93, entity ports declared with mode `out` are strictly write-only. Reading an `out` port on the right-hand side of an assignment is a compilation error:

```text
-- ILLEGAL in VHDL-93: Cannot read entity output port on RHS
valid_out <= ready_out and ack_out; 
```

**Idiomatic FPGA Solution**:
1. Declare an internal intermediate signal in the architecture declarative region (before `begin`).
2. Drive and read the intermediate signal freely throughout the architecture.
3. Concurrently assign the intermediate signal to the entity `out` port:

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity intermediate_signal_demo is
    port (
        in_a      : in  std_logic_vector(7 downto 0);
        in_b      : in  std_logic_vector(7 downto 0);
        data_out  : out std_logic_vector(7 downto 0);
        flag_out  : out std_logic
    );
end entity intermediate_signal_demo;

architecture rtl of intermediate_signal_demo is
    signal internal_data : std_logic_vector(7 downto 0);
begin
    -- Compute into intermediate signal
    internal_data <= in_a and in_b;
    -- Drive external output port
    data_out <= internal_data;
    -- Read internal signal for feedback logic (bypassing VHDL-93 out port read restriction)
    flag_out <= internal_data(0);
end architecture rtl;
```

## 4.4 Conditional Signal Assignment when
Conditional Signal Assignment implements decision branches in concurrent code using the `when-else` construct:

```text
target <= expr_1 when condition_1 else
          expr_2 when condition_2 else
          expr_default;
```

### Hardware Synthesis Implications: Priority Logic
- **Inferred Hardware**: Synthesizes to a **Priority Multiplexer Network** (cascaded 2:1 multiplexers).
- **Evaluation Semantics**: Conditions are tested sequentially in order of appearance. The first condition evaluating to true commits its associated expression, and all subsequent branches are bypassed.
- **Timing Impact**: In high-speed FPGA designs, deep cascades of `when-else` statements create long combinational propagation paths through multiple LUT levels, which can degrade setup timing slack ($F_{max}$).

### Literal Representation Invariants
- Single-bit `std_logic` literals require single quotes: `'0'`, `'1'`, `'Z'`.
- Multi-bit `std_logic_vector` literals require double quotes: `"00"`, `"1101"`, `x"FF"`.

## 4.5 Selected Signal Assignment with select
Selected Signal Assignment evaluates a single selector expression against mutually exclusive choices:

```text
with selector_expression select
    target <= expr_1 when choice_1,
              expr_2 when choice_2,
              expr_default when others;
```

### Hardware Synthesis Implications: Balanced Multiplexing
- **Inferred Hardware**: Synthesizes to a **Balanced Multiplexer** or parallel decoder/LUT without evaluation priority.
- **Timing Impact**: Each input path experiences identical propagation delay through the multiplexer structure, making it ideal for timing-critical data paths.

### Rules of Selection:
1. **Mutual Exclusivity**: Choices must not overlap; no two branches can match the same selector state.
2. **Exhaustive Coverage**: Every possible value of the selector expression's type must be accounted for.
3. **Mandatory `when others` Clause**: Because `std_logic` and `std_logic_vector` types support 9 logic states (`'0'`, `'1'`, `'U'`, `'X'`, `'Z'`, `'W'`, `'L'`, `'H'`, `'-'`), a `when others` clause is **mandatory** to cover unassigned simulation and meta-logic states. Omitting `when others` results in compilation errors.
4. **Grouped Choices (`|`)**: Multiple choices mapping to the same output can be grouped using the vertical bar (`|`) operator:
   ```text
   when "0001" | "0010" | "0100" | "1000" => ...
   ```

### Vector Concatenation Operator "&"
The concatenation operator `&` combines individual bits and smaller vectors into composite bundles:

```text
combined_sel <= mode_bit & ctrl_vector;
```

Concatenation is frequently used in selected assignments to construct composite selector words, enabling concise truth-table decoders and steering logic.

## 4.6 Process Statement
The `process` statement is itself a concurrent statement within the architecture. However, code statements enclosed *within* the process execute sequentially from top to bottom. The process statement bridges concurrent hardware structures and procedural algorithmic descriptions, which will be explored in depth in subsequent chapters.

## 4.7 Summary
- The VHDL architecture is concurrent: all statements execute simultaneously and independently of textual ordering.
- Concurrent Signal Assignment (`<=`) infers parallel Boolean logic networks.
- Conditional Signal Assignment (`when-else`) infers priority multiplexer chains.
- Selected Signal Assignment (`with-select`) infers balanced, symmetric multiplexers and requires exhaustive coverage with `when others`.
- Intermediate signals declared in the architecture declarative area are required to overcome VHDL-93 `out` port read limitations and route internal feedback nets.

## Synthesizable Architectural Example
The following complete, valid VHDL design unit demonstrates all major concurrent constructs: simple CSA, intermediate signals overcoming `out` limitations, vector concatenation `&`, conditional assignment (`when-else`), and selected assignment (`with-select-when`) with `when others`.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity concurrent_router is
    port (
        in_a       : in  std_logic_vector(3 downto 0);
        in_b       : in  std_logic_vector(3 downto 0);
        prio_high  : in  std_logic;
        prio_low   : in  std_logic;
        sel_mode   : in  std_logic_vector(1 downto 0);
        active_in  : in  std_logic;
        routed_out : out std_logic_vector(3 downto 0);
        status_led : out std_logic
    );
end entity concurrent_router;

architecture rtl of concurrent_router is
    -- Declarative region: Intermediate signals for internal routing and out-port read-back
    signal internal_data : std_logic_vector(3 downto 0);
    signal composite_sel : std_logic_vector(2 downto 0);
begin
    -- Vector concatenation combining control lines into a composite selector
    composite_sel <= prio_high & sel_mode;

    -- Conditional signal assignment inferring priority multiplexer logic
    internal_data <= in_a when prio_high = '1' else
                     in_b when prio_low  = '1' else
                     (in_a and in_b);

    -- Selected signal assignment inferring balanced multiplexer logic with exhaustive choices
    with composite_sel select
        routed_out <= internal_data         when "100" | "101",
                      in_a                  when "000",
                      in_b                  when "001",
                      (not internal_data)   when "010",
                      (others => '0')       when others;

    -- Reading intermediate signal to drive status output (overcomes VHDL-93 out port read restriction)
    status_led <= internal_data(0) and active_in;
end architecture rtl;
```
