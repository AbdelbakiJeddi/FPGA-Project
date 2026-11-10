# Chapter 7: Finite State Machine Design Using VHDL

## FSM Architectural Anatomy & Classification
A Finite State Machine (FSM) is a sequential digital circuit modeled by three interconnected functional sub-blocks:

1. **State Register**: A synchronous storage element composed of edge-triggered D flip-flops that samples the next state (`NS`) on active clock transitions to update the present state (`PS`).
2. **Next-State Decoder**: Pure combinational logic evaluating present state (`PS`) and external input signals to compute the upcoming state (`NS`).
3. **Output Decoder**: Combinational logic deriving external system outputs based on current operating state and inputs.

```text
       ┌────────────────────────────────────────────────────────┐
       │                                                        │
       ▼                                                        │
┌──────────────┐     Next State (NS)     ┌──────────────┐       │ Present State (PS)
│  Next-State  │────────────────────────▶│    State     │───────┴───────────────────┐
│   Decoder    │                         │   Register   │                           │
│ (Comb Logic) │                         │ (D Flip-Flop)│                           │
└──────────────┘                         └──────────────┘                           │
       ▲                                        ▲                                   │
       │ Inputs                                 │ CLK, RESET                        │
       │                                                                            ▼
       │                                                                    ┌──────────────┐
       │                               Mealy Path                           │    Output    │──▶ Outputs
       └───────────────────────────────────────────────────────────────────▶│   Decoder    │
                                                                            │ (Comb Logic) │
                                                                            └──────────────┘
```

### Moore vs Mealy FSM Architectures
FSMs are categorized according to output timing dependencies:

| Classification | Output Functional Dependence | Timing & Glitch Characteristics | Hardware Implications |
| :--- | :--- | :--- | :--- |
| **Moore Machine** | Exclusively depends on Present State (`PS`):<br>`Outputs = f(PS)` | **Glitch-free** relative to inputs. Output changes are strictly synchronized with clock edges. | Extra state may be required; 1 clock cycle latency to react to inputs. |
| **Mealy Machine** | Depends on both Present State (`PS`) and External Inputs:<br>`Outputs = f(PS, Inputs)` | **Combinational feedthrough**: input glitches immediately propagate to outputs within the same clock cycle. | Can react within the same cycle; requires fewer states, but output paths may create critical timing bottlenecks. |

---

## 7.1 FSM Behavioral Representation in VHDL
The industry standard methodology for implementing robust, synthesizable FSMs in VHDL is the **Dependent PS/NS 2-Process FSM Architecture**.

### The Canonical 2-Process FSM Model
Separating the FSM into exactly two concurrent processes enforces a clean hardware partition between synchronous sequential storage and combinational evaluation:

#### Process 1: Synchronous State Register Process
Responsible solely for clocking and asynchronous/synchronous reset. It contains no combinational transition logic:
- Sensitive only to `CLK` and asynchronous reset (`RESET`).
- Evaluates `rising_edge(CLK)` to transfer `PS <= NS;`.

#### Process 2: Combinational Next-State and Output Decoder Process
Contains all next-state transition conditions, branch decoding, and output driving:
- **Sensitivity List**: Must include `PS` and all external state transition and Mealy input signals. Omitting an input causes simulation-synthesis mismatches.
- **Golden Rule — Output Pre-Assignment**: To completely eliminate unintended transparent latches, **assign default values to `NS` and all outputs at the very top of the process body** before entering the `case` construct.
- **The `case PS is` Construct**: Exhaustively details the operational behavior for each defined state.
- **Moore Output Placement**: Assigned unconditionally inside the `when STATE =>` branch (outside any input `if` condition).
- **Mealy Output Placement**: Assigned conditionally inside the transition `if (input = ...)` branches.

---

## State Enumeration & Driving State to External Pins

### State Enumeration
In VHDL, state variables are formally defined using user-defined **enumeration types**:

