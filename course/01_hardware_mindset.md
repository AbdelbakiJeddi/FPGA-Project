# Lesson 01: The Hardware Mindset

> **Objective**: Understand how an FPGA works physically at the silicon level, and rewire your brain from sequential C/C++ execution to concurrent digital hardware design.

---

## 1. Sequential Software vs. Concurrent Hardware

As an embedded engineer working with microcontrollers (ESP32, STM32, ARM Cortex-M), you are accustomed to the **Von Neumann / Harvard processor model**:

```
[ Flash Memory ] ──(Fetch Instruction)──► [ CPU Core / ALU ] ──(Write Result)──► [ RAM / Registers ]
```

In software:
- Code executes **sequentially**, one instruction at a time.
- Even with multi-threading or interrupts, a single core is just time-slicing or pausing to handle events.
- Variables represent locations in RAM or CPU registers.

### In an FPGA, there is NO CPU.
When you write VHDL, **you are not writing a program for a processor to execute**. You are drawing a schematic of electrical components.

```c
/* In C (Sequential) */
int a = b + c;  // Step 1: ALU computes addition
int d = a << 1; // Step 2: Executes strictly AFTER Step 1 finishes
```

```vhdl
-- In VHDL (Concurrent)
a <= b + c;     -- An actual physical adder circuit
d <= a(6 downto 0) & '0'; -- Physical copper traces routed to shift bits
```
In VHDL, both `a` and `d` exist **at the exact same time as physical copper and silicon**. If `b` changes voltage, `a` changes nanoseconds later through gate delays, and `d` updates immediately with it.

---

## 2. What Is Actually Inside an FPGA?

An FPGA (Field Programmable Gate Array) is an "ocean" of reconfigurable digital hardware resources:

```
        ┌────────────────────────────────────────────────────────┐
        │  [IOB]      [IOB]      [IOB]      [IOB]      [IOB]     │
        │   │          │          │          │          │        │
[IOB] ──┼───[ CLB ]────┼──────────[ CLB ]────┼──────────[BRAM]───┼── [IOB]
        │     │                   │                     │        │
[IOB] ──┼─────┼────────[ CLB ]────┼──────────[ DSP ]────┼────────┼── [IOB]
        │     │          │        │            │        │        │
[IOB] ──┼───[ CLB ]──────┼────────┼──────────[ CLB ]────┼────────┼── [IOB]
        │   │          │          │          │          │        │
        │  [IOB]      [IOB]      [IOB]      [IOB]      [IOB]     │
        └────────────────────────────────────────────────────────┘
```

The four primary building blocks:

### 1. Configurable Logic Blocks (CLBs / Slices)
These are the workhorses of the FPGA. Each slice contains:
- **LUT (Look-Up Table)**: Typically a 4-input or 6-input LUT. A 6-input LUT is literally a tiny $2^6 = 64$-bit static RAM with a multiplexer. Any mathematical or logical truth table of 6 inputs (AND, OR, XOR, full-adder logic) is implemented simply by storing the output bits in the LUT!
- **Flip-Flops (D-FF)**: 1-bit memory registers that capture data on a clock edge (`clk`). This is where digital memory lives.
- **Carry Logic**: Dedicated ultra-fast silicon paths for arithmetic (addition, subtraction, counters).

### 2. Programmable Interconnect (Routing)
A massive grid of segmented wire tracks and programmable switch matrices that connect any LUT output to any other LUT input across the entire chip.

### 3. Block RAM (BRAM)
Dedicated dual-port SRAM blocks (usually 18 Kb or 36 Kb each) scattered throughout the die. You use these for FIFOs, video frame buffers, and CPU caches.

### 4. DSP Slices
Dedicated high-speed hardware multipliers and accumulators ($18 \times 18$ or $25 \times 18$ bit). Doing a multiplication using pure LUTs is slow and eats up space; DSP slices do it in a single clock cycle at 400+ MHz.

---

## 3. The Compilation Pipeline: C vs. FPGA

| Step in C / Embedded | Equivalent Step in FPGA | What It Actually Does |
| :--- | :--- | :--- |
| **Source Code (`.c`)** | **VHDL Source (`.vhd`)** | Human-readable description. |
| **Compilation** | **Synthesis** | Parses VHDL and converts code logic into a **Netlist** of generic gates, LUTs, and Flip-Flops. |
| **Linking** | **Translate / Map** | Maps the generic netlist to the specific silicon resources available on your target FPGA chip. |
| **Relocation / Binary** | **Place & Route (P&R)** | Decides the exact physical $(X, Y)$ location for every LUT on the silicon die and routes the physical metal wires between them. |
| **Flash Image (`.bin`)** | **Bitstream (`.bit`)** | A binary configuration file that sets the switches in the FPGA routing matrix and initializes LUT RAM contents on power-up. |

---

## 4. Summary & The Core Rule

> [!IMPORTANT]
> **The Golden Rule**: Every time you write a line of VHDL, pause and ask yourself:
> *"Am I generating a wire (combinational logic) or am I generating a register (flip-flop clocked on a clock edge)?"*

---

## Mental Check (Before Moving to Lesson 2)

Reflect on these questions:
1. In C, if you write `for(int i=0; i<8; i++)`, the CPU takes at least 8 loop iterations over time. If you write a `for...generate` loop in VHDL, does it take 8 clock cycles, or what does it physically do?
2. Why is an FPGA capable of processing 4K 60fps video or multi-gigabit Ethernet with zero frame drops, while a fast microcontroller often struggles?

When you are ready, share your thoughts on these two questions, and we will proceed to **Lesson 02: VHDL Anatomy & Concurrency**!
