# Chapter 12: Standard Digital Circuits in VHDL

## 12.1 Overview of Standard Building Block Templates

Modern digital FPGA architectures are built from a small set of canonical building blocks: registers, multiplexers, decoders, counters, shift registers, and comparators. Writing standard, idiomatic VHDL for these blocks ensures that modern synthesis tools map them directly to dedicated silicon resources—such as Slice Flip-Flops (FDRE/FDPE), Look-Up Tables (LUTs), dedicated carry chains (CARRY4/CARRY8), and shift register primitives (SRL16E/SRL32E).

This chapter presents complete, verified VHDL templates for each standard circuit, accompanied by hardware mapping analysis and explicit corrections for common textbook errata.

---

## 12.2 RET D Flip-Flop (Rising-Edge-Triggered)

The fundamental atomic storage element in synchronous digital logic.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity dff_ret is
    port (
        CLK : in  std_logic;
        D   : in  std_logic;
        Q   : out std_logic
    );
end entity dff_ret;

architecture behavioral of dff_ret is
begin
    process(CLK)
    begin
        if rising_edge(CLK) then
            Q <= D;
        end if;
    end process;
end architecture behavioral;
```

### Hardware Mapping:
- Synthesizes to a single D flip-flop (FDRE in Xilinx, DFFE in Intel).
- `D` connects to the flip-flop D input pin; `CLK` routes via global clock networks (BUFG).

---

## 12.3 FET D Flip-Flop with Active-Low Asynchronous Preset

A falling-edge-triggered flip-flop with an overriding active-low asynchronous preset (`S = '0'`).

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity dff_fet_preset is
    port (
        CLK : in  std_logic;
        S   : in  std_logic; -- Active-low asynchronous preset
        D   : in  std_logic;
        Q   : out std_logic
    );
end entity dff_fet_preset;

architecture behavioral of dff_fet_preset is
begin
    process(CLK, S)
    begin
        if S = '0' then
            Q <= '1'; -- Asynchronous preset has highest priority
        elsif falling_edge(CLK) then
            Q <= D;
        end if;
    end process;
end architecture behavioral;
```

### Hardware Mapping & Design Rules:
- Both `CLK` and asynchronous `S` appear in the process sensitivity list.
- Maps to an asynchronous preset flip-flop (FDPE).
- Because `S` is checked outside the clock edge condition, assertion of `S = '0'` immediately forces `Q <= '1'` independently of `CLK`.

---

## 12.4 8-Bit Register with Synchronous Load Enable

Multi-bit vector storage with conditional clock enable (`LD`).

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity reg8_en is
    port (
        CLK   : in  std_logic;
        LD    : in  std_logic;
        D_IN  : in  std_logic_vector(7 downto 0);
        D_OUT : out std_logic_vector(7 downto 0)
    );
end entity reg8_en;

architecture behavioral of reg8_en is
begin
    process(CLK)
    begin
        if rising_edge(CLK) then
            if LD = '1' then
                D_OUT <= D_IN;
            end if;
        end if;
    end process;
end architecture behavioral;
```

### Hardware Mapping:
- Synthesizes to 8 parallel D flip-flops.
- The scalar `LD` net directly connects to the dedicated Clock Enable (`CE`) input pin of all 8 flip-flops. No external logic gates are inserted into the clock path.

---

## 12.5 Synchronous 8-Bit Up/Down Counter with Async Reset and Sync Load

A versatile counter incorporating asynchronous clear, synchronous parallel load, and directional counting using standard `ieee.numeric_std.all`.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity count_8b is
    port (
        CLK   : in  std_logic;
        RESET : in  std_logic; -- Active-high asynchronous reset
        LD    : in  std_logic; -- Synchronous parallel load
        UP    : in  std_logic; -- 1 = count up, 0 = count down
        DIN   : in  std_logic_vector(7 downto 0);
        COUNT : out std_logic_vector(7 downto 0)
    );
end entity count_8b;

architecture behavioral of count_8b is
    signal t_cnt : unsigned(7 downto 0);
begin
    process(CLK, RESET)
    begin
        if RESET = '1' then
            t_cnt <= (others => '0');
        elsif rising_edge(CLK) then
            if LD = '1' then
                t_cnt <= unsigned(DIN);
            elsif UP = '1' then
                t_cnt <= t_cnt + 1;
            else
                t_cnt <= t_cnt - 1;
            end if;
        end if;
    end process;

    COUNT <= std_logic_vector(t_cnt);
end architecture behavioral;
```

### Hardware Mapping:
- Synthesizes to 8 flip-flops with dedicated fast carry chains (CARRY4/CARRY8) to achieve single-cycle increment/decrement up to hundreds of megahertz.

---

## 12.6 Shift Register with Synchronous Parallel Load

