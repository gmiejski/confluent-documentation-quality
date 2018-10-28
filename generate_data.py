import csv
import datetime
import os
import pathlib

from requests_html import HTMLSession
# starting_page_url = "https://docs.confluent.io/current/"
starting_page_url = "https://docs.confluent.io/current/api-javadoc.html"
from typing import Dict, Tuple, List


def extract_rating_from_line(line: str) -> (int, int):
    ratings = [int(s) for s in line.split() if s.isdigit()]
    if len(ratings) == 2:
        return ratings[0], ratings[1]
    return -1, -1


def get_page_with_rating(session: HTMLSession, url: str) -> (List[str], int, int):
    r = session.get(url)
    r.html.render()
    split = str(r.html.full_text).split("\n")
    for line in split:
        if line != None and "rate this page" in line.lower():
            good_ratings, bad_ratings = extract_rating_from_line(line)
            if good_ratings >= 0:
                return r.html.links, good_ratings, bad_ratings
    raise Exception("Couldn't find rating on page {}".format(url))  # TODO  page not found - "Page not found"


def unify_links(current_url: str, links: List[str]) -> List[str]:
    unified = []
    for link in links:
        if link.startswith("/"):
            continue
        elif link.startswith("http"):
            unified.append(link)
        else:
            unified.append(current_url + link)
    return unified


def get_all_links_ratings(starting_page_url: str, stop_after: int = 0) -> Dict[str, Tuple[int, int]]:
    all_ratings = {}
    session = HTMLSession()
    links_to_see = [starting_page_url]
    while len(links_to_see) > 0:
        current_url = links_to_see[0]
        print("Scrapping site : {}".format(current_url))
        links, good_ratings, bad_ratings = get_page_with_rating(session, current_url)
        links = unify_links(current_url, links)
        print("Site: {} -> {}:{}".format(current_url, good_ratings, bad_ratings))
        all_ratings[current_url] = (good_ratings, bad_ratings)
        for link in links:
            if link not in links_to_see and link not in all_ratings:
                links_to_see.append(link)
        links_to_see = links_to_see[1:]
        if stop_after > 0 and len(all_ratings.keys()) >= stop_after:
            break
    return all_ratings


def save_to_file(ratings_per_page: Dict[str, Tuple[int, int]]) -> None:
    pathlib.Path("./data").mkdir(exist_ok=True)

    with open('./data/{}.csv'.format(datetime.datetime.now()),'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["url", "good_ratings", "bad_ratings"])
        for url, data in ratings_per_page.items():
            writer.writerow([url, data[0], data[1]])

if __name__ == "__main__":
    # ratings_per_page = get_all_links_ratings(starting_page_url, stop_after=1)
    dsdsaads_ = {"dsdsaads":(10, 20), "ads": (0,30)}
    save_to_file(dsdsaads_)
    # save_to_file(ratings_per_page)
