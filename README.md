# File Combiner

Merge multiple files easily with a friendly GUI interface 🤝

## Features

- **Add Files** via file dialog or drag-and-drop 🖱️
- **Refresh Files** to update the list 🔄
- **Set Save Path** to choose output location 📁
- **Remove Selected Files** when you change your mind ❌
- **Merge All Files** into a single text document 💖
- **Persistent Settings** saved between sessions 🔧
- **Encoding Support** (UTF-8, CP949) for various file types 📄

## Requirements

- Python 3.6 or higher 🐍
- **tkinter** (built-in) for the GUI 🪟
- **tkinterdnd2** (optional) for drag-and-drop support 📦

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/file-combiner.git
   ```
2. (Optional) Install `tkinterdnd2` for drag-and-drop:
   ```bash
   pip install tkinterdnd2
   ```

## Usage

1. Run the app:
   ```bash
   python file_combiner.py
   ```
2. Click **Add Files** ("파일 추가하기 📂") or drag files into the window.
3. (Optional) Click **Refresh Files** ("파일 새로고침 🔄") to reload the list.
4. Click **Set Save Path** ("합칠 경로 지정 📌") to pick an output folder.
5. Click **Merge Files** ("파일 합치기 💖") to generate your combined text file.
6. Your merged file includes a timestamped header, file structure, and full contents ✨

## Settings

User settings are stored in:

```
~/.file_merger/settings.json
```

- `save_path`: last used output file path 📌

## File Format

The merged file consists of:

1. A header with creation timestamp and purpose 🕒
2. A list of all file paths included 📋
3. Dividers and full content of each file, in order ✂️

## Troubleshooting

- **Read Errors**: Check file permissions or encodings 🔍
- **Drag-and-Drop**: Ensure `tkinterdnd2` is installed 🛠️
- **Other Bugs**: Report issues on GitHub Issues 💬

## License

This project is licensed under the MIT License 📝. See [LICENSE](LICENSE) for details.

