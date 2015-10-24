Feature:
  Provide an API on top of heath expendenture data.
  This service provides a way to query research statistics from CMS sources.


Scenario Outline: load-data
  Given a client
  When the client makes a load data request.
  Then the client can observe that data is loaded.

