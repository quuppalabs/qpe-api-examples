# Quuppa Positioning Engine (QPE) API examples

This project **is not** meant to serve as any comprehensive documentation of the Quuppa Positioning Engine (QPE) API but simply shows some use case how the API can be used for different purposes. Both the *Classic QPE* and *Quuppa for Enterprise* include up-to-date, embedded documentation for the API.

## Monitoring the Positioning Engine's Health

The Positioning Engine is a critical component of the Quuppa system, and so most monitoring implementations pull at least some of the data fields from the /getPEInfo endpoint. The data available through the /getPEInfo endpoint gives you a good overview of your Positioning Engine's health. Pulling the data into your existing monitoring systems will make it easy for you to keep and eye on the system and make adjustments accordingly. Use the data fields that are most relevant for your use case. For more options and full descriptions, refer to our full API documentation.

The API examples are implemented in Python. See further [project documentation](https://github.com/quuppalabs/qpe-api-examples/blob/main/docs/index.md) for running the examples.
