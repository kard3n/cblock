from enum import Enum


class SourceAction(Enum):
    BLOCK = 0,  # block the request/response
    FILTER = 1,  # filter the content of the response
    PASS = 2,  # do nothing, let it pass as-is
