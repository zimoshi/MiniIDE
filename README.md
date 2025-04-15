
# MiniIDE

MiniIDE is a lightweight Python IDE built with Tkinter, designed for simplicity, extensibility, and a touch of AI assistance.

## ✨ Features

- 📝 Tabbed file editor with syntax highlighting (via Pygments)
- 📂 Open individual files or entire folders
- 📜 Outline viewer for Python functions and classes
- 🤖 Built-in AI Assistant (powered by GPT-4o)
- 🔍 Search with inline highlighting
- 💾 Save and run scripts
- 💬 Real terminal support using subprocess
- 🌙 Dark mode toggle (coming soon)

## 🔧 Requirements

- Python 3.8+
- `pygments`
- `openai` (v1.0+)
- Set `CHATWIDGET_OPENAI_API_KEY` in your environment for AI integration

## 🚀 Quick Start

```bash
pip install pygments openai
export CHATWIDGET_OPENAI_API_KEY=your_openai_api_key
python minieditor.py
```

## 📁 Folder Mode

You can open an entire folder, and MiniIDE will list the Python files for quick access and editing.

## 🤝 Contributions

Contributions welcome! Feel free to fork and open a pull request with your improvements or feature ideas.

## 🧠 AI Usage

MiniAI integrates GPT-4o using your API key. It can provide code explanations, refactor suggestions, and more — context-aware based on the current file you're editing.

---

© 2025 [Zimoshi]
