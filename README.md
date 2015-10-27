health monger
=============

A json query API on top of heath expendenture data. This service provides a way
to query research statistics from the following CMS sources:
https://www.cms.gov/Research-Statistics-Data-and-Systems/Statistics-Trends-and-Reports/NationalHealthExpendData/index.html


How do I run this?
------------------

To test you type in the following:

```
make check
```

This will check syntax, run unit tests, start up a local test service, run integration tests and then stop the service.


To run a local instance:

```
make start
```

This will start a flask http server hosting the API. It will also attempt to load the database.

To check if it is running you can type:

```
make status
```

To stop this local instance:

```
make stop
```


What does the API look like?
----------------------------

For help on the API type the following:

```
make start # only if a local instance is not running
make status # wait to start up
make api-example
```

Example:

```
curl "http://localhost:5000/query?q=%28gender%3Amales%29&table=age_and_gender&filter=2010"
{
  "result_count": 10,
  "results": [
    {
      "2010": "307",
      "Age Group": "Total",
      "Gender": "Males",
      "Service": "Dental Services"
    },
    {
      "2010": "348",
      "Age Group": "0-18",
      "Gender": "Males",
      "Service": "Dental Services"
    },
    {
      "2010": "278",
      "Age Group": "19-64",
      "Gender": "Males",
      "Service": "Dental Services"
    },
    {
      "2010": "372",
      "Age Group": "65+",
      "Gender": "Males",
      "Service": "Dental Services"
    },
    {
      "2010": "104",
      "Age Group": "Total",
      "Gender": "Males",
      "Service": "Durable Medical Equipment"
    },
    {
      "2010": "42",
      "Age Group": "0-18",
      "Gender": "Males",
      "Service": "Durable Medical Equipment"
    },
    {
      "2010": "84",
      "Age Group": "19-64",
      "Gender": "Males",
      "Service": "Durable Medical Equipment"
    },
    {
      "2010": "354",
      "Age Group": "65+",
      "Gender": "Males",
      "Service": "Durable Medical Equipment"
    },
    {
      "2010": "170",
      "Age Group": "Total",
      "Gender": "Males",
      "Service": "Home Health Care"
    },
    {
      "2010": "90",
      "Age Group": "0-18",
      "Gender": "Males",
      "Service": "Home Health Care"
    }
  ],
  "version": "1.0"
```

The integration tests use the API and has good examples. They are located in the `healthmonger/integration` directory.


How does it work?
-----------------

The main API service uses flask for its web framework. See: `healthmonger/healmonger.py`
  - configuration is in the `healthmonger/config.py` module.

When starting the service it attempts to download data in the configuration.
  - It uses the `healthmonger/loader.py` module.
  - Access to the CMS website is required.
  - Data is loaded into the search index and datastore.

When started you can load data by calling the load endpoint.
  - This will load new data and attempt to do it atomically.
  - The index is whoosh which is a fully python search index.
  - The datastore is an in memory dictionary. It can be any database as long as an API is written.
    - There are hooks for doing this in the loader and database code.

When querying the data via the API
  - An http request is made to the service.
  - There is a 'client' providing an API so the flask parts can query into the data.
  - The request is parsed and used in the db 'client'
  - The db client parses the query using whoosh's parser
  - The whoosh searcher is used to find the indexed data.
  - The results are ids or references to data in the data store.
  - That data is then fetched and formated for the return


When running `make check` the following things happen:

- Stops a running service, cleans old files and data.
- Sets up a python environment and dependencies using virtualenv
- Checks for flake errors using flake8
- Runs unit tests using nose. Tests are located in the `healthmonger/tests` directory.
- Starts a locally hosted healthmonger service
- Runs integration tests
- Cleans up

