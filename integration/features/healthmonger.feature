Feature:
  Provide an API on top of heath expendenture data.
  This service provides a way to query research statistics from CMS sources.


Scenario: load-data
  Given a client
  When the client makes a status request
  Then the status is OK
  When the client makes a load data request.
  Then the client can observe that data is loaded.

Scenario: query-age-gender-health-expenditures
  Given a client
  When the client queries "age_and_gender" for "age:total" returning all "years"
  Then from "age_and_gender" the "total" value is ">1"

@skip
Scenario: query-all
  Given a client
  When the client queries "age_and_gender" for "" returning all "years"
  Then from "age_and_gender" the "2002" value is ">1"
