import pandas as pd
import numpy as np
from datetime import datetime


def create_customer_activity_file():
    """
    Function to create customer_activity.csv file based on transactions file
    """
    print("Creating new customer_activity.csv...")
    
    # read from transaction files
    df_transactions = pd.read_csv('output/customer_transactions.csv')

    # create new column for month
    df_transactions["transaction_month"] = pd.to_datetime(df_transactions.transaction_datetime)
    df_transactions['transaction_month'] = df_transactions['transaction_month'].dt.strftime('%Y-%m-01')

    # consolidate transactions by month
    df_transactions_by_month = df_transactions.groupby(["id", "transaction_month"]).size().reset_index()

    # rename count column from 0 to num_of_transactions
    df_transactions_by_month.rename(columns={0:"num_of_transactions"}, inplace=True)

    # gets all months available on the dataset
    min_month = df_transactions_by_month["transaction_month"].min()
    max_month = datetime.today()
    df_months = pd.DataFrame(data=pd.date_range(min_month, max_month, freq='MS').strftime("%Y-%m-01").tolist(), columns=["month"])
    df_months['index'] = 1

    # gets minimum transaction date for each id
    df_client_mindt = df_transactions_by_month.groupby(["id"])[["transaction_month"]].min().reset_index()
    df_client_mindt['index'] = 1

    # gets all combinations for future dates for each id
    #
    # Similar to:
    # SELECT *
    # FROM df_client_mindt a,
    #      df_months b
    # WHERE b.months >= a.transaction_month
    df_client_months = pd.merge(df_client_mindt, df_months, how="outer", on=["index"])
    df_client_months = df_client_months[df_client_months["month"] >= df_client_months["transaction_month"]]
    df_client_months.drop(columns=["transaction_month", "index"], inplace=True)
    df_client_months.rename(columns={"month": "transaction_month"}, inplace=True)

    # join dataframes with all possibilities x transactions
    df_churn = pd.merge(df_client_months, df_transactions_by_month, how="left", on=["id", "transaction_month"])
    df_churn["num_of_transactions_prev"] = (df_churn.sort_values(by=["transaction_month"], ascending=True)).groupby(["id"])["num_of_transactions"].shift(1)

    # replace nulls and convert to integer
    df_churn["num_of_transactions"] = df_churn["num_of_transactions"].fillna(0)
    df_churn["num_of_transactions"] = df_churn["num_of_transactions"].astype('Int64')
    df_churn["num_of_transactions_prev"] = df_churn["num_of_transactions_prev"].fillna(0)
    df_churn["num_of_transactions_prev"] = df_churn["num_of_transactions_prev"].astype('Int64')

    # flags for new_active / churn
    df_churn["flag_new_active"] = np.where((df_churn["num_of_transactions"] > 0) & (df_churn["num_of_transactions_prev"] == 0), 1, 0)
    df_churn["flag_churn"] = np.where((df_churn["num_of_transactions"] == 0) & (df_churn["num_of_transactions_prev"] > 0), 1, 0)

    # Output result to a csv file
    df_churn.to_csv('output/customer_activity.csv')

    print("New file customer_activity.csv done!")
