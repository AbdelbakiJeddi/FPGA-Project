library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

--------------------------------------------------------------------------------
-- Entity: tb_mux4to1
-- Description: Self-checking testbench for 4:1 Multiplexer (mux4to1).
--------------------------------------------------------------------------------
entity tb_mux4to1 is
end entity tb_mux4to1;

architecture sim of tb_mux4to1 is
    signal d   : std_logic_vector(3 downto 0) := (others => '0');
    signal sel : std_logic_vector(1 downto 0) := (others => '0');
    signal en  : std_logic := '0';
    signal y   : std_logic;
begin

    -- Instantiate Device Under Test (DUT)
    dut : entity work.mux4to1(rtl_when)
        port map (
            d   => d,
            sel => sel,
            en  => en,
            y   => y
        );

    stim_proc : process
    begin
        ------------------------------------------------------------------------
        -- Test Case 1: Disabled mode (en = '0')
        -- Output must stay '0' regardless of data or select inputs
        ------------------------------------------------------------------------
        en  <= '0';
        d   <= "1111";
        sel <= "00";
        wait for 10 ns;
        assert y = '0'
            report "TC1.1 Failed: Output must be '0' when en='0'"
            severity error;

        sel <= "11";
        wait for 10 ns;
        assert y = '0'
            report "TC1.2 Failed: Output must be '0' when en='0' for sel='11'"
            severity error;

        ------------------------------------------------------------------------
        -- Test Case 2: Enabled mode (en = '1'), channel-by-channel sweep
        ------------------------------------------------------------------------
        en <= '1';

        -- Channel 0 (sel = "00")
        sel <= "00";
        d   <= "0000"; wait for 10 ns;
        assert y = '0' report "TC2.0a Failed: d(0)='0' expected y='0'" severity error;
        d   <= "0001"; wait for 10 ns;
        assert y = '1' report "TC2.0b Failed: d(0)='1' expected y='1'" severity error;
        d   <= "1110"; wait for 10 ns; -- other channels '1', d(0)='0'
        assert y = '0' report "TC2.0c Failed: channel isolation failed for sel=00" severity error;

        -- Channel 1 (sel = "01")
        sel <= "01";
        d   <= "0000"; wait for 10 ns;
        assert y = '0' report "TC2.1a Failed: d(1)='0' expected y='0'" severity error;
        d   <= "0010"; wait for 10 ns;
        assert y = '1' report "TC2.1b Failed: d(1)='1' expected y='1'" severity error;
        d   <= "1101"; wait for 10 ns;
        assert y = '0' report "TC2.1c Failed: channel isolation failed for sel=01" severity error;

        -- Channel 2 (sel = "10")
        sel <= "10";
        d   <= "0000"; wait for 10 ns;
        assert y = '0' report "TC2.2a Failed: d(2)='0' expected y='0'" severity error;
        d   <= "0100"; wait for 10 ns;
        assert y = '1' report "TC2.2b Failed: d(2)='1' expected y='1'" severity error;
        d   <= "1011"; wait for 10 ns;
        assert y = '0' report "TC2.2c Failed: channel isolation failed for sel=10" severity error;

        -- Channel 3 (sel = "11")
        sel <= "11";
        d   <= "0000"; wait for 10 ns;
        assert y = '0' report "TC2.3a Failed: d(3)='0' expected y='0'" severity error;
        d   <= "1000"; wait for 10 ns;
        assert y = '1' report "TC2.3b Failed: d(3)='1' expected y='1'" severity error;
        d   <= "0111"; wait for 10 ns;
        assert y = '0' report "TC2.3c Failed: channel isolation failed for sel=11" severity error;

        ------------------------------------------------------------------------
        -- End of Simulation
        ------------------------------------------------------------------------
        report "==================================================";
        report "ALL TESTS PASSED: 4:1 Multiplexer (mux4to1) verified!";
        report "==================================================";
        wait;
    end process stim_proc;

end architecture sim;
