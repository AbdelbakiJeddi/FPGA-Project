# Chapter 6: VHDL Operators & Storage Induction

## VHDL Operators Overview
VHDL provides a comprehensive suite of operators spanning logical, arithmetic, relational, shift, and concatenation operations. In digital hardware design, these operators synthesize directly to physical combinatorial logic (LUTs, carry chains, and DSP slices) or routing networks.

---

## 6.1 Logical Operators
VHDL defines seven bitwise logical operators: `and`, `or`, `nand`, `nor`, `xor`, `xnor`, and `not`:
- **Operands and Types**: Defined for types `std_logic`, `std_logic_vector`, `bit`, `bit_vector`, and `boolean`.
- **Precedence Rule**: All binary logical operators share the **exact same precedence level**. Expressions are evaluated strictly from left to right.
- **Mandatory Parenthesization**: Unlike languages with implicit operator hierarchies (e.g., C where `&&` has priority over `||`), mixing different logical operators without parentheses (such as `A and B or C`) is illegal in VHDL and triggers compilation errors. Always write `(A and B) or C`.

---

## 6.2 Relational Operators
Relational operators test equality and relative magnitude, returning a `boolean` result (`true` or `false`):
- **Operators**: `=` (equality), `/=` (inequality), `<` (less than), `<=` (less than or equal), `>` (greater than), `>=` (greater than or equal).
- **Type Compatibility**: Both operands must belong to the same base type. Comparing an `integer` with a `std_logic_vector` directly is a strict compilation error; operands must be explicitly converted using `ieee.numeric_std` types (`unsigned`, `signed`, `to_integer()`).
- **Hardware Mapping**: Equality tests (`=`, `/=`) synthesize to multi-input XOR/XNOR trees; magnitude comparisons (`<`, `<=`, `>`, `>=`) infer dedicated fast carry-lookahead comparator chains in FPGA slices.

---

## 6.3 Shift Operators & Rotate Operations
Defined in `ieee.numeric_std` (for `unsigned` and `signed`) and `ieee.numeric_bit`:

| Operator | Operation Name | Description | Hardware Synthesis Effect |
| :--- | :--- | :--- | :--- |
| `sll` | Shift Left Logical | Shifts bits left, fills vacated LSBs with `'0'` | Direct bus rewiring (no gates) for constant shifts; barrel shifter for variable shifts |
| `srl` | Shift Right Logical | Shifts bits right, fills vacated MSBs with `'0'` | Constant shift = bus rewiring; variable = barrel shifter |
| `sla` | Shift Left Arithmetic | Shifts left, replicates the existing LSB | Replicates bit 0 into vacated positions |
| `sra` | Shift Right Arithmetic | Shifts right, replicates MSB (sign bit) | Preserves sign of signed two's complement integers |
| `rol` | Rotate Left | Circular left shift, MSB wraps around to LSB | Bit permutation / routing network |
| `ror` | Rotate Right | Circular right shift, LSB wraps around to MSB | Bit permutation / routing network |

*Design Practice*: For constant bit shifts (e.g., multiplying or dividing by powers of 2), explicit slice concatenation (e.g., `A(5 downto 0) & "00"`) is widely preferred in RTL design for absolute readability and zero-gate routing efficiency.

---

## 6.4 Other Operators & Precedence Table
VHDL groups operators into seven precedence levels listed below in descending order:

| Precedence Tier | Operator Category      | Operators                                        | Evaluation Order                     |
| :-------------: | :--------------------- | :----------------------------------------------- | :----------------------------------- |
| **1 (Highest)** | Exponential, Absolute  | `**`, `abs`                                      | Left to right                        |
|      **2**      | Logical                | `not`, `and`, `or`, `nand`, `nor`, `xor`, `xnor` | Left to right (no internal priority) |
|      **3**      | Multiplying            | `*`, `/`, `mod`, `rem`                           | Left to right                        |
|      **4**      | Sign / Unary           | `+`, `-`                                         | Unary sign prefix                    |
|      **5**      | Addition / Subtraction | `+`, `-`                                         | Left to right                        |
|      **6**      | Concatenation & Shift  | `&`, `sll`, `srl`, `sla`, `sra`, `rol`, `ror`    | Left to right                        |
| **7 (Lowest)**  | Relational             | `=`, `/=`, `<`, `<=`, `>`, `>=`                  | Left to right                        |

*Golden Precedence Rule*: **Never rely on implicit operator precedence in production RTL**. Cryptic precedence leads to simulation errors and faulty hardware synthesis. Always use explicit parentheses to enforce intended evaluation order.

---

