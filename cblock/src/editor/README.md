The content editors receive a string (the data), split it into logical parts (depending on schema).
For each part, a ContentAnalyzer gets asked to check for offending content, and depending on the result
the part gets changed or not.

### JSON Schema Tags:

Elements that do not matter do not need to be specified

#### Actions (when set for a list, applies to each value)

r: replace
d: delete
o: delete, but at least one needs to stay

#### Types of individual elements (used to pick elements to scan, and to replace properly when r replace is set)

t: title
s: summary
b: body
p: picture
v: video
c: categories/hashtags/topics
d: don't analyze. Element that should be replaced according to category, but does not need to be analyzed

```

"items"r:
[
    {"topics"c:"politics,sports", "title"t:"This is a title", "summary"s:"This is a summary",
    "picture"p:"pic.jpg",
    "other_data":
        {
        "summary_2"dt:"Not important"
        },
]
````

As dictionary used for scanning:

````
{
'items':
    ElementContainer{
        'tags': [ContentTag.REPLACE],
        'type': 'list', 
        'value': { # value is a dict
            'topics': ElementContainer{
                'tags': [ContentTag.CATEGORIES],
                'type': 'final', 
                'value': None
                },
            'title': ElementContainer{
                'tags': [ContentTag.TITLE],
                'type': 'final', 
                'value': None
                }
            'summary': ElementContainer{
                'tags': [ContentTag.SUMMARY],
                'type': 'final', 
                'value': None
                },
            'picture': ElementContainer{
                'tags': [ContentTag.PICTURE],
                'type': 'final', 
                'value': None
                },
            'other_data': ElementContainer{
                'tags': [ContentTag.REPLACE],
                'type': 'dict', 
                'value': ElementContainer{
                    'tags': [ContentTag.SUMMARY],
                    'type': 'final', 
                    'value': None
                    },
                },
    }
}
````

ElementContainer: class that contains:

* value content
* tags of current elements

  def json_schema_to_object(self, json_schema: str):
  in_dict: bool = False
  in_name: bool = False
  current_name: str = ''
  result: dict = {}
  current_container: ElementContainer = ElementContainer()
  stage: int = 0 # 1: found name for variable, get tags

        for char in json_schema:
            if char == '"' and in_name is False: #TODO escaped chars
                in_name = True
            elif char == '"' and in_dict is True:
                in_name = False

            # TODO error when in_dict is already true?
            if char == '{' and in_dict is False and in_name is False:
                in_dict = True
            elif char == '{' and in_name is True:
                raise SchemaParsingException('Found bracket in name.')


            if char == ':' and current_name != '':
                stage = 1
            if stage == 1:
                if char in ContentTag:
                    current_container.tags.append(ContentTag[char])
                else:
                    raise SchemaParsingException('Invalid content tag: ' + char)
            if char not in ['}', '{', ',', ':']:
                current_name += char

    @classmethod
    def parse_json_schema(cls, json_schema: str):
        result: ElementContainer = ElementContainer()

        in_quotes: bool = False
        current_child_name: str = ''
        in_child_element: bool = False
        current_child_content: str = ''
        opened_dividers: int = 0
        position: int = 0

        while position < len(json_schema):
            
            # 1 jump all whitespaces and line breaks until another symbol is found
            if not in_quotes and not in_child_element and json_schema[position] in ['\n', " "]:
                position += 1

            if in_child_element:
                while json_schema[position] in ['\n', " "]:
                    position += 1

                if json_schema[position] in ['{', "["]:
                    opened_dividers += 1
                    position += 1
                elif json_schema[position] in ['}', "]"]:
                    opened_dividers -= 1
                    position += 1

                current_child_content += json_schema[position]

                if opened_dividers == 0:
                    in_child_element = False

                    if type(result.value) == dict:
                        result.value = cls.parse_json_schema(current_child_content)

            
            # detect quotes. Used to determine the name of a field
            if json_schema[position] == '"' and in_quotes is False:
                in_quotes = True
                position += 1
            elif json_schema[position] == '"':
                in_quotes = False
                position += 1
            
            
            # if we are in quotes and not reading content that belongs to children, add it to the current name
            if in_quotes and json_schema[position].isalpha() or json_schema[position].isnumeric():
                current_child_name += json_schema[position]
                position += 1
            elif in_quotes:
                raise SchemaParsingException(f"Invalid character between quotes: {json_schema[position]} at position {position}")
            
            # 
            if json_schema[position] == ':':
                while json_schema[position] in ['\n', " "]:
                    position += 1

                if json_schema[position] == '[':
                    in_child_element = True
                    result.value = []
                elif json_schema[position] == '{':
                    in_child_element = True
                    result.value = {}


    # divide and conquer
    @classmethod
    def parse_json_schema_object(cls, json_schema: str) -> ElementContainer:
        result: ElementContainer = ElementContainer()

        in_quotes: bool = False

        position: int = 0

        while position < len(json_schema):
            if not in_quotes and json_schema[position] in ['\n', " "]:
                position += 1

            if json_schema[position] == '"' and in_quotes is False:
                in_quotes = True
            elif json_schema[position] == '"':
                in_quotes = False

            if json_schema[position].isalpha() or json_schema[position].isnumeric():
                result.