import pandas
from pandas import DataFrame


def create_dataset(ds_location: str, only_title: bool = False) -> DataFrame:
    df = pandas.read_csv(ds_location)

    data = {"content": [], "topic": []}
    if only_title:
        for index, row in df.iterrows():
            data["content"].append(row["title"])
            data["topic"].append(row["label"])
            # topic_set.add(row["category_level_1"])
    else:
        for index, row in df.iterrows():
            data["content"].append(
                row["title"] + " " + (row["text"] if type(row["text"]) is str else "")
            )
            data["topic"].append(row["label"])
            # topic_set.add(row["category_level_1"])

    result: DataFrame = DataFrame(data)

    return result
