import pandas as pd
import random
import decimal
from datetime import datetime
from faker import Faker


def create_customer_transactions_file():
    """
    Function responsible for generating a file (customer_transactions.csv) containing fake transactions
    to be used in customer activity related analysis
    """
    print("Creating new customer_transactions.csv...")

    # Reads original customer datasource
    df = pd.read_csv('output/customer_datasource.csv')

    # Create a new faker object to be used later
    fake = Faker(['en_US'])

    # Gets the initial deposit datetimes since this is supposed to be 
    # the first transaction of a customer
    df_initial_deposit = df[df['client_initial_deposit_dt'].notnull()][['id', 'client_initial_deposit_dt']]
    df_initial_deposit.rename(columns={'client_initial_deposit_dt': 'transaction_datetime'}, inplace=True)

    # Sets the type of transaction as income, this way we don't have to
    # worry about clients with negative balances in the end (for now)
    df_initial_deposit['operation'] = "Income"

    # Sets a random value to the transaction
    df_initial_deposit['amount'] = df_initial_deposit.apply(
        lambda row: float(decimal.Decimal(random.randrange(15500, 38900))/100),
        axis = 1
    )

    # Creates a new set of transactions after the initial deposit
    transaction_list = []
    # For each client with initial deposit
    for ix, row in df_initial_deposit.iterrows():        
        # Generate a random number of transactions (up to 10)
        num_of_transactions = random.randrange(0,10)
        for i in range(0, num_of_transactions, 1):
            # Create a new transaction dictionary
            transaction_row = {        
                'id': row.id,
                'transaction_datetime': fake.date_time_between_dates(
                    datetime_start = datetime.strptime(row.transaction_datetime, '%Y-%m-%d %H:%M:%S')
                ).strftime('%Y-%m-%d %H:%M:%S'),
                'operation': "Income",
                'amount': float(decimal.Decimal(random.randrange(15500, 38900))/100),
            }
            transaction_list.append(transaction_row)
    
    # Create a new dataframe from the list of fake transactions
    df_fake_transactions = pd.DataFrame(data=transaction_list)

    # Union both dataframes into a final one
    objs = [
        df_initial_deposit, 
        df_fake_transactions
    ]
    df_final_transactions = pd.concat(objs=objs)

    # Output the information into customer_transactions.csv
    df_final_transactions.to_csv('output/customer_transactions.csv')

    print("New file customer_transactions.csv done!")