import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TabVisualization(ttk.Frame):
    def __init__(self, master, dataframe: pd.DataFrame = None):
        super().__init__(master)
        self.dataframe = dataframe
        self.selected_region = tk.StringVar()
        self.available_regions = []
        self.create_widgets()

        if self.dataframe is not None:
            self.update_available_regions()

    def create_widgets(self):
        tk.Label(self, text="Biểu đồ trực quan hóa dữ liệu", font=("Segoe UI", 14, "bold")).pack(pady=10)

        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="Biểu đồ tròn", command=self.plot_pie_chart).grid(row=0, column=0, padx=4)
        ttk.Button(button_frame, text="Biểu đồ đường", command=self.plot_line_chart).grid(row=0, column=1, padx=4)
        ttk.Button(button_frame, text="Biểu đồ cột", command=self.plot_bar_chart).grid(row=0, column=2, padx=4)
        # ttk.Button(button_frame, text="Biểu đồ cột chồng", command=self.plot_stacked_bar_chart).grid(row=0, column=3, padx=4)
        ttk.Button(button_frame, text="Biểu đồ khu vực", command=self.plot_area_chart).grid(row=0, column=4, padx=4)

        # Filter
        filter_frame = tk.Frame(self)
        filter_frame.pack(pady=5)
        tk.Label(filter_frame, text="Chọn quốc gia/vùng lãnh thổ:").pack(side="left", padx=(0, 5))
        self.region_combobox = ttk.Combobox(filter_frame, textvariable=self.selected_region, state="readonly")
        self.region_combobox.pack(side="left")
        self.region_combobox.bind("<<ComboboxSelected>>", self.on_region_selected)

        # Canvas
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True)

    def set_dataframe(self, df: pd.DataFrame):
        self.dataframe = df
        self.update_available_regions()

    def update_available_regions(self):
        if self.dataframe is not None:
            regions = ["Toàn bộ"] + sorted(self.dataframe['Quốc gia/Vùng lãnh thổ'].dropna().unique().tolist())
            self.available_regions = regions
            self.region_combobox['values'] = regions
            self.region_combobox.current(0)

    def on_region_selected(self, event=None):
        pass  

    def get_filtered_dataframe(self):
        if self.dataframe is None:
            return None
        df = self.dataframe.copy()
        selected = self.selected_region.get()
        if selected and selected != "Toàn bộ":
            df = df[df['Quốc gia/Vùng lãnh thổ'] == selected]
        return df

    def clear_canvas(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

    def display_plot(self, fig):
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def plot_pie_chart(self):
        df = self.get_filtered_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng chọn khu vực có dữ liệu.")
            return
        self.clear_canvas()

        df_latest = df.sort_values("Ngày").iloc[-1]
        labels = ['Ca xác nhận', 'Tử vong', 'Hồi phục', 'Đang điều trị']
        sizes = [df_latest['Ca xác nhận'], df_latest['Tử vong'], df_latest['Hồi phục'], df_latest['Đang điều trị']]

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')
        ax.set_title(f"Tỉ lệ ca bệnh mới nhất ({self.selected_region.get()})")
        self.display_plot(fig)

    def plot_line_chart(self):
        df = self.get_filtered_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng chọn khu vực có dữ liệu.")
            return
        self.clear_canvas()

        df['Ngày'] = pd.to_datetime(df['Ngày'])
        df_grouped = df.groupby('Ngày')[['Ca xác nhận', 'Tử vong', 'Hồi phục', 'Đang điều trị']].sum()

        fig, ax = plt.subplots()
        df_grouped.plot(ax=ax)
        ax.set_title(f"Diễn biến theo thời gian ({self.selected_region.get()})")
        ax.set_xlabel("Ngày")
        ax.set_ylabel("Số ca")
        self.display_plot(fig)

    def plot_bar_chart(self):
        df = self.get_filtered_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng chọn khu vực có dữ liệu.")
            return
        self.clear_canvas()

        df_grouped = df.groupby('Quốc gia/Vùng lãnh thổ')[['Ca xác nhận']].sum()
        df_top = df_grouped.sort_values(by='Ca xác nhận', ascending=False).head(10)

        fig, ax = plt.subplots()
        df_top.plot(kind='bar', ax=ax, legend=False)
        ax.set_title("Top 10 quốc gia có số ca xác nhận cao nhất")
        ax.set_ylabel("Ca xác nhận")
        self.display_plot(fig)

    def plot_stacked_bar_chart(self):
        df = self.get_filtered_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng chọn khu vực có dữ liệu.")
            return
        self.clear_canvas()

        df['Ngày'] = pd.to_datetime(df['Ngày'])
        df_grouped = df.groupby('Ngày')[['Ca xác nhận', 'Tử vong', 'Hồi phục', 'Đang điều trị']].sum()

        fig, ax = plt.subplots()
        df_grouped.plot(kind='bar', stacked=True, ax=ax)
        ax.set_title(f"Biểu đồ cột chồng ({self.selected_region.get()})")
        ax.set_xlabel("Ngày")
        ax.set_ylabel("Số ca")
        self.display_plot(fig)

    def plot_area_chart(self):
        df = self.get_filtered_dataframe()
        if df is None or df.empty:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng chọn khu vực có dữ liệu.")
            return
        self.clear_canvas()

        df['Ngày'] = pd.to_datetime(df['Ngày'])
        df_grouped = df.groupby('Ngày')[['Ca xác nhận', 'Tử vong', 'Hồi phục', 'Đang điều trị']].sum()

        fig, ax = plt.subplots()
        df_grouped.plot.area(ax=ax, alpha=0.5)
        ax.set_title(f"Biểu đồ khu vực ({self.selected_region.get()})")
        ax.set_xlabel("Ngày")
        ax.set_ylabel("Số ca")
        self.display_plot(fig)
