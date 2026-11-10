library ieee;
use ieee.std_logic_1164.all;

--------------------------------------------------------------------------------
-- Entity: mux4to1
-- Description: 4-to-1 Multiplexer with active-high Enable.
-- Reference: Free Range VHDL, Chapter 4 (VHDL Programming Paradigm).
--
-- Hardware Semantics:
-- - Combinational multiplexer mapping 4 data lines to 1 output.
-- - When en = '0', output is forced to '0' (active-high gate).
-- - Demonstrates two canonical concurrent modeling paradigms:
--   1. Conditional Signal Assignment (when ... else)
--   2. Selected Signal Assignment (with ... select)
--------------------------------------------------------------------------------
entity mux4to1 is
    port (
        d   : in  std_logic_vector(3 downto 0); -- Data inputs: d(0)=D0 .. d(3)=D3
        sel : in  std_logic_vector(1 downto 0); -- Channel select lines
        en  : in  std_logic;                    -- Active-high enable
        y   : out std_logic                     -- Multiplexer output
    );
end entity mux4to1;

--------------------------------------------------------------------------------
-- Architecture: rtl_when (Default)
-- Uses Conditional Signal Assignment (evaluated with priority, like if-else)
--------------------------------------------------------------------------------
architecture rtl_when of mux4to1 is
begin
    y <= '0'  when en = '0' else
         d(0) when sel = "00" else
         d(1) when sel = "01" else
         d(2) when sel = "10" else
         d(3) when sel = "11" else
         '0';
end architecture rtl_when;

--------------------------------------------------------------------------------
-- Architecture: rtl_select
-- Uses Selected Signal Assignment (evaluated as parallel decode / MUX)
--------------------------------------------------------------------------------
architecture rtl_select of mux4to1 is
    signal ctrl : std_logic_vector(2 downto 0);
begin
    ctrl <= en & sel;

    with ctrl select
        y <= d(0) when "100",
             d(1) when "101",
             d(2) when "110",
             d(3) when "111",
             '0'  when others;
end architecture rtl_select;
