# Exercise 01: 4-to-1 Multiplexer with Enable (`mux4to1`)

A hands-on implementation based on **Chapter 4 of *Free Range VHDL*** demonstrating concurrent signal assignment paradigms.

---

## 1. Specifications & Interface

```
               +-------------+
        d(0) --|             |
        d(1) --|             |
        d(2) --|   mux4to1   |--> y
        d(3) --|             |
               +------+------+
                 |      |
               sel(1:0) en
```

### Truth Table
| `en` | `sel(1)` | `sel(0)` | Selected Input | `y` |
|:---:|:---:|:---:|:---:|:---:|
| `0` | `X` | `X` | None (Disabled) | `'0'` |
| `1` | `0` | `0` | `d(0)` | `d(0)` |
| `1` | `0` | `1` | `d(1)` | `d(1)` |
| `1` | `1` | `0` | `d(2)` | `d(2)` |
| `1` | `1` | `1` | `d(3)` | `d(3)` |

---

## 2. Architectures Provided
1. **`rtl_when`**: Uses conditional signal assignment (`when ... else`), evaluating conditions in priority order.
2. **`rtl_select`**: Uses selected signal assignment (`with ... select`), evaluating the concatenated control word `en & sel`.

---

## 3. Simulation & Verification

```bash
# Compile and run self-checking testbench with GHDL
make sim

# Open waveform in GTKWave
make wave

# Clean build artifacts
make clean
```
