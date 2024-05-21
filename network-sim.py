#!/usr/bin/env python3
"""
IP Address and Subnet Mask Trainer Script

This script generates random IP addresses and subnet masks, displays their binary
and decimal representations, and provides information about the subnet, network address,
broadcast address, and addressable range. The script is designed as a training tool
for networking students to practice and understand IP address and subnet mask concepts.

Features:
- Randomly generates IP addresses.
- Determines appropriate subnet masks for private and public IP ranges.
- Displays IP address and subnet mask in both binary and decimal formats.
- Calculates and displays network address, broadcast address, and first and last
  addressable IPs within the subnet.
- Clears the screen between each presentation to focus on the same spots.
- Indicates when the IP address is within a private IP space.
- Ensures a private IP address is generated every 5th turn.
- Allows users to generate new IP addresses and subnets by pressing Enter.

Usage:
Run the script in a terminal. Press Enter to generate a new IP address and subnet mask,
or use Ctrl+C to exit the loop.

Author: [Your Name]
Date: [Current Date]
"""

import random
import ipaddress
import os

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_random_ip():
    """Generates a random IP address."""
    return [random.randint(0, 255) for _ in range(4)]

def generate_random_private_ip():
    """Generates a random private IP address."""
    private_prefix = random.choice([
        [10, random.randint(0, 255), random.randint(0, 255), random.randint(1, 254)],        # Class A
        [172, random.randint(16, 31), random.randint(0, 255), random.randint(1, 254)],       # Class B
        [192, 168, random.randint(0, 255), random.randint(1, 254)]                           # Class C
    ])
    return private_prefix

def generate_random_subnet_mask():
    """Generates a random subnet mask with a length between /8 and /30."""
    mask_length = random.randint(8, 30)
    return ipaddress.IPv4Network((0, mask_length)).netmask.packed

def generate_private_subnet_mask(ip):
    """
    Generates a subnet mask for private IP ranges with recommended lengths.

    Parameters:
    ip (list): The IP address as a list of 4 octets.

    Returns:
    bytes: The subnet mask in binary format.
    """
    if ip[0] == 10:
        mask_length = random.randint(8, 30)  # Class A private range
    elif ip[0] == 172 and 16 <= ip[1] <= 31:
        mask_length = random.randint(12, 30)  # Class B private range
    elif ip[0] == 192 and ip[1] == 168:
        mask_length = random.randint(16, 30)  # Class C private range
    else:
        mask_length = random.randint(8, 30)  # Public IP
    return ipaddress.IPv4Network((0, mask_length)).netmask.packed

def format_ip(ip):
    """Formats an IP address as a string with periods between octets."""
    return '.'.join(map(str, ip))

def format_subnet_mask(subnet_mask):
    """Formats a subnet mask as a string with periods between octets."""
    return '.'.join(str(octet) for octet in subnet_mask)

def display_ip_info(ip, subnet_mask, turn_counter):
    """
    Displays IP address information in binary and decimal formats.

    Parameters:
    ip (list): The IP address as a list of 4 octets.
    subnet_mask (bytes): The subnet mask in binary format.
    turn_counter (int): The current turn counter.
    """
    cidr = sum(bin(octet).count('1') for octet in subnet_mask)
    network = ipaddress.IPv4Network(f'{ip[0]}.{ip[1]}.{ip[2]}.{ip[3]}/{cidr}', strict=False)

    # Check if the IP is within a private range
    is_private = (ip[0] == 10) or (ip[0] == 172 and 16 <= ip[1] <= 31) or (ip[0] == 192 and ip[1] == 168)

    print(f"\nTurn: {turn_counter}")
    if is_private:
        print("\nNote: This IP address is within a private IP range.")

    print("\nIP Address:")
    print(' '.join(f'{octet:08b}' for octet in ip))
    print(format_ip(ip))

    print("\nSubnet Mask (CIDR /{}):".format(cidr))
    print(' '.join(f'{octet:08b}' for octet in subnet_mask))
    print(format_subnet_mask(subnet_mask))

    print("\nNetwork Address:")
    print(' '.join(f'{octet:08b}' for octet in network.network_address.packed))
    print(network.network_address)

    print("\nClient ID/Address:")
    print(' '.join(f'{octet:08b}' for octet in ip))
    print(format_ip(ip))

    print("\nBroadcast Address:")
    print(' '.join(f'{octet:08b}' for octet in network.broadcast_address.packed))
    print(network.broadcast_address)

    print("\nFirst Addressable IP:")
    first_address = list(network.network_address.packed)
    first_address[-1] += 1
    print(' '.join(f'{octet:08b}' for octet in first_address))
    print(network.network_address + 1)

    print("\nLast Addressable IP:")
    last_address = list(network.broadcast_address.packed)
    last_address[-1] -= 1
    print(' '.join(f'{octet:08b}' for octet in last_address))
    print(network.broadcast_address - 1)

if __name__ == "__main__":
    # Initialize counter
    turn_counter = 0

    # Clear the screen and initialize with a private IP address
    clear_screen()
    ip_address = [192, 168, 1, 1]
    subnet_mask = generate_private_subnet_mask(ip_address)

    # Display the initial IP information
    display_ip_info(ip_address, subnet_mask, turn_counter)
    input("\nPress Enter to generate a new IP address and subnet...")

    while True:
        # Clear the screen
        clear_screen()

        # Increment the turn counter
        turn_counter += 1

        # Generate a random IP address, ensuring a private IP every 5th turn
        if turn_counter % 5 == 0:
            ip_address = generate_random_private_ip()
        else:
            ip_address = generate_random_ip()

        # Determine if the IP is in a private range and generate an appropriate subnet mask
        if (ip_address[0] == 10) or (ip_address[0] == 172 and 16 <= ip_address[1] <= 31) or (ip_address[0] == 192 and ip_address[1] == 168):
            subnet_mask = generate_private_subnet_mask(ip_address)
        else:
            subnet_mask = generate_random_subnet_mask()

        # Display IP information
        display_ip_info(ip_address, subnet_mask, turn_counter)

        # Prompt to generate another IP
        input("\nPress Enter to generate a new IP address and subnet, or Ctrl+C to exit...")
