import pandas as pd

class DataLoader:
    def __init__(self, filepath):
        self.filepath = filepath

    def load_data(self):
        try:
            df = pd.read_csv(self.filepath)
            return df
        except Exception as e:
            print(f"Lỗi khi đọc dữ liệu: {e}")
            return pd.DataFrame(columns=["date", "province", "cases"])

    def save_data(self, df):
        try:
            df.to_csv(self.filepath, index=False)
        except Exception as e:
            print(f"Lỗi khi ghi dữ liệu: {e}")