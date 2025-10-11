
def modulo10(number: int) -> int:
    """
    Computes the Modulo-10 checksum for a numeric string.
    The input must contain only digits 0–9.
    """

    table = [0, 9, 4, 6, 8, 2, 7, 1, 3, 5]
    carry = 0

    for ch in str(number):
        carry = table[(carry + int(ch)) % 10]

    return (10 - carry) % 10

def add_checksum(number: int) -> str:
    """
    Adds a Modulo-10 checksum to the given number and returns it as a string.
    """
    checksum = modulo10(number)
    return 10*number+checksum