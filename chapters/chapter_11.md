# Chapter 11: Looping Constructs

## 11.1 Looping Semantics in Hardware: Spatial Unrolling vs. Temporal Iteration

In procedural software (such as C or Python), loops execute **temporally**: a single central processor re-executes instructions across consecutive clock cycles. In VHDL synthesis, looping constructs execute **spatially**: the synthesizer unrolls the loop completely, instantiating physical replicas of the internal logic across the FPGA fabric.

```text
Software (Temporal):             Hardware Synthesis (Spatial Unrolling):
   +---------------+                 +----------+     +----------+     +----------+
   | Loop Body     |<--+             | Stage 0  | --> | Stage 1  | --> | Stage N-1|
   | (1 execution  |   |             | (LUT/Mux)|     | (LUT/Mux)|     | (LUT/Mux)|
   |  unit in time)|---+             +----------+     +----------+     +----------+
   +---------------+               <--- Replicated across silicon area in space --->
```

### Hardware Implications of Spatial Unrolling:
1. **Area Scaling**: A loop with $N$ iterations generates $N$ physical copies of the combinational logic (multiplexers, adders, gates). If the loop body contains complex arithmetic, resource consumption multiplies by $N$.
2. **Timing and Critical Path**: Unrolling cascaded dependencies inside a combinational process creates deep logic chains. The cumulative propagation delay ($t_{pd}$) increases linearly or logarithmically with $N$, substantially degrading maximum clock frequency ($F_{max}$).
3. **Elaboration-Time Static Bounds**: The synthesizer must know the exact number of iterations during elaboration to generate the physical netlist. Any loop whose bounds cannot be determined at compile time cannot be synthesized into static hardware.

---

## 11.2 The `for` Loop Construct

The `for` loop is the primary synthesizable looping construct in VHDL, executing a sequential block across a pre-determined range of index values.

```text
[loop_label:] for index_variable in discrete_range loop
    -- sequential statements
end loop [loop_label];
```

