# Schemas
Schemas tell ContentBlock which web requests to filter and how to interpret their content.
Each schema has a name (or ID), a type and an associated specific schema like a JSON or Generic schema.
All schemas ContentBlock should use must be saved in the schema_definitions directory, with the name of their file
being their own name followed by `.cbs` (ContentBlockSchema).

An example file could look like this:

Name:
`basic_web_schema.cbs`

Content:

```
url: basic_web.com/data
type: json
schema: # after the schema line, the definition of the underlying specialized schema is specified.
{}
```

## ContentTags
Here's a list of all possible ContentTags and what they mean:

| Name | Symbol | Description |
|--------------|-----------|------------|
| ELEMENT | e | Marks element as container/segment, whose children should be analyzed together |
| DELETE | d | Element should be deleted. |
| DELETE_LEAVE_ONE | o | Child elements should be deleted, but at least one must remain (for lists). |
| DELETE_UNCONDITIONAL | u | Item should be deleted unconditionally |
| TITLE | t | A leaf that contains a title as value. Its value will be replaced with another |
| SUMMARY | s | A leaf that contains a summary as value. Its value will be replaced with another |
| FULL_CONTENT | f | A leaf whose value is a larger text. Its value will be replaced with another |
| PICTURE | p | A leaf that has a picture as its value. Its value will be replaced with another |
| VIDEO | v | A leaf that has a videos as its value. Its value will be replaced with another |
| CATEGORIES | c | A leaf element that contains one or more tags/categories for the content |
| ANALYZE | a | Needs to be set for every item that should be analyzed |

## Schema options:
### json -> JSONSchema
A JSON schema is similar to a normal JSON file, but it only describes its fields. Unlike in real JSON, names are optionally followed
by a number of ContentTags identified by their letter, and optionally the name of an embedded schema between parenthesis.
Example: A list that serves as a container for multiple dictionaries which contain a field "summary", that is a summary and should be analyzed.

```
{
    "contained_list"e: [
        {"summary"sa(embedded_schema_name):"What's written here does not matter!",}
    ]
}
```
