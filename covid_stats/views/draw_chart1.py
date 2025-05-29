import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TabVisualization(ttk.Frame):
    def __init__(self, master, dataframe: pd.DataFrame = None):
        super().__init__(master)
        self.dataframe = dataframe
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Biểu đồ trực quan hóa dữ liệu", font=("Segoe UI", 14, "bold")).pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Biểu đồ tròn", command=self.plot_pie_chart).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Biểu đồ đường", command=self.plot_line_chart).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Biểu đồ cột", command=self.plot_bar_chart).grid(row=0, column=2, padx=5)

        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True)

    def clear_canvas(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def plot_pie_chart(self):
        if self.dataframe is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng nhập hoặc làm sạch dữ liệu trước.")
            return

        self.clear_canvas()
        df_latest = self.dataframe.sort_values("Ngày").iloc[-1]
        labels = ['Ca xác nhận', 'Tử vong', 'Hồi phục', 'Đang điều trị']
        sizes = [df_latest['Ca xác nhận'], df_latest['Tử vong'], df_latest['Hồi phục'], df_latest['Đang điều trị']]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')

        self.display_plot(fig)

    def plot_line_chart(self):
        if self.dataframe is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng nhập hoặc làm sạch dữ liệu trước.")
            return

        self.clear_canvas()
        df = self.dataframe.copy()
        df['Ngày'] = pd.to_datetime(df['Ngày'])
        df_grouped = df.groupby('Ngày')[['Ca xác nhận', 'Tử vong', 'Hồi phục', 'Đang điều trị']].sum()

        fig, ax = plt.subplots()
        df_grouped.plot(ax=ax)
        ax.set_title('Thống kê theo ngày')
        ax.set_xlabel('Ngày')
        ax.set_ylabel('Số ca')

        self.display_plot(fig)

    def plot_bar_chart(self):
        if self.dataframe is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng nhập hoặc làm sạch dữ liệu trước.")
            return

        self.clear_canvas()
        df = self.dataframe.copy()
        df_grouped = df.groupby('Quốc gia/Vùng lãnh thổ')[['Ca xác nhận']].sum().sort_values(by='Ca xác nhận', ascending=False).head(10)

        fig, ax = plt.subplots()
        df_grouped.plot(kind='bar', ax=ax, legend=False)
        ax.set_title('Top 10 quốc gia có số ca xác nhận cao nhất')
        ax.set_xlabel('Quốc gia')
        ax.set_ylabel('Ca xác nhận')

        self.display_plot(fig)

    def display_plot(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
