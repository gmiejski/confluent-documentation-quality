from typing import Dict, Set

from plot_data import read_all_data


def load_all_sites_per_day() -> Dict[str, Set[str]]:
    data = read_all_data()

    results = []
    for date_result in data:
        date_urls = set([x[0] for x in date_result[1]])
        results.append((date_result[0], date_urls))

    return results


if __name__ == '__main__':
    urls_by_date = load_all_sites_per_day()
    for i in range(0, len(urls_by_date) - 1):
        if "initial" in urls_by_date[i][1]:
            continue
        today = urls_by_date[i][1]
        tommorow = urls_by_date[i + 1][1]
        print("Verifying -> {}: {}, {}: {}".format(urls_by_date[i][0], len(today), urls_by_date[i + 1][0], len(tommorow)))
        if len(today) >= len(tommorow):
            lacking_in_tommorow = today.difference(tommorow)
            lacking_in_today = tommorow.difference(today)
            print("Lacking in tommorow -> {}".format(urls_by_date[i + 1]))
            print(lacking_in_tommorow)
            print("Lacking in today -> {}".format(urls_by_date[i]))
            print(lacking_in_today)
            raise Exception()
