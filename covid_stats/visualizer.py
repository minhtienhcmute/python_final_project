import matplotlib.pyplot as plt

class Visualizer:
    @staticmethod
    def plot_cases_by_date(df, date_col="date", cases_col="cases", province_col=None):
        plt.figure(figsize=(10, 5))
        if province_col and province_col in df.columns:
            for prov in df[province_col].unique():
                sub = df[df[province_col] == prov]
                plt.plot(sub[date_col], sub[cases_col], marker='o', label=prov)
            plt.legend()
        else:
            plt.plot(df[date_col], df[cases_col], marker='o')
        plt.title("COVID Cases by Date")
        plt.xlabel("Date")
        plt.ylabel("Cases")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()