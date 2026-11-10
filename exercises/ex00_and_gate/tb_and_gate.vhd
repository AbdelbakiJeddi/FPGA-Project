library ieee;
use ieee.std_logic_1164.all;

entity tb_and_gate is end entity;

architecture sim of tb_and_gate is
  signal a, b, y : std_logic := '0';
begin
  dut : entity work.and_gate port map (a => a, b => b, y => y);

  stim : process
  begin
    a <= '0'; b <= '0'; wait for 10 ns;
    assert y = '0' report "00 failed" severity error;

    a <= '0'; b <= '1'; wait for 10 ns;
    assert y = '0' report "01 failed" severity error;

    a <= '1'; b <= '0'; wait for 10 ns;
    assert y = '0' report "10 failed" severity error;

    a <= '1'; b <= '1'; wait for 10 ns;
    assert y = '1' report "11 failed" severity error;

    report "ALL TESTS DONE";
    wait;
  end process;
end architecture;
