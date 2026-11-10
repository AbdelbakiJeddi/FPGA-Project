# Chapter 3: VHDL Design Units

## 3.1 Entity Interface Specification
In hierarchical digital design, the black-box abstraction isolates the external interface from the internal circuit implementation. In VHDL, the **entity** defines this black-box interface:

```text
entity entity_name is
    port (
        port_identifier : mode data_type;
        -- ...
        last_identifier : mode data_type  -- Note: NO trailing semicolon on final port
    );
end entity entity_name;
```

A complete, syntactically valid entity and trivial passthrough architecture illustrating the interface declaration:

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity interface_spec_demo is
    port (
        clk      : in  std_logic;
        reset    : in  std_logic;
        data_in  : in  std_logic_vector(7 downto 0);
        data_out : out std_logic_vector(7 downto 0)
    );
end entity interface_spec_demo;

architecture rtl of interface_spec_demo is
begin
    data_out <= data_in;
end architecture rtl;
```

### Port Modes & Electrical Semantics
- **`in`**: Unidirectional input. Driven by external circuitry and read-only inside the architecture. Cannot be assigned within the architecture.
- **`out`**: Unidirectional output. Driven by the internal architecture to external nets. Under standard VHDL-93, **`out` ports cannot be read on the right-hand side of an assignment** within the architecture body. Reading an `out` port causes a compiler error (`cannot read output port`).
- **`inout`**: Bidirectional pin. Represents a physical pin that both drives and samples signals (e.g., external data buses). Typically requires tri-state buffer modeling (`'Z'`) to prevent electrical contention.
- **`buffer`**: Output port with internal read-back capability. Restricted to single-driver nets and imposes strict hierarchical port-matching rules; widely discouraged in professional RTL in favor of intermediate architecture signals.

### Bundles vs. Buses and Vector Directionality
- **Scalar vs. Bundle**: Single-wire signals use scalar `std_logic`. Grouped physical wires sharing an architectural purpose are designated as a **bundle** and declared using `std_logic_vector`. The term *bundle* denotes physical grouped wiring, whereas *bus* denotes a formal communications protocol with arbitration.
- **`downto` vs. `to`**:
  - `(N downto 0)`: Little-endian / MSB-on-left orientation (bit $N$ is MSB, bit $0$ is LSB). Standard across arithmetic and FPGA RTL designs because bit indices align directly with binary positional weights ($2^N$).
  - `(0 to N)`: Big-endian orientation (bit $0$ is MSB). Primarily used in telecommunications protocols; mixing `to` and `downto` vectors without explicit slicing causes compile errors.

## 3.2 IEEE Libraries and Packages
Modern synthesizable RTL requires standard IEEE package declarations:

```text
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
```

### The IEEE 1164 9-Valued Logic System and std_logic Types
The `std_logic` and `std_logic_vector` types support 9 distinct logic states modeling electrical properties and simulation anomalies:

| Value | Meaning | Hardware & Simulation Implication |
|---|---|---|
| `'0'` | Forcing Logic 0 | Active low / GND |
| `'1'` | Forcing Logic 1 | Active high / $V_{DD}$ |
| `'U'` | Uninitialized | Default simulation state for unassigned signals; detects unreset registers |
| `'X'` | Forcing Unknown | Electrical contention (two conflicting active drivers on same net) |
| `'Z'` | High Impedance | Floating / tri-state bus driver |
| `'W'` | Weak Unknown | Resistive contention |
| `'L'` | Weak Logic 0 | Resistive pull-down |
| `'H'` | Weak Logic 1 | Resistive pull-up |
| `'-'` | Don't Care | Synthesis wild card allowing optimizer to minimize LUT equations |

### Deprecation of Non-Standard Synopsys Packages
Avoid legacy third-party Synopsys libraries (`std_logic_arith`, `std_logic_unsigned`, `std_logic_signed`). These libraries are non-standard, introduce conflicting operator overloads, and prevent code portability. Always use IEEE standard **`ieee.numeric_std`** with explicit `unsigned` or `signed` casting.

## 3.3 Architecture Implementation
The architecture specifies the internal implementation of an entity:

```text
architecture rtl of entity_name is
    -- Declarative Region: local signals, types, constants, components
