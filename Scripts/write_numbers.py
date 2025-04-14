def write_numbers_to_file(filename):
    with open(filename, 'w') as f:
        for i in range(1, 2**28 + 1):
            f.write(f"{i} ")

if __name__ == "__main__":
    write_numbers_to_file("Player-Data/Input-P0-0")