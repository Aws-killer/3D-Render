from elasticsearch import Elasticsearch
import os

ELASTIC_HOST = os.environ.get("ELASTIC_HOST")

# initialize elasticSearch
es = Elasticsearch([ELASTIC_HOST])


def FetchDocuments(ids, order="asc"):
    es_index_name = "telegram_media"
    res = es.search(
        index=es_index_name,
        body={
            "size": 1000,
            "query": {"terms": {"imdb_id.keyword": ids, "boost": 1.0}},
            "collapse": {
                "field": "imdb_id.keyword",
                "inner_hits": {
                    "name": "simple",
                    "collapse": {"field": "caption"},
                    "sort": [{"season_number": {"order": order}}],
                    "size": 1,
                },
            },
        },
    )

    response = []
    for data in res["hits"]["hits"]:
        temp = data["inner_hits"]["simple"]["hits"]["hits"][0]["_source"]
        temp["_id"] = data["inner_hits"]["simple"]["hits"]["hits"][0]["_id"]

        response.append(temp)
    return response
