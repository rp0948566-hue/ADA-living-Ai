import os

def read_all_files_in_project(directory="."):
    """
    Reads all text-based files in the project directory and its subdirectories,
    and returns their concatenated content.

    Args:
        directory (str): The root directory of the project. Defaults to the current directory.

    Returns:
        str: A string containing the content of all found files, each prefixed with its path.
    """
    all_files_content = ""
    ignored_dirs = {'.venv', '__pycache__', '.git', 'screenshots', 'memory'}
    ignored_extensions = {'.pyc', '.pyo', '.pyd', '.log', '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.exe', '.dll', '.so', '.chm', '.zip', '.gz'}

    for root, dirs, files in os.walk(directory):
        # Exclude ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_dirs]

        for file in files:
            file_path = os.path.join(root, file)
            _, extension = os.path.splitext(file)

            if extension in ignored_extensions:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    all_files_content += f"--- File: {file_path} ---\n"
                    all_files_content += content
                    all_files_content += "\n\n"
            except Exception as e:
                all_files_content += f"--- Error reading file: {file_path} ---\n"
                all_files_content += f"{str(e)}\n\n"
    
    if not all_files_content:
        return "No readable files found in the project."
        
    return all_files_content

def read_project_files_tool():
    """
    A tool to read and return the content of all files in the current project directory.
    This helps in understanding the entire codebase at once.
    """
    return read_all_files_in_project()


if __name__ == '__main__':
    # For testing purposes
    print(read_project_files_tool())