Unidirectional serial shift register with synchronous parallel load capability.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity shift_reg_8b is
    port (
        CLK         : in  std_logic;
        D_IN        : in  std_logic; -- Serial shift input
        P_LOAD      : in  std_logic; -- Active-high synchronous parallel load
        P_LOAD_DATA : in  std_logic_vector(7 downto 0);
        D_OUT       : out std_logic  -- Serial shift output
    );
end entity shift_reg_8b;

architecture behavioral of shift_reg_8b is
    signal s_reg : std_logic_vector(7 downto 0);
begin
    process(CLK)
    begin
        if rising_edge(CLK) then
            if P_LOAD = '1' then
                s_reg <= P_LOAD_DATA;
            else
                s_reg <= s_reg(6 downto 0) & D_IN; -- Bit concatenation shift
            end if;
        end if;
    end process;

    -- Corrected assignment: concurrent and external to clocked process
    D_OUT <= s_reg(7);
end architecture behavioral;
```

### Critical Textbook Erratum Analysis:
In the original text (Listing 12.5), the assignment `D_OUT <= REG_TMP(7);` was placed inside `process(CLK)` but **outside** the `if rising_edge(CLK)` block:

```text
-- TEXTBOOK ERRATUM (Listing 12.5):
process (CLK)
begin
    if (rising_edge(CLK)) then
        s_reg <= ...;
    end if;
    D_OUT <= REG_TMP(7); -- MALFORMED: Combinational assignment in clocked process!
end process;
```

#### Why this fails:
1. `D_OUT` is evaluated whenever `CLK` toggles (both rising and falling edges) regardless of the clock edge condition.
2. In simulation, `D_OUT` updates on falling edges as well as rising edges.
3. In synthesis, tools either reject this construct or infer an unintended transparent latch or asynchronous feedback loop.
**Correct Fix**: Assign `D_OUT <= s_reg(7);` as a concurrent signal assignment outside the process (as shown above), or move it inside the `if rising_edge(CLK)` block to register the output pin.

---

## 12.7 8-Bit Magnitude Comparator

Compares two 8-bit unsigned vectors, asserting `ALB` ($A < B$), `AGB` ($A > B$), or `AEB` ($A = B$).

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity comp_8b is
    port (
        A_IN : in  std_logic_vector(7 downto 0);
        B_IN : in  std_logic_vector(7 downto 0);
        ALB  : out std_logic;
        AGB  : out std_logic;
        AEB  : out std_logic
    );
end entity comp_8b;

architecture behavioral of comp_8b is
begin
    process(A_IN, B_IN)
    begin
        -- Default assignments guarantee complete coverage and prevent latch inference
        ALB <= '0';
        AGB <= '0';
        AEB <= '0';

        if A_IN < B_IN then
            ALB <= '1';
        elsif A_IN > B_IN then
            AGB <= '1';
        else
            AEB <= '1';
        end if;
    end process;
end architecture behavioral;
```

### Critical Textbook Erratum Analysis:
In the original text (Listing 12.6), the comparator was written as:

```text
-- TEXTBOOK ERRATUM (Listing 12.6):
process(CLK) -- MALFORMED: CLK in sensitivity list of purely combinational logic!
begin
    if (A_IN < B_IN) then ALB <= '1'; else ALB <= '0'; end if;
    if (A_IN > B_IN) then AGB <= '1'; else AGB <= '0'; end if;
    if (A_IN = B_IN) then AEB <= '1'; else AEB <= '0'; end if;
end process;
```

#### Why this fails:
1. The process sensitivity list contains only `CLK`, but the process body contains **no** edge detection (`rising_edge(CLK)`).
2. The outputs only evaluate when `CLK` changes, not when data inputs `A_IN` or `B_IN` change. In simulation, changing `A_IN` produces zero output change until the next clock transition.
3. In synthesis, this creates an unresolvable simulation-synthesis mismatch: synthesizers synthesize pure combinational logic while simulation behaves like a dual-edge pseudo-latch.
**Correct Fix**: Provide a proper combinational sensitivity list `process(A_IN, B_IN)` (or registered architecture with `rising_edge(CLK)`).

---

## 12.8 BCD to 7-Segment Decoder (Hexadecimal Display)

Decodes 4-bit hexadecimal inputs ($0\text{--}F$) to active-low 7-segment LED cathodes (`SSEG(6 downto 0)` representing segments $A$ through $G$).

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity bcd_to_7seg is
    port (
        BCD_IN : in  std_logic_vector(3 downto 0);
        SSEG   : out std_logic_vector(6 downto 0) -- Active-low: ABCDEFG
    );
end entity bcd_to_7seg;

