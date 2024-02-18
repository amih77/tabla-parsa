## Document Parser And Validator
### Description
This project is meant for parsing documents, and validating them according to some 
rules. It presents a programmatic API for storing, getting, updating and deleting a document.
### Usage
1. Install all dependencies in `requirements.txt`
2. Pass the documents directory to `api.create_documents()`
3. Perform CRUD operations on the stored documents

### Design Minutes
* The parsing of the `html` documents is done by `beautifulsoup`
* Both `Document` and `Discrepancy` are ODM classes (Object Document Model) and implement relevant DB methods
* I am using `pydantic` class framework whenever I can. I like it for its simplicity, cleanness and parsing/validating power
* I chose to implement `DocumentValidator` with _Strategy_ design pattern as it provides great extensibility and dynamic flexibility. This pattern involves defining a family of algorithms, encapsulating each one, and making them interchangeable. It lets the algorithm vary independently from the clients that use it, which in the context of calculating discrepancies, allows for flexible and maintainable discrepancy detection logic which can be further developed and enriched.
* I separated `Document`s and `Discrepancy`s among different DB collections for the following reasons:
  * Modularity: It allows us to tailor the schema, indexing, and access patterns to the specific needs of each type of data, enhancing clarity and maintainability of the database structure,
  * Performance: we can optimize queries, updates, and indexes for each collection independently,
  * Scalability: We shouldn't expect the same growth behavior from the two collections therefore we have the flexibility of treating each one differently yet having minimal effect on the entire system.
* I decided to go with _soft deletion_ as the mean of db document deletion - I think it's considered to be a good practice (never actually delete from the DB...)
* I contemplated a bit about the implementation of `creation_date` and `location`. Decided to go with computing them dynamically as properties and storing the raw footer.
### Tech Debt
Many improvements come to mind, here are some of them:
* `MongoDB` improvements, such as inserting and fetching multiple documents at once
* The async job of calculating document's discrepancies can be impelemnted with a more robust framework such as `Celery` etc.
* update and delete document should have a transaction/lock mechanism as it involves document and discrepancies

### Conclusion
I had great fun working on this exercise, especially getting to experience with `MongoDB` and _Strategy_ design pattern.

Thanks and see you on Wednesday!