import os
from argparse import ArgumentParser

def is_python_file(file):
    return file.endswith(".py") or file.endswith(".sh")

def is_markdown_file(file):
    return file.endswith(".md") or 'README' in file

def is_data_file(file):
    file_endings = [".csv", ".txt", ".json", ".tsv", ".xml", ".yaml"]
    return any([file.endswith(ending) for ending in file_endings])

def is_virtual_env(dir_name, base_dir):
    if "venv" in dir_name or ".venv" in dir_name:# or 'Venv' in dir_name:
        return True
    elif os.path.exists(os.path.join(base_dir, dir_name, "bin")):
        return True

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

def read_head(file_path, max_lines=5):

    with open(file_path, "r") as f:
        if max_lines is None:
            lines = f.readlines()  # Read all lines if max_lines is None
        else:
            lines = []
            for _ in range(max_lines):
                line = f.readline()
                if not line:
                    break  # Stop reading if end of file is reached
                lines.append(line)
    return ''.join(lines)

def generate_repository_summary(input_path, output_path, max_source_lines=5, max_data_lines=5, exclude_dirs=None):
    exclude_dirs = exclude_dirs or []
    summary = "Project Structure:\n"

    for root, dirs, files in os.walk(input_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not is_virtual_env(d, input_path)]

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
                content = read_head(file_path, max_source_lines)
                file_type = "python" if is_python_file(file) else "markdown"
                summary += f"```{file_type}\n{content}\n```\n"
                summary += "\n" + "<END OF FILE>" + "\n"

            elif is_data_file(file):
                summary += f"\nData File: {rel_path}\n"
                if file.endswith(".csv"):
                    content = read_csv_head(file_path, max_data_lines)
                    summary += f"```\n{content}\n```\n"
                else:
                    content = read_head(file_path, max_data_lines)
                    summary += f"```\n{content}\n...\n```\n"
                summary += "\n" + "<END OF FILE>" + "\n"

    if output_path:
        with open(output_path, "w") as output_file:
            output_file.write(summary)
    else:
        print(summary)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_path", help="Path to the repository")
    parser.add_argument("output_path", nargs='?', default=None, help="Path to the output file, if None then print to console")
    parser.add_argument("--max_source_lines", default=None, type=int, help="Maximum number of lines to print from source code files")
    default_excluded_dirs = ["venv", ".venv", ".git", "__pycache__", '.idea', '.vscode', '.pytest_cache', 'wandb']
    parser.set_defaults(exclude_dirs=default_excluded_dirs)
    parser.add_argument("--exclude_dirs", default=default_excluded_dirs, nargs="+", help="Directories to exclude from the summary")
    args = parser.parse_args()
    args.exclude_dirs.extend(default_excluded_dirs)
    generate_repository_summary(args.input_path, args.output_path, max_source_lines=args.max_source_lines,
                                exclude_dirs=args.exclude_dirs)
