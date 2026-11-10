# FPGA Digital Design & VHDL: Zero to VGA Display Controller

A hands-on, first-principles course designed for embedded software developers transitioning to digital hardware design.

---

## Course Philosophy
- **No magic code generation**: Every concept is explained, designed, written, and verified step-by-step.
- **Hardware-first thinking**: Understand the silicon (LUTs, Flip-Flops, Routing) behind every VHDL keyword.
- **Simulation-driven**: You will verify your circuits using testbenches and waveform viewers without needing physical hardware upfront.

---

## Course Roadmap

| Module | Title | Focus & Core Concepts |
| :---: | :--- | :--- |
| **01** | **The Hardware Mindset** | Silicon anatomy: LUTs, Flip-Flops, Routing. How FPGAs differ fundamentally from Microcontrollers (C/C++). |
| **02** | **VHDL Anatomy & Concurrency** | Entities, Architectures, Signals vs. Variables, Concurrent statements, and the Simulation Cycle (Delta delays). |
| **03** | **Synchronous Design Rules** | The Golden Rules of FPGA clocking, synchronous resets, setup/hold times, avoiding latches, and metastability. |
| **04** | **Toolchain & Simulation Lab** | GHDL compiler flow (analyze, elaborate, run), writing your first clock generator testbench, viewing waveforms in VS Code. |
| **05** | **VGA Protocol & Physics** | CRT electron beam physics, HSYNC, VSYNC, blanking porches, and pixel clock timing calculation (640x480 @ 60Hz). |
| **06** | **Designing the VGA Sync Generator** | Hands-on coding of horizontal and vertical counters, comparator logic, and registered glitch-free outputs. |
| **07** | **Timing Verification & Assertions** | Writing a self-checking VHDL testbench with `assert` and `report` statements to validate protocol compliance. |
| **08** | **Pattern & Color Generation** | Coordinate-based pixel generation, RGB color spaces, pipeline latency matching, and color bars. |
| **09** | **Animation & State Machines (FSM)** | Introducing dynamics: clock-divided tick generators, collision detection, and a bouncing box/ball. |
| **10** | **The Frame Grabber & Next Steps** | Capturing simulated frames to image files (.ppm), hardware synthesis checklist, and transitioning to a physical FPGA board. |
