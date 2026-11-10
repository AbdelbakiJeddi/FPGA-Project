# Chapter 10: Data Objects and Types

## 10.1 Data Object Classification and Declaration Scopes

VHDL provides four classes of data objects: **signals**, **variables**, **constants**, and **files**. In hardware synthesis, signals, variables, and constants represent the physical and logical fabric of the FPGA, while files are reserved for testbenches and simulation stimuli.

```vhdl
architecture demo_scopes of obj_demo is
    -- Signal declaration (Architecture declarative region)
    signal bus_data : std_logic_vector(15 downto 0) := (others => '0');

    -- Constant declaration (Package, architecture, or process scope)
    constant TIMEOUT_CYCLES : integer := 250;
begin
    process(CLK)
        -- Variable declaration (Strictly within sequential blocks: process, procedure, function)
        variable loop_idx : integer range 0 to 15 := 0;
    begin
        if rising_edge(CLK) then
            loop_idx := loop_idx + 1;
            bus_data(0) <= '1';
        end if;
    end process;
end architecture demo_scopes;
```

### Scope and Visibility Rules
1. **Signals (`signal`)**: Declared in architecture declarative regions (between `architecture` and `begin`) or packages. Signals have global visibility within the architecture and represent physical inter-module wiring, bus traces, or register outputs.
2. **Variables (`variable`)**: Declared exclusively in the declarative region of sequential constructs (processes, functions, procedures) before the sequential `begin`. Variables are local to their declaring block and cannot be accessed across process boundaries.
3. **Constants (`constant`)**: Declared in packages, entities, architectures, or processes. Once initialized, their values cannot be modified during simulation or synthesis. Constants map to hardwired logic levels (VCC/GND) or static parameters during logic minimization.
4. **Files (`file`)**: Used exclusively in non-synthesizable verification environments for reading and writing data streams (e.g. text file vectors).

---

## 10.2 Signals vs. Variables: Simulation Timing vs. Hardware Synthesis

Understanding the fundamental semantic differences between signals and variables is essential for preventing simulation-synthesis mismatches.

| Semantic Property | Signal (`<=`) | Variable (`:=`) |
|---|---|---|
| **Assignment Operator** | `<=` (Signal assignment) | `:=` (Variable assignment) |
| **Update Timing** | Deferred: scheduled for the end of the simulation delta cycle | Immediate: updates sequentially and synchronously within the process pass |
| **Scope of Visibility** | Architectural: global across processes | Sequential: strictly private to declaring process/subprogram |
| **Multiple Assignments** | Only the last scheduled assignment within a process pass takes effect | Each assignment immediately overwrites previous value in sequence |
| **Synthesized Hardware** | Physical wire, multiplexer net, or flip-flop output | Combinational intermediate wire OR flip-flop/latch (usage-dependent) |
| **Recommended Usage** | Inter-process communication, registers, hardware buses | Loop counters, temporary algorithmic buffers, arithmetic stages |

### 10.2.1 Delta-Cycle Simulation Timing
Signal assignments inside a process do not update immediately. The value is scheduled to update only after the process suspends at the end of the current delta cycle ($\delta$). Consequently:
- If a signal is assigned on line $N$, reading that same signal on line $N+1$ within the same process returns its **old** value (prior to entering the process).
- If multiple assignments are made to the same signal in a single process pass, only the **last** executed assignment takes effect:

```vhdl
process(CLK)
begin
    if rising_edge(CLK) then
        sig_a <= '1';
        sig_a <= '0'; -- Only '0' takes effect at end of delta cycle
    end if;
end process;
```

Variables, conversely, update instantaneously. An assignment `var_a := var_a + 1;` takes effect immediately, and any subsequent read in that process evaluates the updated value.

### 10.2.2 Hardware Synthesis Implications of Variables
A variable does not possess an inherent hardware identity; its physical synthesis depends strictly on whether its value is read before or after being assigned:
1. **Combinational Wire (Intermediate Logic)**: When a variable is assigned a value before being read within the same clock cycle/process execution, the synthesizer treats it as a temporary combinational wire or intermediate logic gate output.
2. **Sequential Storage Element (Flip-Flop or Latch)**: If a variable is read before it is assigned within a process execution pass, or if its value must persist across multiple process invocations/clock edges, the synthesizer must infer a memory element (a flip-flop in clocked processes or a latch in combinational processes) to preserve its state.

Because variables that maintain state can obscure the intended hardware structure and lead to subtle race conditions, industry best practice mandates: **Use signals for all register outputs and physical buses; restrict variables to loop iteration counters and purely local, temporary combinational calculations.**

---

## 10.3 Constrained Integer Types and Synthesis Bit Sizing

