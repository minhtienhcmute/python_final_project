import datetime
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkinter import filedialog
from covid_stats.data_loader import DataLoader
from covid_stats.models import CovidStats
from covid_stats.views.AddRecord import RecordModal
from covid_stats.views.clean_data import TabCleaning
from covid_stats.views.draw_chart import TabVisualization
DATA_FILE = "datasets/covid_19_clean_complete.csv"
PAGE_SIZE = 20

class CovidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("COVID Data Manager (Paging & CRUD)")
        self.root.geometry("1200x600")
        self.root.configure(bg="white")
        
        self.loader = DataLoader(DATA_FILE)
        self.df = None
        self.modelCoVidStats = None
        self.page = 1
        self.total_pages = 1
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
        self.column_map = column_map  # Lưu lại để dùng khi mở file

        
        # Tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: 
    
        self.tab_manage = tk.Frame(self.notebook, bg="white")

        self.tab_cleaning = TabCleaning(self.notebook, self.df)
        self.tab_cleaning.bind_tab_event(self.notebook)
        self.notebook.add(self.tab_cleaning, text="Làm sạch dữ liệu")
        
        
        self.tab_visualization = TabVisualization(self.notebook, self.df)
        
        # self.tab_visualization.bind_tab_event(notebook)
        self.notebook.add(self.tab_visualization, text="Biểu đồ")
        self.notebook.add(self.tab_manage, text="Quản lý ca bệnh")
        self.notebook.add(ttk.Frame(self.notebook), text="Tổng quan")
        self.notebook.add(ttk.Frame(self.notebook), text="Phân tích")
        self.notebook.add(ttk.Frame(self.notebook), text="Khác")
		
    
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
        tk.Button(tool_frame, text="<<", command=self.first_page).grid(row=0, column=6, padx=(20, 2))
        tk.Button(tool_frame, text="<", command=self.prev_page).grid(row=0, column=7)
        self.page_label = tk.Label(tool_frame, text="")
        self.page_label.grid(row=0, column=8, padx=5)
        tk.Label(tool_frame, text="Đến trang:").grid(row=0, column=9)
        self.goto_entry = tk.Entry(tool_frame, width=5)
        self.goto_entry.grid(row=0, column=10)
        tk.Button(tool_frame, text="Đi", command=self.goto_page).grid(row=0, column=11)
        tk.Button(tool_frame, text=">", command=self.next_page).grid(row=0, column=12)
        tk.Button(tool_frame, text=">>", command=self.last_page).grid(row=0, column=13)

        # Tìm kiếm và sắp xếp 
        # Tìm kiếm theo cột (sử dụng column_map)
        tk.Label(tool_frame, text="Tìm kiếm:", font=("Segoe UI", 10)).grid(row=0, column=14, padx=(30, 2), sticky="e")


        tk.Label(tool_frame, text="Cột:", font=("Segoe UI", 10)).grid(row=0, column=15, sticky="e")
        self.search_column = ttk.Combobox(tool_frame, values=list(self.column_map.values()), width=20, state="readonly")
        self.search_column.grid(row=0, column=16, padx=2)
        self.search_column.set(list(self.column_map.values())[0])
        self.search_entry = tk.Entry(tool_frame, width=20)
        self.search_entry.grid(row=0, column=17, padx=5)
        tk.Button(tool_frame, text="Tìm", command=self.search_records).grid(row=0, column=18, padx=2)


        tk.Button(tool_frame, text="Tăng", command=lambda: self.sort_records(True)).grid(row=0, column=21, padx=2)
        tk.Button(tool_frame, text="Giảm", command=lambda: self.sort_records(False)).grid(row=0, column=22, padx=2)
        self.sort_column = ttk.Combobox(tool_frame, values=[""], width=10)
        self.sort_column.grid(row=0, column=23)

        self.total_record = tk.Label(tool_frame, text="")
        self.total_record.grid(row=0, column=24, padx=(15, 0))

        tk.Button(tool_frame, text="Export", bg="lightyellow", command=self.export_data).grid(row=0, column=4, padx=4)
        tk.Button(tool_frame, text="Mở file", bg="lightcyan", command=self.open_file).grid(row=0, column=5, padx=4)
        # Bảng
        self.table = ttk.Treeview(self.tab_manage, columns=[], show='headings')
        self.table.pack(fill=tk.BOTH, expand=True)

        


        # self.refresh_table()

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Chọn file CSV để mở"
        )
        if file_path:
            self.loader.filepath = file_path
            self.df = self.loader.load_data()
            self.df.rename(columns=self.column_map, inplace=True)
            self.modelCoVidStats = CovidStats(self.df)
            self.page = 1
            self.total_pages = self.modelCoVidStats.get_total_pages(PAGE_SIZE)
            # Tạo lại bảng với cột mới
            self.table.destroy()
            self.table = ttk.Treeview(self.tab_manage, columns=list(self.df.columns), show='headings')
            for col in self.df.columns:
                self.table.heading(col, text=col)
                self.table.column(col, width=110)
            self.table.pack(fill=tk.BOTH, expand=True)
            self.sort_column['values'] = list(self.df.columns)
            if len(self.df.columns) > 0:
                self.sort_column.set(self.df.columns[0])

            self.tab_visualization.update_dataframe(self.df)
            self.refresh_table()
            messagebox.showinfo("Mở file", f"Đã nạp dữ liệu từ file:\n{file_path}")
    def refresh_table(self):
        if not self.modelCoVidStats:
            for item in self.table.get_children():
                self.table.delete(item)
            self.page_label.config(text="Trang 0/0")
            self.total_record.config(text="Tổng số bản ghi: 0")
            return
        for item in self.table.get_children():
            self.table.delete(item)
        page_df = self.modelCoVidStats.get_page(self.page, PAGE_SIZE)
        for i, row in page_df.iterrows():
            self.table.insert("", tk.END, values=list(row))
        self.total_pages = self.modelCoVidStats.get_total_pages(PAGE_SIZE)
        self.page_label.config(text=f"Trang {self.page}/{self.total_pages}")
        total_records = len(self.modelCoVidStats.get_all())
        self.total_record.config(text=f"Tổng số bản ghi: {total_records}")


