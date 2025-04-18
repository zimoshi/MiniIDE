import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.scrolledtext import ScrolledText
import subprocess
import os
import ast
from pygments import lex
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name
from pygments.token import Token
from openai import OpenAI
import os
import threading
import platform
import pty
import os   
import select
import threading
import pyte
import queue
import sys

client = OpenAI(api_key=os.getenv("CHATWIDGET_OPENAI_API_KEY"))

class MiniIDE(tk.Tk):
    def __init__(self, role, name):
        super().__init__()
        self.role = role
        self.name = name
        self.title("MiniIDE")
        self.geometry("1200x750")
        try:
            if sys.argv[1] == "--iconphoto-v1":
                self.iconphoto(False, tk.PhotoImage(file="appicon.png"))
            elif sys.argv[1] == "--iconphoto-v2":
                self.iconphoto(False, tk.PhotoImage(file="appicon2.png"))
            elif sys.argv[1] == "--iconphoto-v3":
                self.iconphoto(False, tk.PhotoImage(file="appicon3.png"))
            elif sys.argv[1] == "--iconphoto-v4":
                self.iconphoto(False, tk.PhotoImage(file="appicon4.png"))
            else:
                self.iconphoto(False, tk.PhotoImage(file="appicon4.png"))
        except IndexError:
            self.iconphoto(False, tk.PhotoImage(file="appicon4.png"))
        self.configure(bg="#eee")
        self.open_files = {}
        self.dark_mode = False
        self.themes = {
            "light": {
                "bg": "#eee",
                "fg": "black",
                "editor_bg": "white",
                "editor_fg": "black",
                "terminal_bg": "black",
                "terminal_fg": "lime"
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#cccccc",
                "editor_bg": "#2e2e2e",
                "editor_fg": "#ffffff",
                "terminal_bg": "#000000",
                "terminal_fg": "#00ff88"
            }
        }
        self.create_layout()
        self.terminal_process = None
        self.terminal_fd = None
        # self.start_terminal()
        # self.init_terminal()

        self.shell_queue = queue.Queue()
        self.run_shell()  # <-- Make sure this is called after defining shell_queue


    def update_outline(self, code):
        self.outline_list.delete(0, "end")
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    entry = f"{'Class' if isinstance(node, ast.ClassDef) else 'Func'}: {node.name} @ line {node.lineno}"
                    self.outline_list.insert("end", entry)
        except Exception as e:
            self.outline_list.insert("end", f"⚠️ Parse error: {e}")

    def create_layout(self):
        
        
        
        
        # === Top Bar ===
        topbar = tk.Frame(self, bg="#ddd", height=40)
        topbar.pack(side="top", fill="x")
        
        ttk.Button(topbar, text="📁 Open Folder [beta]", command=self.open_folder).pack(side="left", padx=5, pady=5)
        ttk.Button(topbar, text="🌙 Toggle Theme", command=self.toggle_theme).pack(side="left", padx=5, pady=5)
        ttk.Button(topbar, text="Open", command=self.open_file).pack(side="left", padx=5, pady=5)
        tk.Label(topbar, text=f"Welcome, {self.name}!", bg="#f5f5f5").pack(anchor="w", padx=5)
        self.search_entry = ttk.Entry(topbar)
        self.search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        ttk.Button(topbar, text="Search", command=self.search_text).pack(side="left", padx=5, pady=5)
        ttk.Button(topbar, text="Reset", command=self.resetter).pack(side="left", padx=5, pady=5)

        # === Resizable Paned Layout ===
        main_pane = ttk.PanedWindow(self, orient="horizontal")
        main_pane.pack(fill="both", expand=True)

        # Left Sidebar
        sidebar = tk.Frame(main_pane, width=200, bg="#f5f5f5")
        main_pane.add(sidebar, weight=0)

        self.file_list = tk.Listbox(sidebar)
        self.file_list.pack(fill="both", expand=True, padx=5, pady=5)
        tk.Label(sidebar, text="Outline", bg="#f5f5f5").pack(anchor="w", padx=5)
        self.outline_list = tk.Listbox(sidebar, height=8)
        self.outline_list.pack(fill="x", padx=5, pady=5)
        self.outline_list.bind("<<ListboxSelect>>", self.jump_to_outline)
        ttk.Button(sidebar, text="▶ Run", command=self.run_code).pack(fill="x", padx=5, pady=2)
        ttk.Button(sidebar, text="Save", command=self.save_file).pack(fill="x", padx=5, pady=2)

        # Center Pane (Editor + Terminal)
        center_pane = ttk.PanedWindow(main_pane, orient="vertical")
        main_pane.add(center_pane, weight=1)

        # Editor and MiniAI Panes
        editor_ai_pane = ttk.PanedWindow(center_pane, orient="horizontal")
        center_pane.add(editor_ai_pane, weight=3)

        # Editor Panel
        editor_frame = tk.Frame(editor_ai_pane)
        self.notebook = ttk.Notebook(editor_frame)
        self.notebook.pack(fill="both", expand=True)
        editor_ai_pane.add(editor_frame, weight=3)

        # AI Panel
        ai_pane = tk.Frame(editor_ai_pane, bg="#f0f0f0")
        editor_ai_pane.add(ai_pane, weight=1)

        tk.Label(ai_pane, text="MiniAI", bg="#f0f0f0").pack(anchor="n", pady=5)
        self.ai_box = ScrolledText(ai_pane, height=20, state="disabled")
        self.ai_box.pack(fill="both", expand=True, padx=5, pady=5)

        self.ai_panel = tk.Frame(ai_pane, bg="#f9f9f9", relief="sunken", borderwidth=1)
        self.ai_panel.pack(fill="both", expand=False)
        tk.Label(self.ai_panel, text="MiniAI").pack(anchor="w", padx=5, pady=(5, 0))
        self.ai_input = tk.Text(self.ai_panel, height=3, wrap="word")
        self.ai_input.pack(fill="x", padx=5)
        tk.Button(self.ai_panel, text="Send", command=self.ask_ai).pack(padx=5, pady=3)
        self.ai_output = ScrolledText(self.ai_panel, height=10, wrap="word", state="disabled")
        self.ai_output.pack(fill="both", expand=True, padx=5, pady=5)
        self.ai_input.bind("<Return>", lambda e: (self.ask_ai(), "break"))

        # Terminal Panel
        terminal_frame = tk.Frame(center_pane, bg="#ddd", height=120)
        self.output_box = ScrolledText(terminal_frame, height=6, bg="black", fg="lime", insertbackground="white")
        self.output_box.pack(fill="both", expand=True, padx=5, pady=2)
        center_pane.add(terminal_frame, weight=1)

        
        # # === Main Area ===
        # main_area = tk.Frame(self)
        # main_area.pack(fill="both", expand=True)

        # # === Sidebar (Left) ===
        # sidebar = tk.Frame(main_area, width=200, bg="#f5f5f5")
        # sidebar.pack(side="left", fill="y")

        # self.file_list = tk.Listbox(sidebar)
        # self.file_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # tk.Label(sidebar, text="Outline", bg="#f5f5f5").pack(anchor="w", padx=5)
        # self.outline_list = tk.Listbox(sidebar, height=8)
        # self.outline_list.pack(fill="x", padx=5, pady=5)
        # self.outline_list.bind("<<ListboxSelect>>", self.jump_to_outline)

        # # === Resizable Paned Layout ===
        # paned = ttk.PanedWindow(main_area, orient="horizontal")
        # paned.pack(fill="both", expand=True)

        # # Editor Pane
        # editor_pane = tk.Frame(paned)
        # self.notebook = ttk.Notebook(editor_pane)
        # self.notebook.pack(fill="both", expand=True)
        # paned.add(editor_pane, weight=3)

        # # AI Pane
        # ai_pane = tk.Frame(paned, bg="#f0f0f0")
        # paned.add(ai_pane, weight=1)

        # # Add MiniAI widgets to ai_pane
        # tk.Label(ai_pane, text="MiniAI", bg="#f0f0f0").pack(anchor="n", pady=5)
        # self.ai_box = ScrolledText(ai_pane, height=20, state="disabled")
        # self.ai_box.pack(fill="both", expand=True, padx=5, pady=5)

        # self.ai_panel = tk.Frame(ai_pane, bg="#f9f9f9", relief="sunken", borderwidth=1)
        # self.ai_panel.pack(fill="both", expand=False)
        # tk.Label(self.ai_panel, text="MiniAI").pack(anchor="w", padx=5, pady=(5, 0))
        # self.ai_input = tk.Text(self.ai_panel, height=3, wrap="word")
        # self.ai_input.pack(fill="x", padx=5)
        # tk.Button(self.ai_panel, text="Send", command=self.ask_ai).pack(padx=5, pady=3)
        # self.ai_output = ScrolledText(self.ai_panel, height=10, wrap="word", state="disabled")
        # self.ai_output.pack(fill="both", expand=True, padx=5, pady=5)
        # self.ai_input.bind("<Return>", lambda e: (self.ask_ai(), "break"))


        # # mini_ai = tk.Frame(main_area, width=200, bg="#f0f0f0")
        # # mini_ai.pack(side="right", fill="y")
        # # # tk.Label(mini_ai, text="MiniAI", bg="#f0f0f0").pack(anchor="n", pady=5)
        # # # self.ai_box = ScrolledText(mini_ai, height=20, state="disabled")
        # # # self.ai_box.pack(fill="both", expand=True, padx=5, pady=5)
        # # # Create the MiniAI panel inside the right pane or bottom1
        # # self.ai_panel = tk.Frame(right_pane, bg="#f9f9f9", relief="sunken", borderwidth=1)
        # # self.ai_panel.pack(side="bottom", fill="both", expand=False)


        # # tk.Label(self.ai_panel, text="MiniAI").pack(anchor="w", padx=5, pady=(5, 0))

        # # self.ai_input = tk.Text(self.ai_panel, height=3, wrap="word")
        # # self.ai_input.pack(fill="x", padx=5)

        # # tk.Button(self.ai_panel, text="Send", command=self.ask_ai).pack(padx=5, pady=3)

        # # self.ai_output = ScrolledText(self.ai_panel, height=10, wrap="word", state="disabled")
        # # self.ai_output.pack(fill="both", expand=True, padx=5, pady=5)
        
        # # self.ai_input.bind("<Return>", lambda e: (self.ask_ai(), "break"))


        # === Bottom Terminal & Status Bar ===
        bottom = tk.Frame(self, bg="#ddd", height=10)
        bottom.pack(side="bottom", fill="x")

        # # Terminal Output
        # self.output_box = ScrolledText(bottom, height=6, bg="black", fg="lime", insertbackground="white")
        # self.output_box.pack(fill="both", expand=True, padx=5, pady=2)
        # self.output_box.bind("<Return>", self.send_command)

        status = tk.Label(self, text="Line 1, Column 1 | UTF-8 | Python | MiniIDE", anchor="w")
        status.pack(side="bottom", fill="x")

        # # === Buttons on Sidebar ===
        # ttk.Button(sidebar, text="▶ Run", command=self.run_code).pack(fill="x", padx=5, pady=2)
        # ttk.Button(sidebar, text="Save", command=self.save_file).pack(fill="x", padx=5, pady=2)
        
        # === Bind functions ===
        if self.role == "User":
            self.disable_user_restricted_features()
        elif self.role == "Developer":
            self.restrict_admin_only()


    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py"), ("All Files", "*.*")])
        if path and path not in self.open_files:
            with open(path, 'r') as f:
                content = f.read()

            frame = ttk.Frame(self.notebook)
            editor = ScrolledText(frame)
            editor.insert("1.0", content)
            editor.pack(fill="both", expand=True)
            self.notebook.add(frame, text=os.path.basename(path))

            self.open_files[path] = {
            "editor": editor,
            "frame": frame
            }

            self.file_list.insert("end", os.path.basename(path))
            editor.bind("<KeyRelease>", lambda e: self.update_outline(editor.get("1.0", "end-1c")))
            editor.bind("<KeyRelease>", lambda e: [
                self.update_outline(editor.get("1.0", "end-1c")),
                self.highlight_code(editor)
            ])
            self.highlight_code(editor)
            self.update_outline(content)

    def run_code(self):
        try:
            path = self.get_current_path()
            editor = self.open_files[path]["editor"]
        except Exception:
            self.output_box.insert("1.0", "❌ Could not retrieve editor.\n")
            return

        code = editor.get("1.0", "end-1c")
        with open(".miniide/run.mfx", "w") as f:
            f.write(code)

        result = subprocess.run(["python3", ".miniide/run.mfx"], capture_output=True, text=True)
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", result.stdout + result.stderr)




    def save_file(self):
        current_tab = self.notebook.select()
        if not current_tab:
            return
        editor = self.notebook.nametowidget(current_tab).winfo_children()[0]
        path = filedialog.asksaveasfilename(defaultextension=".py")
        if path:
            with open(path, "w") as f:
                f.write(editor.get("1.0", "end-1c"))
            self.output_box.insert("1.0", f"✅ Saved: {path}\n")

    # def search_text(self):
    #     query = self.search_entry.get()
    #     self.output_box.insert("1.0", f"🔍 Search: {query} (coming soon)\n")
    
    def get_current_path(self):
        current_index = self.notebook.index(self.notebook.select())
        return list(self.open_files.keys())[current_index]
    
    def jump_to_outline(self, event):
        selection = self.outline_list.curselection()
        if not selection:
            return

        line_text = self.outline_list.get(selection[0])
        if "@ line" in line_text:
            try:
                lineno = int(line_text.split("@ line")[1].strip())
                path = self.get_current_path()
                editor = self.open_files[path]["editor"]
                editor.see(f"{lineno}.0")
                editor.mark_set("insert", f"{lineno}.0")
            except Exception:
                pass

    def highlight_code(self, editor):
        code = editor.get("1.0", "end-1c")
        for tag in editor.tag_names():
            editor.tag_remove(tag, "1.0", "end")

        lines = code.splitlines()
        for lineno, line in enumerate(lines, start=1):
            index = 0
            for token, content in lex(line, PythonLexer()):
                if content.strip() == "":
                    index += len(content)
                    continue
                tag = str(token)
                color = self.get_color(token)
                editor.tag_configure(tag, foreground=color)
                start = f"{lineno}.{index}"
                end = f"{lineno}.{index + len(content)}"
                editor.tag_add(tag, start, end)
                index += len(content)



    def get_color(self, token):
        return {
            Token.Keyword: "blue",
            Token.Name.Builtin: "purple",
            Token.Literal.String: "green",
            Token.Comment: "gray",
            Token.Operator: "red",
            Token.Name.Function: "#d35400",
            Token.Name.Class: "#2980b9"
        }.get(token, "black")

    def ask_ai(self):
        prompt = self.ai_input.get("1.0", "end-1c").strip()
        if not prompt:
            return

        # Get editor content (optional)
        try:
            path = self.get_current_path()
            editor = self.open_files[path]["editor"]
            file_content = editor.get("1.0", "end-1c").strip()
        except Exception:
            file_content = None

        messages = [{"role": "system", "content": "You are a helpful coding assistant inside a mini IDE."}]
        if file_content:
            messages.append({"role": "user", "content": f"The user is editing this file:\n\n{file_content}"})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"❌ Error: {e}"

        # Latest result
        self.ai_output.config(state="normal")
        self.ai_output.delete("1.0", "end")
        self.ai_output.insert("1.0", reply)
        self.ai_output.config(state="disabled")

        # Append to history
        self.ai_box.config(state="normal")
        self.ai_box.insert("end", f">> {prompt}\n{reply}\n\n")
        self.ai_box.see("end")
        self.ai_box.config(state="disabled")



    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        theme = self.themes["dark" if self.dark_mode else "light"]

        self.configure(bg=theme["bg"])
        for widget in self.winfo_children():
            widget.configure(bg=theme["bg"])
        
        # Update editors
        for data in self.open_files.values():
            editor = data["editor"]
            editor.configure(bg=theme["editor_bg"], fg=theme["editor_fg"], insertbackground=theme["editor_fg"])

        # Update terminal
        self.output_box.configure(bg=theme["terminal_bg"], fg=theme["terminal_fg"], insertbackground=theme["terminal_fg"])

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if not folder_path:
            return
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".py"):  # optionally filter to only Python files
                    full_path = os.path.join(root, file)
                    if full_path not in self.open_files:
                        with open(full_path, 'r') as f:
                            content = f.read()

                        frame = ttk.Frame(self.notebook)
                        editor = ScrolledText(frame)
                        editor.insert("1.0", content)
                        editor.pack(fill="both", expand=True)
                        self.notebook.add(frame, text=os.path.basename(full_path))

                        self.open_files[full_path] = {
                            "editor": editor,
                            "frame": frame
                        }

                        self.file_list.insert("end", os.path.basename(full_path))
                        editor.bind("<KeyRelease>", lambda e: self.update_outline(editor.get("1.0", "end-1c")))
                        editor.bind("<KeyRelease>", lambda e: [
                            self.update_outline(editor.get("1.0", "end-1c")),
                            self.highlight_code(editor)
                        ])
                        self.highlight_code(editor)
                        self.update_outline(content)
                        
                        
    def search_text(self):
        query = self.search_entry.get()
        if not query:
            return

        try:
            path = self.get_current_path()
            editor = self.open_files[path]["editor"]
        except Exception:
            self.output_box.insert("1.0", "❌ No file is currently open.\n")
            return

        editor.tag_remove("search_highlight", "1.0", "end")
        count = 0
        start = "1.0"

        while True:
            pos = editor.search(query, start, stopindex="end", nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(query)}c"
            editor.tag_add("search_highlight", pos, end_pos)
            start = end_pos
            count += 1

        editor.tag_config("search_highlight", background="yellow", foreground="black")
        self.output_box.insert("1.0", f"🔍 Found {count} match(es) for '{query}'.\n")

    def resetter(self):
        try:
            editor = self.open_files[self.get_current_path()]["editor"]
            editor.tag_remove("search_highlight", "1.0", "end")
        except Exception:
            pass

    def start_terminal(self):
        system = platform.system()
        if system in ["Linux", "Darwin"]:  # Unix/macOS
            import pty
            pid, fd = pty.fork()
            if pid == 0:
                os.execvp("zsh", ["zsh"])
            else:
                self.terminal_fd = fd
                threading.Thread(target=self.read_unix_terminal, daemon=True).start()
        elif system == "Windows":
            import subprocess
            self.terminal_process = subprocess.Popen(
                ["powershell.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            threading.Thread(target=self.read_windows_terminal, daemon=True).start()

    def read_unix_terminal(self):
        while True:
            try:
                data = os.read(self.terminal_fd, 1024).decode(errors="ignore")
                self.output_box.insert("end", data)
                self.output_box.see("end")
            except Exception:
                break

    def read_windows_terminal(self):
        while True:
            try:
                data = self.terminal_process.stdout.readline()
                self.output_box.insert("end", data)
                self.output_box.see("end")
            except Exception:
                break

    # def send_command(self, event):
    #     line = self.output_box.get("insert linestart", "insert lineend").strip()
    #     if not line:
    #         return "break"
    #     system = platform.system()
    #     if system in ["Linux", "Darwin"]:
    #         os.write(self.terminal_fd, (line + "\n").encode())
    #     elif system == "Windows" and self.terminal_process:
    #         self.terminal_process.stdin.write(line + "\n")
    #         self.terminal_process.stdin.flush()
    #     return "break"

    def init_terminal(self):
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream()
        self.stream.attach(self.screen)

        self.master_fd, self.slave_fd = pty.openpty()
        self.terminal_thread = threading.Thread(target=self.terminal_loop, daemon=True)
        self.terminal_thread.start()

        self.output_box.bind("<Key>", self.send_input_to_terminal)

    def terminal_loop(self):
        while True:
            r, _, _ = select.select([self.master_fd], [], [], 0.1)
            if self.master_fd in r:
                output = os.read(self.master_fd, 1024).decode(errors="ignore")
                self.stream.feed(output)
                display_text = "\n".join(self.screen.display)
                self.output_box.after(0, lambda: self.update_terminal_display(display_text))

    def update_terminal_display(self, text):
        self.output_box.config(state="normal")
        self.output_box.delete("1.0", "end")
        self.output_box.insert("1.0", text)
        self.output_box.config(state="disabled")

    def send_input_to_terminal(self, event):
        os.write(self.master_fd, event.char.encode())
        return "break"  # Prevent tkinter from adding the char itself

    def run_shell(self):
        try:
            self.terminal_proc = subprocess.Popen(
                ["/bin/zsh"],  # or "/bin/bash"
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            threading.Thread(target=self.read_terminal_output, daemon=True).start()
        except Exception as e:
            self.output_box.insert("end", f"❌ Terminal error: {e}\n")

    def read_terminal_output(self):
        for line in self.terminal_proc.stdout:
            self.output_box.insert("end", line)
            self.output_box.see("end")

    def send_command(self, event=None):
        cmd = self.output_box.get("insert linestart", "insert lineend") + "\n"
        try:
            self.terminal_proc.stdin.write(cmd)
            self.terminal_proc.stdin.flush()
        except Exception as e:
            self.output_box.insert("end", f"❌ Write error: {e}\n")

    def run_shell(self):
        self.terminal_proc = subprocess.Popen(
            ["/bin/zsh"],  # or "bash"
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        threading.Thread(target=self.read_shell_output, daemon=True).start()
        threading.Thread(target=self.write_shell_input, daemon=True).start()

    def read_shell_output(self):
        for line in self.terminal_proc.stdout:
            self.output_box.insert("end", line)
            self.output_box.see("end")

    def write_shell_input(self):
        while True:
            cmd = self.shell_queue.get()
            if cmd is None:
                break
            try:
                self.terminal_proc.stdin.write(cmd + "\n")
                self.terminal_proc.stdin.flush()
            except Exception as e:
                self.output_box.insert("end", f"❌ {e}\n")

    def send_command(self, event=None):
        line = self.output_box.get("insert linestart", "insert lineend").strip()
        self.shell_queue.put(line)
        return "break"  # Prevent newline insertion

    def disable_user_restricted_features(self):
        # Disable or hide buttons or panels for regular users
        # Example:
        self.ai_panel.pack_forget()
        self.output_box.insert("1.0", "🔒 AI Assistant disabled for regular users.\n")

    def restrict_admin_only(self):
        # Hide admin-only features, but allow more than regular users
        # You can customize this based on feature sets
        pass

    # You can also apply role restrictions in other methods if needed
    # def run_code(self):
    #     if self.role == "User":
    #         self.output_box.insert("1.0", "❌ Running code is restricted for your role.\n")
    #         return
    #     super().run_code()

