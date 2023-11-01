# OTF Data Preprocessing Library
This repository contains a Python library for preprocessing and enriching HubSpot CRM contact data. The library utilizes the HubSpot API to collect allowed contacts and then provides functions to recognize country and city information, extract email addresses, and format phone numbers according to location.

### Key Features
`contact_collection`: Retrieves allowed contacts from HubSpot API applying pagination and rate limiting
`country_recognition`: Identifies country and city from location data on a per-contact basis
`found_emails`: Extracts email address from raw_email string for a given contact
`fix_phone_numbers`: Formats phone numbers by country using phonenumbers library
The library aims to provide an easy way to enrich contact data from HubSpot before further processing and analysis. By handling API interactions, location parsing, and phone number formatting it simplifies downstream data wrangling.

The code follows Python best practices and principles such as:

- Modular functions with docstring documentation
- Handling of errors and edge cases
- Use of appropriate external libraries
- Performance considerations with caching and reuse

### Acknowledgements
I'd like to thank the OTF team for the opportunity to participate in this technical test. It was a rewarding experience that allowed me to demonstrate my skills. While certainly the code can be improved further with more robust error handling, debugging, and handling of missing values, I appreciated the chance to work through the tasks and provide my solutions. Constructive feedback is always welcome to continue improving as a data professional.

### Hoping to be the next Fuzer!
