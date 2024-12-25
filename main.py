import tkinter as tk
from tkinter import messagebox, simpledialog, Listbox, Scrollbar, Text, Button, Toplevel, scrolledtext, filedialog
import subprocess
import os
import markdown
import tempfile
import webbrowser

class HexoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hexo GUI")
        self.root.geometry("700x500")

        # Initialize server_process as None
        self.server_process = None

        # Left Frame for Buttons
        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.label = tk.Label(self.left_frame, text="Hexo Blog Manager", font=("Arial", 16))
        self.label.pack(pady=20)

        self.new_post_button = tk.Button(self.left_frame, text="Hexo New Post", command=self.create_new_post)
        self.new_post_button.pack(pady=10)

        self.generate_button = tk.Button(self.left_frame, text="Hexo Generate", command=self.generate_blog)
        self.generate_button.pack(pady=10)

        self.server_button = tk.Button(self.left_frame, text="Hexo Serve", command=self.server_blog)
        self.server_button.pack(pady=10)

        self.deploy_button = tk.Button(self.left_frame, text="Hexo Deploy", command=self.deploy_blog)
        self.deploy_button.pack(pady=10)
        
        self.clean_button = tk.Button(self.left_frame, text="Hexo Clean", command=self.clean_blog)
        self.clean_button.pack(pady=10)
        
        self.exit_button = tk.Button(self.left_frame, text="Exit", command=self.exit_system)
        self.exit_button.pack(pady=10)

        # Right Frame for Listbox
        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Label for Contents
        self.contents_label = tk.Label(self.right_frame, text="Contents", font=("Arial", 12))
        self.contents_label.pack(pady=5)

        self.listbox = Listbox(self.right_frame, width=50, height=20)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(self.right_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # Bind double-click event to open file with Typora
        self.listbox.bind("<Double-1>", self.open_with_typora)

        self.update_source_list()

    def run_hexo_command(self, command):
        try:
            result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            messagebox.showinfo("Success", result.stdout.decode())
            self.update_source_list()  # Update the list after running a command
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", e.stderr.decode())

    def create_new_post(self):
        title = simpledialog.askstring("Input", "Enter post title:")
        if title:
            command = f"hexo new {title}"
            self.run_hexo_command(command)

    def generate_blog(self):
        command = "hexo generate"
        self.run_hexo_command(command)

    def create_server_window(self):
        """
        创建并配置服务器窗口及其组件.
        """
        self.server_window = Toplevel(self.root)
        self.server_window.title("Hexo Server")
        self.server_window.geometry("600x400")

        self.server_output = Text(self.server_window, wrap='word', height=20, width=70)
        self.server_output.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.stop_button = Button(self.server_window, text="Stop Server", command=self.stop_server)
        self.stop_button.pack(pady=10)
        
    def server_blog(self):
        self.server_process = subprocess.Popen(["powershell", "-Command", "hexo serve"])
        
    def create_stop_button(self):
        if self.server_stop_button is None:
            self.server_stop_button = tk.Button(self.left_frame, text="Stop Server", command=self.stop_server)
            self.server_stop_button.pack(pady=10)

    def deploy_blog(self):
        command = "hexo deploy"
        self.run_hexo_command(command)

    def clean_blog(self):
        command = "hexo clean"
        self.run_hexo_command(command)

    def update_source_list(self):
        self.listbox.delete(0, tk.END)
        source_dir = "source/_posts"
        if os.path.exists(source_dir) and os.path.isdir(source_dir):
            for item in os.listdir(source_dir):
                self.listbox.insert(tk.END, item)

    def open_with_typora(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_file = self.listbox.get(selected_index)
            file_path = os.path.join("source/_posts", selected_file)
            if os.path.isfile(file_path):
                self.open_markdown_editor(file_path)

    def open_markdown_editor(self, file_path):
        editor_window = Toplevel(self.root)
        editor_window.title(f"Edit {os.path.basename(file_path)}")
        editor_window.geometry("800x600")

        # Create a scrolled text widget for editing Markdown
        self.text_area = scrolledtext.ScrolledText(editor_window, wrap=tk.WORD, font=("Arial", 12))
        self.text_area.pack(expand=True, fill=tk.BOTH)

        # Load the file content into the text area
        with open(file_path, 'r', encoding='utf-8') as file:
            self.text_area.insert(tk.END, file.read())

        # Create a preview button
        preview_button = Button(editor_window, text="Preview", command=lambda: self.preview_markdown(editor_window, self.text_area.get("1.0", tk.END)))
        preview_button.pack(pady=10)

        # Create a save button
        save_button = Button(editor_window, text="Save", command=lambda: self.save_markdown(file_path, self.text_area.get("1.0", tk.END)))
        save_button.pack(pady=10)

    def preview_markdown(self, editor_window, markdown_text):
        # Convert Markdown to HTML
        html_content = markdown.markdown(markdown_text)

        # Create a temporary HTML file
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_file_path = temp_file.name

        # Open the HTML file in the default web browser
        webbrowser.open(f'file://{temp_file_path}')

    def save_markdown(self, file_path, markdown_text):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(markdown_text)
        messagebox.showinfo("Success", "File saved successfully.")

    def exit_system(self):
        if self.server_process:
            self.stop_server()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = HexoGUI(root)
    root.mainloop()