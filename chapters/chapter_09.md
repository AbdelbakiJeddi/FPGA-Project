# Chapter 9: Registers and Register Transfer Level

## 9.1 Register Architecture and Storage Element Inference

In digital hardware, a register is a collection of binary storage elements (flip-flops) sharing common clock and control lines, operating concurrently on multi-bit data words. While a single D flip-flop stores a scalar `std_logic`, an $N$-bit register stores a vector (`std_logic_vector(N-1 downto 0)`), latching all bits simultaneously on the active clock edge.

### 9.1.1 Register Inference via Uncompleted `if` Statements
Hardware synthesis tools infer sequential storage (flip-flops) whenever a signal assignment is conditioned on a clock transition and lacks an explicit assignment in an alternative branch:

```vhdl
reg_proc: process(CLK)
begin
    if rising_edge(CLK) then
        if LD = '1' then
            REG_OUT <= REG_IN;
            -- No 'else' branch: REG_OUT retains its previous state
        end if;
    end if;
end process reg_proc;
```

In software programming, an unhandled `else` condition simply implies doing nothing during that execution pass. In FPGA synthesis, memory is physical: "doing nothing" means the hardware must preserve its existing state across clock cycles. Because the process is synchronized to `rising_edge(CLK)`, the synthesizer maps this behavior directly to the dedicated Clock Enable (`CE`) pin of FPGA slice flip-flops. When `LD = '0'`, the clock enable is deasserted, inhibiting state updates without requiring clock gating.

### 9.1.2 Clock-Isolation Nested `if` Idiom
A fundamental rule in synchronous VHDL design is the strict isolation of the clock event condition from synchronous control conditions:

- **Correct (Nested `if`)**:
  ```vhdl
  if rising_edge(CLK) then
      if LD = '1' then
          Q <= D;
      end if;
  end if;
  ```
- **Anti-Pattern (Compound Condition)**:
  ```vhdl
  -- AVOID: Disrupts clock-tree synthesis and causes tool incompatibilities
  if (rising_edge(CLK) and LD = '1') then
      Q <= D;
  end if;
  ```

Combining clock edge detection with data/enable conditions in a single boolean expression violates synchronous synthesis conventions. The synthesizer must identify the clock signal unambiguously to route it onto dedicated low-skew global clock buffers (BUFG in AMD/Xilinx, Global Clock Networks in Intel/Altera). A compound condition can cause the synthesis tool to infer combinational gating on the clock path, introducing clock skew, runt pulses, and severe timing violations.

### 9.1.3 Sensitivity List Discipline for Synchronous Circuits
For purely synchronous registers:
1. Only the clock signal `CLK` appears in the process sensitivity list.
2. Synchronous control inputs (`LD`) and synchronous data inputs (`REG_IN`) **must not** appear in the sensitivity list.
3. If an asynchronous reset or preset is present, it must be included in the sensitivity list alongside `CLK`.

Including synchronous inputs like `LD` or `REG_IN` in the sensitivity list causes unnecessary simulation event evaluations without affecting synthesis, leading to simulation-synthesis discrepancies.

---

## 9.2 Synthesizable 8-Bit Register with Load Enable

Below is the complete, self-contained VHDL design entity and architecture for an 8-bit synchronous register with an active-high parallel load enable:

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity reg8 is
    port (
        CLK     : in  std_logic;
        LD      : in  std_logic;
        REG_IN  : in  std_logic_vector(7 downto 0);
        REG_OUT : out std_logic_vector(7 downto 0)
    );
end entity reg8;

architecture behavioral of reg8 is
begin
    reg_proc : process(CLK)
    begin
        if rising_edge(CLK) then
            if LD = '1' then
                REG_OUT <= REG_IN;
            end if;
        end if;
    end process reg_proc;
end architecture behavioral;
```

### Hardware Mapping Details:
- **Target Primitives**: 8 D-type flip-flops (FDRE in Xilinx primitives).
- **Control Line**: The scalar `LD` net directly drives the `CE` pin of all 8 flip-flops in parallel.
- **Clock Line**: `CLK` connects directly to the dedicated clock pins, driven from global clock routing.

---

## 9.3 RTL Datapath and Control Partitioning

Digital architectures at the Register Transfer Level (RTL) are partitioned into two complementary domains:
1. **Datapath**: Comprises registers, ALUs, adders, shifters, and routing multiplexers that store and transform multi-bit data words.
2. **Control Path**: Comprises finite state machines (FSMs) or microsequencers that evaluate status flags and assert enable, select, and read/write control signals to direct datapath operations.

Data transfer between registers occurs across shared bus lines governed by multiplexers. Intermediate signals represent internal physical routing traces connecting datapath blocks.

---

## 9.4 Multi-Process Behavioral RTL vs. Structural Composition

RTL designs can be captured using either a multi-process behavioral model or a structural interconnection of pre-existing component entities.

### 9.4.1 Multi-Process Behavioral RTL Model
In this approach, functional blocks within a single entity are separated into distinct concurrent statements: dedicated synchronous processes for individual registers and concurrent signal assignments for combinational multiplexers. Internal signals provide inter-process communication.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity ckt_rtl_behavioral is
    port (
        CLK     : in  std_logic;
        SEL     : in  std_logic;
        LDA     : in  std_logic;
        LDB     : in  std_logic;
        D1_IN   : in  std_logic_vector(7 downto 0);
        D2_IN   : in  std_logic_vector(7 downto 0);
        REG_A   : out std_logic_vector(7 downto 0);
        REG_B   : out std_logic_vector(7 downto 0)
    );
end entity ckt_rtl_behavioral;

architecture rtl of ckt_rtl_behavioral is
    -- Internal bus routing multiplexer output to register inputs
    signal s_mux_result : std_logic_vector(7 downto 0);
begin
    -- Combinational data-flow multiplexer
    with SEL select
        s_mux_result <= D1_IN when '1',
                        D2_IN when '0',
                        (others => '0') when others;

    -- Synchronous Register A process
    proc_reg_a : process(CLK)
    begin
        if rising_edge(CLK) then
            if LDA = '1' then
                REG_A <= s_mux_result;
            end if;
        end if;
    end process proc_reg_a;

    -- Synchronous Register B process
    proc_reg_b : process(CLK)
    begin
        if rising_edge(CLK) then
            if LDB = '1' then
                REG_B <= s_mux_result;
            end if;
        end if;
    end process proc_reg_b;
end architecture rtl;
```

