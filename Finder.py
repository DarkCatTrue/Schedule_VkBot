# coding: utf-8
import difflib
import json
import os
import re
from dotenv import load_dotenv
load_dotenv()
local_path = os.getenv('local_path')


async def filter_keys_by_pattern(keys, group_name):
    regex = re.compile(re.escape(group_name), re.IGNORECASE)
    return [key for key in keys if regex.search(key)]


async def rank_keys_by_similarity(keys, group_name):
    return sorted(keys, key=lambda key: difflib.SequenceMatcher(None, key, group_name).ratio(), reverse=True)


async def find_closest_keys(data, variable):
    keys = list(data.keys())
    filtered_keys = await filter_keys_by_pattern(keys, variable)
    ranked_keys = await rank_keys_by_similarity(filtered_keys, variable)
    return ranked_keys


async def group_finder(group_name):
    with open(f"{local_path}groups.json") as file:
        data = json.load(file)
    closest_keys = await find_closest_keys(data, group_name)
    if closest_keys:
        keys = '\n '.join(closest_keys)
        return keys
    else:
        return False