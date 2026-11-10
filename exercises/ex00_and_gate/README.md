# Exercise 00: 2-Input AND Gate

A minimal baseline circuit to verify your GHDL simulation and GTKWave toolchain setup.

---

## 1. Circuit Specifications
* **Entity**: `and_gate`
* **Inputs**: `a`, `b` (`std_logic`)
* **Output**: `y` (`std_logic`)
* **Logic Equation**: `y = a AND b`

---

## 2. Simulation Commands

```bash
# Compile and run simulation
make sim

# Open waveform in GTKWave
make wave

# Clean build artifacts
make clean
```