## 6.5 Concatenation Operator
The concatenation operator (`&`) combines scalar elements and vectors into composite arrays:
- **Vector Construction**: Forms wider buses from narrower slices: `byte_bus <= msb_nibble & lsb_nibble;`.
- **Sign Extension**: `extended <= (15 downto 8 => val(7)) & val;` or `ext_val <= (7 downto 0 => '0') & d_in;`.
- Operands can be scalar bits or multi-bit arrays of the same base element type.

---

## 6.6 Modulus and Remainder Operators
VHDL distinguishes between the integer remainder (`rem`) and modulus (`mod`):
- **Remainder (`rem`)**: Satisfies `A = (A / B) * B + (A rem B)`. The result **adopts the algebraic sign of the dividend `A`**.
  - Example: `8 rem 5 = 3`; `(-8) rem 5 = -3`.
- **Modulus (`mod`)**: Satisfies `A = B * N + (A mod B)`. The result **adopts the algebraic sign of the divisor `B`**.
  - Example: `8 mod 5 = 3`; `(-8) mod 5 = 2`.
- **FPGA Synthesis Warning**: Arbitrary integer division, `rem`, and `mod` with non-power-of-two constants infer massive, timing-critical combinational divider trees or multi-cycle DSP macrocells. Power-of-two modular operations should always be implemented using bitmasking or bit-slicing (e.g., `val and "0111"` instead of `val mod 8`).

---

## 6.7 Review of Key Operational Rules
1. **Parentheses are mandatory**: Eliminate ambiguity in mixed logical expressions.
2. **Bit-width preservation**: VHDL enforces strict typing; assignment between vectors of differing widths or incompatible types is forbidden.
3. **Arithmetic synthesis**: High-level arithmetic (`+`, `-`, `*`) maps directly to dedicated FPGA DSP slices and carry chains when targeting `ieee.numeric_std`.

---

## 6.8 Using VHDL for Sequential Circuits
Sequential circuits possess internal memory where the next output depends on both current inputs and present stored state. In modern FPGA synchronous design:
- Digital systems are driven by periodic clock networks.
- State storage elements (flip-flops, registers, BRAM) sample data synchronously on active clock transitions.
- Storage isolation decouples combinational propagation delays between pipeline stages, establishing deterministic timing closure ($T_{clk} \ge T_{cq} + T_{comb} + T_{setup}$).

---

## 6.9 Simple Storage Elements & Storage Induction

### Storage Elements Induction via Incomplete Specification
A fundamental principle of VHDL is that **the language contains no explicit primitive keyword for a flip-flop or register**. Instead, hardware memory is **induced by incomplete specification**:
- If a signal assignment condition is evaluated and no alternative condition (`else`) specifies an output value, the simulation and synthesis engines deduce that the output must **preserve its prior value**.
- In combinational processes, this mechanism unintentionally infers level-sensitive transparent latches.
- Inside a clock-monitored process, this mechanism intentionally infers edge-triggered D flip-flops, holding state indefinitely until the next active clock event.

### Clock Edge Detection Idioms
Two syntax idioms detect active clock transitions in VHDL:

1. **Standard IEEE Function — `rising_edge(CLK)`**:
   ```vhdl
   if rising_edge(CLK) then
       Q <= D;
   end if;
   ```
   *Technical Semantics*: Defined in `ieee.std_logic_1164`. Verifies that `CLK` underwent an event AND transitioned specifically from `'0'` or `'L'` to `'1'`. This filters out false simulation transitions from uninitialized (`'U'`) or unknown (`'X'`) states.

2. **Pre-1993 Attribute Idiom — `CLK'event and CLK = '1'`**:
   ```vhdl
   if (CLK'event and CLK = '1') then
       Q <= D;
   end if;
   ```
   *Technical Semantics*: `CLK'event` returns `true` on any transition of `CLK`. If `CLK` transitions from `'X'` to `'1'` during simulation startup, this condition evaluates to `true`, occasionally causing transient initialization artifacts.

*Best Practice*: Always use `rising_edge(CLK)` and `falling_edge(CLK)` in modern RTL code.

---

## 6.10 Synchronous vs Asynchronous Reset

| Feature | Synchronous Reset | Asynchronous Reset |
| :--- | :--- | :--- |
| **Sensitivity List** | Clock only: `process(CLK)` | Clock and Reset: `process(CLK, RST)` |
| **Evaluation Timing** | Evaluated **inside** the clock-edge block | Evaluated **before** the clock-edge block |
| **FPGA Mapping** | Dedicated synchronous set/reset pin (`FDRE` in Xilinx) | Dedicated asynchronous clear pin (`FDCE` in Xilinx) |
| **Noise & Glitch Immunity** | Immune to combinational input glitches; reset occurs only on clock edge | Susceptible to glitches on reset lines; requires reset synchronizer on release |
| **Timing Closure** | Reset path is timed as standard synchronous data path | De-assertion must meet recovery and removal timing constraints |

