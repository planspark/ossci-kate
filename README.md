# OSSciKate

A basic CRUD web app that enables authenticated users to a) add and update three entity types, b) indicate if they are related, and c) browse a visualization of the resulting network graph.

The three entities are:

* OSS tools
* Published research papers
* People

Possible relations are:

* Tool --> person (e.g., maintainer, contributor)
* Paper --> person (author)
* Tool --> paper (e.g., citation, quote, reference)

