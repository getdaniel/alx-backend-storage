#!/usr/bin/env python3
"""Insert a document."""


def insert_school(mongo_collection, **kwargs):
    """Inserts a new document in a collection based on kwargs."""
    res = mongo_collection.insert_one(kwargs)
    return res.inserted_id