### Synchronous Reset Coding Template
```text
process(CLK) is
begin
    if rising_edge(CLK) then
        if (RST = '1') then
            Q <= '0';
        else
            Q <= D;
        end if;
    end if;
end process;
```

### Asynchronous Reset Coding Template
```text
process(CLK, RST) is
begin
    if (RST = '1') then
        Q <= '0';  -- Asynchronous assertion takes immediate priority
    elsif rising_edge(CLK) then
        Q <= D;
    end if;
end process;
```
*Synthesis Rule*: In an asynchronous reset process, **no other signal or condition may be checked in the reset branch**. Only the reset signal itself may appear in the leading `if`.

---

## 6.11 Entity Port Limitations & Intermediate Signal Idiom
In VHDL-93 and VHDL-2002, ports declared with mode `out` are strictly write-only:
- **The Output Read Limitation**: Attempting to read an `out` port on the RHS of an expression (e.g., toggling an output: `Q <= not Q;`) triggers a fatal compiler syntax error: `cannot read output port "Q"`.
- **Why `buffer` Mode is Prohibited**: VHDL provides the `buffer` port mode to allow reading back driven outputs. However, `buffer` mode imposes severe structural constraints: any higher-level hierarchical port connected to a `buffer` port must also be declared as `buffer`. This cascades across the entire hierarchy, breaking modularity.
- **The Standard Intermediate Signal Idiom**: Declare an internal intermediate signal in the architecture declarative region, perform all internal read and write operations on that signal, and concurrently drive the output port:

```text
architecture rtl of toggle_circuit is
    signal q_reg : std_logic;
begin
    process(CLK, RST) is
    begin
        if (RST = '1') then
            q_reg <= '0';
        elsif rising_edge(CLK) then
            if (TOGGLE = '1') then
                q_reg <= not q_reg;  -- Reading internal signal is 100% legal
            end if;
        end if;
    end process;

    Q <= q_reg;  -- Continuous drive to external output pin
end architecture rtl;
```

---

## Synthesizable Architectural Examples

### Example 1: D Flip-Flop with Asynchronous Reset, Synchronous Clock Enable, and Intermediate Feedback
```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity d_ff_async_rst_en is
    port (
        clk     : in  std_logic;
        rst_n   : in  std_logic;  -- Asynchronous active-low reset
        en      : in  std_logic;  -- Synchronous clock enable
        d_in    : in  std_logic;
        q_out   : out std_logic;
        q_not   : out std_logic
    );
end entity d_ff_async_rst_en;

architecture rtl of d_ff_async_rst_en is
    -- Intermediate signal for output feedback and RHS reading
    signal q_reg : std_logic;
begin
    -- Asynchronous reset + synchronous clock enable process
    ff_proc: process(clk, rst_n) is
    begin
        if (rst_n = '0') then
            q_reg <= '0';
        elsif rising_edge(clk) then
            if (en = '1') then
                q_reg <= d_in;
            end if;
        end if;
    end process ff_proc;

    -- Concurrent driving of external output ports from internal intermediate signal
    q_out <= q_reg;
    q_not <= not q_reg;
end architecture rtl;
```

### Example 2: Universal Shift and Rotate Register (Demonstrating Shift Operators & Synch Control)
```vhdl
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity universal_shifter is
    port (
        clk      : in  std_logic;
        rst      : in  std_logic;
        mode_sel : in  std_logic_vector(1 downto 0);
        d_in     : in  std_logic_vector(7 downto 0);
        d_out    : out std_logic_vector(7 downto 0)
    );
end entity universal_shifter;

architecture rtl of universal_shifter is
    signal shift_reg : unsigned(7 downto 0);
begin
    shift_proc: process(clk, rst) is
    begin
        if (rst = '1') then
            shift_reg <= (others => '0');
        elsif rising_edge(clk) then
            case mode_sel is
                when "00" =>  -- Parallel load
                    shift_reg <= unsigned(d_in);
                when "01" =>  -- Shift Left Logical (sll)
                    shift_reg <= shift_reg sll 1;
                when "10" =>  -- Shift Right Arithmetic (sra, sign-preserving)
                    -- Replicate MSB into vacant position for signed arithmetic shift
                    shift_reg <= shift_reg(7) & shift_reg(7 downto 1);
                when others =>  -- Rotate Left (rol)
                    shift_reg <= shift_reg rol 1;
            end case;
        end if;
    end process shift_proc;

    d_out <= std_logic_vector(shift_reg);
end architecture rtl;
```
