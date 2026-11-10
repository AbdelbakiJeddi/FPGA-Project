# Chapter 8: Structural Modeling In VHDL

## Structural Modeling & Hierarchical Design
Structural modeling implements complex digital systems through hierarchical netlisting, interconnecting pre-existing design units (entities/architectures) analogous to instantiating classes or calling functions in modular software engineering:
- **Clean Abstraction**: Decouples the external pin interface (`entity`) from the underlying structural interconnect (`architecture`).
- **Scalability and Reuse**: Encapsulates verified low-level subsystems (ALUs, registers, communication transceivers) into reusable black boxes, eliminating code duplication across FPGA projects.
- **Hierarchical Layout**: Allows complex FPGA systems to be partitioned across multiple specialized files and logical libraries.

---

## 8.1 Modularity with Components
In VHDL, modularity is realized through **components**. A component serves as an interface prototype, informing the parent architecture of the ports and generics of a lower-level subsystem.

### The 4-Step Structural Implementation Workflow
Implementing a structural VHDL design follows a strict, repeatable 4-step engineering procedure:

1. **Step 1: Top-Level Entity Declaration**  
   Define the physical pins crossing the top-level boundary of the design unit.
2. **Step 2: Component Declaration**  
   Inside the architecture declarative region (between `architecture ... is` and `begin`), declare component prototypes matching the interface of each child entity.
3. **Step 3: Intermediate Signal Declaration**  
   Declare internal interconnect wires (in the architecture declarative region) that link component pins together. Intermediate signals have data types (such as `std_logic` or `std_logic_vector`), but **never possess mode specifiers** (`in`/`out`).
4. **Step 4: Component Instantiation and Port Mapping**  
   In the architecture statement body (between `begin` and `end architecture`), instantiate labeled component instances and bind their ports to top-level pins or internal intermediate nets using `port map`.

---

## Component Declaration vs Component Instantiation

### Component Declaration
Declared once in the architecture declarative region before `begin`:

```text
component generic_reg is
    generic (
        DATA_WIDTH : positive := 8
    );
    port (
        clk      : in  std_logic;
        clr      : in  std_logic;
        en       : in  std_logic;
        data_in  : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        data_out : out std_logic_vector(DATA_WIDTH - 1 downto 0)
    );
end component generic_reg;
```
The component prototype mirrors the target entity's generic and port list, allowing the compiler to perform type and width validation during elaboration.

### Component Instantiation
Created after `begin` in the architecture concurrent statement body:

```text
u_reg1: generic_reg
    generic map (
        DATA_WIDTH => 16
    )
    port map (
        clk      => sys_clk,
        clr      => sys_clr,
        en       => reg1_en,
        data_in  => data_bus,
        data_out => pipeline_net
    );
```
Each instance must have a unique **instance label** (e.g., `u_reg1`). Multiple physical instances of the same component can be instantiated within a single architecture.

---

## Port Map Syntax: Named vs Positional Association

### Named (Direct) Association
Associates ports explicitly using the formal-to-actual operator `=>`:

```text
u1: big_xnor port map (
    A => sig_a,
    B => sig_b,
    F => net_f
);
```
- **LHS (`formal`)**: The internal port name as defined in the component declaration.
- **RHS (`actual`)**: The external signal or top-level pin in the parent architecture.
- **Advantages**: Order-independent, self-documenting, resilient against port reordering in child entities, and completely unambiguous. **Mandatory in production RTL design**.

### Positional (Implied) Association
Associates signals strictly by their sequential order in the port list:

```text
u1: big_xnor port map (sig_a, sig_b, net_f);
```
- **Critical Hazard**: If a developer changes the port order in the child entity (e.g., swapping `A` and `B` or control pins), positional mapping silently binds incorrect signals if types match, producing catastrophic logic defects without compiler warnings. Positional mapping is strongly discouraged.

### Identifier Scope and Disambiguation
When an internal component port shares the identical identifier as a parent architecture signal (e.g., `clk` or `reset`), no name collision occurs:

```text
u_core: cpu_core port map (
    clk   => clk,    -- LHS is component port; RHS is architecture net
    reset => reset
);
```
The VHDL compiler isolates namespaces: the LHS strictly references the child component interface, while the RHS references the parent architecture signal scope.

---

## 8.2 Generic and Generic Map

### Parameterized Hardware Design
Generics allow entities to be parameterized with scalable attributes such as bus widths, FIFO depths, address ranges, or timing constants:

- **Entity Generic Clause**: Declared in the entity header before the port list:
  ```text
  entity fifo_buffer is
      generic (
          ADDR_WIDTH : positive := 4;
          DATA_WIDTH : positive := 8
      );
      port ( ... );
  end entity fifo_buffer;
  ```