```text
type state_type is (ST_IDLE, ST_READ, ST_PROCESS, ST_DONE);
signal PS, NS : state_type;
```
Enumeration abstractly models state transitions without locking the architecture to a specific hardware encoding, allowing the synthesis compiler to optimize state assignment.

### Outputting State Variables to External Pins
Because enumeration types are internal symbolic constructs, they cannot be driven directly onto standard digital output ports (`std_logic_vector`). To observe state variables on external pins (e.g., for system debug or status telemetry), decode the symbolic state using a concurrent selected signal assignment (`with-select`):

```text
with PS select
    state_bus_out <= "00" when ST_IDLE,
                     "01" when ST_READ,
                     "10" when ST_PROCESS,
                     "11" when ST_DONE,
                     "00" when others;
```

---

## 7.2 One-Hot Encoding for FSMs

### State Encoding Schemes: Binary vs One-Hot
When mapping abstract symbolic states to physical flip-flops in silicon, two primary encoding schemes are employed:

| Encoding Scheme | Flip-Flop Count ($N_{FF}$) | Combinational Logic Depth | FPGA Architecture Suitability |
| :--- | :--- | :--- | :--- |
| **Binary (Full) Encoding** | $N_{FF} = \lceil \log_2(\text{states}) \rceil$ | High fan-in decoding trees; multi-level LUT delay | Optimal for CPLDs and ASIC cells where flip-flop silicon area is costly. |
| **One-Hot Encoding** | $N_{FF} = \text{states}$ | Single-gate decoding; shallow 1-level LUT logic | **Optimal for FPGAs**: FPGAs are register-rich; one-hot minimizes LUT logic levels, maximizing operating frequency ($F_{\max}$). |

In one-hot encoding, exactly one flip-flop is asserted ('1') for any legal state (e.g., `"1000"`, `"0100"`, `"0010"`, `"0001"` for a 4-state machine). Because each state is directly identified by a dedicated register output, next-state and output decoding logic requires minimal combinational gating.

### Controlling State Encoding via Synthesis Attributes
To explicitly enforce one-hot bit assignments directly in VHDL rather than relying on automated synthesis heuristics, apply user-defined synthesis attributes (`ENUM_ENCODING`):

```text
type state_type is (ST0, ST1, ST2, ST3);
attribute ENUM_ENCODING : STRING;
attribute ENUM_ENCODING of state_type : type is "1000 0100 0010 0001";
signal PS, NS : state_type;
```
During elaboration, synthesis tools (such as Vivado or Quartus) recognize `ENUM_ENCODING` and bind the specified bitstrings directly to the inferred state registers.

### Fault-Tolerant Safe State Recovery
One-hot encoding creates $2^N - N$ illegal states (where zero bits or more than one bit are asserted). In radiation environments or noisy power rails, single-event upsets (SEUs) can bump an FSM into an undefined state.
- **Golden Safe Rule**: Inside the combinational `case PS is` construct, configure the `when others =>` branch to force a transition back to a valid reset/idle state (`NS <= ST_RESET;`) rather than holding an undefined lock-up state.

---

## 7.3 Important Points & Design Rules
1. **Always use the 2-Process FSM architecture**: Strictly separate the synchronous state register process from the combinational next-state/output process.
2. **Eliminate latches with default pre-assignments**: Assign default values to `NS` and all outputs at the top of the combinational process.
3. **Sensitivity list completeness**: Include `PS` and all transition/Mealy inputs in the combinational process sensitivity list to guarantee simulation-synthesis equivalence.
4. **Distinguish Moore and Mealy outputs clearly**: Assign Moore outputs unconditionally in the state branch; assign Mealy outputs conditionally inside transition branches.
5. **Leverage one-hot encoding in FPGAs**: Take advantage of FPGA register density to maximize clock speeds ($F_{\max}$) and reduce LUT utilization.

---

## Synthesizable Architectural Examples

