# Chapter 2: VHDL Invariants

## 2.1 Case Sensitivity
VHDL exhibits complete case insensitivity across all language tokens, including reserved keywords, user identifiers, port names, signal names, and type definitions. The compiler treats lowercase, uppercase, and mixed-case tokens identically during lexical analysis. 

The following complete entity and architecture illustrates case insensitivity:

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity case_insensitivity_demo is
    port (
        a_in, b_in : in  std_logic;
        dout1      : out std_logic;
        dout2      : out std_logic
    );
end entity case_insensitivity_demo;

architecture rtl of case_insensitivity_demo is
begin
    -- Case insensitivity allows identical evaluation of different casing
    dout1 <= a_in and b_in;
    DOUT2 <= A_IN AND B_IN;
end architecture rtl;
```

While VHDL compilers support case insensitivity, professional FPGA engineering teams establish strict casing rules (e.g., lowercase for signals and architectures, uppercase for constants and generics) to maintain readability across large hardware designs.

## 2.2 White Space
VHDL tokenization treats spaces, horizontal tabs, carriage returns, and line feeds interchangeably as whitespace delimiters. A single statement may span arbitrarily across multiple lines without requiring continuation characters:

```text
-- Unconstrained line-wrapping supported by VHDL tokenization
out_sig <= (data_bus_a or data_bus_b) 
           and enable_flag;
```

Indentation carries no semantic meaning for synthesis or compilation, but 2-space or 4-space hierarchical indentation is universally applied to delimit nested blocks.

## 2.3 Comments
- Single-line comments are designated by two consecutive hyphens (`--`). The compiler ignores all subsequent text through the end of that physical line.
- Standard VHDL has **no multi-line block comment syntax** (C-style `/* ... */` is illegal and causes syntax errors). Multi-line comment blocks require leading `--` markers on every line.
- In production RTL, comments should convey engineering rationale—such as clock domain assumptions, pipeline stage latency, and handshake protocols—rather than trivial restatements of code syntax.

## 2.4 Parentheses
VHDL defines explicit operator precedence classes:
1. Highest precedence: `**`, `abs`, `not`
2. Multiplying operators: `*`, `/`, `mod`, `rem`
3. Sign operators: `+`, `-`
4. Adding operators: `+`, `-`, `&`
5. Shift operators: `sll`, `srl`, `sla`, `sra`, `rol`, `ror`
6. Relational operators: `=`, `/=`, `<`, `<=`, `>`, `>=`
7. Logical operators: `and`, `or`, `nand`, `nor`, `xor`, `xnor`

### Critical Precedence Invariant: Logical Operators
Unlike C-derived languages where logical AND takes precedence over logical OR, all VHDL binary logical operators (`and`, `or`, `nand`, `nor`, `xor`, `xnor`) share the **same precedence level** and evaluate strictly left-to-right. Mixing distinct logical operators in an expression without explicit parentheses is a **fatal compilation error**:

```text
-- ILLEGAL: Causes VHDL compilation error due to operator ambiguity
y <= a and b or c;

-- LEGAL: Explicit parenthetical grouping resolves operator evaluation
y <= (a and b) or c;
```

Liberal use of explicit parentheses eliminates Boolean ambiguity and guarantees that synthesized logic gate topologies map precisely to intended Boolean trees.

## 2.5 VHDL Statements and Terminators
Every VHDL statement must terminate with a semicolon (`;`). Semicolons in VHDL are statement terminators rather than separators.
- **Common Compiler Pitfall**: Superfluous semicolons cause syntax errors. Specifically, placing a trailing semicolon after the final port item in an entity declaration port list, or after a generic parameter list before the closing parenthesis, causes immediate compilation rejection.

## 2.6 if, case and loop Statements
Sequential control constructs inside processes enforce strict syntax requirements:

### The `if` Statement
- Every `if` condition must be terminated by the keyword `then`.
- Intermediate branches must use the exact keyword **`elsif`** (NEVER `else if` or `elseif`). Writing `else if` creates an unclosed nested `if` structure requiring an additional `end if;`.
- Must terminate with `end if;`.

### The `case` Statement
- Syntax: `case <expression> is when <choice> => <statements>; ... end case;`.
- Requires mutually exclusive and exhaustive choices. Any unhandled evaluation state in hardware models will cause compiler rejection or infer unintended transparent latches.

### The `loop` Statement
- Forms include basic `loop`, `for <idx> in <range> loop`, and `while <cond> loop`.
- Must terminate with `end loop;`.
- **Synthesis Constraint**: Synthesis tools only support loops whose range bounds are static constants known at compile time, unrolling the iterations spatially into replicated physical hardware logic.

## 2.7 Identifiers
VHDL enforces strict lexical rules on user-defined identifiers (signals, constants, variables, entities, architectures):
1. Allowed characters: Letters `[A-Za-z]`, decimal digits `[0-9]`, and the underscore character (`_`).
2. Must begin with an alphabetic character (e.g., `3bus_val` is illegal).
3. Must **not end with an underscore** (e.g., `data_out_` is illegal).
4. Must **not contain consecutive underscores** (e.g., `clk__in` is illegal).
5. Cannot be a reserved VHDL keyword.

## 2.8 Reserved Words
VHDL reserves key language tokens that cannot serve as user identifiers. Key examples include:
- Structural & Design Units: `entity`, `architecture`, `is`, `begin`, `end`, `port`, `generic`, `component`, `package`, `configuration`.
- Data Objects & Scope: `signal`, `variable`, `constant`, `type`, `subtype`, `range`, `downto`, `to`.
- Port Modes: `in`, `out`, `inout`, `buffer`.
- Control Structures: `process`, `if`, `then`, `elsif`, `else`, `case`, `when`, `with`, `select`, `loop`, `for`, `while`, `next`, `exit`, `wait`.
- Predefined Operators: `and`, `or`, `nand`, `nor`, `xor`, `xnor`, `not`, `rem`, `mod`.

## 2.9 VHDL Coding Style
Professional VHDL design styles enforce deterministic hardware synthesis:
- Descriptive, consistent snake_case identifiers (`fifo_wr_en`, `rx_byte_valid`).
- Explicit clock domain and active-low naming conventions (e.g., `rst_n` or `sys_rst_b`).
- Clean visual alignment of port modes and types for module maintainability.
- Elimination of dead logic, redundant assignments, and ambiguous operator cascades.

## Synthesizable Architectural Example
The following complete, valid VHDL module illustrates lexical invariants: parenthesized mixed Boolean expressions, valid identifiers, `elsif` branching, and comment formatting.

```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity invariant_decoder is
    port (
        enable      : in  std_logic;
        mode_select : in  std_logic_vector(1 downto 0);
        data_in_a   : in  std_logic;
        data_in_b   : in  std_logic;
        fault_flag  : in  std_logic;
        valid_out   : out std_logic;
        status_code : out std_logic_vector(1 downto 0)
    );
end entity invariant_decoder;

architecture rtl of invariant_decoder is
begin
    -- Parentheses explicitly group mixed boolean operators with equal precedence
    valid_out <= enable and (not fault_flag) and ((data_in_a and data_in_b) or (mode_select(0) xor mode_select(1)));

    -- Combinational process demonstrating strict elsif control invariant
    decode_proc : process(enable, mode_select)
    begin
        if enable = '0' then
            status_code <= "00";
        elsif mode_select = "01" then
            status_code <= "01";
        elsif mode_select = "10" then
            status_code <= "10";
        else
            status_code <= "11";
        end if;
    end process decode_proc;
end architecture rtl;
```