# Hàm tìm kiếm bản ghi
    def search_records(self):
        search_value = self.search_entry.get().strip()
        search_column_vn = self.search_column.get()

        if not search_value:
            messagebox.showwarning("Tìm kiếm", "Vui lòng nhập giá trị để tìm kiếm.")
            return

        if search_column_vn not in self.df.columns:
            messagebox.showwarning("Tìm kiếm", "Cột tìm kiếm không hợp lệ.")
            return

        filtered_df = self.df[self.df[search_column_vn].str.contains(search_value, case=False, na=False)]

        self.modelCoVidStats = CovidStats(filtered_df)
        self.total_pages = self.modelCoVidStats.get_total_pages(PAGE_SIZE)
        self.refresh_table()
        
    

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
        # Hàm xử lý khi lưu bản ghi mới
        def on_save(record):
            #kiểm tra
            if not record.get("Quốc gia/Vùng lãnh thổ", "").strip():
                messagebox.showwarning("Thiếu thông tin", "Bạn phải nhập Quốc gia/Vùng lãnh thổ!")
                return
            ca_xac_nhan = record.get("Ca xác nhận", "").strip()
            if not ca_xac_nhan.isdigit() or int(ca_xac_nhan) < 0:
                messagebox.showwarning("Sai dữ liệu", "Ca xác nhận phải là số nguyên không âm!")
                return
            ngay = record.get("Ngày", "").strip()
            try:
                date_request = datetime.datetime.strptime(ngay, "%Y-%m-%d")
                time_now = datetime.datetime.now()
                if not (2020 <= date_request.year <= time_now.year):
                    messagebox.showwarning("Sai năm", f"Năm phải từ 2020 đến {time_now.year}!")
                    return
                # Nếu là năm hiện tại thì không cho nhập ngày lớn hơn ngày hôm nay
                if date_request.year == time_now.year and date_request > time_now:
                    messagebox.showwarning("Sai ngày", "Không được nhập ngày lớn hơn thời điểm hiện tại!")
                    return
            except ValueError:
                messagebox.showwarning("Sai định dạng", "Ngày phải hợp lệ và theo định dạng yyyy-MM-dd!")
                return

            self.modelCoVidStats.add_record(record)
            self.refresh_table()
        RecordModal(self.root, self.df.columns, on_save)

    def edit_record(self):
        selected = self.table.selection()
        if not selected:
            messagebox.showwarning("Sửa", "Chọn bản ghi để sửa")
            return
        idx_in_page = self.table.index(selected[0])
        idx = (self.page - 1) * PAGE_SIZE + idx_in_page
        current = self.modelCoVidStats.get_all().iloc[idx].to_dict()
        def on_save(record):
            self.modelCoVidStats.update_record(idx, record)
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
            self.modelCoVidStats.delete_record(idx)
        self.refresh_table()

# Hàm sắp xếp bản ghi
    def sort_records(self, ascending=True):
        col = self.sort_column.get()
        if not col or not self.modelCoVidStats:
            return
        # Sắp xếp DataFrame hiện tại
        sorted_df = self.modelCoVidStats.get_all().sort_values(by=col, ascending=ascending)
        self.modelCoVidStats = CovidStats(sorted_df)
        self.page = 1
        self.total_pages = self.modelCoVidStats.get_total_pages(PAGE_SIZE)
        self.refresh_table()


    def save_data(self):
        self.loader.save_data(self.modelCoVidStats.get_all())
        messagebox.showinfo("Lưu", "Đã lưu dữ liệu thành công.")
        
    def export_data(self):
        # Hỏi người dùng nơi lưu file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Chọn nơi lưu file xuất dữ liệu"
        )
        if file_path:
            try:
                self.modelCoVidStats.get_all().to_csv(file_path, index=False)
                messagebox.showinfo("Export", f"Đã xuất dữ liệu ra file:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export", f"Lỗi khi xuất dữ liệu:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CovidApp(root)
    root.mainloop()
