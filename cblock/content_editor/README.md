The content editors receive a string (the data), split it into logical parts (depending on schema).
For each part, a ContentAnalyzer gets asked to check for offending content, and depending on the result
the part gets changed or not.