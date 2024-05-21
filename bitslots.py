#!/usr/bin/env python3

"""
This script simulates a bit-pyramid slot machine game. It initializes the game state,
performs random draws to generate a 32-bit number, and parses this number into four 7-bit
registers and one 4-bit bonus register. The script then displays the bit pyramid of these
values. After the fifth random draw, it simulates various jackpot conditions, displays
them, and then returns to random draws for the duration of the game.

Jackpot Conditions:
- Super Mega Jackpot: All 1's in all 5 registers.
- Fools Jackpot: All 0's in all 5 registers.
- Mega Jackpot: All 1's in the 4 main registers, all 0's in the bonus register.
- Super Jackpot: All 0's in the 4 main registers, all 1's in the bonus register.
- Double Slit Experiment Jackpot: Alternating 1's and 0's throughout all registers in either order but must be continuous through all 4 registers and into the bonus.
"""

import random
import os

def random_32bit_number():
    """Generates a random 32-bit number."""
    return random.getrandbits(32)

def parse_registers_from_32bit(num):
    """
    Parses a 32-bit number into four 7-bit registers and one 4-bit bonus register.

    Args:
    num (int): The 32-bit number to parse.

    Returns:
    tuple: A tuple containing the list of four 7-bit registers and one 4-bit bonus register.
    """
    registers = [(num >> (7 * i)) & 0b1111111 for i in range(4)]
    bonus_register = (num >> 28) & 0b1111
    return registers, bonus_register

def display_pyramid(registers, bonus_register):
    """
    Displays the bit-pyramid and decimal values from the registers.

    Args:
    registers (list): The list of four 7-bit registers.
    bonus_register (int): The 4-bit bonus register.
    """
    # Convert registers to binary strings
    bit_strings = [f'{reg:07b}' for reg in registers]
    bonus_bit_string = f'{bonus_register:04b}'
    
    # Create the complete binary array for the registers
    complete_binary_array = ''.join(bit_strings)
    
    # Display the complete 32-bit binary number
    full_32bit_string = complete_binary_array + bonus_bit_string
    print(f'Full 32-bit number: {full_32bit_string}')
    
    # Display the bonus register separately
    print(f'Bonus Register: {bonus_bit_string} ({int(bonus_bit_string, 2)})\n')

    # Display the pyramid
    length = len(full_32bit_string)
    for i in range(1, length + 1):
        row = []
        for start in range(length - i + 1):
            row_bits = full_32bit_string[start:start + i]
            decimal_value = int(row_bits, 2)
            if i == 1:
                row.append(f'{row_bits}')
            else:
                row.append(f'{decimal_value}')
        print(' '.join(row).center(120))

def check_jackpot(registers, bonus_register):
    """
    Checks for jackpot conditions based on the current state of the registers.

    Args:
    registers (list): The list of four 7-bit registers.
    bonus_register (int): The 4-bit bonus register.

    Returns:
    str: The name of the jackpot if any, otherwise "No Jackpot".
    """
    if all(reg == 0b1111111 for reg in registers) and bonus_register == 0b1111:
        return "Super Mega Jackpot"
    elif all(reg == 0b0000000 for reg in registers) and bonus_register == 0b0000:
        return "Fools Jackpot"
    elif all(reg == 0b1111111 for reg in registers) and bonus_register == 0b0000:
        return "Mega Jackpot"
    elif all(reg == 0b0000000 for reg in registers) and bonus_register == 0b1111:
        return "Super Jackpot"
    elif check_double_slit_experiment(registers, bonus_register):
        return "Double Slit Experiment Jackpot"
    return "No Jackpot"

def check_double_slit_experiment(registers, bonus_register):
    """
    Checks for the Double Slit Experiment Jackpot condition.

    Args:
    registers (list): The list of four 7-bit registers.
    bonus_register (int): The 4-bit bonus register.

    Returns:
    bool: True if the Double Slit Experiment Jackpot condition is met, otherwise False.
    """
    bit_strings = ''.join(f'{reg:07b}' for reg in registers) + f'{bonus_register:04b}'
    if bit_strings == '01' * 16 or bit_strings == '10' * 16:
        return True
    return False

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    
    # Start by displaying the highest possible win condition (all 1's)
    registers = [0b1111111] * 4
    bonus_register = 0b1111

    print("Initial State (Super Mega Jackpot):")
    display_pyramid(registers, bonus_register)
    print(check_jackpot(registers, bonus_register))

    draw_count = 0
    jackpot_displayed = False

    while True:
        command = input("Press Enter to generate a random draw or type 'exit' to quit: ").strip().lower()
        
        if command == 'exit':
            print("Exiting the game.")
            break
        
        clear_screen()
        
        if draw_count < 5:
            # Perform a single 32-bit random draw and parse the registers
            random_number = random_32bit_number()
            registers, bonus_register = parse_registers_from_32bit(random_number)
        elif draw_count == 5:
            # After 5 random draws, display each jackpot once
            jackpots = [
                ([0b1111111] * 4, 0b1111, "Super Mega Jackpot"),
                ([0b0000000] * 4, 0b0000, "Fools Jackpot"),
                ([0b1111111] * 4, 0b0000, "Mega Jackpot"),
                ([0b0000000] * 4, 0b1111, "Super Jackpot"),
                ([0b1010101, 0b0101010, 0b1010101, 0b0101010], 0b1010, "Double Slit Experiment Jackpot"),
                ([0b0101010, 0b1010101, 0b0101010, 0b1010101], 0b0101, "Double Slit Experiment Jackpot")
            ]
            
            for reg_set, bonus, name in jackpots:
                input(f"Press Enter to display {name}...")
                clear_screen()
                registers = reg_set
                bonus_register = bonus
                print(f"\n{name}:")
                display_pyramid(registers, bonus_register)
                print(name)
            
            jackpot_displayed = True
        else:
            # Continue with normal random draws after displaying jackpots once
            random_number = random_32bit_number()
            registers, bonus_register = parse_registers_from_32bit(random_number)

        draw_count += 1

        print("\nAfter Random Draws:")
        display_pyramid(registers, bonus_register)
        print(check_jackpot(registers, bonus_register))

if __name__ == "__main__":
    main()
