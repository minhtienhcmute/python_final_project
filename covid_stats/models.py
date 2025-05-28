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

    def filter_data(self, column, keyword):
        return self.data[self.data[column].astype(str).str.contains(keyword, case=False, na=False)]

    def sort_data(self, column, ascending=True):
        self.data = self.data.sort_values(by=column, ascending=ascending).reset_index(drop=True)

    def get_all(self):
        return self.data