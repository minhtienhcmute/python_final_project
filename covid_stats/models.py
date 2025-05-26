import pandas as pd

class CovidStats:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def add_record(self, record: dict):
        self.data = pd.concat([self.data, pd.DataFrame([record])], ignore_index=True)

    def update_record(self, idx: int, record: dict):
        for key, value in record.items():
            self.data.at[idx, key] = value

    def delete_record(self, idx: int):
        self.data = self.data.drop(idx).reset_index(drop=True)

    def get_page(self, page=1, page_size=20):
        start = (page - 1) * page_size
        end = start + page_size
        return self.data.iloc[start:end]

    def get_total_pages(self, page_size=20):
        return (len(self.data) + page_size - 1) // page_size

    def get_all(self):
        return self.data