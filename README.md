# OTF Data Preprocessing Library
This repository contains a Python library for preprocessing and enriching HubSpot CRM contact data. The library utilizes the HubSpot API to collect allowed contacts and then provides functions to recognize country and city information, extract email addresses, and format phone numbers according to location.

### Key Features
A library aiming to provide the correct data pre-proccessing contact data from HubSpot before further analysis. It contains fundamental functions to perform a ETL process, like:

`contact_collection`: Retrieves allowed contacts from HubSpot API applying pagination and rate limiting

`manage_duplicates`: Manage duplicate contacts from the contacts list to filter the list of contacts

`country_recognition`: Identifies country and city from location data on a per-contact basis

`found_emails`: Extracts email address from raw_email string for a given contact

`fix_phone_numbers`: Formats phone numbers by country using phonenumbers library

Also, it stores:

1. A Jupyter NoteBook where a data pipeline covering an entire ETL Process to migrate all contact records from the
Source HubSpot Account to your HubSpot Account automatically.

2. The Extraction and Transformation data results in .csv file format.

3. A file with the answers to the test questions.


The code follows Python best practices and principles such as:

- Modular functions with docstring documentation
- Handling of errors and edge cases
- Use of appropriate external libraries
- Performance considerations with caching and reuse

### Acknowledgements
I'd like to thank the OTF team for the opportunity to participate in this technical test. It was a rewarding experience that allowed me to demonstrate my skills. While certainly the code can be improved further with more robust error handling, debugging, and handling of missing values, I appreciated the chance to work through the tasks and provide my solutions. Constructive feedback is always welcome to continue improving as a data professional.

### Hoping to be the next Fuzer!
