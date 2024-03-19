# Schemas
Schemas tell ContentBlock which web requests to filter and how to interpret their content.
Each schema has a name (or ID), a type and an associated specific schema like a JSON or Generic schema.
All schemas ContentBlock should use must be saved in the schema_definitions directory, with the name of their file
being their own name followed by `.cbs` (ContentBlockSchema). Root schemas (those that aren't embedded in another one)
also have an URL attribute (the name followed by the website, like "mywebsite.com") and a PATH attribute (for example, "/files").
While the URL attribute is a normal string, PATH can (and often must) be a regular expression.

A schema may have embedded schemas of a different type than that of itself. They may only be set for leaf elements,
or in other words, elements that have a basic value (and therefore no children) and can not be interpreted by
the current schema type. Elements with an embedded schema may not have any tags.

An example file could look like this:

Name:
`basic_web_schema.cbs`

Content:

```
url: basic_web.com
path: /data
type: json
schema: # after the schema line, the definition of the underlying specialized schema is specified.
{}
```

## ContentTags
Here's a list of all possible ContentTags and what they mean:

General Tags:

| Name                 | Symbol | Description |
|----------------------|-----------|------------|
| DELETE_UNCONDITIONAL | u | Item should be deleted unconditionally |
| CONTAINER            | e | Marks element as container/segment, whose children should be analyzed together |

Tags used for children of a CONTAINER element

| Name | Symbol | Description |
|--------------|-----------|------------|
| ANALYZE | a | Needs to be set for every item that should be analyzed |
| DELETE | d | Element should be deleted. |
| TITLE | t | A leaf that contains a title as value. Its value will be replaced with another |
| SUMMARY | s | A leaf that contains a summary as value. Its value will be replaced with another |
| FULL_CONTENT | f | A leaf whose value is a larger text. Its value will be replaced with another |
| PICTURE | p | A leaf that has a picture as its value. Its value will be replaced with another |
| VIDEO | v | A leaf that has a videos as its value. Its value will be replaced with another |
| CATEGORIES | c | A leaf element that contains one or more tags/categories for the content |

## Schema options:
### json -> JSONSchema
A JSON schema is similar to a normal JSON file, but it only describes its fields. Unlike in real JSON, names are optionally followed
by a number of ContentTags identified by their letter, and optionally the name of an embedded schema between parenthesis.
Example: Schema that contains the following fields:
* "contained_list": A list that serves as a container for multiple dictionaries which contain a field "summary", that is a summary and should be analyzed.
* "html_content": A leaf element whose value should be edited according to another schema called "some_embedded_schema"

```
{
    "contained_list"e: [
        {"summary"sa:"What's written here does not matter!",}
    ],
    "html_content"(some_embedded_schema): "<p>Hello there<\p>"
}
```


### generic -> GenericSchema
All leaves must be children of an element with the ELEMENT tag, or have one themselves.
Always use non-greedy quantifiers when possible. For example, `.*` should be `.*?`, as `.*` would match as much as possible while `.*?` tries to find the shortest match possible (which is what we usually want)