#### Behavioral Multi-Process Advantages:
- **Decoupled Logic**: Each process has a single responsibility (e.g. driving a single register or bus).
- **Synthesis Predictability**: Eliminates monolithic process bottlenecks where unintended variable updates or nested conditions synthesize unintended multiplexer cascades or latches.
- **Maintainability**: Register bit widths and control logic can be modified locally without altering surrounding blocks.

### 9.4.2 Structural Component Composition Model
The structural approach explicitly declares and instantiates verified sub-modules (`mux2t1`, `reg8`), binding them together using internal signals and `port map` associations.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

-- 2:1 Multiplexer Component Unit
entity mux2t1 is
    port (
        A     : in  std_logic_vector(7 downto 0);
        B     : in  std_logic_vector(7 downto 0);
        SEL   : in  std_logic;
        M_OUT : out std_logic_vector(7 downto 0)
    );
end entity mux2t1;

architecture dataflow of mux2t1 is
begin
    with SEL select
        M_OUT <= A when '1',
                 B when '0',
                 (others => '0') when others;
end architecture dataflow;

library IEEE;
use IEEE.std_logic_1164.all;

-- Structural RTL Datapath composing mux2t1 and two reg8 instances
entity ckt_rtl_structural is
    port (
        CLK     : in  std_logic;
        SEL     : in  std_logic;
        LDA     : in  std_logic;
        LDB     : in  std_logic;
        D1_IN   : in  std_logic_vector(7 downto 0);
        D2_IN   : in  std_logic_vector(7 downto 0);
        REG_A   : out std_logic_vector(7 downto 0);
        REG_B   : out std_logic_vector(7 downto 0)
    );
end entity ckt_rtl_structural;

architecture structural of ckt_rtl_structural is
    component mux2t1 is
        port (
            A     : in  std_logic_vector(7 downto 0);
            B     : in  std_logic_vector(7 downto 0);
            SEL   : in  std_logic;
            M_OUT : out std_logic_vector(7 downto 0)
        );
    end component mux2t1;

    component reg8 is
        port (
            CLK     : in  std_logic;
            LD      : in  std_logic;
            REG_IN  : in  std_logic_vector(7 downto 0);
            REG_OUT : out std_logic_vector(7 downto 0)
        );
    end component reg8;

    signal s_mux_result : std_logic_vector(7 downto 0);
begin
    m1 : mux2t1
        port map (
            A     => D1_IN,
            B     => D2_IN,
            SEL   => SEL,
            M_OUT => s_mux_result
        );

    ra : reg8
        port map (
            CLK     => CLK,
            LD      => LDA,
            REG_IN  => s_mux_result,
            REG_OUT => REG_A
        );

    rb : reg8
        port map (
            CLK     => CLK,
            LD      => LDB,
            REG_IN  => s_mux_result,
            REG_OUT => REG_B
        );
end architecture structural;
```

---

## 9.5 Architectural Comparison and Golden Design Rules

| Feature | Multi-Process Behavioral RTL | Structural RTL Composition |
|---|---|---|
| **Abstraction Level** | High: algorithm and bus transfers expressed directly | Low: netlist of interconnected instances |
| **Code Verbosity** | Compact, minimal boilerplate | High: requires component declarations and port maps |
| **Logic Reusability** | Scoped to current entity/architecture | High: components can be parameterized and reused across designs |
| **Synthesis Mapping** | Synthesizer infers muxes and registers from sequential/concurrent constructs | Netlist maps directly to instantiated component modules |
| **Refactoring Agility** | Quick modifications to internal data paths | Interface changes require updating declarations and port maps |

### Golden Synthesis Rules for RTL Registers:
1. **Keep processes single-purpose**: Dedicate one process per register or tightly coupled register bank.
2. **Never gate clocks in RTL code**: Implement all conditional loading through the synchronous clock enable input (`CE`) via nested `if LD = '1'`, keeping clock nets pure.
3. **Use aggregate defaults**: Always specify `(others => '0')` for unassigned vector choices to avoid synthesis-time default latch generation.
4. **Isolate clock domains**: Ensure signals passing between different clock domains utilize proper synchronization registers (dual-rank flip-flops) rather than direct register transfer.