VHDL integers are 32-bit signed values by default, conforming to the range:
$$-(2^{31} - 1) \text{ to } +(2^{31} - 1) \quad (-2,147,483,647 \text{ to } +2,147,483,647)$$

### Hardware Cost of Unconstrained Integers
Declaring a signal or port as an unconstrained `integer` instructs the logic synthesizer to allocate 32 flip-flops and 32-bit wide arithmetic carry chains. In FPGA design, where flip-flop count and routing delay directly determine $F_{max}$, using unconstrained integers for small counters or state variables causes severe silicon resource bloat.

### Constrained Integers and Exact Bit Allocation
Always constrain integers using explicit range bounds:
```vhdl
signal small_cnt : integer range 0 to 15; -- Synthesizes to exactly 4 flip-flops (ceil(log2(15+1)))
type state_code is range 0 to 99;         -- Synthesizes to exactly 7 flip-flops (ceil(log2(100)))
```
The synthesis tool calculates the minimum bit width $W$ required to represent the specified range:
$$W = \lceil \log_2(\text{MAX} - \text{MIN} + 1) \rceil$$

### Strong Typing Enforcement
VHDL is strictly strongly typed. Custom integer types with identical ranges are distinct, incompatible types:
```vhdl
architecture strong_typing of type_demo is
    type apples is range 0 to 15;
    type oranges is range 0 to 15;
    signal my_apple  : apples  := 0;
    signal my_orange : oranges := 0;
begin
    -- my_apple <= my_orange; -- ILLEGAL: Synthesis/compilation error (type mismatch)
    my_apple <= apples(my_orange); -- LEGAL: Explicit type conversion
end architecture strong_typing;
```
Furthermore, synthesizers enforce static range bounds: assigning an out-of-range literal (e.g. `my_apple <= 20;`) generates an immediate compile-time error.

---

## 10.4 User-Defined Types and Array Memories (ROM/RAM)

VHDL allows the creation of composite array types to model multi-dimensional structures, memory blocks, and lookup tables.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity rom_lookup is
    port (
        addr     : in  std_logic_vector(3 downto 0);
        data_out : out std_logic_vector(7 downto 0)
    );
end entity rom_lookup;

architecture behavioral of rom_lookup is
    -- Define a 1D array type containing 16 8-bit std_logic_vector elements
    type rom_array_t is array (0 to 15) of std_logic_vector(7 downto 0);

    -- Declare a constant ROM lookup table initialized with hex values
    constant ROM_TABLE : rom_array_t := (
        0  => x"10", 1  => x"21", 2  => x"32", 3  => x"43",
        4  => x"54", 5  => x"65", 6  => x"76", 7  => x"87",
        8  => x"98", 9  => x"A9", 10 => x"BA", 11 => x"CB",
        12 => x"DC", 13 => x"ED", 14 => x"FE", 15 => x"FF"
    );
begin
    -- Asynchronous ROM lookup: convert address vector to integer index
    data_out <= ROM_TABLE(to_integer(unsigned(addr)));
end architecture behavioral;
```

### Synthesis Mapping:
- **Asynchronous Read**: If read asynchronously (combinational process without clock), the synthesizer infers distributed ROM using FPGA LUTs as function generators.
- **Synchronous Read**: If read synchronously within `rising_edge(CLK)`, the synthesizer maps the table to dedicated Block RAM (BRAM) or UltraRAM primitives.

---

## 10.5 Numeric Representation: `numeric_std` vs. "Bags of Bits"

In pure standard VHDL (IEEE 1076 / IEEE 1164), `std_logic_vector` is defined simply as an uninterpreted array of `std_logic` values—a **bag of bits**. It carries no inherent arithmetic meaning (neither signed nor unsigned, nor integer).

### 10.5.1 The Standard `ieee.numeric_std` Package
Standard arithmetic operations (`+`, `-`, `*`, `/`, `>`, `<`, etc.) require the IEEE standard library `ieee.numeric_std.all`, which defines two numeric vector types:
1. `unsigned`: Represents non-negative binary integers ($0 \text{ to } 2^N - 1$).
2. `signed`: Represents two's complement binary integers ($-2^{N-1} \text{ to } 2^{N-1} - 1$).

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity arithmetic_unit is
    port (
        in1       : in  std_logic_vector(7 downto 0);
        in2       : in  std_logic_vector(7 downto 0);
        unsig_in  : in  unsigned(7 downto 0);
        unsig_out : out unsigned(7 downto 0);
        sum_slv   : out std_logic_vector(7 downto 0);
        diff_slv  : out std_logic_vector(7 downto 0)
    );
end entity arithmetic_unit;

architecture rtl of arithmetic_unit is
begin
    -- LEGAL arithmetic operations in numeric_std:
    unsig_out <= unsig_in + 1;
    sum_slv   <= std_logic_vector(unsigned(in1) + unsigned(in2));
    diff_slv  <= std_logic_vector(signed(in1) - signed(in2));

    -- ILLEGAL: Cannot perform arithmetic directly on std_logic_vector
    -- sum_slv <= in1 + in2; -- COMPILE ERROR: '+' not defined on std_logic_vector
    -- sum_slv <= in1 + 1;   -- COMPILE ERROR: type mismatch
end architecture rtl;
```

