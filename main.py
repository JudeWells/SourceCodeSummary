import os
import sys


def is_python_file(file):
    return file.endswith(".py")

def is_markdown_file(file):
    return file.endswith(".md") or 'README' in file

def is_data_file(file):
    return file.endswith(".csv") or file.endswith(".txt")


def is_virtual_env(dir_name):
    return "venv" in dir_name or ".venv" in dir_name


def is_compiled_file(file):
    return file.endswith(".pyc") or file.endswith(".pyo")


def is_standard_file(file):
    standard_files = [".gitignore", "LICENSE", "pyproject.toml"]
    return file in standard_files


def read_csv_head(file_path, max_lines=5):
    with open(file_path, "r") as f:
        head_lines = []
        for _ in range(max_lines):
            line = f.readline()
            if not line:
                break
            head_lines.append(line)
    return ''.join(head_lines)


def generate_repository_summary(input_path, output_path, max_lines=20):
    summary = "Project Structure:\n"

    for root, dirs, files in os.walk(input_path):
        dirs[:] = [d for d in dirs if not is_virtual_env(d)]

        level = root.replace(input_path, '').count(os.sep)
        indent = ' ' * 4 * level
        summary += f"{indent}{os.path.basename(root)}/\n"

        for file in files:
            if is_compiled_file(file) or is_standard_file(file):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, input_path)

            summary += f"{indent}  {file}\n"

            if is_python_file(file) or is_markdown_file(file):
                summary += f"\nFile: {rel_path}\n"
                with open(file_path, "r") as f:
                    content = f.read()
                    summary += f"```python\n{content}\n```\n"
                    summary += "\n" + "-" * 50 + "\n"

            elif is_data_file(file):
                summary += f"\nData File: {rel_path}\n"
                if file.endswith(".csv"):
                    content = read_csv_head(file_path, max_lines)
                    summary += f"```\n{content}\n```\n"
                else:
                    with open(file_path, "r") as f:
                        content = f.read()
                        truncated_content = "\n".join(content.split("\n")[:max_lines])
                        summary += f"```\n{truncated_content}\n...\n```\n"
                summary += "\n" + "-" * 50 + "\n"

    with open(output_path, "w") as output_file:
        output_file.write(summary)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_path> <output_path>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    generate_repository_summary(input_path, output_path)
