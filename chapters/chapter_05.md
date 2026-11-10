# Chapter 5: Standard Models in VHDL Architectures

## Architectural Styles Overview
VHDL architectures describe the operational implementation of an entity using three foundational modeling styles:

| Modeling Style | Primary Abstraction | Core Language Constructs | Hardware Synthesis Mapping |
| :--- | :--- | :--- | :--- |
| **Data-Flow** | Logic gates, continuous data progression | Concurrent signal assignment (`<=`), conditional (`when-else`), selected (`with-select`) | Direct combinatorial logic gates, decoders, and multiplexers |
| **Behavioral** | Algorithmic input-to-output transfer functions | The `process` statement, sequential statements (`if`, `case`, loops) | High-level synthesis determines RTL registers, priority networks, and MUXes |
| **Structural** | Hierarchical black-box netlisting | `component` declarations, `port map`, `generic map` | Interconnected instances of sub-modules and silicon primitives |

In real-world FPGA design, robust architectures are rarely purely monolithic; production designs are **hybrid models** blending structural module instantiations, concurrent data-flow assignments for simple routing, and behavioral processes for sequential control and complex decision logic.

---

## 5.1 Data-flow Style Architecture
A data-flow architecture describes a circuit by showing how data moves concurrently from right-hand side (RHS) operands across language operators to left-hand side (LHS) targets:
- Uses concurrent signal assignments, conditional assignments (`when-else`), and selected assignments (`with-select`).
- Highly transparent: an experienced designer can visualize the underlying logic gates and multiplexer trees directly from the source code.
- Well-suited for shallow combinational datapath slices, but becomes unwieldy when describing multi-state sequencers, complex nested control flows, or priority encoders.

---

## 5.2 Behavioral Style Architecture
Behavioral architectures define how circuit outputs react to inputs algorithmically without prescribing gate-level topologies:
- Evaluates inputs and derives outputs using abstract sequential decision trees, delegating logic minimization, LUT placement, and flip-flop binding to the synthesis compiler.
- Operates at a higher level of abstraction, acting as an algorithmic specification of digital function.
- The fundamental structural container of behavioral VHDL is the **`process` statement**.

---

## 5.3 Process Statement
The `process` statement is itself a **concurrent statement** within an architecture body, but the statements placed between its `begin` and `end process` delimiters execute **sequentially**:

```text
[process_label:] process (sensitivity_list) is
    -- Declarative region: local variables, types, constants
begin
    -- Sequential statements executed in sequence
end process [process_label];
```

### Execution Mechanics & Sensitivity Lists
1. **Event Activation**: In simulation, a process is suspended until an event (value change) occurs on one or more signals declared in its **sensitivity list**. When triggered, the process executes from the top `begin` to the bottom `end process`, schedules target signal updates, and suspends again.
2. **Combinational Sensitivity Rule**: For pure combinational logic processes, **every signal read on the RHS of an expression or evaluated in a condition MUST appear in the sensitivity list**. 
3. **Simulation vs. Synthesis Mismatch Hazard**: 
   - Simulators evaluate processes strictly upon events on sensitivity list signals. If an input is omitted, the simulator ignores input transitions when the other signals remain stable.
   - Logic synthesizers synthesize complete physical combinational logic networks regardless of sensitivity list omissions. This discrepancy causes catastrophic simulation-vs-synthesis divergence.
4. **Inter-Process Concurrency**: Multiple processes in an architecture run concurrently in parallel, communicating via interconnect signals. Complex systems should be partitioned into multiple communicating, single-purpose processes rather than a monolithic process.

---

## 5.4 Sequential Statements
Inside a process, sequential execution enables branching and scheduling constructs:

### 5.4.1 Signal Assignment Statement
The sequential signal assignment (`<=`) is syntactically identical to concurrent signal assignment but differs fundamentally in its update scheduling:
- **Scheduled Assignment**: Evaluating `Target <= Value;` inside a process does not update `Target` immediately. The assignment is scheduled into the simulation delta queue.
- **Delta-Delay Overwrite**: If a signal is assigned multiple times within a single execution cycle of a process, **only the last evaluated assignment takes effect** when the process suspends. Intermediate assignments are overwritten.

### 5.4.2 if Statement
The `if` statement provides conditional sequential branching, serving as the sequential counterpart to concurrent `when-else`:

```text
if (condition_1) then
    <sequential_statements_1>
elsif (condition_2) then
    <sequential_statements_2>
else
    <sequential_statements_default>
end if;
```

#### Hardware Implications
- **Priority Logic Chain**: Because conditions are evaluated in strict top-to-bottom sequence, synthesizers implement `if-elsif` structures as a **cascaded priority multiplexer network**. Condition 1 has highest priority, adding cascaded logic delay for deeper `elsif` branches.
- **Latch Inference**: Omitting the `else` clause in a combinational process leaves outputs unspecified for unhandled input permutations. The synthesizer infers a **level-sensitive transparent latch** to retain the signal's previous value.

### 5.4.3 case Statement
The `case` statement provides multi-path selection based on the evaluation of a single control expression, serving as the sequential counterpart to concurrent `with-select`:

```text
case (expression) is
    when choices_1 =>
        <sequential_statements_1>
    when choices_2 =>
        <sequential_statements_2>
    when others =>
        <sequential_statements_default>
end case;
```

#### Hardware Implications & Idioms
- **Parallel Multiplexer Synthesis**: Unlike the priority chain of `if-elsif`, `case` choices are evaluated simultaneously, synthesizing to **balanced parallel multiplexers or single-level LUT decoders** with equal propagation delays across branches.
- **Exhaustive Coverage**: VHDL mandates that every possible permutation of the selector expression type be covered. Using `when others =>` guarantees complete coverage and prevents accidental storage induction.
- **Signal Aggregation via Concatenation (`&`)**: Multiple discrete input bits can be concatenated into an intermediate vector to evaluate truth tables or state combinations cleanly within a single `case` construct:
  ```text
  abc_bus <= A & B & C;
  case abc_bus is
      when "100" | "011" => F_OUT <= '1';
      when others        => F_OUT <= '0';
  end case;
  ```