### Example 1: Robust 2-Process FSM with Moore and Mealy Outputs
```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity fsm_moore_mealy is
    port (
        clk     : in  std_logic;
        reset   : in  std_logic;
        x_in    : in  std_logic;
        z_moore : out std_logic;
        z_mealy : out std_logic
    );
end entity fsm_moore_mealy;

architecture rtl of fsm_moore_mealy is
    -- State enumeration type
    type state_type is (ST_IDLE, ST_ACTIVE, ST_WAIT);
    signal ps, ns : state_type;
begin
    -- Process 1: Synchronous State Register (Clocking & Asynchronous Reset)
    sync_proc: process(clk, reset) is
    begin
        if (reset = '1') then
            ps <= ST_IDLE;
        elsif rising_edge(clk) then
            ps <= ns;
        end if;
    end process sync_proc;

    -- Process 2: Combinational Next-State and Output Decoder
    comb_proc: process(ps, x_in) is
    begin
        -- Golden Rule: Output Pre-Assignment to prevent latch inference
        z_moore <= '0';
        z_mealy <= '0';
        ns      <= ps;

        case ps is
            when ST_IDLE =>
                -- Moore output: depends exclusively on present state
                z_moore <= '0';
                if (x_in = '1') then
                    ns      <= ST_ACTIVE;
                    z_mealy <= '1';  -- Mealy output: depends on state AND input
                else
                    ns      <= ST_IDLE;
                    z_mealy <= '0';
                end if;

            when ST_ACTIVE =>
                z_moore <= '1';  -- Moore output asserted in ST_ACTIVE
                if (x_in = '0') then
                    ns      <= ST_WAIT;
                    z_mealy <= '0';
                else
                    ns      <= ST_ACTIVE;
                    z_mealy <= '1';
                end if;

            when ST_WAIT =>
                z_moore <= '0';
                ns      <= ST_IDLE;
                z_mealy <= '0';

            when others =>
                ns      <= ST_IDLE;
                z_moore <= '0';
                z_mealy <= '0';
        end case;
    end process comb_proc;
end architecture rtl;
```

### Example 2: One-Hot Encoded FSM with Synthesis Attributes and State Bus Output
```vhdl
library ieee;
use ieee.std_logic_1164.all;

entity one_hot_fsm is
    port (
        clk       : in  std_logic;
        reset     : in  std_logic;
        req_in    : in  std_logic;
        ack_out   : out std_logic;
        state_bus : out std_logic_vector(3 downto 0)
    );
end entity one_hot_fsm;

architecture rtl of one_hot_fsm is
    type state_type is (S_RESET, S_IDLE, S_RUN, S_DONE);

    -- Explicit One-Hot Synthesis Encoding Attributes
    attribute enum_encoding : string;
    attribute enum_encoding of state_type : type is "1000 0100 0010 0001";

    signal ps, ns : state_type;
begin
    -- Synchronous State Register
    sync_proc: process(clk, reset) is
    begin
        if (reset = '1') then
            ps <= S_RESET;
        elsif rising_edge(clk) then
            ps <= ns;
        end if;
    end process sync_proc;

    -- Combinational Logic with Default Output Pre-Assignments
    comb_proc: process(ps, req_in) is
    begin
        ack_out <= '0';
        ns      <= ps;

        case ps is
            when S_RESET =>
                ns <= S_IDLE;

            when S_IDLE =>
                if (req_in = '1') then
                    ns <= S_RUN;
                else
                    ns <= S_IDLE;
                end if;

            when S_RUN =>
                ack_out <= '1';
                ns      <= S_DONE;

            when S_DONE =>
                ack_out <= '0';
                ns      <= S_IDLE;

            when others =>
                -- Safe state machine recovery: return to valid reset state
                ns <= S_RESET;
        end case;
    end process comb_proc;

    -- Concurrent output decoding driving symbolic state to external monitoring pins
    with ps select
        state_bus <= "1000" when S_RESET,
                     "0100" when S_IDLE,
                     "0010" when S_RUN,
                     "0001" when S_DONE,
                     "1000" when others;
end architecture rtl;
```
