import random
import os

def build_pyramid(initial_row):
    rows = []

    # Generate the pyramid
    for group_size in range(1, len(initial_row) + 1):
        current_row = []
        for start in range(len(initial_row) - group_size + 1):
            combined_bits = "".join(map(str, initial_row[start:start + group_size]))
            combined_value = int(combined_bits, 2)
            current_row.append(combined_value)
        rows.append(current_row)

    return rows

def print_pyramid(rows):
    max_width = len(" ".join(map(str, rows[0]))) * 2  # Calculate the maximum width of the first row
    for row in rows:
        decimal_values = " ".join(str(x) for x in row)
        print(decimal_values.center(max_width))

def main():
    # Initial array with 32 bits set to 1
    initial_row = [1] * 32
    rows = build_pyramid(initial_row)

    print("Initial Pyramid:")
    print_pyramid(rows)
    print("\nPress any key to generate a new random 32-bit number and update the pyramid...")

    while True:
        input()
        os.system('cls' if os.name == 'nt' else 'clear')
        random_value = random.getrandbits(32)
        random_row = [int(bit) for bit in bin(random_value)[2:].zfill(32)]
        rows = build_pyramid(random_row)
        print_pyramid(rows)
        print("\nPress any key to generate a new random 32-bit number and update the pyramid...")

if __name__ == "__main__":
    main()
