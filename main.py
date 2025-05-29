import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from covid_stats.data_loader import DataLoader
from covid_stats.models import CovidStats
from covid_stats.views.AddRecord import RecordModal

DATA_FILE = "datasets/covid_19_clean_complete.csv"
PAGE_SIZE = 20

class CovidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID Data Manager (Paging & CRUD)")
        self.root.geometry("1200x600")
        self.root.configure(bg="white")

        # Load data
        self.loader = DataLoader(DATA_FILE)
        self.df = self.loader.load_data()

        # Đổi tên cột
        column_map = {
            'Province/State': 'Tỉnh/Bang',
            'Country/Region': 'Quốc gia/Vùng lãnh thổ',
            'Lat': 'Vĩ độ',
            'Long': 'Kinh độ',
            'Date': 'Ngày',
            'Confirmed': 'Ca xác nhận',
            'Deaths': 'Tử vong',
            'Recovered': 'Hồi phục',
            'Active': 'Đang điều trị',
            'WHO Region': 'Khu vực WHO'
        }
        self.df.rename(columns=column_map, inplace=True)


        self.model = CovidStats(self.df)
        self.page = 1
        self.total_pages = self.model.get_total_pages(PAGE_SIZE)

        # Tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_manage = tk.Frame(notebook, bg="white")
        notebook.add(self.tab_manage, text="Quản lý ca bệnh")
        notebook.add(ttk.Frame(notebook), text="Tổng quan")
        notebook.add(ttk.Frame(notebook), text="Phân tích")
        notebook.add(ttk.Frame(notebook), text="Biểu đồ")
        notebook.add(ttk.Frame(notebook), text="Khác")

        # Tiêu đề
        title = tk.Label(self.tab_manage, text="Quản Lý Số Ca Mắc COVID-19",
                         font=("Segoe UI", 22, "bold"), bg="white", fg="purple")
        title.pack(pady=15)

        # Toolbar
        tool_frame = tk.Frame(self.tab_manage)
        tool_frame.pack(fill="x", pady=5)

        tk.Button(tool_frame, text="Thêm mới", bg="lightgreen", command=self.add_record).grid(row=0, column=0, padx=4)
        tk.Button(tool_frame, text="Sửa", bg="lightblue", command=self.edit_record).grid(row=0, column=1, padx=4)
        tk.Button(tool_frame, text="Xóa", bg="tomato", command=self.delete_record).grid(row=0, column=2, padx=4)
        tk.Button(tool_frame, text="Lưu", bg="orange", command=self.save_data).grid(row=0, column=3, padx=4)

        # nút
        tk.Button(tool_frame, text="<<", command=self.first_page).grid(row=0, column=4, padx=(20, 2))
        tk.Button(tool_frame, text="<", command=self.prev_page).grid(row=0, column=5)
        self.page_label = tk.Label(tool_frame, text="")
        self.page_label.grid(row=0, column=6, padx=5)
        tk.Label(tool_frame, text="Đến trang:").grid(row=0, column=7)
        self.goto_entry = tk.Entry(tool_frame, width=5)
        self.goto_entry.grid(row=0, column=8)
        tk.Button(tool_frame, text="Đi", command=self.goto_page).grid(row=0, column=9)
        tk.Button(tool_frame, text=">", command=self.next_page).grid(row=0, column=10)
        tk.Button(tool_frame, text=">>", command=self.last_page).grid(row=0, column=11)

        # Tìm kiếm và sắp xếp 
        tk.Label(tool_frame, text="Tìm kiếm:").grid(row=0, column=12, padx=(30, 2))
        tk.Label(tool_frame, text="Cột:").grid(row=0, column=13)
        self.search_column = ttk.Combobox(tool_frame, values=[""], width=10)
        self.search_column.grid(row=0, column=14)
        self.search_entry = tk.Entry(tool_frame, width=20)
        self.search_entry.grid(row=0, column=15, padx=5)
        tk.Button(tool_frame, text="Tìm").grid(row=0, column=16)

        tk.Label(tool_frame, text="Sắp xếp theo:").grid(row=0, column=17, padx=(20, 2))
        self.sort_column = ttk.Combobox(tool_frame, values=[""], width=10)
        self.sort_column.grid(row=0, column=18)
        tk.Checkbutton(tool_frame, text="Tăng dần").grid(row=0, column=19, padx=5)

        self.total_label = tk.Label(tool_frame, text="")
        self.total_label.grid(row=0, column=20, padx=(15, 0))

        # Bảng
        self.table = ttk.Treeview(self.tab_manage, columns=list(self.df.columns), show='headings')
        for col in self.df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=110)
        self.table.pack(fill=tk.BOTH, expand=True)

        # Refresh lần đầu
        self.refresh_table()

    def refresh_table(self):
        self.table.delete(*self.table.get_children())
        page_df = self.model.get_page(self.page, PAGE_SIZE)
        for _, row in page_df.iterrows():
            self.table.insert("", tk.END, values=list(row))
        self.total_pages = self.model.get_total_pages(PAGE_SIZE)
        self.page_label.config(text=f"Trang {self.page}/{self.total_pages}")
        total_records = len(self.model.get_all())
        self.total_label.config(text=f"Tổng số: {total_records} dòng")

    def first_page(self):
        self.page = 1
        self.refresh_table()

    def last_page(self):
        self.page = self.total_pages
        self.refresh_table()

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.refresh_table()

    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            self.refresh_table()

    def goto_page(self):
        try:
            page = int(self.goto_entry.get())
            if 1 <= page <= self.total_pages:
                self.page = page
                self.refresh_table()
            else:
                messagebox.showwarning("Trang", f"Chỉ số trang phải từ 1 đến {self.total_pages}")
        except ValueError:
            messagebox.showwarning("Trang", "Vui lòng nhập số trang hợp lệ.")

    def add_record(self):
        def on_save(record):
            self.model.add_record(record)
            self.refresh_table()
        RecordModal(self.root, self.df.columns, on_save)

    def edit_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Sửa", "Chọn bản ghi để sửa")
            return
        idx_in_page = self.table.index(selected[0])
        idx = (self.page - 1) * PAGE_SIZE + idx_in_page
        current = self.model.get_all().iloc[idx].to_dict()
        def on_save(record):
            self.model.update_record(idx, record)
            self.refresh_table()
        RecordModal(self.root, self.df.columns, on_save, init_values=current)

    def delete_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Xóa", "Chọn bản ghi để xóa")
            return
        if not messagebox.askyesno("Xóa", f"Bạn có chắc muốn xóa {len(selected)} bản ghi?"):
            return
        idxs_in_page = [self.table.index(item) for item in selected]
        idxs = sorted([(self.page - 1) * PAGE_SIZE + idx for idx in idxs_in_page], reverse=True)
        for idx in idxs:
            self.model.delete_record(idx)
        self.refresh_table()

    def save_data(self):
        self.loader.save_data(self.model.get_all())
        messagebox.showinfo("Lưu", "Đã lưu dữ liệu thành công.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CovidApp(root)
    root.mainloop()
