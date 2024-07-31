import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import os
import threading
import time
import hashlib
import configparser

class FileDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API图片下载工具--版本1.0.9    By:EscaWorkTeam")

        self.config_filename = "config.ini"
        self.load_config()

        self.texts = {
            '中文': {
                'status_label': '状态: 未开始下载',
                'api_label': 'API链接:',
                'save_dir_label': '保存目录:',
                'browse_button': '浏览...',
                'download_count_label': '下载次数:',
                'download_interval_label': '下载间隔秒数:',
                'download_button': '下载文件',
                'log_toggle_button': '显示日志',
                'progress_label': '已下载0个文件，剩余0个文件，共0个文件',
                'toggle_language_button': 'English',
                'delete_images_button': '删除图片',
                'delete_config_button': '删除配置文件',
                'open_dir_button': '打开下载目录',
                'complete_message': '下载完成，{fail_count}个失败，{success_count}个成功'
            },
            'English': {
                'status_label': 'Status: Not Started',
                'api_label': 'API Link:',
                'save_dir_label': 'Save Directory:',
                'browse_button': 'Browse...',
                'download_count_label': 'Download Count:',
                'download_interval_label': 'Download Interval (s):',
                'download_button': 'Download Files',
                'log_toggle_button': 'Show Log',
                'progress_label': 'Downloaded 0 files, Remaining 0 files, Total 0 files',
                'toggle_language_button': '中文',
                'delete_images_button': 'Delete Images',
                'delete_config_button': 'Delete Config File',
                'open_dir_button': 'Open Download Directory',
                'complete_message': 'Download complete, {fail_count} failed, {success_count} successful'
            }
        }

        self.create_widgets()

    def create_widgets(self):
        self.status_label = tk.Label(self.root, text=self.texts[self.language]['status_label'])
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.api_label = tk.Label(self.root, text=self.texts[self.language]['api_label'])
        self.api_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.api_combobox = ttk.Combobox(self.root, width=47)
        self.api_combobox.grid(row=1, column=1, padx=5, pady=5, columnspan=2)
        self.api_combobox.set(self.api_link)
        self.api_combobox['values'] = tuple(self.api_history)

        self.save_dir_label = tk.Label(self.root, text=self.texts[self.language]['save_dir_label'])
        self.save_dir_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.save_dir_entry = tk.Entry(self.root, width=50)
        self.save_dir_entry.grid(row=2, column=1, padx=5, pady=5)
        self.save_dir_entry.insert(0, self.save_dir)
        self.browse_button = tk.Button(self.root, text=self.texts[self.language]['browse_button'], command=self.browse_directory)
        self.browse_button.grid(row=2, column=2, padx=5, pady=5)

        self.download_count_label = tk.Label(self.root, text=self.texts[self.language]['download_count_label'])
        self.download_count_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.download_count_entry = tk.Entry(self.root, width=10)
        self.download_count_entry.grid(row=3, column=1, padx=5, pady=5)
        self.download_count_entry.insert(0, self.download_count)

        self.download_interval_label = tk.Label(self.root, text=self.texts[self.language]['download_interval_label'])
        self.download_interval_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.download_interval_entry = tk.Entry(self.root, width=10)
        self.download_interval_entry.grid(row=4, column=1, padx=5, pady=5)
        self.download_interval_entry.insert(0, self.download_interval)

        self.download_button = tk.Button(self.root, text=self.texts[self.language]['download_button'], command=self.start_download)
        self.download_button.grid(row=5, column=0, columnspan=3, pady=10)

        self.progress_label = tk.Label(self.root, text=self.texts[self.language]['progress_label'])
        self.progress_label.grid(row=6, column=0, columnspan=3, pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=7, column=0, columnspan=3, pady=10)

        self.progress_percentage_label = tk.Label(self.root, text="0%")
        self.progress_percentage_label.grid(row=8, column=0, columnspan=3, pady=5)

        self.log_frame = tk.Frame(self.root)
        self.log_frame.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

        self.log_toggle_button = tk.Button(self.root, text=self.texts[self.language]['log_toggle_button'], command=self.toggle_log)
        self.log_toggle_button.grid(row=10, column=0, columnspan=3, pady=5)

        self.log_text = tk.Text(self.log_frame, height=10, width=60)
        self.log_text.pack()
        self.log_text.config(state=tk.DISABLED)

        self.log_frame.grid_remove()  # 初始时隐藏日志框

        self.toggle_language_button = tk.Button(self.root, text=self.texts[self.language]['toggle_language_button'], command=self.toggle_language)
        self.toggle_language_button.grid(row=11, column=2, padx=5, pady=5, sticky=tk.E)

        self.delete_images_button = tk.Button(self.root, text=self.texts[self.language]['delete_images_button'], command=self.delete_images)
        self.delete_images_button.grid(row=12, column=0, padx=5, pady=5)

        self.delete_config_button = tk.Button(self.root, text=self.texts[self.language]['delete_config_button'], command=self.delete_config_file)
        self.delete_config_button.grid(row=12, column=1, padx=5, pady=5)

        self.open_dir_button = tk.Button(self.root, text=self.texts[self.language]['open_dir_button'], command=self.open_download_directory)
        self.open_dir_button.grid(row=12, column=2, padx=5, pady=5)

    def load_config(self):
        if not os.path.exists(self.config_filename):
            self.api_link = ""
            self.save_dir = ""
            self.download_count = "1"
            self.download_interval = "1"  # 默认下载间隔为1秒
            self.language = '中文'  # 默认语言为中文
            self.api_history = []
            self.save_config()
        else:
            config = configparser.ConfigParser()
            config.read(self.config_filename)
            self.api_link = config.get("Settings", "api_link", fallback="")
            self.save_dir = config.get("Settings", "save_dir", fallback="")
            self.download_count = config.get("Settings", "download_count", fallback="1")
            self.download_interval = config.get("Settings", "download_interval", fallback="1")
            self.language = config.get("Settings", "language", fallback="中文")
            self.api_history = config.get("Settings", "api_history", fallback="").split(',')

    def save_config(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'api_link': self.api_link,
            'save_dir': self.save_dir,
            'download_count': self.download_count,
            'download_interval': self.download_interval,
            'language': self.language,
            'api_history': ','.join(self.api_history)
        }
        with open(self.config_filename, 'w') as configfile:
            config.write(configfile)

    def browse_directory(self):
        save_dir = filedialog.askdirectory()
        if save_dir:
            self.save_dir_entry.delete(0, tk.END)
            self.save_dir_entry.insert(0, save_dir)

    def open_download_directory(self):
        if os.path.exists(self.save_dir):
            os.startfile(self.save_dir)
        else:
            messagebox.showerror("错误", "保存目录不存在！" if self.language == '中文' else "Save directory does not exist!")

    def delete_images(self):
        confirmation = messagebox.askyesno(
            "确认删除", 
            "您确定要删除保存目录中的所有图片吗？" if self.language == '中文' else "Are you sure you want to delete all .png files in the save directory?"
        )
        if confirmation:
            try:
                files = os.listdir(self.save_dir)
                for file in files:
                    file_path = os.path.join(self.save_dir, file)
                    if file.lower().endswith('.png') and os.path.isfile(file_path):
                        os.remove(file_path)
                self.log_message("所有图片文件已删除！" if self.language == '中文' else "All image files have been deleted!")
            except Exception as e:
                self.log_message(f"删除图片文件时出错：{e}" if self.language == '中文' else f"Error deleting image files: {e}")

    def delete_config_file(self):
        confirmation = messagebox.askyesno(
            "确认删除", 
            "您确定要删除配置文件吗？" if self.language == '中文' else "Are you sure you want to delete the config file?"
        )
        if confirmation:
            try:
                os.remove(self.config_filename)
                self.log_message("配置文件已删除！" if self.language == '中文' else "Config file has been deleted!")
            except Exception as e:
                self.log_message(f"删除配置文件时出错：{e}" if self.language == '中文' else f"Error deleting config file: {e}")

    def toggle_log(self):
        if self.log_frame.winfo_ismapped():
            self.log_frame.grid_remove()
            self.log_toggle_button.config(text=self.texts[self.language]['log_toggle_button'])
        else:
            self.log_frame.grid()
            self.log_toggle_button.config(text=self.texts[self.language]['log_toggle_button'])

    def toggle_language(self):
        self.language = '中文' if self.language == 'English' else 'English'
        self.save_config()
        self.refresh_ui()

    def refresh_ui(self):
        self.status_label.config(text=self.texts[self.language]['status_label'])
        self.api_label.config(text=self.texts[self.language]['api_label'])
        self.save_dir_label.config(text=self.texts[self.language]['save_dir_label'])
        self.browse_button.config(text=self.texts[self.language]['browse_button'])
        self.download_count_label.config(text=self.texts[self.language]['download_count_label'])
        self.download_interval_label.config(text=self.texts[self.language]['download_interval_label'])
        self.download_button.config(text=self.texts[self.language]['download_button'])
        self.progress_label.config(text=self.texts[self.language]['progress_label'])
        self.log_toggle_button.config(text=self.texts[self.language]['log_toggle_button'])
        self.toggle_language_button.config(text=self.texts[self.language]['toggle_language_button'])
        self.delete_images_button.config(text=self.texts[self.language]['delete_images_button'])
        self.delete_config_button.config(text=self.texts[self.language]['delete_config_button'])
        self.open_dir_button.config(text=self.texts[self.language]['open_dir_button'])

    def start_download(self):
        self.api_link = self.api_combobox.get().strip()
        self.save_dir = self.save_dir_entry.get().strip()
        self.download_count = self.download_count_entry.get().strip()
        self.download_interval = self.download_interval_entry.get().strip()

        if not self.api_link or not self.save_dir or not self.download_count or not self.download_interval:
            messagebox.showerror("错误", "所有字段都是必填的！" if self.language == '中文' else "All fields are required!")
            return

        try:
            self.download_count = int(self.download_count)
            self.download_interval = float(self.download_interval)
        except ValueError:
            messagebox.showerror("错误", "下载次数和下载间隔必须是数字！" if self.language == '中文' else "Download count and interval must be numeric!")
            return

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        if self.api_link not in self.api_history:
            self.api_history.append(self.api_link)

        self.save_config()

        self.progress["value"] = 0
        self.progress["maximum"] = self.download_count
        self.progress_label.config(text=self.texts[self.language]['progress_label'])
        self.progress_percentage_label.config(text="0%")
        self.status_label.config(text=self.texts[self.language]['status_label'])

        threading.Thread(target=self.download_files).start()

    def log_message(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.yview(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def download_files(self):
        success_count = 0
        fail_count = 0

        for i in range(self.download_count):
            try:
                response = requests.get(self.api_link)
                response.raise_for_status()

                content_disposition = response.headers.get("Content-Disposition", "")
                filename = content_disposition.split("filename=")[-1].strip('"') if "filename=" in content_disposition else f"image_{int(time.time())}.png"
                file_path = os.path.join(self.save_dir, filename)

                with open(file_path, "wb") as file:
                    file.write(response.content)

                if self.is_duplicate_file(file_path):
                    os.remove(file_path)
                    raise Exception("文件重复，已删除！" if self.language == '中文' else "Duplicate file, deleted!")

                success_count += 1
                self.log_message(f"文件已下载: {file_path}" if self.language == '中文' else f"File downloaded: {file_path}")
            except Exception as e:
                fail_count += 1
                self.log_message(f"下载文件时出错: {e}" if self.language == '中文' else f"Error downloading file: {e}")

            self.progress["value"] += 1
            percentage = (self.progress["value"] / self.download_count) * 100
            self.progress_percentage_label.config(text=f"{percentage:.2f}%")

            remaining_files = self.download_count - self.progress["value"]
            self.progress_label.config(text=f"已下载{self.progress['value']}个文件，剩余{remaining_files}个文件，共{self.download_count}个文件" if self.language == '中文' else f"Downloaded {self.progress['value']} files, Remaining {remaining_files} files, Total {self.download_count} files")

            self.status_label.config(text=self.texts[self.language]['status_label'])
            self.save_config()

            time.sleep(self.download_interval)

        messagebox.showinfo("完成", self.texts[self.language]['complete_message'].format(fail_count=fail_count, success_count=success_count))

    def is_duplicate_file(self, file_path):
        try:
            with open(file_path, "rb") as file:
                file_hash = hashlib.md5(file.read()).hexdigest()

            for existing_file in os.listdir(self.save_dir):
                existing_file_path = os.path.join(self.save_dir, existing_file)
                if existing_file_path != file_path:
                    with open(existing_file_path, "rb") as existing:
                        existing_file_hash = hashlib.md5(existing.read()).hexdigest()
                        if file_hash == existing_file_hash:
                            return True
        except Exception as e:
            self.log_message(f"计算哈希值时出错: {e}" if self.language == '中文' else f"Error calculating hash: {e}")

        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = FileDownloaderApp(root)
    root.mainloop()
