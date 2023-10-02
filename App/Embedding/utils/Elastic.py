from elasticsearch import Elasticsearch


# initialize elasticSearch
es = Elasticsearch(
    [
        "https://u46hxt12c:3qcatejimc@movies-search-5264494072.us-west-2.bonsaisearch.net:443"
    ]
)


def FetchDocuments(ids):
    es_index_name = "telegram_media"
    res = es.search(
        index=es_index_name,
        body={
            "query": {"terms": {"imdb_id.keyword": ids, "boost": 1.0}},
            "collapse": {
                "field": "imdb_id.keyword",
                "inner_hits": {
                    "name": "simple",
                    "collapse": {"field": "caption"},
                    "sort": [{"season_number": {"order": "asc"}}],
                    "size": 1,
                },
            },
        },
    )

    response=[]
    for data in res["hits"]["hits"]:
        temp=data["inner_hits"]["simple"]["hits"]["hits"][0]['_source']
        temp['_id']=data["inner_hits"]["simple"]["hits"]["hits"][0]['_id']

        response.append(temp)
    return response
