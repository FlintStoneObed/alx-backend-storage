#!/usr/bin/env python3

def insert_school(mongo_collection, **kwargs):
    """
    Inserts a new document in a collection.

    Args:
        mongo_collection (pymongo.collection.Collection): The pymongo collection object.
        **kwargs: Keyword arguments to be inserted as a new document.

    Returns:
        ObjectId: The _id of the newly inserted document.
    """
    result = mongo_collection.insert_one(kwargs)
    return result.inserted_id
