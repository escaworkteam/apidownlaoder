import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import requests
import os
import string
import random
import threading
import time
import configparser

class FileDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("API下载器----作者EscaWorkTeam(escateam.icu)")

        # 配置文件名
        self.config_filename = "config.ini"
        self.load_config()

        # 界面文本字典
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
                'percentage_label': '0%',
                'toggle_language_button': 'English',
                'delete_images_button': '删除图片',
                'delete_config_button': '删除配置文件',
                'open_dir_button': '打开下载目录'
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
                'percentage_label': '0%',
                'toggle_language_button': '中文',
                'delete_images_button': 'Delete Images',
                'delete_config_button': 'Delete Config File',
                'open_dir_button': 'Open Download Directory'
            }
        }

        self.create_widgets()

    def create_widgets(self):
        # 销毁所有现有部件
        for widget in self.root.winfo_children():
            widget.destroy()

        # 状态标签
        self.status_label = tk.Label(self.root, text=self.texts[self.language]['status_label'])
        self.status_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        # API链接标签和输入框
        tk.Label(self.root, text=self.texts[self.language]['api_label']).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.api_combobox = ttk.Combobox(self.root, width=50)
        self.api_combobox.grid(row=1, column=1, padx=5, pady=5, columnspan=2, sticky=tk.W)
        self.api_combobox.set(self.api_link)
        self.api_combobox['values'] = tuple(self.api_history)

        # 保存目录标签、输入框和浏览按钮
        tk.Label(self.root, text=self.texts[self.language]['save_dir_label']).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.save_dir_entry = tk.Entry(self.root, width=50)
        self.save_dir_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.save_dir_entry.insert(0, self.save_dir)
        self.browse_button = tk.Button(self.root, text=self.texts[self.language]['browse_button'], command=self.browse_directory)
        self.browse_button.grid(row=2, column=2, padx=5, pady=5)

        # 下载次数标签和输入框
        tk.Label(self.root, text=self.texts[self.language]['download_count_label']).grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.download_count_entry = tk.Entry(self.root, width=10)
        self.download_count_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        self.download_count_entry.insert(0, self.download_count)

        # 下载间隔标签和输入框
        tk.Label(self.root, text=self.texts[self.language]['download_interval_label']).grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.download_interval_entry = tk.Entry(self.root, width=10)
        self.download_interval_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.download_interval_entry.insert(0, self.download_interval)

        # 下载按钮
        self.download_button = tk.Button(self.root, text=self.texts[self.language]['download_button'], command=self.start_download)
        self.download_button.grid(row=5, column=0, columnspan=3, pady=10)

        # 进度标签
        self.progress_label = tk.Label(self.root, text=self.texts[self.language]['progress_label'])
        self.progress_label.grid(row=6, column=0, columnspan=3, pady=5)

        # 进度条
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=7, column=0, columnspan=3, pady=10)

        # 进度百分比标签
        self.percentage_label = tk.Label(self.root, text=self.texts[self.language]['percentage_label'])
        self.percentage_label.grid(row=8, column=0, columnspan=3, pady=5)

        # 日志框
        self.log_frame = tk.Frame(self.root)
        self.log_frame.grid(row=9, column=0, columnspan=3, padx=5, pady=5)

        # 显示/隐藏日志按钮
        self.log_toggle_button = tk.Button(self.root, text=self.texts[self.language]['log_toggle_button'], command=self.toggle_log)
        self.log_toggle_button.grid(row=10, column=0, columnspan=3, pady=5)

        # 日志文本框
        self.log_text = tk.Text(self.log_frame, height=10, width=60)
        self.log_text.pack()
        self.log_text.config(state=tk.DISABLED)

        # 初始隐藏日志框
        self.log_frame.grid_remove()

        # 语言切换按钮
        self.toggle_language_button = tk.Button(self.root, text=self.texts[self.language]['toggle_language_button'], command=self.toggle_language)
        self.toggle_language_button.grid(row=11, column=2, padx=5, pady=5, sticky=tk.E)

        # 删除图片按钮
        self.delete_images_button = tk.Button(self.root, text=self.texts[self.language]['delete_images_button'], command=self.delete_images)
        self.delete_images_button.grid(row=12, column=0, padx=5, pady=5)

        # 删除配置文件按钮
        self.delete_config_button = tk.Button(self.root, text=self.texts[self.language]['delete_config_button'], command=self.delete_config_file)
        self.delete_config_button.grid(row=12, column=1, padx=5, pady=5)

        # 打开下载目录按钮
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
            messagebox.showerror("错误", "下载目录不存在。" if self.language == '中文' else "Download directory does not exist.")

    def delete_images(self):
        confirmation = messagebox.askyesno(
            "确认删除", 
            "您确定要删除保存目录中的所有图片吗？" if self.language == '中文' else "Are you sure you want to delete all images in the save directory?"
        )
        if confirmation:
            try:
                for file in os.listdir(self.save_dir):
                    file_path = os.path.join(self.save_dir, file)
                    if file.endswith(".png"):
                        os.remove(file_path)
                messagebox.showinfo("完成", "图片已删除。" if self.language == '中文' else "Images have been deleted.")
            except Exception as e:
                messagebox.showerror("错误", f"删除图片时发生错误：{str(e)}" if self.language == '中文' else f"An error occurred while deleting images: {str(e)}")

    def delete_config_file(self):
        confirmation = messagebox.askyesno(
            "确认删除", 
            "您确定要删除配置文件吗？" if self.language == '中文' else "Are you sure you want to delete the config file?"
        )
        if confirmation:
            try:
                os.remove(self.config_filename)
                messagebox.showinfo("完成", "配置文件已删除。" if self.language == '中文' else "Config file has been deleted.")
                self.load_config()
                self.create_widgets()
            except Exception as e:
                messagebox.showerror("错误", f"删除配置文件时发生错误：{str(e)}" if self.language == '中文' else f"An error occurred while deleting config file: {str(e)}")

    def start_download(self):
        api_link = self.api_combobox.get()
        save_dir = self.save_dir_entry.get()
        try:
            download_count = int(self.download_count_entry.get())
            download_interval = int(self.download_interval_entry.get())
        except ValueError:
            messagebox.showerror("错误", "下载次数和下载间隔必须是整数。" if self.language == '中文' else "Download count and interval must be integers.")
            return

        if not api_link or not save_dir:
            messagebox.showerror("错误", "API链接和保存目录不能为空。" if self.language == '中文' else "API link and save directory cannot be empty.")
            return

        # 更新配置
        self.api_link = api_link
        self.save_dir = save_dir
        self.download_count = str(download_count)
        self.download_interval = str(download_interval)

        if api_link not in self.api_history:
            self.api_history.append(api_link)
            if len(self.api_history) > 10:
                self.api_history.pop(0)

        self.save_config()

        self.status_label.config(text="状态: 正在下载..." if self.language == '中文' else "Status: Downloading...")
        self.download_button.config(state=tk.DISABLED)

        self.download_thread = threading.Thread(target=self.download_files, args=(api_link, save_dir, download_count, download_interval))
        self.download_thread.start()

    def download_files(self, api_link, save_dir, download_count, download_interval):
        self.progress["maximum"] = download_count
        self.progress["value"] = 0

        for i in range(download_count):
            try:
                response = requests.get(api_link)
                if response.status_code == 200:
                    filename = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + ".png"
                    file_path = os.path.join(save_dir, filename)
                    with open(file_path, 'wb') as file:
                        file.write(response.content)
                    self.log(f"文件 {filename} 下载成功。")
                else:
                    self.log(f"下载失败，状态码: {response.status_code}")

                self.progress["value"] += 1
                percentage = int((self.progress["value"] / download_count) * 100)
                self.progress_label.config(text=f"已下载{i+1}个文件，剩余{download_count-i-1}个文件，共{download_count}个文件")
                self.percentage_label.config(text=f"{percentage}%")
                time.sleep(download_interval)
            except Exception as e:
                self.log(f"下载时发生错误: {str(e)}")

        self.status_label.config(text="状态: 下载完成" if self.language == '中文' else "Status: Download Complete")
        self.download_button.config(state=tk.NORMAL)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.yview(tk.END)

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
        self.create_widgets()

if __name__ == "__main__":
    root = tk.Tk()
    app = FileDownloaderApp(root)
    root.mainloop()