architecture dataflow of bcd_to_7seg is
begin
    with BCD_IN select
        SSEG <= "0000001" when "0000", -- 0
                "1001111" when "0001", -- 1
                "0010010" when "0010", -- 2
                "0000110" when "0011", -- 3
                "1001100" when "0100", -- 4
                "0100100" when "0101", -- 5
                "0100000" when "0110", -- 6
                "0001111" when "0111", -- 7
                "0000000" when "1000", -- 8
                "0000100" when "1001", -- 9
                "0001000" when "1010", -- A
                "1100000" when "1011", -- b
                "0110001" when "1100", -- C
                "1000010" when "1101", -- d
                "0110000" when "1110", -- E
                "0111000" when "1111", -- F
                "1111111" when others; -- Blank (all segments disabled)
end architecture dataflow;
```

---

## 12.9 4:1 Multiplexer: Behavioral and Data-Flow Models

### 12.9.1 Behavioral Model (Sequential `case`)
```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity mux_4t1_beh is
    port (
        SEL     : in  std_logic_vector(1 downto 0);
        A       : in  std_logic;
        B       : in  std_logic;
        C       : in  std_logic;
        D       : in  std_logic;
        MUX_OUT : out std_logic
    );
end entity mux_4t1_beh;

architecture behavioral of mux_4t1_beh is
begin
    process(SEL, A, B, C, D)
    begin
        case SEL is
            when "00"   => MUX_OUT <= A;
            when "01"   => MUX_OUT <= B;
            when "10"   => MUX_OUT <= C;
            when "11"   => MUX_OUT <= D;
            when others => MUX_OUT <= '0'; -- Corrected scalar literal
        end case;
    end process;
end architecture behavioral;
```

### 12.9.2 Data-Flow Model (Concurrent `with-select`)
```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity mux_4t1_df is
    port (
        SEL     : in  std_logic_vector(1 downto 0);
        A       : in  std_logic;
        B       : in  std_logic;
        C       : in  std_logic;
        D       : in  std_logic;
        MUX_OUT : out std_logic
    );
end entity mux_4t1_df;

architecture dataflow of mux_4t1_df is
begin
    with SEL select
        MUX_OUT <= A   when "00",
                   B   when "01",
                   C   when "10",
                   D   when "11",
                   '0' when others; -- Corrected scalar literal
end architecture dataflow;
```

### Critical Textbook Erratum Analysis:
In original Listings 12.8 and 12.9:

```text
-- TEXTBOOK ERRATUM (Listing 12.8):
when others => (others => '0'); -- MALFORMED: Missing signal target and invalid scalar aggregate!

-- TEXTBOOK ERRATUM (Listing 12.9):
(others => '0') when others;    -- MALFORMED: Vector aggregate assigned to scalar std_logic!
```

The notation `(others => '0')` is an array aggregate syntax, valid strictly for composite array types (`std_logic_vector`). Assigning an array aggregate to a scalar `std_logic` port (`MUX_OUT`) is a fatal VHDL syntax error. The correct assignment is the scalar character literal `'0'`.

---

## 12.10 Active-High 3:8 Decoder

Converts a 3-bit binary address into an 8-bit one-hot asserted output vector.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;

entity decoder_3t8 is
    port (
        D_IN  : in  std_logic_vector(2 downto 0);
        F_OUT : out std_logic_vector(7 downto 0)
    );
end entity decoder_3t8;

architecture dataflow of decoder_3t8 is
begin
    with D_IN select
        F_OUT <= "00000001" when "000",
                 "00000010" when "001",
                 "00000100" when "010",
                 "00001000" when "011",
                 "00010000" when "100",
                 "00100000" when "101",
                 "01000000" when "110",
                 "10000000" when "111",
                 "00000000" when others;
end architecture dataflow;
```

### Hardware Mapping:
- Synthesizes efficiently across 8 LUTs (one LUT per output bit).
- Each bit implements an independent 3-variable minterm equation.

---

## 12.11 Synthesis Pitfall and Errata Matrix

| Circuit | Textbook Listing | Failure / Flaw in Textbook | Consequence in EDA Tools | Correct Industry Implementation |
|---|---|---|---|---|
| **Shift Register** | Listing 12.5 | `D_OUT <= REG_TMP(7);` inside clocked process but outside `rising_edge` | Simulation glitching on falling clock edges; synthesis warnings or latch inference | Concurrent assignment `D_OUT <= s_reg(7);` outside process |
| **Magnitude Comparator** | Listing 12.6 | Process sensitive only to `CLK` with no `rising_edge` check | Combinational logic does not respond to input transitions until clock toggles; sim-synth mismatch | Purely combinational `process(A_IN, B_IN)` with latch-avoidance defaults |
| **4:1 Mux (Behavioral)** | Listing 12.8 | `when others => (others => '0');` | Omitted target signal and illegal vector aggregate assigned to scalar `std_logic` | `when others => MUX_OUT <= '0';` |
| **4:1 Mux (Data-flow)** | Listing 12.9 | `(others => '0') when others;` | Type mismatch: vector aggregate assigned to scalar `std_logic` | `'0' when others;` |
