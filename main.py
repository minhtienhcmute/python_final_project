import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from covid_stats.data_loader import DataLoader
from covid_stats.models import CovidStats

DATA_FILE = "datasets/country_wise_latest.csv"
PAGE_SIZE = 20

class CovidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID Data Manager (Paging & CRUD)")
        self.root.geometry("1200x600")

        self.loader = DataLoader(DATA_FILE)
        self.df = self.loader.load_data()

        # Đổi tên cột sang tiếng Việt
        column_map = {
            "Country/Region": "Quốc gia",
            "Confirmed": "Ca xác nhận",
            "Deaths": "Tử vong",
            "Recovered": "Bình phục",
            "Active": "Đang điều trị",
            "New cases": "Ca mới",
            "New deaths": "Tử vong mới",
            "New recovered": "Bình phục mới",
            "Deaths / 100 Cases": "Tử vong/100 ca",
            "Recovered / 100 Cases": "Bình phục/100 ca",
            "Deaths / 100 Recovered": "Tử vong/100 bình phục",
            "Confirmed last week": "Ca xác nhận tuần trước",
            "1 week change": "Thay đổi 1 tuần",
            "1 week % increase": "Tỉ lệ tăng 1 tuần",
            "WHO Region": "Khu vực WHO"
        }
        self.df.rename(columns=column_map, inplace=True)

        self.model = CovidStats(self.df)

        self.page = 1
        self.total_pages = self.model.get_total_pages(PAGE_SIZE)

        self.table = ttk.Treeview(root, columns=list(self.df.columns), show='headings')
        for col in self.df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=110)
        self.table.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill=tk.X, pady=4)

        tk.Button(btn_frame, text="Trang trước", command=self.prev_page).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Trang sau", command=self.next_page).pack(side=tk.LEFT, padx=2)
        self.page_label = tk.Label(btn_frame, text=f"Trang {self.page}/{self.total_pages}")
        self.page_label.pack(side=tk.LEFT, padx=6)

        tk.Button(btn_frame, text="Thêm", command=self.add_record).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Sửa", command=self.edit_record).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Xóa", command=self.delete_record).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Lưu", command=self.save_data).pack(side=tk.LEFT, padx=2)

        self.refresh_table()

    def refresh_table(self):
        self.table.delete(*self.table.get_children())
        page_df = self.model.get_page(self.page, PAGE_SIZE)
        for i, row in page_df.iterrows():
            self.table.insert("", tk.END, values=list(row))
        self.total_pages = self.model.get_total_pages(PAGE_SIZE)
        self.page_label.config(text=f"Trang {self.page}/{self.total_pages}")

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.refresh_table()

    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            self.refresh_table()

    def add_record(self):
        new_rec = {}
        for col in self.df.columns:
            val = simpledialog.askstring("Thêm mới", f"{col}:", parent=self.root)
            new_rec[col] = val
        self.model.add_record(new_rec)
        self.refresh_table()

    def edit_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Sửa", "Chọn bản ghi để sửa")
            return
        idx_in_page = self.table.index(selected[0])
        idx = (self.page - 1) * PAGE_SIZE + idx_in_page
        current = self.model.get_all().iloc[idx].to_dict()
        for col in self.df.columns:
            val = simpledialog.askstring("Sửa", f"{col}:", initialvalue=current[col], parent=self.root)
            current[col] = val
        self.model.update_record(idx, current)
        self.refresh_table()

    def delete_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Xóa", "Chọn bản ghi để xóa")
            return
        idx_in_page = self.table.index(selected[0])
        idx = (self.page - 1) * PAGE_SIZE + idx_in_page
        if messagebox.askyesno("Xóa", "Bạn có chắc muốn xóa?"):
            self.model.delete_record(idx)
            self.refresh_table()

    def save_data(self):
        self.loader.save_data(self.model.get_all())
        messagebox.showinfo("Lưu", "Đã lưu dữ liệu thành công.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CovidApp(root)
    root.mainloop()