### Unique Rules Governing the Loop Index Variable
1. **Implicit Declaration**: The loop index (`index_variable`) is declared implicitly by its appearance in the `for` statement. Declaring it explicitly in the process declarative region causes a compilation error or unintended variable hiding.
2. **Read-Only Immutability**: The loop index is strictly read-only within the loop body. It may be read and used in expressions or array indexing, but it **cannot** be assigned to (`index := index + 2;` is illegal).
3. **Strict Unit Stepping**: The index steps strictly by $+1$ (when using `to`) or $-1$ (when using `downto`). VHDL provides no native step size modifier (such as C's `i += 2`). Non-unit stepping must be implemented via internal arithmetic or `next` statements.
4. **Identifier Shadowing**: If the loop index shares an identifier with a process variable or architecture signal, the loop index hides the outer object within the loop body. To avoid severe debugging confusion, always use distinct index names.
5. **Range Specifications**: The iteration range can be specified using integer literals (`0 to 7`), custom integer ranges (`my_range`), or array attributes (`data_vector'range`, `data_vector'reverse_range`).

---

## 11.3 Synthesizable `for` Loop Examples

### 11.3.1 Bit-Reversal, Parity Tree, and Population Counter
The following module demonstrates spatial hardware unrolling. In a single clockless process, an 8-bit input is reversed, an 8-input parity tree (XOR chain) is synthesized, and the total number of set bits (population count) is calculated.

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity bit_processor is
    port (
        data_in   : in  std_logic_vector(7 downto 0);
        data_rev  : out std_logic_vector(7 downto 0);
        odd_par   : out std_logic;
        ones_cnt  : out std_logic_vector(3 downto 0)
    );
end entity bit_processor;

architecture rtl of bit_processor is
begin
    process(data_in)
        variable v_par : std_logic;
        variable v_cnt : unsigned(3 downto 0);
    begin
        v_par := '0';
        v_cnt := (others => '0');

        -- Spatial unrolling: generates wire reversal, an XOR tree, and adder cascade
        for i in 0 to 7 loop
            data_rev(i) <= data_in(7 - i);
            v_par := v_par xor data_in(i);
            if data_in(i) = '1' then
                v_cnt := v_cnt + 1;
            end if;
        end loop;

        odd_par  <= v_par;
        ones_cnt <= std_logic_vector(v_cnt);
    end process;
end architecture rtl;
```

#### Synthesized Hardware:
- `data_rev`: Synthesizes to zero silicon logic (pure metal routing transposition).
- `odd_par`: Synthesizes to a balanced 8-input XOR tree (3 levels of 2-input XORs in FPGA LUTs).
- `ones_cnt`: Synthesizes to a multi-stage combinational adder tree.

---

## 11.4 Loop Control: `next` and `exit` Statements

VHDL provides two sequential control statements to alter loop iteration flow: `next` and `exit`. Both can be formulated either with an enclosing `if` statement or as an inline conditional clause (`when`).

### 11.4.1 The `next` Statement (Continue Iteration)
The `next` statement skips the remaining sequential statements in the current iteration and immediately increments the loop index for the next pass:

```vhdl
process(clk)
    variable v_cnt : integer := 0;
begin
    if rising_edge(clk) then
        for i in 0 to 7 loop
            if i = 3 then
                next; -- Enclosing if form
            end if;
            next when i = 5; -- Inline when form
            v_cnt := v_cnt + 1;
        end loop;
    end if;
end process;
```

In synthesis, `next` generates combinational multiplexing that bypasses assignments for specific iteration indices.

### 11.4.2 The `exit` Statement (Break Loop)
The `exit` statement terminates the loop entirely, transferring execution immediately to the first statement following `end loop`:

```vhdl
process(clk)
    variable v_cnt : integer := 0;
begin
    if rising_edge(clk) then
        for i in 0 to 7 loop
            if i = 4 then
                exit; -- Enclosing if form
            end if;
            exit when i = 6; -- Inline when form
            v_cnt := v_cnt + 1;
        end loop;
    end if;
end process;
```

In synthesis, an `exit` statement creates priority-encoded exit logic. Once the exit condition evaluates to true, subsequent stages in the spatial unrolling are masked out.

### 11.4.3 Synthesizable Priority Encoder with `exit`
The following leading-zero detector / priority encoder searches an 8-bit vector from MSB to LSB and terminates immediately upon finding the first asserted bit:

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity priority_encoder_8b is
    port (
        req_in    : in  std_logic_vector(7 downto 0);
        valid_out : out std_logic;
        prio_idx  : out std_logic_vector(2 downto 0)
    );
end entity priority_encoder_8b;

architecture rtl of priority_encoder_8b is
begin
    process(req_in)
        variable v_found : boolean;
        variable v_idx   : unsigned(2 downto 0);
    begin
        v_found := false;
        v_idx   := (others => '0');

        -- Evaluates from MSB (7) down to LSB (0)
        prio_search : for i in 7 downto 0 loop
            if req_in(i) = '1' then
                v_found := true;
                v_idx   := to_unsigned(i, 3);
                exit prio_search; -- Breaks spatial unrolling at first match
            end if;
        end loop prio_search;

        if v_found then
            valid_out <= '1';
            prio_idx  <= std_logic_vector(v_idx);
        else
            valid_out <= '0';
            prio_idx  <= (others => '0');
        end if;
    end process;
end architecture rtl;
```

---

## 11.5 The `while` Loop Construct and Synthesizability Boundaries

The `while` loop executes iteratively as long as a specified boolean condition evaluates to `true`:

```text
[loop_label:] while boolean_condition loop
    -- sequential statements
end loop [loop_label];
```

### Why Unbounded `while` Loops are Non-Synthesizable
A `while` loop has no inherent index variable and terminates only when its condition changes. In hardware:
1. If the condition depends on runtime input signals or signals updated across clock cycles, the synthesizer cannot determine how many hardware stages to instantiate at compile time.
2. A process cannot "stall" or "spin" waiting for an event inside a combinational loop—doing so in hardware forms an asynchronous combinational feedback loop (oscillator or latch lockup).

Therefore: **Unbounded `while` loops are strictly non-synthesizable and rejected by FPGA EDA tools.**

### Synthesizable Use of `while` Loops
A `while` loop is synthesizable **only** if the synthesizer can statically determine at elaboration time that the loop terminates within a fixed, constant maximum number of iterations. To ensure synthesis acceptance, an explicit static iteration limit must be provided:

```vhdl
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity int_divider is
    port (
        dividend  : in  std_logic_vector(7 downto 0);
        divisor   : in  std_logic_vector(7 downto 0);
        quotient  : out std_logic_vector(7 downto 0);
        remainder : out std_logic_vector(7 downto 0)
    );
end entity int_divider;

architecture rtl of int_divider is
begin
    process(dividend, divisor)
        variable v_num   : unsigned(7 downto 0);
        variable v_den   : unsigned(7 downto 0);
        variable v_quot  : unsigned(7 downto 0);
        variable v_loops : integer range 0 to 255;
    begin
        v_num   := unsigned(dividend);
        v_den   := unsigned(divisor);
        v_quot  := (others => '0');
        v_loops := 0;

        if v_den /= 0 then
            -- While loop with explicit static upper bound for synthesis tools
            while (v_num >= v_den) and (v_loops < 255) loop
                v_num   := v_num - v_den;
                v_quot  := v_quot + 1;
                v_loops := v_loops + 1;
            end loop;
        end if;

        quotient  <= std_logic_vector(v_quot);
        remainder <= std_logic_vector(v_num);
    end process;
end architecture rtl;
```

### Primary Application of `while` Loops: Testbenches
In verification testbenches, `while` loops are used extensively for clock generation, handshaking timeouts, and stimulus streaming:

```vhdl
tb_poll : process
    variable timeout_cnt : integer := 0;
begin
    wait_ack : while (ack = '0') and (timeout_cnt < 1000) loop
        wait until rising_edge(clk);
        timeout_cnt := timeout_cnt + 1;
    end loop wait_ack;
    assert (timeout_cnt < 1000) report "Slave ACK timeout!" severity failure;
    wait;
end process tb_poll;
```

---

## 11.6 Synthesis Guidelines and Best Practices for Loops

1. **Prefer `for` loops with attribute ranges**: Use `for i in data'range loop` or `data'reverse_range` to make vector manipulations width-independent and parameterizable.
2. **Label all loops**: Always provide descriptive labels (e.g. `bit_slice_loop: for ...`). In nested loops, explicit labels disambiguate `next` and `exit` targets (e.g. `exit outer_loop;`).
3. **Budget for logic depth**: Keep loop iteration bounds modest ($N \le 32$) in combinational processes. If $N$ is large, pipeline the operation across multiple clock cycles using a sequential state machine or shift register rather than a single-cycle unrolled loop.
4. **Never assign to signals across spatial iterations expecting sequential reads**: Since signal updates are deferred to the end of the delta cycle, reading an updated signal within an unrolled loop returns the initial pre-process value. Use local variables for iterative accumulation.
