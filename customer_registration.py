"""
This script creates the first source (output/customer_datasource.csv) file containing 
all customers basic information and registration statuses.
"""

import pandas as pd
import numpy as np
from faker import Faker


def create_new_random_user(account_id, months_back):
    """
    Function to create a new random user
    The registration workflow is like the following:
    New Account > Confirm email > New Client Info > Approve / Deny > Initial Deposit

    @param account_id <int>: id of the account
    @param months_back <int>: how many months back the client registered the account
    """
    
    # Create a new faker instance
    fake = Faker(['en_US'])

    # Set initial statuses and dates
    status = "Account registered"
    start_date = "-{}M".format(months_back)
    account_registration_dt = fake.date_time_between(start_date=start_date)
    account_email_confirmation_dt = None
    account_email_confirmation_dt_str = None
    client_registration_dt = None
    client_registration_dt_str = None
    client_approval_dt = None
    client_approval_dt_str = None
    client_denial_dt = None
    client_denial_dt_str = None
    client_initial_deposit_dt = None
    client_initial_deposit_dt_str = None

    # Randomly sets if client confirmed email
    if fake.boolean():
        account_email_confirmation_dt = fake.date_time_between_dates(
            datetime_start = account_registration_dt
        )
        account_email_confirmation_dt_str = account_email_confirmation_dt.strftime('%Y-%m-%d %H:%M:%S')
        status = "Email confirmed"

    # Randomly sets if client finished registration
    if account_email_confirmation_dt is not None and fake.boolean():
        client_registration_dt = fake.date_time_between_dates(
            datetime_start = account_email_confirmation_dt
        )
        client_registration_dt_str = client_registration_dt.strftime('%Y-%m-%d %H:%M:%S')
        status = "Client registered"

    # Randomly sets if client was approved
    if client_registration_dt is not None and fake.boolean():
        client_approval_dt = fake.date_time_between_dates(
            datetime_start = client_registration_dt
        )
        client_approval_dt_str = client_approval_dt.strftime('%Y-%m-%d %H:%M:%S')
        status = "Client approved"

    # Randomly sets if client was denied
    if client_registration_dt is not None and client_approval_dt is not None and fake.boolean():
        client_denial_dt = fake.date_time_between_dates(
            datetime_start = client_registration_dt
        )
        client_denial_dt_str = client_denial_dt.strftime('%Y-%m-%d %H:%M:%S')
        status = "Client denied"

    # Randomly sets initial deposit (only for approved clients)
    if client_approval_dt is not None and fake.boolean():
        client_initial_deposit_dt = fake.date_time_between_dates(
            datetime_start = client_approval_dt
        )
        client_initial_deposit_dt_str = client_initial_deposit_dt.strftime('%Y-%m-%d %H:%M:%S')
        status = "Client denied"        

    # Creates a new dictionary containing all client information to be written on the output file
    user = {
        'id': account_id,
        'name': fake.unique.name(),
        'address': fake.address(),
        'birthdate': fake.date_this_century().strftime('%Y-%m-%d'),
        'status': status,
        'account_registration_dt': account_registration_dt.strftime('%Y-%m-%d %H:%M:%S'),
        'account_email_confirmation_dt': account_email_confirmation_dt_str,
        'client_registration_dt': client_registration_dt_str,
        'client_approval_dt': client_approval_dt_str,
        'client_denial_dt': client_denial_dt_str,
        'client_initial_deposit_dt': client_initial_deposit_dt_str,
    }

    return user


def create_customer_registration_file(number_of_customers, months_back):
    """
    Function to create a new file (customer_datasource.csv) into the output folder
    containing all fake customers and registration datetimes
    
    @param numer_of_customers <int>: amount of fake customers to create
    @param months_back <int>: how many months back the client registered the account
    """    

    print("Creating new customer_datasource.csv with {} customers, {} months back...".format(number_of_customers, months_back))

    # Create list of random users
    users_list = []
    for i in range(number_of_customers):
        users_list.append(create_new_random_user(i, months_back))

    # Creates a dataframe based on the user list
    df = pd.DataFrame(users_list)

    # Output result to a csv file
    df.to_csv('output/customer_datasource.csv')

    print("New file customer_datasource.csv done!")