import tkinter as tk

class RecordModal(tk.Toplevel):
    def __init__(self, master, columns, on_save, init_values=None):
        super().__init__(master)
        self.title("Nhập dữ liệu")
        self.entries = {}
        self.on_save = on_save

        for i, col in enumerate(columns):
            tk.Label(self, text=col, font=("Segoe UI", 12)).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(self, font=("Segoe UI", 12), width=25)
            entry.grid(row=i, column=1, padx=5, pady=5)

            # nếu có giá trị truyền qua, điền vào ô nhập
            if init_values and col in init_values:
                entry.insert(0, str(init_values[col]))

            self.entries[col] = entry # lưu trữ các ô nhập vào từ điển để dễ dàng truy cập

        btn_save = tk.Button(self, text="Lưu", font=("Segoe UI", 12, "bold"), bg="green", fg="white", command=self.save)
        btn_save.grid(row=len(columns), column=0, columnspan=2, pady=10)

    def save(self):
        record = {col: entry.get() for col, entry in self.entries.items()}
        self.on_save(record)
        self.destroy()