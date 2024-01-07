# %%
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
# %%

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")


headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


# %%
def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    # Comment this out to dump all data to a file
    # import json
    # with open('db.json', 'w', encoding='utf8') as f:
    #    json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


# %%
pages = get_pages()
pages_dict = {}
for page in pages:
    page_id = page["id"]
    props = page['properties']
    status = props['Status']['status']['name']

    title = None
    for t in props["Title"]['title']:
        if title is not None and 'plain_text' in t.keys():
            title = props["Title"]['title'][0]['plain_text']
        else:
            title = None
    tags = props['Tags']['multi_select'][0]['name'] if len(props['Tags']['multi_select']) != 0 else None  # None
    priority = props['Priority']['multi_select']
    duedate = props['DueDate']['date']

    if duedate is None:
        duedate_start = None
        duedate_end = None
    else:
        duedate_start, duedate_end = 0, 0
        for edge_name, edge_val in zip(
            ['start', 'end'],
            [duedate_start, duedate_end]
        ):
            if duedate[edge_name] is None:
                edge_val = None
            else:
                edge_val = datetime.fromisoformat(duedate[edge_name])
    Manhour = props['Manhour']['number']

    # save
    pages_dict['id'] = {}
    pages_dict['props'] = props
    pages_dict['status'] = status
    pages_dict['title'] = title
    pages_dict['tags'] = tags
    pages_dict['priority'] = priority
    pages_dict['duedate_start'] = duedate_start
    pages_dict['duedate_end'] = duedate_end
    pages_dict['Manhour'] = Manhour


# %%
