import pandas
from pandas import DataFrame


def create_dataset(
    ds_location: str, only_title: bool = False, categories_to_remove: [str] = list
) -> DataFrame:
    df = pandas.read_csv(ds_location)

    data = {"content": [], "topic": []}
    if only_title:
        for index, row in df.iterrows():
            data["content"].append(row["title"])
            if row["label"] in categories_to_remove:
                data["topic"].append("none")
            else:
                data["topic"].append(row["label"])
    else:
        for index, row in df.iterrows():
            data["content"].append(
                row["title"] + " " + (row["text"] if type(row["text"]) is str else "")
            )
            if row["label"] in categories_to_remove:
                data["topic"].append("none")
            else:
                data["topic"].append(row["label"])

    result: DataFrame = DataFrame(data)

    return result
