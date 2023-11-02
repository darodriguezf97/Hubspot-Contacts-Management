# Library for OTF Data Preprocessing

import time
import pycountry
import requests
from geotext import GeoText
from geopy.geocoders import Nominatim
import re
import phonenumbers

contact_collection_called = False


def contact_collection(api_key):
    # Declare contacts and global variable contact_collection_called
    contacts = []
    global contact_collection_called

    # Start the contact collection process
    print("Starting contact collection...")

    # Start measuring time
    start_time = time.time()

    # Define url
    url = "https://api.hubapi.com/crm/v3/objects/contacts/search"

    # Print the API request URL
    print(f"Making API request to {url}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Initialize 'after' for paging and 'request_count' for request counting
    after = ''
    request_count = 0

    # Loop indefinitely until all pages are fetched
    while True:
        request_count += 1

        # Construct the request body with 'after' and 'limit' for pagination
        body = {
            "filterGroups": [
                {
                    "filters": [
                        {
                            "propertyName": "allowed_to_collect",
                            "operator": "EQ",
                            "value": "true"
                        }
                    ]
                }
            ],
            "properties": [
                "raw_email",
                "country",
                "phone",
                "technical_test___create_date",
                "industry",
                "address",
                "hs_object_id"
            ],
            'after': after,  # Set 'after' for pagination
            'limit': 100  # Set 'limit' to control page size
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code != 200:
            print(f"Error making API request: {response.content}")
            return contacts  # Return collected contacts in case of an error

        # Collect contacts and add them to the list
        contacts_data = response.json()
        contacts.extend(contacts_data['results'])

        # Check for more pages of results
        if 'paging' in contacts_data and 'next' in contacts_data['paging']:
            after = contacts_data['paging']['next']['after']
        else:
            if contacts:
                print(f"Collected {len(contacts)} contacts.")
            else:
                print("No contacts were able to collect.")

        if 'paging' not in contacts_data or 'next' not in contacts_data['paging']:
            break  # Exit the loop when there are no more pages

    # Calculate end time
    end_time = time.time()

    # Calculate total time
    total_time = end_time - start_time

    # Print the total number of request and the total time of the function
    print(f"Total requests: {request_count}")
    print(f"Total execution time: {total_time} seconds")

    # Change collected_contacts_called to True
    contact_collection_called = True

    return contacts


country = ''


def country_recognition(contact_id, contacts):
    """
    Recognize the country and city, if present, in a HubSpot contact.

    Args:
        contact_id (str): The id of the contact to be searched in the contacts list as a string.
        contacts (list): The list of contacts managed to process.

    Returns:
        tuple: A tuple containing the country and city of the HubSpot contact.
    """
    # Declare a global variable 'country' to store the recognized country.
    global country

    try:
        # Check if the input contact_id matches the current contact's ID
        for contact in contacts:
            if str(contact['id']) == contact_id:
                # Get the 'country' property from the contact's properties or set it to an empty string if not present.
                country_or_city = contact["properties"].get("country", "")

                # Use the GeoText library to identify countries and cities in the 'country_or_city' string.
                places = GeoText(country_or_city)

                if places.countries:
                    # If GeoText recognizes a country, return it directly
                    country = places.countries[0]
                    return (country, "")

                elif places.cities:
                    # If GeoText recognizes a city, get the corresponding country through geopy nominatim but returns
                    # only the country mentioned.
                    geolocator = Nominatim(user_agent="geoapiExercises")
                    city = places.cities[0]
                    location = geolocator.geocode(city)
                    # Use GeoText to recognize the country from the geopy location's address.
                    country = GeoText(location.address).countries[0]
                    return (country, city)
    except Exception as e:
        # Print an error message if an exception occurs.
        print(f"Error: {e}")


def found_emails(contact_id, contacts):
    """
    This function extracts the email address from the 'raw_email' property of each contact
    in the contacts list whose id matches the input contact_id.

    Args:
        contact_id (str): The id of the contact for which to find the email address as a string.
        contacts (list): The list of contacts managed contacts to process.

    Returns:
        str: The email address of the contact if found, otherwise None.
    """

    # Iterate over each contact in the contacts list
    for contact in contacts:
        # Check if the input contact_id matches the current contact's ID
        if str(contact['id']) == contact_id:
            # Extract the "raw_email" property
            raw_email = contact["properties"]["raw_email"]
            # If a match is found, extract the email address from 'raw_email'
            email = re.search('<(.*)>', raw_email)
            if email:
                # Return the extracted email address
                return email.group(1)

    # If no match is found, return None
    return None


def fix_phone_numbers(contact_id, contacts):
    """
    This function formats a contact phone number according to the country's phone code.

    Args:
        contact_id (str): The id of the contact for which to find the phone, country and fix the number.
        contacts (list): The list of contacts managed contacts to process.

    Returns:
        str: The formatted phone number.
    """
    # Check if contacts have been collected from HubSpot
    if not contact_collection_called or not contacts:
        raise Exception("Please extract the contacts from HubSpot first using the contact_collection function.")

    # Iterate over each contact in the contacts list
    for contact in contacts:
        # Check if the input contact_id matches the current contact's ID
        if str(contact['id']) == contact_id:
            # Get the 'phone' property from the contact
            phone = contact["properties"]["phone"]
            if phone is None:
                # If no phone number is found, print a warning and continue to the next contact.
                print(f"Warning: No phone number found for contact '{contact_id}'.")
                continue

            contact_country = country
            # Convert country name to ISO 3166-1 alpha-2 code
            country_iso = pycountry.countries.get(name=contact_country)
            if country_iso is None:
                # If no matching country is found, print a warning and continue to the next contact.
                print(f"Warning: Could not find a matching country for '{contact_id}'.")
                continue

            country_code = country_iso.alpha_2

            try:
                # Use the phonenumbers library to parse the phone number according to the country code.
                parsed_number = phonenumbers.parse(phone, country_code)
            except phonenumbers.phonenumberutil.NumberParseException as e:
                # If the phone number parsing fails, print a warning and continue to the next contact.
                print(f"Warning: Could not parse phone number for contact '{contact_id}'. Error: {e}")
                continue

            # Format the parsed number in international format
            formatted_number = phonenumbers.format_number(parsed_number,
                                                          phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            # Add parentheses around the country code
            formatted_number = re.sub(r'\+([0-9]+)', r'(\+\1)', formatted_number)

            return formatted_number

    return None


def manage_duplicates(contacts):
    """
    This function manage duplicate contacts from the contacts list.

    Args:
        contacts (list): The list of contacts to be filtered.

    Returns:
        list: The filtered list of contacts.
    """

    email_contacts = {}  # Initialize a dictionary to store contacts based on email addresses.
    name_contacts = {}  # Initialize a dictionary to store contacts based on names.

    # Iterate over each contact in the contacts list
    for contact in contacts:
        # Extract the contact id as string
        contact_id = str(contact["id"])
        # Check if the 'raw_email' property exists for the contact
        if 'raw_email' in contact["properties"]:
            # Extract the "raw_email" property
            raw_email = str(contact["properties"]["raw_email"])
            # Extract the contact name from "raw_email"
            name_match = re.search('(.*) <', raw_email)
            if name_match:
                name = name_match.group(1).strip()
            else:
                # If a name can't be extracted, print a warning and continue to the next contact.
                print(f"Warning: Could not extract a name from 'raw_email' for contact {contact['id']}.")
                continue

        # Get the email address using the found_emails function.
        email = found_emails(contact_id, contacts)

        if email not in email_contacts:
            # If the email is not already in the email_contacts dictionary, add it with the corresponding contact.
            email_contacts[email] = contact

        if name and name not in name_contacts:
            # If a name is available and it is not already in the name_contacts dictionary, add it with the
            # corresponding contact.
            name_contacts[name] = contact

        else:
            existing = email_contacts[email]
            if existing["properties"]["createdate"] < contact["properties"]["createdate"]:
                # Update with the most recent record
                email_contacts[email] = contact

                # Adding missing properties from the existing contact
                for prop in existing["properties"]:
                    if prop not in contact["properties"]:
                        contact["properties"][prop] = existing["properties"][prop]

            existing = name_contacts[name]
            if existing["properties"]["createdate"] < contact["properties"]["createdate"]:
                # Same process but for name
                name_contacts[name] = contact

                for prop in existing["properties"]:
                    if prop not in contact["properties"]:
                        contact["properties"][prop] = existing["properties"][prop]

    # Create a list of contacts from the email_contacts dictionary.
    final_contacts = list(email_contacts.values())

    for contact in final_contacts:

        # Implement the industries process
        industries = []
        if "Industry" in contact["properties"]:
            industries.append(contact["properties"]["Industry"])

        # Convert the industries list to a set to remove duplicates.
        industries = set(industries)

        # Join the industries with semicolons.
        concat_industries = ";".join(industries)

        # Update the "Industry" property.
        contact["properties"]["Industry"] = concat_industries

    # Return the filtered list of contacts.
    return final_contacts


def saving_contacts(contacts):
    """
    This function processes a list of contacts, applying the country_recognition, found_emails,
    and fixed_phone_numbers functions to each contact. Then, saves the new properties with the transformed data in
    the contact list and uploaded to the HubSpot API.

    Args:
        contacts (list): The list of contacts to process.

    Returns:
        list: The processed list of contacts.
    """
    # Start measuring time
    start_time = time.time()

    # Iterate over each contact in the contacts list
    for contact in contacts:
        # Extract the contact id as a str
        contact_id = str(contact["id"])

        if contact["properties"]["hs_object_id"] == contact_id:
            # Apply the country_recognition function and store the result in new properties
            country_city = country_recognition(contact_id, contacts)
            if country_city is not None:
                contact_country, contact_city = country_city
                contact["properties"]["Country"] = contact_country
                contact["properties"]["City"] = contact_city

            # Apply the found_emails function and store the result in a new property
            if 'raw_email' in contact["properties"]:
                # Extract the "raw_email" property
                raw_email = str(contact["properties"]["raw_email"])
                # Extract the contact name from "raw_email"
                name_match = re.search('(.*) <', raw_email)
                if name_match:
                    name = name_match.group(1).strip()
                else:
                    print(f"Warning: Could not extract a name from 'raw_email' for contact {contact['id']}.")
                    continue

            # Apply the fixed_phone_numbers function and store the result in a new property
            phone_number = fix_phone_numbers(contact_id, contacts)
            if phone_number is not None:
                contact["properties"]["Phone Number"] = phone_number

        # Calculate end time
        end_time = time.time()

        # Calculate total time
        total_time = end_time - start_time

    print(f"Total execution time: {total_time} seconds")
    return contacts


def upload_transformed_data(api_key, contacts):
    """
      Upload transformed contacts to HubSpot.

      Parameters:
      - api_key: HubSpot API key
      - contacts: List of dictionaries with contact data

      Returns: None
      """
    # Define the base URL for the HubSpot API
    base_url = "https://api.hubapi.com/crm/v3/objects/contacts"

    # Authentication Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    print(f"Starting uploading process of transformed contacts...")

    # Start measuring time
    start_time = time.time()

    for contact in contacts:

        try:
            # Define the data to update
            data = {
                "properties":
                    {
                        "email": contact["properties"]["Email"],
                        "phone": contact["properties"]["Phone Number"],
                        "country": contact["properties"]["Country"],
                        "city": contact["properties"]["City"],
                        "original_create_date": contact["properties"]["technical_test___create_date"],
                        "original_industry": contact["properties"]["industry"],
                        "temporary_id": contact["properties"]["hs_object_id"]
                    }
            }

            # Make the request
            response = requests.post(base_url, headers=headers, json=data)

            # Check that the request was successful
            response.raise_for_status()

            print(f"Contact {contact['id']} uploaded")

            # Management of exceptions
        except KeyError as e:
            print(f"Error getting property for {contact['id']}: {e}")

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error {response.status_code} for {contact['id']}: {response.text}")

        except Exception as e:
            print(f"Error uploading {contact['id']}: {e}")

    # Calculate end time
    end_time = time.time()

    # Calculate total time
    total_time = end_time - start_time

    print(f"Total execution time: {total_time} seconds")

    print("Migration process completed!")
