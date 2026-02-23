import math
import statistics
import decimal
from pathlib import Path
import groq



class Calculator:
    def __init__(self):
        self.history = []

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = decimal.Decimal(a) / decimal.Decimal(b)
        self.history.append(f"{a} / {b} = {result}")
        return result

    def square_root(self, a):
        result = math.sqrt(a)
        self.history.append(f"√{a} = {result}")
        return result

    def average(self, numbers: list):
        result = statistics.mean(numbers)
        self.history.append(f"avg({numbers}) = {result}")
        return result

    def show_history(self):
        for entry in self.history:
            print(entry)


if __name__ == "__main__":
    calc = Calculator()
    print(calc.add(10, 5))
    print(calc.subtract(10, 5))
    print(calc.multiply(10, 5))
    print(calc.divide(10, 3))
    print(calc.square_root(16))
    print(calc.average([1, 2, 3, 4, 5]))
    calc.show_history()