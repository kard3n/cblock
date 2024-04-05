import pandas
from pandas import DataFrame


def create_dataset(ds_location: str, only_title: bool = False) -> DataFrame:
    df = pandas.read_csv(ds_location)
    topic_conversion_dict: dict = {
        "weather": "none",
        "economy, business and finance": "finance",
        "society": "none",
        "education": "none",
        "sport": "none",
        "labour": "none",
        "lifestyle and leisure": "none",
        "disaster, accident and emergency incident": "disaster_environment",
        "politics": "politics",
        "science and technology": "none",
        "conflict, war and peace": "war_crime",
        "crime, law and justice": "war_crime",
        "religion and belief": "religion_belief",
        "human interest": "none",
        "environment": "disaster_environment",
        "arts, culture, entertainment and media": "none",
        "health": "health",
    }

    data = {"content": [], "topic": []}
    if only_title:
        for index, row in df.iterrows():
            data["content"].append(row["title"])
            data["topic"].append(topic_conversion_dict[row["category_level_1"]])
            # topic_set.add(row["category_level_1"])
    else:
        for index, row in df.iterrows():
            data["content"].append(row["title"] + " " + row["content"])
            data["topic"].append(topic_conversion_dict[row["category_level_1"]])
            # topic_set.add(row["category_level_1"])

    result: DataFrame = DataFrame(data)

    return result
