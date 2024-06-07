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

### Example:
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

Explanation:
* _basic_web_schema_: the name of the schema
* _url_: when a file from this URL is received, and _path_ matches too, the contents will be edited according to the underlying specialized schema
* _path_: the path of the file that should be edited. This can be a regular expression
* _type_: the type of the schema. For example _json_, _generic_ or _html_
* _schema_: after this line until the end of the file, the definition of the underlying specialized schema is written.

## ContentTags
Here's a list of all possible ContentTags and what they mean:

General Tags:

| Name                 | Symbol | Description |
|----------------------|-----------|------------|
| DELETE_UNCONDITIONAL | u | Item should be deleted unconditionally |
| CONTAINER            | e | Marks element as container/segment, whose children should be analyzed together |

Tags used for children of a CONTAINER element (leaves)

| Name         | Symbol | Description                                                                      |
|--------------|--------|----------------------------------------------------------------------------------|
| ANALYZE      | a      | Needs to be set for every item that should be analyzed                           |
| DELETE       | d      | Element should be deleted.                                                       |
| TITLE        | t      | A leaf that contains a title as value. Its value will be replaced with another   |
| SUMMARY      | s      | A leaf that contains a summary as value. Its value will be replaced with another |
| FULL_CONTENT | f      | A leaf whose value is a larger text. Its value will be replaced with another     |
| PICTURE      | p      | A leaf that has a picture as its value. Its value will be replaced with another  |
| VIDEO        | v      | A leaf that has a videos as its value. Its value will be replaced with another   |
| CATEGORIES   | c      | A leaf element that contains one or more tags/categories for the content         |
| ORIGIN       | o      | A leaf element that contains the origin of the content (author, website, ...)    |
| LINK         | l      | A leaf element that contains a link to another page                              |

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
This type of schema can be used in cases where none of the other types would work. It uses regular expressions to find the content that should be edited, making use of Python's named-group feature.
For example, to delete any content that is between double underscores (__) one could use the following rule: `pattern:'__(?P<content>.*?)__', tags:'ed'`.
* pattern: describes which content to match. The content of the `content` group is what is actually going to be edited. Anything that is not part of the _content_ will need to be matched, but is not part of the content that is edited.
* tags: These are just content tags, just like with any other schema type

To have the matched content be edited according to another schema, it is possible to add another field:
* embedded_schema: when set contains the name of another schema, which is used to edit the content inside the _content_ group.

It is also possible to have a hierarchy of rules, for example if we now instead of deleting the whole content of the previous rule just want to delete any "a" we could do the following:
````
pattern:'__(?P<content>.*?)__', tags:''
# Note: the child rule must be indented exactly 4 more spaces than the parent.
# Also, this is how to make a comment (first non-whitespace character is a "#"
    pattern:'(?P<content>a*)', tags:'ed'
````

Any line whose first non-whitespace symbol is a "#" is considered a comment. It is also possible to add a description to a specific rule by adding a field that starts with "desc".

Good to know:
> Try to use non-greedy quantifiers when possible. For example, `.*` should be `.*?`, as `.*` would match as much as possible while `.*?` tries to find the shortest match possible (which is usually we want).

> All leaves (those rules who contain a leaf tag such as "DELETE") must be children of a container element (one that has the "CONTAINER" tag), or be one themselves.

> To add info to a pattern, another parameter whose name starts with "desc" can be added to it.

> To add a comment, add a line whose first non-whitespace character is a "#"


### html -> HTMLSchema
This type of schema is used for HTML document. It is similar to the GenericSchema, but has the following possible fields:
* _html\_tag_: the tag of the html content. To match, for example, a <a></a> element, this would be set to "a". Allows regular expressions
* _recursive_: if set to 'False', only direct children of the parent element will be considered. If set to 'True' (default), all descendents will be considered using a recursive search.
* _content\_tags_: just content tags. Example: "de" for "DELETE" and "ELEMENT"
* _edit\_attrs_: the elements attributes that should be edited. Contains a whitespace-separated list with values in the style of `attribute_name:contentTag1ContentTag2`. Example for an _href_ and _src_ attribute: `'href:l src:p'`
* _not\_attrs_: if the element contains one of the attributes, it is ignored. Example to ignore elements with "class" or "src" attributes: 'class src'
* _precondition_: a precondition that must be met for the element to be matched. Is a regex, and only applies to elements with the DELETE_UNCONDITIONAL or CONTAINER tags
* all other fields: will be considered attribute names and their value a regex that must match its value.
  * If the name is followed by a "!", the value will be traded as a list of values which must be found in the attribute.
  * In case only elements that contain a link to `example.com`, the following could be added to the rule: `href: 'https:\/\/example\.com'`

> Note: every field's value must be enclosed by single quotes

To add a comment, To add a comment, add a line whose first non-whitespace character is a "#". Just like with GenericSchemas