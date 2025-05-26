import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import pandas as pd
from covid_stats.data_loader import DataLoader
from covid_stats.models import CovidStats
from covid_stats.visualizer import Visualizer

DATA_FILE = "data/raw/vietnam_covid_2024.csv"

class CovidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID Stats Manager")
        self.root.geometry("900x600")

        self.loader = DataLoader(DATA_FILE)
        self.df = self.loader.load_data()
        self.model = CovidStats(self.df)

        # Search and sort frame
        search_sort_frame = tk.Frame(root)
        search_sort_frame.pack(fill=tk.X, pady=4)

        tk.Label(search_sort_frame, text="Tìm kiếm:").pack(side=tk.LEFT, padx=2)
        self.search_col = ttk.Combobox(search_sort_frame, values=list(self.df.columns), width=12)
        self.search_col.current(0)
        self.search_col.pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_sort_frame)
        self.search_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(search_sort_frame, text="Lọc", command=self.filter_data).pack(side=tk.LEFT, padx=2)
        tk.Button(search_sort_frame, text="Hiện tất cả", command=self.refresh_table).pack(side=tk.LEFT, padx=2)

        tk.Label(search_sort_frame, text="Sắp xếp theo:").pack(side=tk.LEFT, padx=8)
        self.sort_col = ttk.Combobox(search_sort_frame, values=list(self.df.columns), width=12)
        self.sort_col.current(0)
        self.sort_col.pack(side=tk.LEFT)
        self.sort_order = ttk.Combobox(search_sort_frame, values=["Tăng dần", "Giảm dần"], width=8)
        self.sort_order.current(0)
        self.sort_order.pack(side=tk.LEFT, padx=2)
        tk.Button(search_sort_frame, text="Sắp xếp", command=self.sort_data).pack(side=tk.LEFT, padx=2)

        # Table
        self.table = ttk.Treeview(root, columns=list(self.df.columns), show='headings')
        for col in self.df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=120)
        self.table.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        self.refresh_table()

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, pady=4)

        tk.Button(btn_frame, text="Thêm", command=self.add_record).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Sửa", command=self.edit_record).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Xóa", command=self.delete_record).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Lưu", command=self.save_data).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Vẽ biểu đồ", command=self.plot_data).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Mở file CSV", command=self.load_other_file).pack(side=tk.LEFT, padx=2)

    def refresh_table(self):
        self.table.delete(*self.table.get_children())
        for i, row in self.model.get_all().iterrows():
            self.table.insert("", tk.END, values=list(row))

    def add_record(self):
        new_rec = {}
        for col in self.df.columns:
            val = simpledialog.askstring("Thêm mới", f"{col}:", parent=self.root)
            if col == "cases":
                try:
                    val = int(val)
                except:
                    messagebox.showerror("Lỗi", "Số ca phải là số nguyên!")
                    return
            new_rec[col] = val
        self.model.add_record(new_rec)
        self.refresh_table()

    def edit_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Sửa", "Chọn bản ghi để sửa")
            return
        idx = self.table.index(selected[0])
        current = self.model.get_all().iloc[idx].to_dict()
        for col in self.df.columns:
            val = simpledialog.askstring("Sửa", f"{col}:", initialvalue=current[col], parent=self.root)
            if col == "cases":
                try:
                    val = int(val)
                except:
                    messagebox.showerror("Lỗi", "Số ca phải là số nguyên!")
                    return
            current[col] = val
        self.model.update_record(idx, current)
        self.refresh_table()

    def delete_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Xóa", "Chọn bản ghi để xóa")
            return
        idx = self.table.index(selected[0])
        if messagebox.askyesno("Xóa", "Bạn có chắc muốn xóa?"):
            self.model.delete_record(idx)
            self.refresh_table()

    def save_data(self):
        self.loader.save_data(self.model.get_all())
        messagebox.showinfo("Lưu", "Đã lưu dữ liệu thành công.")

    def plot_data(self):
        df = self.model.get_all()
        if "date" in df.columns and "cases" in df.columns:
            Visualizer.plot_cases_by_date(df, "date", "cases", "province")
        else:
            messagebox.showwarning("Biểu đồ", "Thiếu cột 'date' hoặc 'cases'.")

    def filter_data(self):
        col = self.search_col.get()
        keyword = self.search_entry.get()
        if keyword.strip() == "":
            self.refresh_table()
            return
        filtered = self.model.filter_data(col, keyword)
        self.table.delete(*self.table.get_children())
        for i, row in filtered.iterrows():
            self.table.insert("", tk.END, values=list(row))

    def sort_data(self):
        col = self.sort_col.get()
        asc = self.sort_order.get() == "Tăng dần"
        self.model.sort_data(col, ascending=asc)
        self.refresh_table()

    def load_other_file(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not filename:
            return
        self.loader = DataLoader(filename)
        self.df = self.loader.load_data()
        self.model = CovidStats(self.df)
        # Cập nhật các combobox theo cột mới (nếu có)
        cols = list(self.df.columns)
        self.table["columns"] = cols
        for col in cols:
            self.table.heading(col, text=col)
            self.table.column(col, width=120)
        self.search_col["values"] = cols
        self.sort_col["values"] = cols
        self.refresh_table()

if __name__ == "__main__":
    root = tk.Tk()
    app = CovidApp(root)
    root.mainloop()