- **Generic Map Clause**: In structural instantiations, `generic map` overrides default values for specific instances:
  ```text
  u_fifo: fifo_buffer
      generic map (
          ADDR_WIDTH => 8,
          DATA_WIDTH => 32
      )
      port map ( ... );
  ```

### Parameter Propagation and Dynamic Array Attributes
Generics defined at the top-level entity can be propagated downward throughout the structural hierarchy, configuring deep sub-modules dynamically. Inside parameterized modules, use predefined VHDL array attributes (`'range`, `'length`, `'high`, `'low`) to write generic-agnostic behavioral logic:

```text
for i in data_in'range loop
    parity_var := parity_var xor data_in(i);
end loop;
```

---

## 8.3 Important Points: Compilation Order & Silicon Primitives

### Compilation-Order Dependencies
VHDL enforces strict **bottom-up compilation**:
1. Lower-level packages and child entities must be compiled into the working library (`work`) **before** any architecture instantiating them can be analyzed.
2. If a child entity's port list is modified, all parent architectures instantiating that component must be recompiled.

### FPGA Vendor Macrocell / Silicon Primitive Instantiation
Structural modeling allows direct instantiation of vendor-specific dedicated silicon primitives (e.g., AMD Xilinx UltraScale+ or Intel Stratix primitives) without relying on synthesis inference:

```text
library UNISIM;
use UNISIM.VComponents.all;

-- Direct instantiation of dedicated global clock buffer primitive
u_bufg: BUFG
    port map (
        I => raw_clk_pin,
        O => sys_clk_global
    );
```
- **Advantages**: Guarantees utilization of specialized silicon features (dedicated clock routing, DSP multiply-accumulators, block RAMs, fast carry lookaheads, transceivers).
- **Trade-off**: Hardwires design code to a specific FPGA vendor silicon architecture, sacrificing cross-vendor portability.

---

## Synthesizable Architectural Examples

### Example 1: Parameterized Child Module (Generic N-bit Register with Enable)
```vhdl
library ieee;
use ieee.std_logic_1164.all;

-- Child Module: Parameterized N-bit Register with Enable and Synchronous Clear
entity generic_reg is
    generic (
        DATA_WIDTH : positive := 8
    );
    port (
        clk      : in  std_logic;
        clr      : in  std_logic;
        en       : in  std_logic;
        data_in  : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
        data_out : out std_logic_vector(DATA_WIDTH - 1 downto 0)
    );
end entity generic_reg;

architecture rtl of generic_reg is
begin
    reg_proc: process(clk) is
    begin
        if rising_edge(clk) then
            if (clr = '1') then
                data_out <= (others => '0');
            elsif (en = '1') then
                data_out <= data_in;
            end if;
        end if;
    end process reg_proc;
end architecture rtl;
```

### Example 2: Top-Level Structural Architecture (Named Port Mapping & Generic Overrides)
```vhdl
library ieee;
use ieee.std_logic_1164.all;

-- Top-Level Module: Structural Composition of Two Pipelined Registers
entity structural_top is
    generic (
        BUS_WIDTH : positive := 16
    );
    port (
        sys_clk   : in  std_logic;
        sys_clr   : in  std_logic;
        stage1_en : in  std_logic;
        stage2_en : in  std_logic;
        raw_in    : in  std_logic_vector(BUS_WIDTH - 1 downto 0);
        pipe_out  : out std_logic_vector(BUS_WIDTH - 1 downto 0)
    );
end entity structural_top;

architecture structural of structural_top is
    -- Step 2: Component Declaration
    component generic_reg is
        generic (
            DATA_WIDTH : positive := 8
        );
        port (
            clk      : in  std_logic;
            clr      : in  std_logic;
            en       : in  std_logic;
            data_in  : in  std_logic_vector(DATA_WIDTH - 1 downto 0);
            data_out : out std_logic_vector(DATA_WIDTH - 1 downto 0)
        );
    end component generic_reg;

    -- Step 3: Intermediate Signal Declaration for internal interconnection
    signal mid_pipeline_bus : std_logic_vector(BUS_WIDTH - 1 downto 0);
begin
    -- Step 4: Component Instantiations with generic map and named port mapping

    -- Stage 1 Instance
    u_stage1_reg: generic_reg
        generic map (
            DATA_WIDTH => BUS_WIDTH
        )
        port map (
            clk      => sys_clk,
            clr      => sys_clr,
            en       => stage1_en,
            data_in  => raw_in,
            data_out => mid_pipeline_bus
        );

    -- Stage 2 Instance
    u_stage2_reg: generic_reg
        generic map (
            DATA_WIDTH => BUS_WIDTH
        )
        port map (
            clk      => sys_clk,
            clr      => sys_clr,
            en       => stage2_en,
            data_in  => mid_pipeline_bus,
            data_out => pipe_out
        );

end architecture structural;
```
