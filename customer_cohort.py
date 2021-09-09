import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def days_between_dates(date1, date2):
    """
    Function to calculate the difference in days between two dates
    @param date1: first date (latest)
    @param date2: second date (oldest)
    """
    if date1 is not None and date2 is not None:
        date1 = datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.strptime(date2, "%Y-%m-%d")
        return abs((date2 - date1).days)
    else:
        return None


def get_analyzed_date(appr_dt, deny_dt):
    """
    Function to get analyzed datetime (get first non null date)
    @param appr_dt <datetime>: approved datetime
    @param deny_dt <datetime>: denied datetime
    """
    if appr_dt is not None or deny_dt is not None:
        if appr_dt is not None:
            return appr_dt
        else:
            return deny_dt
    else:
        return None


def get_df_client_count(df, columnname_date_from, columnname_date_to, status_from, status_to):
    """
    Function to get the count of clients based on the statuses from and to and dates
    @param df <pandas DataFrame>: dataframe containing client registration data
    @param columnname_date_from <string>: name of the datetime column from status from
    @param columnname_date_to <string>: name of the datetime column from status to
    @param status_from <string>: status from, starting point
    @param status_to <string>: status to, end point
    """

    # filter only relevant values based on date
    df_client_count = df[df[columnname_date_from].notnull()][["id", columnname_date_from, columnname_date_to]]

    # rename date columns
    columns_rename = {
    columnname_date_from : 'status_datetime_from', 
    columnname_date_to : 'status_datetime_to'
    }
    df_client_count.rename(columns=columns_rename, inplace=True)

    # add numbers to count customers in the end
    df_client_count['status_from_count'] = 1
    df_client_count['status_to_count'] = np.where(df_client_count.status_datetime_to.notnull(), 1, 0)

    # transform columns from datetime to date
    df_client_count['status_datetime_from'] = pd.to_datetime(df_client_count.status_datetime_from)
    df_client_count['status_datetime_from'] = df_client_count['status_datetime_from'].dt.strftime('%Y-%m-%d')
    df_client_count['status_datetime_to'] = pd.to_datetime(df_client_count.status_datetime_to)
    df_client_count['status_datetime_to'] = df_client_count['status_datetime_to'].dt.strftime('%Y-%m-%d')

    # count clients: first calculate whole population from, then get conversions and in the end merge both info
    df_client_count_status_from = df_client_count.groupby(["status_datetime_from"]).sum().reset_index()[["status_datetime_from", "status_from_count"]]
    df_client_count_status_to = df_client_count.groupby(["status_datetime_from", "status_datetime_to"]).sum().reset_index()[["status_datetime_from", "status_datetime_to", "status_to_count"]]
    df_client_count = pd.merge(df_client_count_status_to, df_client_count_status_from, how="left", on=["status_datetime_from"])

    # create status columns
    df_client_count['status_from'] = status_from
    df_client_count['status_to'] = status_to

    return df_client_count


def get_all_statuses_dataframe():
    """
    Function to return a dataframe with all status combinations available (from and to)
    """
    statuses = {
        "order": [1, 2, 3, 4, 5],
        "status": [
        'Account registered',
        'Email confirmed',
        'Client registered',
        'Client analyzed (approved or denied)',
        'Initial deposit'      
        ]
    }

    # Creates 2 different dataframes from the statuses
    df_status_list1 = pd.DataFrame(statuses)
    df_status_list1['id'] = 1
    df_status_list2 = pd.DataFrame(statuses)
    df_status_list2['id'] = 1

    # Create a final dataframe with all possible status combinations
    #
    # Similar to:
    # SELECT a.status as status_from, b.status as status_to
    # FROM df_status_list a,
    #      df_status_list b
    # WHERE a.order < b.order
    df_statuses_final = pd.merge(df_status_list1, df_status_list2, on="id", how="outer")
    df_statuses_final = df_statuses_final[df_statuses_final["order_x"] < df_statuses_final["order_y"]][["status_x", "status_y"]]

    # Create a new field to do all possible combinations with date later
    df_statuses_final['id'] = 1

    return df_statuses_final


def get_all_dates_dataframe(df):
    """
    Function that return a dataframe with all date combinations available (from and to)
    It uses the minimum account registration date as a starting date and current date as end date
    @param df <pandas DataFrame>: dataframe containing customer registration data (base file)
    """
    # Create all days from min date to today
    min_registration_date = datetime.strptime(df["account_registration_dt"].min(), '%Y-%m-%d %H:%M:%S')
    start_date = min_registration_date.date()
    end_date = datetime.now().date()
    delta = end_date - start_date
    dates_list = []
    for i in range(delta.days + 1):
        date = start_date + timedelta(days=i)
        dates_list.append(date.strftime('%Y-%m-%d'))

    df_dates = pd.DataFrame(data=dates_list, columns=['date'])

    # Do all possible combinations
    df_dates_list1 = pd.DataFrame(df_dates)
    df_dates_list1['id'] = 1
    df_dates_list2 = pd.DataFrame(df_dates)
    df_dates_list2['id'] = 1

    # Create dataframe with just relevant data (feasible dates)
    #
    # Similar to:
    # SELECT a.date as date_from, b.date as date_to
    # FROM df_dates_list a,
    #      df_dates_list b
    # WHERE a.date <= b.date
    df_dates_final = pd.merge(df_dates_list1, df_dates_list2, on="id", how="outer")
    df_dates_final = df_dates_final[df_dates_final["date_x"] <= df_dates_final["date_y"]][["date_x", "date_y"]]

    # Calculate date difference in days
    df_dates_final['datetime_diff_days'] = df_dates_final.apply(
        lambda row: days_between_dates(row.date_x, row.date_y), 
        axis=1
    )

    # Create a new field to do all possible combinations with statuses
    df_dates_final['id'] = 1

    return df_dates_final


