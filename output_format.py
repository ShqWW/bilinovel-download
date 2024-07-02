from enum import Enum
from pathlib import Path
import subprocess
import os

class OutputFormat(Enum):
    EPUB = "epub"
    MOBI = "mobi"
    PDF = "pdf"
    TXT = "txt"

def is_valid_format(format):
    return format in [item.value for item in OutputFormat]

def convert_format(original_path, target_format):
    if not os.path.isfile(original_path):
        print(f"{original_path} not a file.")
        return 0, None
    
    target_format = target_format.lower()
    if not is_valid_format(target_format):
        print("Not valid target output format.")
        return 0, None
    
    if target_format=="epub":
        print("The file should be epub file already.")
        return 0, None

    path = Path(original_path)
    file_extension = path.suffix.lower()

    if file_extension!=".epub":
        print("This function allows input be .epub format only")
        return 0, None
    
    output_path = path.parent / path.stem
    output_path = output_path.with_suffix(f".{target_format}")

    print(f"converting output format to .{target_format}")
    
    try:
        subprocess.run(
            ["ebook-convert", original_path, output_path], 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )
        print(f"successfully converted {original_path} to {output_path}")
        return 1, output_path
    except Exception as e:
        print(f"failed to convert {original_path} to {output_path}")
        print(f"error {e}")
        return 0, None