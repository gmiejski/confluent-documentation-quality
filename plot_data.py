import csv
import os
import pathlib
from shutil import copyfile
from typing import List, Tuple

import plotly.graph_objs as go
import plotly.io as pio


def read_data(filename: str) -> List[Tuple[str, int, int]]:
    result = []
    with open('./data/{}'.format(filename), newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # skip header
        for row in reader:
            # print(', '.join(row))
            result.append((row[0], int(row[1]), int(row[2])))
    return result


def sum_good(all_data) -> int:
    daily_sum = []
    all_days = [data[1] for data in all_data]
    for day in all_days:
        sum = 0
        for url_data in day:
            sum += url_data[1]
        daily_sum.append(sum)
    return daily_sum


def sum_bad(all_data) -> int:
    daily_sum = []
    all_days = [data[1] for data in all_data]
    for day in all_days:
        sum = 0
        for url_data in day:
            sum += url_data[2]
        daily_sum.append(sum)
    return daily_sum


def produce_plot(all_data: List[Tuple[str, List[Tuple[str, int, int]]]]):
    pathlib.Path("./images").mkdir(exist_ok=True)

    fig = go.Figure()

    x = [data[0] for data in all_data]
    y_good = sum_good(all_data)
    y_bad = sum_bad(all_data)
    fig.add_scatter(x=x,
                    y=y_good,
                    mode='lines',
                    name="Good ratings sum",
                    line=dict(color='#29db23'),
                    )

    fig.add_scatter(x=x,
                    y=y_bad,
                    mode='lines',
                    name="Bad ratings sum",
                    line=dict(color='#ef2b3e')
                    )
    pio.write_image(fig, 'images/{}.png'.format(x[-1]))
    return 'images/{}.png'.format(x[-1])


def get_all_filenames() -> List[str]:
    a = os.listdir("./data")
    a = sorted(a)
    return a


def latest_for_date(data: List[Tuple[str, List[Tuple[str, int, int]]]]):
    result = []
    for record in data:
        if len(result) > 0 != None and result[-1][0] == record[0]:
            result[-1] = record
        else:
            result.append(record)
    return result


# return datetime string (2018-09-09) -> (url, good, bad)
def read_all_data() -> List[Tuple[str, List[Tuple[str, int, int]]]]:
    all_data = []
    data_file_names = get_all_filenames()
    for filename in data_file_names:
        print(filename)
        data = read_data(filename)
        all_data.append((filename.split()[0], data))

    empty_filtered_out = [x for x in all_data if len(x[1]) > 0]
    once_per_day = latest_for_date(empty_filtered_out)
    return once_per_day


def link_as_current(plot_name: str):
    copyfile(plot_name, "./images/latest.png")


if __name__ == "__main__":
    all_data = read_all_data()
    plot_name = produce_plot(all_data)
    link_as_current(plot_name)
