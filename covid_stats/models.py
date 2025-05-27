import pandas as pd

class CovidStats:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def add_record(self, record: dict):
        self.data = pd.concat([self.data, pd.DataFrame([record])], ignore_index=True)
        
    def delete_record(self, idx: int):
        self.data = self.data.drop(idx).reset_index(drop=True)

    def update_record(self, idx: int, record: dict):
        for key, value in record.items():
            self.data.at[idx, key] = value

# Lấy dữ liệu theo trang
    def get_page(self, page=1, page_size=20):
        start = (page - 1) * page_size
        end = start + page_size
        return self.data.iloc[start:end]

# lấy tông số trang dựa trên kích thước trang
    def get_total_pages(self, page_size=20):
        return (len(self.data) + page_size - 1) // page_size

    def get_all(self):
        return self.data
    
    def search_records(self, keyword, columns=None):
        """
        Tìm kiếm keyword trong các cột chỉ định (hoặc tất cả nếu columns=None).
        Trả về DataFrame kết quả.
        """
        if columns is None:
            columns = self.data.columns
        mask = pd.DataFrame(False, index=self.data.index, columns=columns)
        for col in columns:
            mask[col] = self.data[col].astype(str).str.contains(str(keyword), case=False, na=False)
        result = self.data[mask.any(axis=1)]
        return result

    def sort_records(self, by_column, ascending=True):
        """
        Sắp xếp dữ liệu theo cột by_column, tăng (ascending=True) hoặc giảm dần.
        """
        self.data = self.data.sort_values(by=by_column, ascending=ascending).reset_index(drop=True)