begin
    -- Statement Region: concurrent statements executing in parallel
end architecture rtl;
```

### Architectural Regions
1. **Declarative Region** (between `architecture ... is` and `begin`): Defines local resources invisible to external entities. Contains internal intermediate signals, user types, subprograms, and component declarations.
2. **Statement Region** (between `begin` and `end`): Contains concurrent statements executing in parallel.

### Modeling Styles
- **Data-flow**: Concurrent signal assignments and Boolean equations modeling gate-level propagation.
- **Behavioral**: Algorithmic abstraction using sequential `process` statements.
- **Structural**: Netlist interconnection of instantiated child components.
- **Hybrid**: Professional RTL blending concurrent data paths with behavioral control processes.

## 3.4 Signal and Variable Assignments: Signals vs Variables Semantics
VHDL provides two distinct data objects with fundamentally different timing and hardware semantics:

| Property | Signal (`signal`) | Variable (`variable`) |
|---|---|---|
| **Declaration Scope** | Architecture declarative region | Strictly local to `process`, `function`, or `procedure` |
| **Assignment Operator** | Non-blocking: `<=` | Blocking: `:=` |
| **Update Timing** | Deferred: updates after a **delta delay ($\delta$)** | Immediate: updates instantaneously in simulation time |
| **Hardware Implication** | Physical interconnect wire or flip-flop register | Combinational scratchpad net or inferred register |

### Hardware Implications of Delta Delay ($\delta$)
In event-driven simulation, a delta cycle ($\delta$) represents an infinitesimal unit of time required to evaluate concurrent causality without advancing simulation time ($T = T + 0\text{ ns}$).
- When a **signal** is assigned inside a process (`sig <= '1';`), its new value is scheduled for the next delta cycle. Reading `sig` immediately in the subsequent line returns its **old value**.
- When a **variable** is assigned (`var := '1';`), the update is immediate. Subsequent statements within the process see the new value.
- In synthesis, variables assigned and read within the same clock cycle map to combinational intermediate wires; variables read before being assigned infer storage registers.

## 3.5 Summary
- The entity defines the black-box interface pinout; the architecture implements internal behavior and topology.
- Port mode `out` is write-only in VHDL-93; intermediate signals are required for internal state read-back.
- IEEE 1164 defines the 9-valued logic system; IEEE `numeric_std` is the universal standard for arithmetic.
- Signals model physical nets with non-blocking delta-delay updates; variables model local process scratchpads with immediate updates.

## Synthesizable Architectural Example
The following complete, valid VHDL module illustrates entity interface definition, intermediate signals overcoming VHDL-93 `out` port read restrictions, and the behavioral difference between signals and variables.

```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity design_units_demo is
    port (
        clk      : in  std_logic;
        reset    : in  std_logic;
        data_in  : in  std_logic_vector(7 downto 0);
        load_en  : in  std_logic;
        acc_out  : out std_logic_vector(7 downto 0);
        iter_cnt : out std_logic_vector(3 downto 0)
    );
end entity design_units_demo;

architecture rtl of design_units_demo is
    -- Declarative region: Intermediate signals route internal state and bypass 'out' port read restrictions
    signal accumulator_reg : unsigned(7 downto 0);
    signal counter_reg     : unsigned(3 downto 0);
begin
    -- Concurrent signal assignments driving external entity output ports
    acc_out  <= std_logic_vector(accumulator_reg);
    iter_cnt <= std_logic_vector(counter_reg);

    -- Sequential process demonstrating signal vs variable update semantics
    reg_proc : process(clk, reset)
        variable var_temp : unsigned(7 downto 0);
    begin
        if reset = '1' then
            accumulator_reg <= (others => '0');
            counter_reg     <= (others => '0');
        elsif rising_edge(clk) then
            if load_en = '1' then
                -- Variable assignment updates immediately within current process evaluation
                var_temp := unsigned(data_in) + 1;
                
                -- Signal assignments schedule updates for next delta cycle / register clock edge
                accumulator_reg <= accumulator_reg + var_temp;
                counter_reg     <= counter_reg + 1;
            end if;
        end if;
    end process reg_proc;
end architecture rtl;
```
