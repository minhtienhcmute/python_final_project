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

        # Rename columns to Vietnamese
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
        
        # Create Notebook for Tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Manage Cases
        tab_manage = tk.Frame(notebook, bg="white")
        notebook.add(tab_manage, text="Quản lý ca bệnh")
        title = tk.Label(tab_manage, text="Quản Lý Số Ca Mắc COVID-19", font=("Segoe UI", 22, "bold"),
                         bg="white", fg="purple")
        title.pack(pady=15)

        # Input Fields
        input = tk.Frame(tab_manage, bg="white")
        input.pack(pady=10, fill=tk.X, padx=20)
        lbl_width = 12
        entry_width = 25
        # Tạo dict để lưu Entry widgets
        self.entries = {}
        # Labels and Entries
        def add_entry(row, col, label, col_name):
            tk.Label(input, text=label, font=("Segoe UI", 12), bg="white").grid(row=row, column=col*2, sticky="e", pady=5, padx=5)
            entry = tk.Entry(input, font=("Segoe UI", 12), width=entry_width)
            entry.grid(row=row, column=col*2+1, pady=5, padx=5)
            self.entries[col_name] = entry
        add_entry(0, 0, "Quốc gia:", "Quốc gia")
        add_entry(0, 1, "Ca xác nhận:", "Ca xác nhận")
        add_entry(1, 0, "Tử vong:", "Tử vong")
        add_entry(1, 1, "Bình phục:", "Bình phục")
        add_entry(2, 0, "Ca mới:", "Ca mới")
        add_entry(2, 1, "Tử vong mới:", "Tử vong mới")
        add_entry(0, 2, "Tử vong/100 ca:", "Tử vong/100 ca")
        add_entry(2, 2, "Bình phục/100 ca:", "Bình phục/100 ca")
        add_entry(1, 2, "Tử vong/100 bình:", "Tử vong/100 bình phục")
        add_entry(4, 0, "Đang điều trị:", "Đang điều trị")
        add_entry(4, 1, "Bình phục mới:", "Bình phục mới")

     
        tab_filter = tk.Frame(notebook, bg="white")
        notebook.add(tab_filter, text="Lọc dữ liệu")
        
        #sắp xếp dữ liệu
        # search_sort_frame = tk.Frame(tab_manage, bg="white")
        # search_sort_frame.pack(fill=tk.X, padx=20, pady=5)
        # tk.Label(search_sort_frame, text="Tìm kiếm:", font=("Segoe UI", 12), bg="white").pack(side=tk.LEFT)
        # self.search_entry = tk.Entry(search_sort_frame, font=("Segoe UI", 12), width=20)
        # self.search_entry.pack(side=tk.LEFT, padx=5)
        # tk.Button(search_sort_frame, text="Tìm", font=("Segoe UI", 12), command=self.search_records).pack(side=tk.LEFT, padx=5)

        # tk.Label(search_sort_frame, text="Sắp xếp theo:", font=("Segoe UI", 12), bg="white").pack(side=tk.LEFT, padx=10)
        # self.sort_column = tk.StringVar()
        # sort_options = list(self.df.columns)
        # self.sort_column.set(sort_options[0])
        # tk.OptionMenu(search_sort_frame, self.sort_column, *sort_options).pack(side=tk.LEFT)
        # tk.Button(search_sort_frame, text="Tăng", font=("Segoe UI", 12), command=lambda: self.sort_records(True)).pack(side=tk.LEFT, padx=2)
        # tk.Button(search_sort_frame, text="Giảm", font=("Segoe UI", 12), command=lambda: self.sort_records(False)).pack(side=tk.LEFT, padx=2)
    
        # Rename columns in DataFrame
        self.df.rename(columns=column_map, inplace=True)
        self.model = CovidStats(self.df)
        self.page = 1
        self.total_pages = self.model.get_total_pages(PAGE_SIZE)

        
        self.table = ttk.Treeview(tab_manage, columns=list(self.df.columns), show='headings')
        for col in self.df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=110)
        self.table.pack(fill=tk.BOTH, expand=True)

    
        btn_frame = tk.Frame(tab_manage)
        btn_frame.pack(fill=tk.X, pady=4)

        # Action Buttons
            
        btn_frame = tk.Frame(tab_manage)
        btn_frame.pack(fill=tk.X, pady=4)

        tk.Button(btn_frame, text="Trang trước", command=self.prev_page, bg="purple", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Trang sau", command=self.next_page, bg="purple", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)
        
        self.page_label = tk.Label(btn_frame, text=f"Trang {self.page}/{self.total_pages}", font=("Segoe UI", 12, "bold"))
        self.page_label.pack(side=tk.LEFT, padx=6)

        tk.Button(btn_frame, text="Thêm", command=self.add_record, bg="yellow", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Sửa", command=self.edit_record, bg="blue", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Xóa", command=self.delete_record, bg="red", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Lưu", command=self.save_data, bg="green", font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=2)


        self.refresh_table()

# refresh_table sẽ làm mới bảng với dữ liệu hiện tại
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
        # Lấy dữ liệu từ các Entry
        new_rec = {}
        for col in self.df.columns:
            val = self.entries[col].get() if col in self.entries else ""
            new_rec[col] = val
        self.model.add_record(new_rec)
        self.refresh_table()
        # Xóa dữ liệu trong Entry sau khi thêm
        for entry in self.entries.values():
            entry.delete(0, tk.END)

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
        if not messagebox.askyesno("Xóa", f"Bạn có chắc muốn xóa {len(selected)} bản ghi?"):
            return
        # Lấy index các dòng được chọn (theo thứ tự giảm dần để tránh lệch index khi xóa)
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
