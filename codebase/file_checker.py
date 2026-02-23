# file_reader.py
from pathlib import Path
import requests

class FileReader:
    """
    A simple class to read files safely.
    """

    def __init__(self, base_dir=None):
        """
        :param base_dir: Optional base directory for relative paths.
        """
        self.base_dir = Path(base_dir) if base_dir else None

    def read_text(self, file_path):
        """
        Reads the contents of a text file.

        :param file_path: Path to the file (str or Path)
        :return: Contents of the file as a string
        """
        path = Path(file_path)
        if self.base_dir:
            path = self.base_dir / path

        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {path}")

        return path.read_text(encoding="utf-8")

    def read_lines(self, file_path):
        """
        Reads the file and returns a list of lines.

        :param file_path: Path to the file (str or Path)
        :return: List of strings (lines)
        """
        text = self.read_text(file_path)
        return text.splitlines()


# Example usage:
if __name__ == "__main__":
    reader = FileReader(base_dir=".")
    try:
        content = reader.read_text("calculator.py")
        print("File content preview:")
        print(content[:200])  # print first 200 characters
    except Exception as e:
        print("Error reading file:", e)