- **Don't-Care Literal (`'-'`) Caution**: While `'-'` represents a don't-care in synthesis, standard VHDL `case` evaluation treats `'-'` as a literal character match rather than a wildcard. Simulators will fail to match binary `'0'` or `'1'` against `'-'`. Use explicit choices or `std_match` from `ieee.numeric_std` instead.

### 5.4.4 Nesting Sequential Statements
Unlike concurrent conditional and selected assignments (which cannot be nested), sequential statements can be nested arbitrarily: `case` statements can be embedded within `if` branches, and `if` constructs can be placed inside `case` choices. This enables hierarchical control decoding, such as qualifying a wide multiplexer with a global chip-enable signal.

---

## 5.5 Caveats Regarding Sequential Statements

### Incomplete Specification and Latch Inference
In combinational processes, if an output signal is not explicitly assigned a value across all possible conditional branches (`if-elsif` without `else`, or `case` with omitted choices), the synthesis engine must preserve the output's prior state. It satisfies this requirement by inferring a **transparent latch**.

### Latch Avoidance and Prevention Strategies
- **FPGA Hazard**: Standard FPGA architectures (such as AMD Xilinx UltraScale or Intel Agilex) are built from dedicated edge-triggered D flip-flops; transparent latches consume extra logic slices, introduce severe timing hazards (asymmetric setup/hold, clock pulse width violations), and are highly sensitive to glitches on control inputs.
- **Golden Idiom — Output Pre-Assignment**: To guarantee latch prevention in combinational processes, assign safe default values to all outputs at the very top of the process body before any branching statements:
  ```text
  comb_proc: process (sel, data_in) is
  begin
      -- Default pre-assignment eliminates all unintended latches
      output_sig <= (others => '0');
      valid_flag <= '0';

      if (sel = "01") then
          output_sig <= data_in;
          valid_flag <= '1';
      end if; -- No else required; default covers unhandled cases
  end process comb_proc;
  ```

### 2. Avoiding Monolithic Software-Style Processes
A frequent defect in VHDL development is writing large, monolithic processes that attempt to implement software algorithms sequentially. In hardware:
- Deeply nested `if` statements create long combinational paths, destroying clock frequency ($F_{\max}$).
- High signal counts in sensitivity lists bloat simulation runtimes.
- Optimal architectures partition behavior into distinct, communicating processes matching physical hardware boundaries (e.g., separating synchronous state registers from combinational next-state decoders).

---

## 5.6 Summary
- Data-flow modeling maps directly to concurrent logic gates; behavioral modeling uses sequential processes to describe transfer functions.
- Processes execute concurrently in an architecture; statements within a process execute in sequence.
- The sensitivity list triggers execution upon signal transitions; omitting signals in combinational blocks creates simulation-synthesis mismatches.
- `if-elsif` synthesizes to priority multiplexer chains; `case` synthesizes to balanced, parallel multiplexers.
- Incomplete conditional branching induces unwanted transparent latches in combinational logic; use default output pre-assignments to guarantee complete specification.

---

## Synthesizable Architectural Examples

### Example 1: 8:1 Multiplexer with Enable (Demonstrating Nested Sequential Statements)
```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity mux_8to1_ce is
    port (
        data_in : in  std_logic_vector(7 downto 0);
        sel     : in  std_logic_vector(2 downto 0);
        ce      : in  std_logic;
        f_ctrl  : out std_logic
    );
end entity mux_8to1_ce;

architecture behavioral of mux_8to1_ce is
begin
    -- Behavioral process modeling an 8:1 MUX with chip enable
    -- Demonstrates nesting case inside if, complete specification, and latch prevention
    mux_proc: process(data_in, sel, ce) is
    begin
        if (ce = '0') then
            f_ctrl <= '0';
        else
            case sel is
                when "000" => f_ctrl <= data_in(0);
                when "001" => f_ctrl <= data_in(1);
                when "010" => f_ctrl <= data_in(2);
                when "011" => f_ctrl <= data_in(3);
                when "100" => f_ctrl <= data_in(4);
                when "101" => f_ctrl <= data_in(5);
                when "110" => f_ctrl <= data_in(6);
                when "111" => f_ctrl <= data_in(7);
                when others => f_ctrl <= '0';
            end case;
        end if;
    end process mux_proc;
end architecture behavioral;
```

### Example 2: Combinational Function with Default Pre-Assignment & Concatenation
```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity comb_function is
    port (
        a_in   : in  std_logic;
        b_in   : in  std_logic;
        c_in   : in  std_logic;
        f_out  : out std_logic;
        f_flag : out std_logic
    );
end entity comb_function;

architecture rtl of comb_function is
    signal abc_bus : std_logic_vector(2 downto 0);
begin
    -- Intermediate signal aggregation via concatenation
    abc_bus <= a_in & b_in & c_in;

    -- Combinational logic with output default pre-assignment to prevent latch inference
    comb_proc: process(abc_bus) is
    begin
        -- Golden idiom: Default output pre-assignments
        f_out  <= '0';
        f_flag <= '0';

        case abc_bus is
            when "100" | "011" | "111" =>
                f_out  <= '1';
                f_flag <= '1';
            when "001" | "010" =>
                f_out  <= '1';
            when others =>
                -- Handled cleanly by default pre-assignment
                null;
        end case;
    end process comb_proc;
end architecture rtl;
```