def get_all_counts_dataframe(df):
    """
    Function that returns a dataframe with all counts for statuses and dates from -> to
    @param df <pandas DataFrame>: dataframe containing customer registration data (base file)
    """

    # Counts for status from = Account Registration
    df_case1_2 = get_df_client_count(df, "account_registration_dt", "account_email_confirmation_dt", "Account registered", "Email confirmed")
    df_case1_3 = get_df_client_count(df, "account_registration_dt", "client_registration_dt", "Account registered", "Client registered")
    df_case1_4 = get_df_client_count(df, "account_registration_dt", "client_analysis_dt", "Account registered", "Client analyzed (approved or denied)")
    df_case1_5 = get_df_client_count(df, "account_registration_dt", "client_initial_deposit_dt", "Account registered", "Initial deposit")

    # Counts for status from = Email Confirmation
    df_case2_3 = get_df_client_count(df, "account_email_confirmation_dt", "client_registration_dt", "Email confirmed", "Client registered")
    df_case2_4 = get_df_client_count(df, "account_email_confirmation_dt", "client_analysis_dt", "Email confirmed", "Client analyzed (approved or denied)")
    df_case2_5 = get_df_client_count(df, "account_email_confirmation_dt", "client_initial_deposit_dt", "Email confirmed", "Initial deposit")

    # Counts for status from = Client Registration
    df_case3_4 = get_df_client_count(df, "client_registration_dt", "client_analysis_dt", "Client registered", "Client analyzed (approved or denied)")
    df_case3_5 = get_df_client_count(df, "client_registration_dt", "client_initial_deposit_dt", "Client registered", "Initial deposit")

    # Counts for status from = Client Analysis
    df_case4_5 = get_df_client_count(df, "client_analysis_dt", "client_initial_deposit_dt", "Client analyzed (approved or denied)", "Initial deposit")

    # Union all dataframes
    objs=[
        df_case1_2, df_case1_3, df_case1_4, df_case1_5,
        df_case2_3, df_case2_4, df_case2_5,
        df_case3_4, df_case3_5,
        df_case4_5
    ]
    df_client_counts = pd.concat(objs=objs)

    return df_client_counts


def create_customer_cohort_file():
    """
    Function that uses the customer registration information and puts
    into a better format for Tableau
    """
    print("Creating new customer_datasource_cohort.csv...")

    # read the file containing all client information
    df = pd.read_csv('output/customer_datasource.csv')

    # create new column to store analyzed datetime
    df["client_analysis_dt"] = df.apply(
        lambda row: get_analyzed_date(row.client_approval_dt, row.client_denial_dt),
        axis=1
    )

    # get all date combinations
    df_dates_final = get_all_dates_dataframe(df)

    # get all statuses combinations
    df_statuses_final = get_all_statuses_dataframe()

    # Create a dataframe with all combinations of dates and statuses
    #
    # Similar to:
    # SELECT a.date_from, a.date_to, a.status_from, a.status_to
    # FROM df_dates_final a,
    #      df_statuses_final b
    df_final_cohort = pd.merge(df_dates_final, df_statuses_final, on="id", how="outer")

    # Rename columns for the join with client counts and drop unused field (id)
    columns_rename = {
        'date_x': 'status_datetime_from',
        'date_y': 'status_datetime_to',
        'status_x': 'status_from',
        'status_y': 'status_to',
    }
    df_final_cohort.rename(columns=columns_rename, inplace=True)
    df_final_cohort.drop(columns=['id'], inplace=True)

    # get all customer counts
    df_client_counts = get_all_counts_dataframe(df)

    # Join information from all dates and statuses with client counts
    #
    # Similar to:
    # SELECT a.*, b.*
    # FROM df_final_cohort a
    # LEFT JOIN df_client_counts b ON a.status_datetime_from = b.status_datetime_from
    #                             AND a.status_datetime_to = b.status_datetime_to
    #                             AND a.status_from = b.status_from
    #                             AND a.status_to = b.status_to
    df_final_cohort = df_final_cohort.merge(
        df_client_counts, 
        on=[
            "status_datetime_from", 
            "status_datetime_to", 
            "status_from", 
            "status_to"
        ], 
        how="left"
    )

    # Replace non matching rows with 0 on the count
    df_final_cohort['status_from_count'] = df_final_cohort['status_from_count'].fillna(0)
    df_final_cohort['status_from_count'] = df_final_cohort['status_from_count'].astype('Int64')
    df_final_cohort['status_to_count'] = df_final_cohort['status_to_count'].fillna(0)
    df_final_cohort['status_to_count'] = df_final_cohort['status_to_count'].astype('Int64')

    # Output information into csv file
    df_final_cohort.to_csv('output/customer_datasource_cohort.csv')

    print("New file customer_datasource_cohort.csv done!")