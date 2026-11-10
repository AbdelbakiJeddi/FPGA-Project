# FPGA Digital Design & VHDL Learning Track

[![VHDL Standard](https://img.shields.io/badge/VHDL-2008-blue.svg)](https://en.wikipedia.org/wiki/VHDL)
[![Simulator](https://img.shields.io/badge/Simulator-GHDL_4.1.0-orange.svg)](https://github.com/ghdl/ghdl)
[![Waveform Viewer](https://img.shields.io/badge/Waveform-GTKWave-green.svg)](http://gtkwave.sourceforge.net/)
[![Test Suite](https://img.shields.io/badge/Tests-147%2F147_Passed-brightgreen.svg)](tests/)

A first-principles, hands-on learning repository designed for embedded software engineers transitioning to digital hardware design, FPGA architecture, and synthesizable VHDL.

---

## 🎯 Repository Philosophy

- **Hardware-First Thinking**: Every VHDL keyword and construct maps directly to silicon structures (LUTs, Flip-Flops, Multiplexers, Block RAMs, Routing Matrices). No software illusions or magic code generation.
- **Strict Synthesis Awareness**: Direct focus on inferring intended hardware—preventing accidental latches, understanding clock-domain boundaries, and respecting synchronous design rules.
- **Simulation-Driven Verification**: Every circuit is validated using self-checking testbenches with assertion checking in **GHDL**, with waveforms visualized in **GTKWave**.
- **High Signal-to-Noise Ratio**: Concise, technical notes without introductory filler or beginner fluff.

---

## 🗂️ Repository Architecture

```
fpga_project/
├── README.md                      # Central learning dashboard (this file)
├── Book_FreeRangeVHDL.pdf         # Reference textbook (Bryan Mealy & Fabrizio Tappero)
│
├── chapters/                      # Free Range VHDL: 12 Technical Chapter Summaries
│   ├── README.md                  # Complete chapter directory & synthesis index
│   ├── chapter_01.md              # Introduction & Hardware Concurrency
│   ├── ...
│   └── chapter_12.md              # Standard Digital Circuits & Errata Corrections
│
├── course/                        # Lecture Notes: Zero-to-VGA Display Controller
│   ├── README.md                  # Module directory
│   ├── COURSE_PLAN.md             # 10-module comprehensive roadmap
│   ├── 01_hardware_mindset.md     # Silicon anatomy (LUTs, FFs, Microcontroller vs FPGA)
│   ├── 01b_vhdl_design_units.md   # Entity interface contracts & IEEE libraries
│   └── 02_vhdl_programming_paradigm.md # Concurrency & Signal Assignments
│
├── exercises/                     # Hands-on VHDL Simulation Labs
│   ├── README.md                  # Lab workflow & execution guide
│   ├── common/Makefile.inc        # Standard GHDL compilation & GTKWave recipes
│   ├── new_exercise.sh            # Lab scaffold generator
│   ├── ex00_and_gate/             # Baseline verification circuit
│   └── ex01_ch04_multiplexer/     # Free Range VHDL Ch. 4: 4:1 MUX (when/select)
│
└── tests/                         # Automated Markdown & VHDL Syntax Test Suite
    ├── conftest.py                # Test configuration
    ├── run_tests.sh               # 4-tier validation test runner
    ├── test_chapters.py           # Pytest test cases (147 tests)
    └── vhdl_validator.py          # Standalone GHDL extraction & syntax validator
```

---

## 📚 Free Range VHDL Summaries

Direct access to high-density technical summaries for all 12 chapters:

| Chapter | Title | Core FPGA / Synthesis Concept | Link |
| :---: | :--- | :--- | :---: |
| **01** | Introduction to VHDL | Hardware concurrency paradigm, HDL golden rules, toolchain flows | [Summary](chapters/chapter_01.md) |
| **02** | VHDL Invariants | Lexical rules, case insensitivity, reserved keywords, syntax rules | [Summary](chapters/chapter_02.md) |
| **03** | VHDL Design Units | `entity`, `architecture`, port modes (`in`/`out`/`inout`), `std_logic` | [Summary](chapters/chapter_03.md) |
| **04** | VHDL Programming Paradigm | Concurrency, signal assignment (`<=`), `when-else`, `with-select` | [Summary](chapters/chapter_04.md) |
| **05** | Architecture Models | Dataflow, behavioral, `process`, `if`/`case`, latch avoidance | [Summary](chapters/chapter_05.md) |
| **06** | Operators & Storage | Operator precedence, DFF induction, `rising_edge`, sync/async reset | [Summary](chapters/chapter_06.md) |
| **07** | FSM Design | Canonical 2-process FSM, Moore vs Mealy timing, state encoding | [Summary](chapters/chapter_07.md) |
| **08** | Structural Modeling | Hierarchical modularity, component instantiation, generics | [Summary](chapters/chapter_08.md) |
| **09** | Registers & RTL | Register inference, clock isolation, multi-bit registers, clock enable | [Summary](chapters/chapter_09.md) |
| **10** | Data Objects & Simulation | Signals vs variables, delta cycles, `numeric_std` arithmetic | [Summary](chapters/chapter_10.md) |
| **11** | Looping Statements | `for` loops (hardware unrolling), loop control (`exit`/`next`), boundaries | [Summary](chapters/chapter_11.md) |
| **12** | Standard Digital Circuits | Registers, counters, shift registers, decoders, MUXes, errata fixes | [Summary](chapters/chapter_12.md) |

---

## 🔬 Hands-on Simulation Lab

Each exercise contains synthesizable RTL, a self-checking testbench, and a standardized Makefile:

```bash
# Example: Run Exercise 01 (4:1 Multiplexer)
cd exercises/ex01_ch04_multiplexer

# 1. Compile RTL + Testbench and execute simulation
make sim

# 2. Inspect waveforms in GTKWave
make wave

# 3. Clean compilation artifacts
make clean
```

### Creating a New Lab
To scaffold a new exercise with the automated build infrastructure:
```bash
cd exercises
./new_exercise.sh ex02_decoder3to8 tb_decoder3to8
```

---

## 🛠️ Toolchain Prerequisites (Linux / Ubuntu)

Install the simulation and waveform viewing toolchain:

```bash
sudo apt update
sudo apt install -y ghdl gtkwave make python3-pytest
```

---

## 📈 Learning Progress Tracker

- [x] **Phase 0: Toolchain & Verification Infrastructure**
  - [x] GHDL 4.1.0 and GTKWave setup
  - [x] Baseline simulation lab (`ex00_and_gate`)
  - [x] Automated test runner (`./tests/run_tests.sh`)
- [x] **Phase 1: Free Range VHDL Technical Distillation**
  - [x] Chapters 1–4: Design units, interfaces, concurrency, signal assignment
  - [x] Chapters 5–8: Processes, latch prevention, 2-process FSMs, structural modularity
  - [x] Chapters 9–12: RTL registers, delta cycles, hardware loop unrolling, standard circuits
- [ ] **Phase 2: Digital Design Labs**
  - [x] Lab 00: 2-Input AND Gate (`exercises/ex00_and_gate`)
  - [x] Lab 01: 4-to-1 Multiplexer with Enable (`exercises/ex01_ch04_multiplexer`)
  - [ ] Lab 02: 3-to-8 Decoder / Demultiplexer
  - [ ] Lab 03: Generic N-bit Synchronous Counter with Load & Reset
  - [ ] Lab 04: Configurable Universal Shift Register (SISO, SIPO, PISO, PIPO)
  - [ ] Lab 05: 2-Process Moore / Mealy Finite State Machine
- [ ] **Phase 3: VGA Controller Capstone**
  - [ ] Module 05: CRT timing calculations (640x480 @ 60 Hz)
  - [ ] Module 06: Horizontal and vertical sync counter design
  - [ ] Module 07: Self-checking assertion testbench for VGA timing
  - [ ] Module 08: Color coordinate generator & test patterns
  - [ ] Module 09: Dynamic bouncing object FSM
  - [ ] Module 10: Frame grabber export (.ppm) & bitstream synthesis
