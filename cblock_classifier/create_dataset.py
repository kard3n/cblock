import pandas
from pandas import DataFrame


"""
print(df.columns)
print(f"Shape of dataset: {df.shape}")

print(df["category_level_2"])

topic_set = set()

# for value in df["category_level_1"]:
#    topic_set.add(value)

# iterate over all rows
for index, row in df.iterrows():
    topic_set.add(row["category_level_1"])"""

# print(f"Topic set: {topic_set}.\nLength: {len(topic_set)}")


def clean_dataset(ds_location: str) -> DataFrame:
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
    for index, row in df.iterrows():
        data["content"].append(row["title"] + " " + row["content"])
        data["topic"].append(topic_conversion_dict[row["category_level_1"]])
        # topic_set.add(row["category_level_1"])

    result: DataFrame = DataFrame(data)

    return result


"""cleaning_result: DataFrame = clean_dataset()
cleaning_result.to_csv("data.csv")
print(set(cleaning_result["topic"]))"""

# print(df.columns["category_level_1"])