### 10.5.2 Deprecation of Legacy Synopsys Libraries
Legacy VHDL designs frequently included:
- `ieee.std_logic_arith.all`
- `ieee.std_logic_unsigned.all`
- `ieee.std_logic_signed.all`

These packages are non-standard proprietary extensions developed by Synopsys. They overload operators indiscriminately onto `std_logic_vector`, causing namespace collisions, ambiguous function calls, and portability failures across modern EDA synthesis tools (such as Vivado, Quartus, and GHDL). **They are strictly deprecated.** Always use standard `ieee.numeric_std.all`.

---

## 10.6 The 9-Valued IEEE 1164 Logic System and Resolution

The standard type `std_logic` is an enumerated type defined in `ieee.std_logic_1164` with 9 possible states:

| Value | Meaning | Electrical Property | Synthesizable |
|---|---|---|---|
| `'U'` | Uninitialized | Simulation default before power-on | No (Simulation only) |
| `'X'` | Forcing Unknown | Multi-driver conflict or invalid logic | No (Simulation only) |
| `'0'` | Forcing Low | Driven low (Logic 0 / GND) | Yes |
| `'1'` | Forcing High | Driven high (Logic 1 / VCC) | Yes |
| `'Z'` | High Impedance | Disconnected / Floating (Tri-state) | Yes (Internal 3-state or IO buffer) |
| `'W'` | Weak Unknown | Weak pull conflict | No (Simulation only) |
| `'L'` | Weak Low | Pull-down resistor | Translates to `'0'` in synthesis |
| `'H'` | Weak High | Pull-up resistor | Translates to `'1'` in synthesis |
| `'-'` | Don't Care | Unknown / irrelevant output condition | Yes (Allows LUT optimization) |

### `std_ulogic` vs. `std_logic`
- `std_ulogic` is **unresolved**: If two concurrent drivers assign values to the same `std_ulogic` signal, the compiler generates a fatal error.
- `std_logic` is **resolved**: It incorporates a resolution function (`resolved`) that evaluates multiple concurrent drivers using a wired resolution table (e.g. `'0'` and `'Z'` resolves to `'0'`; `'0'` and `'1'` resolves to `'X'`).

In synthesis, `'Z'` is used to infer tri-state buffers at FPGA pin boundaries (IOBs). Modern FPGAs have eliminated internal tri-state buses, so internal `'Z'` assignments are automatically synthesized into multiplexers.

---

## 10.7 Practical Hardware Example: Clock Divider and Variable Usage

The following entity divides an input clock by 64 (toggling every 32 cycles) using an integer range and a process-local variable.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity clk_div is
    port (
        clk    : in  std_logic;
        div_en : in  std_logic;
        sclk   : out std_logic
    );
end entity clk_div;

architecture behavioral of clk_div is
    -- Constrained integer range 0 to 100 maps to 7-bit register in synthesis (2^7 = 128)
    type my_count is range 0 to 100;
    constant MAX_COUNT : my_count := 31; -- 32 cycles high/low = divide by 64
    signal tmp_sclk : std_logic := '0';
begin
    my_div : process(clk, div_en)
        variable div_count : my_count := 0;
    begin
        if div_en = '0' then
            div_count := 0;
            tmp_sclk  <= '0';
        elsif rising_edge(clk) then
            if div_count = MAX_COUNT then
                tmp_sclk  <= not tmp_sclk;
                div_count := 0;
            else
                div_count := div_count + 1;
            end if;
        end if;
    end process my_div;

    sclk <= tmp_sclk;
end architecture behavioral;
```

### FPGA Clocking Architecture Caveat:
While behavioral clock dividers using logic registers are common for low-frequency indicator LEDs or UART baud generators, **they must never be used as clock sources for high-speed synchronous logic**. Logic-generated ripple clocks suffer from significant clock skew and jitter, and bypass dedicated low-skew clock distribution networks. High-speed, phase-aligned, or frequency-synthesized clocks in modern FPGAs must always be instantiated using dedicated Clock Management Blocks (MMCM, PLL, or DCM primitives).
