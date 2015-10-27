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
  When the client queries "age_and_gender" for "age_group:total" returning all "years"
  Then from the "age_and_gender" result the "2002" value is greater than "10"
  Then from the "age_and_gender" result the "2010" value is greater than "10"

Scenario: query-age-gender-other
  Given a client
  When the client queries "age_and_gender" for "gender:males" returning all "2010"
  Then from the "age_and_gender" result the "2002" value is undefined
  Then from the "age_and_gender" result the "2010" value is greater than "10"

Scenario: query-age-gender-invalid
  Given a client
  When the client queries "invalid_table" for "gender:males" returning all "2010"
  Then the "invalid_table" result is empty
  Then the "invalid_table" result is an error
  When the client queries "age_and_gender" for "invalid_query" returning all "2010"
  Then the "age_and_gender" result is empty

