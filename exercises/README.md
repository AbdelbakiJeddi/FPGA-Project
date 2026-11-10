# Hands-on VHDL & FPGA Exercises

Practical simulation labs verified with **GHDL** (VHDL-2008) and inspected with **GTKWave**.

---

## 1. Directory Structure

```
exercises/
├── README.md                  # This guide
├── new_exercise.sh            # Helper script to scaffold a new lab
├── common/
│   └── Makefile.inc           # Standardized GHDL compile/simulate recipes
├── ex00_and_gate/             # Baseline: 2-input AND gate with self-checking testbench
└── ex01_ch04_multiplexer/     # Free Range VHDL Ch. 4: 4:1 Multiplexer (when/select)
```

---

## 2. Quickstart: Running a Lab

Navigate to any exercise folder and run:

```bash
# 1. Compile RTL + Testbench and execute simulation
make sim

# 2. Open generated waveform in GTKWave
make wave

# 3. Clean temporary build objects and simulation waveforms
make clean
```

---

## 3. Creating a New Exercise

To scaffold a new exercise with the standard Makefile integration:

```bash
./new_exercise.sh ex02_decoder3to8 tb_decoder3to8
cd ex02_decoder3to8
# Add your design (.vhd) and testbench (.vhd)
make sim
```
