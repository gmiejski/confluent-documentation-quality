import csv
import datetime
import pathlib
from urllib.parse import urljoin
from urllib.parse import urlparse

from requests_html import HTMLSession

starting_page_url = "https://docs.confluent.io/current/"
from typing import Dict, Tuple, List


def extract_rating_from_line(line: str) -> (int, int):
    ratings = [int(s) for s in line.split() if s.isdigit()]
    if len(ratings) == 2:
        return ratings[0], ratings[1]
    return -1, -1


def get_page_with_rating(session: HTMLSession, url: str) -> (List[str], int, int):
    if ".." in url:
        return [], 0, 0
    r = session.get(url)
    try:
        r.html.render()
    except Exception  as e:
        print("ERROR - Error rendering page {}. Omitting".format(url))
        return [], 0, 0
    if r._html.url == starting_page_url and url != starting_page_url:
        print("WARNING - Redirected at page {} to {}. Omitting!".format(url, starting_page_url))
        return [], 0, 0
    if r.is_redirect or r.is_permanent_redirect:
        print("WARNING - Redirected at page {}. Omitting!".format(url))
        return [], 0, 0

    split = str(r.html.full_text).split("\n")
    for line in split:
        if line != None and "rate this page" in line.lower():
            good_ratings, bad_ratings = extract_rating_from_line(line)
            if good_ratings >= 0:
                return r.html.links, good_ratings, bad_ratings
    print("WARNING - Couldn't find rating on page {}".format(url))
    return [], 0, 0


def unify_links_simple(current_url: str, links: List[str]) -> List[str]:
    unified = []
    for link in links:
        if link.startswith("/"):
            continue
        if link.startswith("https://docs.confluent.io/"):
            link_to_add = urljoin(current_url, link)
            o = urlparse(link_to_add)
            proper_url = "https://" + o.netloc + o.path
            if '#' in proper_url:
                raise Exception()
            unified.append(proper_url)
        elif link.startswith("http"):
            continue
        else:
            link_to_add = urljoin(current_url, link)
            o = urlparse(link_to_add)
            proper_url = "https://" + o.netloc + o.path
            if '#' in proper_url:
                raise Exception()
            unified.append(proper_url)
    return [x for x in unified if "_sources" not in x]


def get_all_links_ratings(starting_page_url: str, stop_after: int = 0) -> Dict[str, Tuple[int, int]]:
    all_ratings = {}
    links_to_see = [starting_page_url]
    while len(links_to_see) > 0:
        try:

            current_url = links_to_see[0]
            print("Scrapping site : {}".format(current_url))
            links, good_ratings, bad_ratings = get_page_with_rating(HTMLSession(), current_url)
            links = unify_links_simple(current_url, links)
            print("Site: {} -> {}:{}".format(current_url, good_ratings, bad_ratings))
            all_ratings[current_url] = (good_ratings, bad_ratings)
            for link in links:
                if link not in links_to_see and link not in all_ratings:
                    links_to_see.append(link)
            if stop_after > 0 and len(all_ratings.keys()) >= stop_after:
                break
        except Exception as e:
            print("Error getting results from url: {}".format(current_url))
            print(str(e))
        finally:
            links_to_see = links_to_see[1:]
            print("Links stats: gathered -> {}, left to scrap -> {}".format(len(all_ratings), len(links_to_see)))

    return all_ratings


def save_to_file(ratings_per_page: Dict[str, Tuple[int, int]]) -> None:
    pathlib.Path("./data").mkdir(exist_ok=True)

    with open('./data/{}.csv'.format(datetime.datetime.now()), 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["url", "good_ratings", "bad_ratings"])
        for url, data in ratings_per_page.items():
            writer.writerow([url, data[0], data[1]])


if __name__ == "__main__":
    ratings_per_page = get_all_links_ratings(starting_page_url)
    save_to_file(ratings_per_page)
