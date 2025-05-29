import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os

class TabCleaning(ttk.Frame):
    def __init__(self, master, dataframe: pd.DataFrame = None, on_cleaned_callback=None):
        super().__init__(master)
        self.dataframe = dataframe
        self.cleaned = False
        self.on_cleaned_callback = on_cleaned_callback
        self.cleaning_options = {
            "autofill_missing": tk.BooleanVar(value=True),
            "remove_duplicates": tk.BooleanVar(value=True),
            "standardize_case": tk.BooleanVar(value=True),
            "convert_date": tk.BooleanVar(value=True),
            # "drop_unused_columns": tk.BooleanVar(value=False),
        }
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Tùy chọn làm sạch dữ liệu", font=("Segoe UI", 14, "bold")).pack(pady=10)

        for key, var in self.cleaning_options.items():
            label = {
                "autofill_missing": "Tự động điền dữ liệu bị khuyết (NaN)",
                "remove_duplicates": "Xóa dữ liệu trùng lặp",
                "standardize_case": "Chuẩn hóa chữ hoa/thường",
                "convert_date": "Chuyển định dạng ngày (nếu có cột ngày)",
                # "drop_unused_columns": "Loại bỏ cột không cần thiết (cột toàn NaN)"
            }.get(key, key)

            tk.Checkbutton(self, text=label, variable=var).pack(anchor="w", padx=20)
        
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="Nhập file CSV", command=self.import_file).grid(row=0,column=0,padx=4)
        ttk.Button(button_frame, text="Kiểm tra dữ liệu", command=self.check_data_issues).grid(row=0,column=1,padx=4)
       
        ttk.Button(button_frame, text="Thực hiện làm sạch", command=self.clean_data).grid(row=0,column=2,padx=4)
        ttk.Button(button_frame, text="Lưu dữ liệu đã làm sạch", command=self.save_cleaned_file).grid(row=0,column=3,padx=4)
        # ttk.Button(self, text="Lưu dữ liệu đã làm sạch", command=self.save_cleaned_file).grid(row=0,column=4,padx=4)
        
        self.status_label = tk.Label(self, text="Chưa có dữ liệu", fg="gray")
        self.status_label.pack(pady=5)

    def import_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self.dataframe = pd.read_csv(file_path)
                self.cleaned = False
                self.status_label.config(text=f"Đã tải file: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không đọc được file CSV:\n{e}")

        if self.dataframe is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng nhập file CSV trước.")
            return

        self.check_data_issues()  
        
    def check_data_issues(self):
        if self.dataframe is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng nhập file CSV trước.")
            return

        df = self.dataframe
        total_rows = len(df)
        total_cols = len(df.columns)
        msg_lines = [
            f"Tổng số dòng: {total_rows}",
            f"Tổng số cột: {total_cols}",
            ""
        ]
        
        if self.cleaning_options["autofill_missing"].get():
            total_missing = df.isnull().sum().sum()  # Tổng số ô NaN trong toàn bộ DataFrame
            msg_lines.append(f"Tổng số ô bị thiếu (NaN): {total_missing}")
        else:
            msg_lines.append("Không kiểm tra giá trị thiếu (NaN).")
            
        # # 1. Kiểm tra NaN (nếu chọn)
        # if self.cleaning_options["remove_missing"].get():
            
        #     rows_with_nan = df.isnull().any(axis=1).sum()
        #     msg_lines.append(f"Số dòng có giá trị thiếu (NaN): {rows_with_nan}")
        # else:
        #     msg_lines.append("Không kiểm tra giá trị thiếu (NaN).")

        # 2. Kiểm tra dòng trùng lặp (nếu chọn)
        if self.cleaning_options["remove_duplicates"].get():
            duplicate_rows = df.duplicated().sum()
            msg_lines.append(f"Số dòng trùng lặp: {duplicate_rows}")
        else:
            msg_lines.append("Không kiểm tra dòng trùng lặp.")

        # 3. Kiểm tra lỗi ngày (nếu chọn)
        if self.cleaning_options["convert_date"].get():
            date_issues = []
            for col in df.columns:
                if "date" in col.lower():
                    try:
                        converted = pd.to_datetime(df[col], errors='coerce')
                        n_invalid = converted.isna().sum()
                        if n_invalid > 0:
                            date_issues.append(f"{col} ({n_invalid} giá trị không đúng định dạng)")
                    except Exception:
                        date_issues.append(f"{col} (lỗi khi chuyển đổi ngày tháng)")
            msg_lines.append("\nCác cột ngày có lỗi định dạng:")
            if date_issues:
                msg_lines += date_issues
            else:
                msg_lines.append("Không có lỗi định dạng ngày.")
        else:
            msg_lines.append("Không kiểm tra định dạng ngày.")

        # 4. Kiểm tra cột toàn NaN (nếu chọn)
        # if self.cleaning_options["drop_unused_columns"].get():
        #     cols_all_nan = df.columns[df.isna().all()].tolist()
        #     msg_lines.append("\nCác cột toàn bộ giá trị thiếu (toàn NaN):")
        #     if cols_all_nan:
        #         msg_lines.append(", ".join(cols_all_nan))
        #     else:
        #         msg_lines.append("Không có cột toàn NaN.")
        # else:
        #     msg_lines.append("Không kiểm tra cột toàn NaN.")

        # Hiển thị kết quả
        messagebox.showinfo("Kết quả kiểm tra dữ liệu", "\n".join(msg_lines))
            
    def clean_data(self):
        if self.dataframe is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng nhập file CSV.")
            return

        try:
            df = self.dataframe.copy()
            original_shape = df.shape

            # Xử lý NaN theo kiểu dữ liệu
            if self.cleaning_options["autofill_missing"].get():
                for col in df.columns:
                    if df[col].isna().any():
                        if pd.api.types.is_numeric_dtype(df[col]):
                            df[col].fillna(df[col].mean(), inplace=True)
                        elif pd.api.types.is_datetime64_any_dtype(df[col]):
                            df[col].fillna(pd.to_datetime("1970-01-01"), inplace=True)
                        else:
                            df[col].fillna("unknown", inplace=True)

            # if self.cleaning_options["remove_missing"].get():
            #     df.dropna(how='all', inplace=True)

            if self.cleaning_options["remove_duplicates"].get():
                df.drop_duplicates(inplace=True)

            if self.cleaning_options["standardize_case"].get():
                for col in df.select_dtypes(include='object').columns:
                    df[col] = df[col].astype(str).str.strip().str.lower()

            if self.cleaning_options["convert_date"].get():
                for col in df.columns:
                    if 'date' in col.lower():
                        df[col] = pd.to_datetime(df[col], errors='coerce')

            # if self.cleaning_options["drop_unused_columns"].get():
            #     df.dropna(axis=1, how='all', inplace=True)

            cleaned_rows = df.shape[0]
            removed_rows = original_shape[0] - cleaned_rows

            self.dataframe = df
            self.cleaned = True
            self.status_label.config(text=f"Đã làm sạch dữ liệu. Số dòng còn lại: {cleaned_rows}")

            if self.on_cleaned_callback:
                self.on_cleaned_callback(df)

        except Exception as e:
            messagebox.showerror("Lỗi khi làm sạch", str(e))

    def save_cleaned_file(self):
        if not self.cleaned:
            messagebox.showinfo("Chưa làm sạch", "Vui lòng làm sạch trước khi lưu.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if file_path:
            try:
                self.dataframe.to_csv(file_path, index=False)
                messagebox.showinfo("Thành công", f"Đã lưu tại: {file_path}")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    
    def reset_state(self):
        self.dataframe = None
        self.cleaned = False
        self.status_label.config(text="Chưa có dữ liệu")

    def bind_tab_event(self, notebook: ttk.Notebook):
        def on_tab_changed(event):
            selected_tab = event.widget.select()
            tab_text = event.widget.tab(selected_tab, "text")
            print(f"Tab changed to: {tab_text}")
            if tab_text == "Làm sạch dữ liệu":
                self.reset_state()
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

