#!/usr/bin/env python
import sqlite3
from pathlib import Path
import re
import os
import sys


def replace_links(path_to_org_files):
    files = Path(path_to_org_files).glob("*.org")
    for file in files:
        links_to_replace = []
        with open(file, "r") as f:
            content = f.read()
        links = org_roam_link_matcher.findall(content)
        for link in links:
            if link not in files_dict:
                cursor.execute(
                    "select file from nodes where id LIKE '%{}%'".format(link)
                )
                files_dict[link] = (
                    "file:./" + cursor.fetchone()[0].strip('"').split("/")[-1]
                )
            links_to_replace.append(link)
        for link in links_to_replace:
            sed_string = "sed -i 's|id:{}|{}|g' {}".format(
                re.escape(link), re.escape(files_dict[link]), file
            )
            f = os.popen(sed_string)
            print("Replaced id:{}, with {}".format(link, files_dict[link]))
            f.close()


if len(sys.argv) < 4:
    print(
        "Usage: script.py ORG_ROAM_DB_PATH ORG_ROAM_NOTES_PATH LOGSEQ_DIR_PATH (ORG_ROAM_DAILIES_PATH)"
    )
    exit(-1)

is_dailies = True if len(sys.argv) == 5 else False

ORG_ROAM_DB_PATH = sys.argv[1]
ORG_ROAM_NOTES_PATH = sys.argv[2]
LOGSEQ_DIR_PATH = sys.argv[3]
LOGSEQ_PAGES_PATH = LOGSEQ_DIR_PATH + "/pages"
ORG_ROAM_DAILIES_PATH, LOGSEQ_JOURNAL_PATH = (
    sys.argv[4],
    LOGSEQ_DIR_PATH + "/journals" if is_dailies else (None, None),
)

b = os.popen(
    "mkdir -p {} 2>/dev/null; cp {}/*.org {}".format(
        LOGSEQ_PAGES_PATH, ORG_ROAM_NOTES_PATH, LOGSEQ_PAGES_PATH
    )
)
b.close()

if is_dailies:
    b = os.popen(
        "mkdir -p {} 2>/dev/null; cp {}/*.org {}".format(
            LOGSEQ_JOURNAL_PATH, ORG_ROAM_DAILIES_PATH, LOGSEQ_JOURNAL_PATH
        )
    )
    b.close()

org_roam_link_matcher = re.compile(r"\[\[id:([a-z0-9\-]+)\]\[.*\]\]")
files_dict = {}

connection = sqlite3.connect(ORG_ROAM_DB_PATH)
cursor = connection.cursor()

replace_links(LOGSEQ_PAGES_PATH)
if is_dailies:
    replace_links(LOGSEQ_JOURNAL_PATH)
