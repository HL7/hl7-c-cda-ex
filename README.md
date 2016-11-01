# HL7 C-CDA Examples Search and Display Rails application

## Introduction
The C-CDA Example Search application was created in an effort to improve the discoverability and retrieval of the various examples that have been created to demonstrate accepted serialization in C-CDA R2.1. The examples for previous version were spread across various git repositories and described using a wiki that only had rudimentary query tools. The proposed solution to be executed in conjunction with updating the examples for C-CDA R2.1 was the collect all of the samples into a single repository and develop a query application similar to the HL7 Tooling Catalogue.

To accomplish the goal of expanded search capabilities, the metadata associated with each example was standardized by the Examples Task Force and stored in Markdown format in a README.md file in the same directory as the example in the repository. A simple, flat directory structure was created to divide the examples up by section (and in the future document and header). Within each section directory, the further set of sub-directories would be created, one for each example, that contained the raw XML example (possibly more than one for the various C-CDA releases) and the metadata file. The section directory would also contain a Markdown readme file with a description of the section.

## Design
### Database
The database contains 3 simple entities, Sections, Examples, and Approvals. Each Section has multiple Examples and each Example can have multiple Approvals.

*Sections*
 have a type and a description. The type is one of section, document or header. The description is the contents of the section readme file.

*Examples*
 entities contain all of the metadata for an example other than the approvals. The metadata is parsed into specific fields such as keywords, description, approval status to enable the query engine. The raw example source is contained in the record to allow for a syntax highlighted display of the example. Additionally, the location of the raw example source file is stored to enable navigation to the example of GitHub.

*Approvals*
log the various approval details parsed from the metadata. These details include approved yes/no, approval date, approval committee and approval comments.

### Query
The query mechanism is based on three axes, text search, section membership and status. The text search uses the PostgreSQL text search engine across an index built from the example title, example description and example keywords. The text search engine is described in more detail [here](http://rachbelaid.com/postgres-full-text-search-is-good-enough/).
 
 ## Operation
 The application runs as a standard Rails web application. The current installed on Heroku. The standard deployment to Heroku described [in the developer documentation](https://devcenter.heroku.com/articles/getting-started-with-rails4) is the best description of the process.
 
 ### Data Generate and Load
The database that supports the web application can be recreated at any time from the current C-CDA Examples repository. The commands to create the load files for the full example repository search are contained as part of the current projects and embedded as rake tasks. Running the data generate will replace the files located in db/load-data with the current state of the C-CDA Example repository.

To run the data generate task, you will need to have a GitHub user id and have access to the GitHub C-CDA Example repository with your GitHub Id. If you are more comfortable generating a personal access token rather than sending your password to generate the load, please use the GitHub interface.


### Unattended Data Update