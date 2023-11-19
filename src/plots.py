import os

from ydata_profiling import ProfileReport

from config import OUTPUTS_PATH


def make_data_plots(df):
    df = ProfileReport(df)
    df.to_file(output_file=os.path.join(OUTPUTS_PATH, "data_report.html"))
